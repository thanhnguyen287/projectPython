from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.a_star import DiagonalMovement
from tech import Age_II, Age_III, Age_IV, iron_sword_tech, food_production_tech, steel_sword_tech, mithril_sword_tech, \
    iron_armor_tech, steel_armor_tech, mithril_armor_tech, improved_masonry_tech, reinforced_masonry_tech, \
    imbued_masonry_tech
import pygame
from math import ceil
from random import randint
from game.utils import tile_founding, GENERAL_UNIT_LIST, GENERAL_BUILDING_LIST, UNIT_TYPES, BUILDING_TYPES, SPEED_OF_BUILDING
from game.animation import BuildingDeathAnimation, VillagerAttackAnimation, VillagerMiningAnimation, \
    IdleDragonAnimation, DeathDragonAnimation


class Building:
    population_produced = 0
    is_being_built = True
    construction_progress = 0

    def __init__(self, pos, map, player_owner_of_unit, ):
        self.owner = player_owner_of_unit
        self.owner.building_list.append(self)
        GENERAL_BUILDING_LIST.append(self)

        #allows to test the types of target in game
        if type(self) not in BUILDING_TYPES:
            BUILDING_TYPES.append(type(self))

        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        self.map = map
        # updating map with the new unit, collision, etc...
        self.map.buildings[self.pos[0]][self.pos[1]] = self
        self.map.entities.append(self)
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = "building"
        # 0 means collision = True
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 0

        # will be used in the timer to increase resources of the player
        self.resource_manager_cooldown = pygame.time.get_ticks()

        self.current_health = 1
        self.is_alive = True

        #self.image_select = pygame.image.load(os.path.join(assets_path, "image_select.png"))
        self.selected = False

        self.resource_manager_cooldown = pygame.time.get_ticks()
        self.now = 0

    def update(self):
        pass


class Farm(Building):
    description = " Provides 50 food every 5 seconds."
    construction_tooltip = " Build a Farm"
    construction_cost = [100, 0, 0, 0]
    construction_time = 4/SPEED_OF_BUILDING
    armor = 0
    armor_age_bonus = 0

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = " Farm"

        self.construction_cost = [100, 0, 0, 0]

        self.max_health = 10
        self.max_population_bonus = 0

        super().__init__(pos, map, player_owner_of_unit)

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health * 0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health * 0.01)

            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if self.now - self.resource_manager_cooldown > Farm.construction_time * 1000:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif self.now - self.resource_manager_cooldown > Farm.construction_time * 750:
                self.construction_progress = 75
            elif self.now - self.resource_manager_cooldown > Farm.construction_time * 500:
                self.construction_progress = 50
            elif self.now - self.resource_manager_cooldown > Farm.construction_time * 250:
                self.construction_progress = 25

        else:
            #every 10 seconds, we get 10 food if tech_food has been researched
            if self.owner.tech_food_unlocked:
                if self.now - self.resource_manager_cooldown > 10000:
                    self.resource_manager_cooldown = self.now
                    self.owner.update_resource("FOOD", 10)


class TownCenter(Building):
    description = " Used to create villagers."
    construction_tooltip = " Build a Town Center"
    construction_cost = [1000, 0, 0, 100]
    construction_time = 8/SPEED_OF_BUILDING
    armor = 2
    armor_age_bonus = 1

    def __init__(self, pos, map, player_owner_of_unit):

        self.name = "Town center"
        # additional collision bc 2x1 building

        map.map[pos[0] + 1][pos[1]]["tile"] = "building"
        map.collision_matrix[pos[1]][pos[0] + 1] = 0

        map.map[pos[0]][pos[1] - 1]["tile"] = "building"
        map.collision_matrix[pos[1] - 1][pos[0]] = 0

        map.map[pos[0] + 1][pos[1] - 1]["tile"] = "building"
        map.collision_matrix[pos[1] - 1][pos[0] + 1] = 0

        self.construction_cost = [0, 0, 0, 0]

        self.max_health = 100
        #becomes true when you create villagers
        self.is_working = False
        #class of unit being trained
        self.unit_type_currently_trained = None
        player_owner_of_unit.max_population += 5
        #used when you order the creation of multiples units
        self.queue = 0
        armor = 3
        self.resource_manager_cooldown = 0

        super().__init__(pos, map, player_owner_of_unit)

    # to create villagers, research techs and upgrade to second age
    def update(self):
        self.now = pygame.time.get_ticks()
        # add a button to stop the current action if the town center is working
        if self.now - self.resource_manager_cooldown > 5000  and not self.is_being_built:
            self.resource_manager_cooldown = self.now
            if self.is_working:
            # if a villager is being created since 5 secs :
                # we determine the nearest free tile and spawn a villager on it
                self.spawn_villager()
                # decrease the queue
                self.queue -= 1
                # if there are no more villagers to train, we can stop there
                if self.queue <= 0:
                    self.is_working = False

            #every 5 sec, it regen 1 pv
            elif self.current_health < self.max_health:
                self.current_health += 1

        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            # the current life increases with the construction progress
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)

            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if self.now - self.resource_manager_cooldown > TownCenter.construction_time * 1000:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                # to fix a little bug
                self.current_health -= 1
                self.is_being_built = False
            elif self.now - self.resource_manager_cooldown > TownCenter.construction_time * 750:
                self.construction_progress = 75
            elif self.now - self.resource_manager_cooldown > TownCenter.construction_time * 500:
                self.construction_progress = 50
            elif self.now - self.resource_manager_cooldown > TownCenter.construction_time * 250:
                self.construction_progress = 25

    #trying to simplify that shit
    def spawn_villager(self):

        available_tile_for_spawn = tile_founding(1, 1, 2, self.map.map, self.owner, "")
        #print(available_tile_for_spawn[0][0])
        self.map.units[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]] = Villager((available_tile_for_spawn[0][0], available_tile_for_spawn[0][1]), self.owner,
                                                                    self.map)
        self.map.map[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]]["tile"] = "unit"
        self.map.map[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]]["collision"] = True

        # update collision for new villager
        self.map.collision_matrix[available_tile_for_spawn[0][1]][available_tile_for_spawn[0][0]] = 0

    def research_tech(self, tech):
        if tech == "Advance to Feudal Age":
            tech = Age_II
            self.owner.age = 2
        elif tech == "Advance to Castle Age":
            tech = Age_III
            self.owner.age = 3
        elif tech == "Advance to Imperial Age":
            tech = Age_IV
            self.owner.age = 4

        for resource_type in range(0, 3):
            self.owner.resources[resource_type] -= tech.construction_costs[resource_type]


    def train(self, unit_type):
        self.queue += 1
        # if the town center is not working
        if not self.is_working:
            self.unit_type_currently_trained = unit_type
            self.is_working = True
            self.resource_manager_cooldown = pygame.time.get_ticks()
        # pay training cost
        unit_type_trained = self.unit_type_currently_trained
        self.owner.pay_entity_cost_bis(unit_type_trained)


class House(Building):
    description = " Each House increases the maximum population by 5."
    construction_tooltip = " Build a House"
    construction_cost = [300, 0, 0, 50]
    construction_time = 4/SPEED_OF_BUILDING
    armor = -2
    armor_age_bonus = 2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "House"

        self.construction_cost = [600, 0, 0, 0]
        self.max_health = 50
        player_owner_of_unit.max_population += 5

        super().__init__(pos, map, player_owner_of_unit)
        self.death_animation_group = pygame.sprite.Group()
        self.death_animation = BuildingDeathAnimation(self, map.hud.all_buildings_death_animations["House"][player_owner_of_unit.color])
        #buildings death animation

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)
            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if progress_time_pourcent > 100:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif progress_time_pourcent > 75:
                self.construction_progress = 75
            elif progress_time_pourcent > 50:
                self.construction_progress = 50
            elif progress_time_pourcent > 25:
                self.construction_progress = 25


class Market(Building):
    description = " Used to research useful technologies."
    construction_tooltip = " Build a Market"
    construction_cost = [300, 0, 0, 50]
    construction_time = 15
    armor = -2
    armor_age_bonus = 2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "Market"

        self.construction_cost = [300, 0, 0, 50]
        self.max_health = 150

        super().__init__(pos, map, player_owner_of_unit)
        self.death_animation_group = pygame.sprite.Group()
        self.death_animation = BuildingDeathAnimation(self, map.hud.all_buildings_death_animations["House"][player_owner_of_unit.color])
        #buildings death animation

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)
            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if progress_time_pourcent > 100:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif progress_time_pourcent > 75:
                self.construction_progress = 75
            elif progress_time_pourcent > 50:
                self.construction_progress = 50
            elif progress_time_pourcent > 25:
                self.construction_progress = 25

    def research_tech(self, tech):
        # if iron swords has been researched, we increase all unit's dmg by 5.
        if tech == "Research Iron Swords":
            tech = iron_sword_tech
            tech.tech_increase_dmg(self.owner)
            self.owner.iron_swords_unlocked = True

        if tech == "Research Steel Swords":
            tech = steel_sword_tech
            tech.tech_increase_dmg(self.owner)
            self.owner.steel_swords_unlocked = True

        if tech == "Research Mithril Swords":
            tech = mithril_sword_tech
            tech.tech_increase_dmg(self.owner)
            self.owner.mithril_swords_unlocked = True

        if tech == "Research Iron Armors":
            tech = iron_armor_tech
            tech.tech_increase_armor(self.owner)
            self.owner.iron_armors_unlocked = True

        if tech == "Research Steel Armors":
            tech = steel_armor_tech
            tech.tech_increase_armor(self.owner)
            self.owner.steel_armors_unlocked = True

        if tech == "Research Mithril Armors":
            tech = mithril_armor_tech
            tech.tech_increase_armor(self.owner)
            self.owner.mithril_armors_unlocked = True


        if tech == "Research Improved Masonry":
            tech = improved_masonry_tech
            tech.tech_increase_armor(self.owner, for_building=True)
            tech.tech_increase_max_health(self.owner)
            self.owner.improved_masonry_unlocked = True

        if tech == "Research Reinforced Masonry":
            tech = reinforced_masonry_tech
            tech.tech_increase_armor(self.owner, for_building=True)
            tech.tech_increase_max_health(self.owner)
            self.owner.reinforced_masonry_unlocked = True

        if tech == "Research Imbued Masonry":
            tech = imbued_masonry_tech
            tech.tech_increase_armor(self.owner, for_building=True)
            tech.tech_increase_max_health(self.owner)
            self.owner.imbued_masonry_unlocked = True

        elif tech == "Research Iron Arrows":
            pass
        elif tech == "Research Iron Horseshoes":
            pass
        elif tech == "Research Super Cows":
            tech = food_production_tech
            self.owner.tech_food_unlocked = True

        for resource_type in range(0, 3):
            self.owner.resources[resource_type] -= tech.construction_costs[resource_type]


class Barracks(Building):
    description = " Used to train military units."
    construction_tooltip = " Build a Barrack"
    construction_cost = [500, 0, 0, 200]
    construction_time = 12/SPEED_OF_BUILDING
    armor = 2
    armor_age_bonus = 1

    def __init__(self, pos, map, player_owner_of_unit):

        self.name = "Barracks"
        # additional collision bc 2x1 building

        map.map[pos[0] + 1][pos[1]]["tile"] = "building"
        map.collision_matrix[pos[1]][pos[0] + 1] = 0

        map.map[pos[0]][pos[1] - 1]["tile"] = "building"
        map.collision_matrix[pos[1] - 1][pos[0]] = 0

        map.map[pos[0] + 1][pos[1] - 1]["tile"] = "building"
        map.collision_matrix[pos[1] - 1][pos[0] + 1] = 0

        self.construction_cost = [500, 0, 0, 200]

        self.max_health = 100
        #becomes true when you train units
        self.is_working = False
        #class of unit being trained
        self.unit_type_currently_trained = None
        #used when you order the creation of multiples units
        self.queue = 0
        armor = 3
        self.resource_manager_cooldown = 0

        super().__init__(pos, map, player_owner_of_unit)

    # to train units, research techs and upgrade to second age
    def update(self):
        self.now = pygame.time.get_ticks()
        if not self.is_being_built:
            if self.now - self.resource_manager_cooldown > 10000:
                self.resource_manager_cooldown = self.now
                if self.is_working:
                # if a clubman is being created since 10 secs :
                    # we determine the nearest free tile and spawn a villager on it
                    self.spawn_clubman()
                    # decrease the queue
                    self.queue -= 1
                    # if there are no more clubman to train, we can stop there
                    if self.queue <= 0:
                        self.is_working = False

        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            # the current life increases with the construction progress
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)

            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if self.now - self.resource_manager_cooldown > Barracks.construction_time * 1000:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                # to fix a little bug
                self.current_health -= 1
                self.is_being_built = False
            elif self.now - self.resource_manager_cooldown > Barracks.construction_time * 750:
                self.construction_progress = 75
            elif self.now - self.resource_manager_cooldown > Barracks.construction_time * 500:
                self.construction_progress = 50
            elif self.now - self.resource_manager_cooldown > Barracks.construction_time * 250:
                self.construction_progress = 25

    def train(self, unit_type):
        self.queue += 1
        # if the town center is not working
        if not self.is_working:
            self.unit_type_currently_trained = unit_type
            self.is_working = True
            self.resource_manager_cooldown = pygame.time.get_ticks()
        # pay training cost
        unit_type_trained = self.unit_type_currently_trained
        self.owner.pay_entity_cost_bis(unit_type_trained)

    def spawn_clubman(self):
        available_tile_for_spawn = tile_founding(1, 1, 2, self.map.map, self.owner, "")
        # print(available_tile_for_spawn[0][0])
        self.map.units[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]] = Clubman(
            (available_tile_for_spawn[0][0], available_tile_for_spawn[0][1]), self.owner,
            self.map)
        self.map.map[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]]["tile"] = "unit"
        self.map.map[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]]["collision"] = True

        # update collision for new villager
        self.map.collision_matrix[available_tile_for_spawn[0][1]][available_tile_for_spawn[0][0]] = 0


class Tower(Building):
    description = " Basic stone tower. Automatically attacks enemy units and buildings within range."
    construction_tooltip = " Build a Tower"
    construction_cost = [100, 0, 0, 75]
    construction_time = 4/SPEED_OF_BUILDING
    armor = -2
    armor_age_bonus = 2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "Tower"
        self.construction_cost = [100, 0, 0, 75]
        self.max_health = 200

        super().__init__(pos, map, player_owner_of_unit)
        #self.death_animation_group = pygame.sprite.Group()
        #self.death_animation = BuildingDeathAnimation(self, map.hud.all_buildings_death_animations["House"][player_owner_of_unit.color])
        #buildings death animation

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)
            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if progress_time_pourcent > 100:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif progress_time_pourcent > 75:
                self.construction_progress = 75
            elif progress_time_pourcent > 50:
                self.construction_progress = 50
            elif progress_time_pourcent > 25:
                self.construction_progress = 25


class Wall(Building):
    description = " Stone wall that is cheap and easy to build. Slows down your enemies and warns you of their approach."
    construction_tooltip = " Build a Wall"
    construction_cost = [0, 0, 0, 50]
    construction_time = 4
    armor = -2
    armor_age_bonus = 2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "Wall"

        self.construction_cost = [0, 0, 0, 50]
        self.max_health = 100
        # can be 0,1 or 2. 0 is for \ like wall and used by default, 1 for / wall and 2 for corners
        self.variation = 0

        super().__init__(pos, map, player_owner_of_unit)
        #self.death_animation_group = pygame.sprite.Group()
        #self.death_animation = BuildingDeathAnimation(self, map.hud.all_buildings_death_animations["House"][player_owner_of_unit.color])
        #buildings death animation

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)
            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if progress_time_pourcent > 100:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif progress_time_pourcent > 75:
                self.construction_progress = 75
            elif progress_time_pourcent > 50:
                self.construction_progress = 50
            elif progress_time_pourcent > 25:
                self.construction_progress = 25

    #variation should be 0,1 or 2.
    def change_angle(self, variation=None):
        if variation is None:
            self.variation = 1 if self.variation == 0 else 0
        else:
            self.variation = variation

# ****************************          UNITS         ***************************************


class Unit:
    armor = 0

    def __init__(self, pos, player_owner_of_unit, map, angle=225):
        self.owner = player_owner_of_unit
        self.map = map
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        #updating map with the new unit, collision, etc...
        self.map.units[self.pos[0]][self.pos[1]] = self
        self.map.entities.append(self)
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = "unit"
        # 0 means collision = True
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 0

        # we add the unit we created to the list of units of the player
        self.owner.unit_list.append(self)
        GENERAL_UNIT_LIST.append(self)
        self.owner.current_population += 1

        # allows to test the types of target in game
        if type(self) not in UNIT_TYPES:
            UNIT_TYPES.append(type(self))

        self.is_alive = True
        self.angle = angle
        self.sprite_index = 0
        #pathfinding
        self.move_timer = pygame.time.get_ticks()
        self.searching_for_path = False
        self.dest = None
        self.attack_cooldown = 0

    def move_to(self, new_tile):
        if not self.map.is_there_collision(new_tile["grid"]):
            self.searching_for_path = True
            self.dest = new_tile
            self.grid = Grid(matrix=self.map.collision_matrix)
            self.start = self.grid.node(self.pos[0], self.pos[1])
            self.end = self.grid.node(new_tile["grid"][0], new_tile["grid"][1])
            #finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

            # how far along the path are we
            self.path_index = 0
            self.path, runs = finder.find_path(self.start, self.end, self.grid)

    # returns True if entity is adjacent to unit/building calling it, else False
    def is_adjacent_to(self, entity):
        if (abs(self.pos[0] - entity.pos[0]) <= 1 and self.pos[1] == entity.pos[1]) or \
                (self.pos[0] == entity.pos[0] and abs(self.pos[1] - entity.pos[1]) <= 1):
            return True
        else:
            return False

    def change_tile(self, new_tile):
        # remove the unit from its current position on the map
        if self.pos != new_tile:
            if self.map.get_angle_between(self.pos, new_tile, self) != -1:
                self.angle = self.map.get_angle_between(self.pos, new_tile, self)

        self.map.units[self.pos[0]][self.pos[1]] = None
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = ""
        #remove collision from old position
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 1
        # update the map
        self.map.units[new_tile[0]][new_tile[1]] = self
        self.pos = tuple(self.map.map[new_tile[0]][new_tile[1]]["grid"])
        #update collision for new tile
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 0
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = "unit"

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.searching_for_path and self.now - self.move_timer > 1000:
            while self.path[self.path_index] == self.pos:
                self.path_index += 1
            new_pos = self.path[self.path_index]
            #update position in the world
            self.change_tile(new_pos)
            self.path_index += 1
            self.move_timer = self.map.timer
            if self.path_index == len(self.path):
                self.searching_for_path = False


class Villager(Unit):

    # Training : 50 FOOD, 20s
    description = " Your best friend. Can work, fight and gather resources."
    construction_tooltip = " Train a Villager"
    name = "Villager"
    attack_speed = 500

    construction_cost = [0, 10, 25, 0]
    construction_time = 5
    population_produced = 1

    def __init__(self, pos, player_owner_of_unit, map, angle=225):

        self.name = "Villager"
        # DISPLAY
        # DATA
        self.max_health = 25
        self.current_health = self.max_health
        self.attack_dmg = 3
        self.attack_speed = 1500
        self.movement_speed = 1.1
        # unit type : melee
        self.is_on_tile = True
        self.range = 0
        # used to gather ressources
        # between 0 and 360, 0 being top, 90 right, etc.... Only 0, 45, 90, 135, etc (up to 360 ofc) supported for now

        self.display_pos = pos

        #to build
        self.is_moving_to_build = False
        self.building_to_create = None

        #to gather
        self.is_moving_to_gather = False
        self.targeted_ressource = None

        #to attack
        self.is_moving_to_attack = False
        self.target = None
        self.strike = 0

        self.is_building = False
        self.is_gathering = False
        self.is_attacking = False

        self.stack_max = 30
        self.gathered_ressource_stack = 0
        self.stack_type = None

        #Training : 25 food and 10 gold, 2s
        self.construction_cost = [0, 25, 10, 0]
        self.construction_time = 5
        self.population_produced = 1
        self.now = 0

        super().__init__(pos, player_owner_of_unit, map, angle)
        self.owner.unit_occupied.append(0)
        #attack animation
        self.attack_animation_group = pygame.sprite.Group()
        self.attack_animation = VillagerAttackAnimation(self, map.hud.villager_attack_animations["Villager"]["sprites"][
            player_owner_of_unit.color])
        #mining animation
        self.mining_animation_group = pygame.sprite.Group()
        self.mining_animation = VillagerMiningAnimation(self, map.hud.mining_sprites_villager[
            player_owner_of_unit.color])

    def go_to_townhall(self):
        if not self.searching_for_path:
            pos_list = tile_founding(10, 1, 1, self.map.map, self.owner, "")
            r = randint(0, len(pos_list) - 1)
            pos = pos_list[r]
            tile = self.map.map[pos[0]][pos[1]]
            self.move_to(tile)

        if (abs(self.pos[0] - self.owner.towncenter_pos[0]) <= 1 and
                abs(self.pos[1] - self.owner.towncenter_pos[1]) <= 1) or \
                (abs(self.pos[0] - (self.owner.towncenter_pos[0]+1)) <= 1 and
                 abs(self.pos[1] - (self.owner.towncenter_pos[1]-1)) <= 1):
            if self.stack_type == "tree":
                self.owner.update_resource("WOOD", self.gathered_ressource_stack)
            elif self.stack_type == "rock":
                self.owner.update_resource("STONE", self.gathered_ressource_stack)
            elif self.stack_type == "gold":
                self.owner.update_resource("GOLD", self.gathered_ressource_stack)
            elif self.stack_type == "berrybush":
                self.owner.update_resource("FOOD", self.gathered_ressource_stack)

            self.gathered_ressource_stack = 0
            self.stack_type = None

    def repair(self, building):
        if building.current_health != building.max_health:
            ...
        else:
            ...

    def go_to_attack(self, pos):
        if self.map.get_empty_adjacent_tiles(pos):
            unit_dest = self.map.get_empty_adjacent_tiles(pos)[0]
            self.move_to(self.map.map[unit_dest[0]][unit_dest[1]])
            self.is_moving_to_attack = True

            if self.map.map[pos[0]][pos[1]]["tile"] == "building":
                for b in GENERAL_BUILDING_LIST:
                    if b.pos == pos:
                        self.target = b
                        break
            else:
                for u in GENERAL_UNIT_LIST:
                    if u.pos == pos:
                        self.target = u
                        break

    def attack(self):
        if abs(self.pos[0] - self.target.pos[0]) <= 1 and abs(self.pos[1] - self.target.pos[1]) <= 1:

            self.angle = self.map.get_angle_between(self.pos, self.target.pos, self)

            if self.is_attacking and (self.now - self.attack_cooldown > self.attack_speed):

                if self.target.current_health > 0:
                    #if the target is a building, our damage are divided by 2
                    if type(self.target) in BUILDING_TYPES:
                        dmg = int((self.attack_dmg/2) - self.target.armor)
                    #else its normal damage
                    else:
                        dmg = int(self.attack_dmg - self.target.armor)
                    #if the damage is 0 or less, it is still 1
                    if dmg <= 0: dmg = 1
                    self.target.current_health -= dmg
                    self.attack_cooldown = self.now
                    self.strike += 1

                # else the unit is dead
                else:
                    tile = self.map.map[self.target.pos[0]][self.target.pos[1]]
                    tile["tile"] = ""
                    if type(self.target) == TownCenter:
                        self.target.owner.towncenter = None
                    tile["collision"] = False
                    self.map.collision_matrix[tile["grid"][1]][tile["grid"][0]] = 1
                    self.target = None
                    self.is_attacking = False
                    self.attack_animation.to_be_played = False
                    self.strike = 0

            if self.target is not None and type(self.target) == Villager and \
                    not self.target.is_attacking and self.strike > 1:
                self.target.target = self
                self.target.is_attacking = True
                self.target.attack()
        else:
            if self.target in GENERAL_UNIT_LIST:
                ind = GENERAL_UNIT_LIST.index(self.target)
                pos = GENERAL_UNIT_LIST[ind].pos
                self.go_to_attack(pos)
            elif self.target in GENERAL_BUILDING_LIST:
                ind = GENERAL_BUILDING_LIST.index(self.target)
                pos = GENERAL_BUILDING_LIST[ind].pos
                self.go_to_attack(pos)

    def go_to_build(self, pos, name):
        if self.map.get_empty_adjacent_tiles(pos):
            villager_dest = self.map.get_empty_adjacent_tiles(pos)[0]
            self.move_to(self.map.map[villager_dest[0]][villager_dest[1]])
            self.is_moving_to_build = True

            self.building_to_create = {"name": name, "pos": pos, "has_construction_started": False}

    def build(self):
        self.is_moving_to_build = False
        if self.building_to_create is not None:
            self.angle = self.map.get_angle_between(self.pos, self.building_to_create["pos"], self)

        new_building = None
        if self.building_to_create["name"] == "Farm":
            new_building = Farm((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                self.owner)

        elif self.building_to_create["name"] == "TownCenter":
            new_building = TownCenter((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                      self.owner)
            # additional collision bc town center is 2x2 tile, not 1x1
            self.map.collision_matrix[self.building_to_create["pos"][1]][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0]] = 0

        elif self.building_to_create["name"] == "House":
            new_building = House((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                 self.owner)

        elif self.building_to_create["name"] == "Tower":
            new_building = Tower((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                 self.owner)

        elif self.building_to_create["name"] == "Wall":
            new_building = Wall((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                 self.owner)

        elif self.building_to_create["name"] == "Barracks":
            new_building = Barracks((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                 self.owner)
            # additional collision bc barrack is 2x2 tile, not 1x1
            self.map.collision_matrix[self.building_to_create["pos"][1]][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0]] = 0

        elif self.building_to_create["name"] == "Market":
            new_building = Market((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map, self.owner)

        # to add it to the entities list on our map
        self.map.entities.append(new_building)
        self.map.buildings[self.building_to_create["pos"][0]][
            self.building_to_create["pos"][1]] = new_building
        # we pay the construction cost
        self.owner.pay_entity_cost_bis(self.building_to_create["name"])
        # we actualize collision
        self.map.collision_matrix[self.building_to_create["pos"][1]][
            self.building_to_create["pos"][0]] = 0

        pos_x = self.building_to_create["pos"][0]
        pos_y = self.building_to_create["pos"][1]
        self.map.map[pos_x][pos_y]["tile"] = "building"
        self.building_to_create["has_construction_started"] = True

    def go_to_ressource(self, pos):
        # if the ressource is near us, we directly gather it
        if (abs(pos[0] - self.pos[0]) <= 1 and abs(pos[1] - self.pos[1]) == 0) or \
                (abs(pos[0] - self.pos[0]) == 0 and abs(pos[1] - self.pos[1]) <= 1):
            self.targeted_ressource = (pos[0], pos[1])
            self.is_gathering = True

        # else we go to an adjacent tile
        else:
            if 0 <= pos[0] - 1 < self.map.grid_length_x and self.map.map[pos[0] - 1][pos[1]]["tile"] == "":
                self.move_to(self.map.map[pos[0] - 1][pos[1]])
                self.targeted_ressource = (pos[0], pos[1])
                self.is_moving_to_gather = True

            elif 0 <= pos[0] + 1 < self.map.grid_length_x and self.map.map[pos[0] + 1][pos[1]]["tile"] == "":
                self.move_to(self.map.map[pos[0] + 1][pos[1]])
                self.targeted_ressource = (pos[0], pos[1])
                self.is_moving_to_gather = True

            elif 0 <= pos[1] - 1 < self.map.grid_length_y and self.map.map[pos[0]][pos[1] - 1]["tile"] == "":
                self.move_to(self.map.map[pos[0]][pos[1] - 1])
                self.targeted_ressource = (pos[0], pos[1])
                self.is_moving_to_gather = True

            elif 0 <= pos[0] + 1 < self.map.grid_length_y and self.map.map[pos[0]][pos[1] + 1]["tile"] == "":
                self.move_to(self.map.map[pos[0]][pos[1] + 1])
                self.targeted_ressource = (pos[0], pos[1])
                self.is_moving_to_gather = True

            else:
                self.targeted_ressource = None

    def gather_ressources(self):
        if self.targeted_ressource is not None and type(self.targeted_ressource) != Villager:
            this_target = self.map.map[self.targeted_ressource[0]][self.targeted_ressource[1]]
            self.angle = self.map.get_angle_between(self.pos, self.targeted_ressource, self)

            if self.is_gathering and (self.now - self.attack_cooldown > self.attack_speed):

                if this_target["health"] > self.attack_dmg:
                    this_target["health"] -= self.attack_dmg
                    self.attack_cooldown = self.now
                # no resource is remaining, we destroy it and give resource to the player:
                else:
                    if this_target["tile"] == "tree":
                        self.stack_type = "tree"
                        self.gathered_ressource_stack += 10
                    elif this_target["tile"] == "rock":
                        self.stack_type = "rock"
                        self.gathered_ressource_stack += 10
                    elif this_target["tile"] == "gold":
                        self.stack_type = "gold"
                        self.gathered_ressource_stack += 10
                    elif this_target["tile"] == "berrybush":
                        self.stack_type = "berrybush"
                        self.gathered_ressource_stack += 10

                    this_target["tile"] = ""
                    this_target["collision"] = False
                    self.map.collision_matrix[this_target["grid"][1]][this_target["grid"][0]] = 1
                    self.targeted_ressource = None
                    self.is_gathering = False
                    self.attack_animation.to_be_played = False

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.move_timer > 400:
            if self.searching_for_path:

                # movement
                # for debug, because the first tile of our path is the pos of unit, not the first tile where we must go
                if self.path_index < len(self.path) and self.path[self.path_index] == self.pos:
                    self.path_index += 1
                #print("debug path index, path)", self.path_index, len(self.path))
                if len(self.path) != 0:
                    new_pos = self.path[self.path_index]
                    #update position in the world
                    self.change_tile(new_pos)

                self.path_index += 1
                if self.path_index == len(self.path):
                    self.searching_for_path = False
                    self.is_on_tile = True
                    if self.is_moving_to_build:
                        self.is_building = True
                        self.build()
                        self.is_moving_to_build = False
                    elif self.is_moving_to_attack:
                        self.is_attacking = True
                        self.is_moving_to_attack = False
                    elif self.is_moving_to_gather:
                        self.is_gathering = True
                        self.is_moving_to_gather = False
            else:
                ...

            #always at the end to reset the timer
            self.move_timer = self.now

        if self.is_gathering:
            self.gather_ressources()

        if self.is_attacking:
            self.attack()


    def print_state(self):
        print("I am ", self)
        print("Gathering : ", self.is_gathering)
        print("Moving to gather : ", self.is_moving_to_gather)
        print("stack", self.gathered_ressource_stack)
        print("Building to create: ", self.building_to_create)
        print("Building : ", self.is_building)
        print("Moving to build : ", self.is_moving_to_build)
        print("Moving : ", self.searching_for_path)

        if self.searching_for_path:
            print("Current pos : ", self.pos)
            print("Starting pos : ", self.start)


class Bowman(Unit):

    def __init__(self, pos, player_owner_of_unit, map):
        super().__init__(pos, player_owner_of_unit, map)

        #DISPLAY
        self.sprite = None
        self.name = "Bowman"

        # DATA
        self.max_health = 35
        self.current_health = self.max_health
        self.attack = 3
        self.attack_speed = 1.4
        self.movement_speed = 1.2
        # unit type : distance
        self.range = 5
        #Training : 20 WOOD, 40 FOOD, 30s
        self.training_cost = [20, 40, 0, 0]
        self.training_time = 30
        self.population_produced = 1
        self.description = "Basic ranged unit."
        self.construction_tooltip = " Train a Bowman"


class Clubman(Unit):

    # Training : 50 food, 100gold, 5s
    description = "  The first and most basic infantry unit. BAGARREEE"
    construction_tooltip = " Train a Clubman"
    name = "Clubman"
    attack_speed = 500

    construction_cost = [0, 100, 50, 0]
    construction_time = 26
    population_produced = 1

    def __init__(self, pos, player_owner_of_unit, map, angle=225):

        #DISPLAY
        self.name = "Clubman"

        # DATA
        self.max_health = 75
        self.current_health = self.max_health
        self.attack_dmg = 10
        self.attack_speed = 1500
        self.movement_speed = 1.2
        # unit type : melee
        self.range = 0
        #Training : 50 FOOD, 26s
        self.training_cost = [0, 100, 50, 0]


        #Training :  100 food and 50 gold, 2s
        self.construction_cost = [0, 100, 50, 0]
        self.construction_time = 26
        self.population_produced = 1
        self.now = 0
        super().__init__(pos, player_owner_of_unit, map, angle)

        # attack animation
        self.attack_animation_group = pygame.sprite.Group()
        self.attack_animation = VillagerAttackAnimation(self, map.hud.villager_attack_animations["Clubman"]["sprites"][
            player_owner_of_unit.color])

        self.is_on_tile = True
        # used to gather ressources
        self.display_pos = pos

        #to attack
        self.is_moving_to_attack = False
        self.target = None
        self.strike = 0

        self.is_attacking = False

    def go_to_attack(self, pos):
        if self.map.get_empty_adjacent_tiles(pos):
            unit_dest = self.map.get_empty_adjacent_tiles(pos)[0]
            self.move_to(self.map.map[unit_dest[0]][unit_dest[1]])
            self.is_moving_to_attack = True

            if self.map.map[pos[0]][pos[1]]["tile"] == "building":
                for b in GENERAL_BUILDING_LIST:
                    if b.pos == pos:
                        self.target = b
                        break
            else:
                for u in GENERAL_UNIT_LIST:
                    if u.pos == pos:
                        self.target = u
                        break

    def attack(self):
        if abs(self.pos[0] - self.target.pos[0]) <= 1 and abs(self.pos[1] - self.target.pos[1]) <= 1:

            self.angle = self.map.get_angle_between(self.pos, self.target.pos, self)

            if self.is_attacking and (self.now - self.attack_cooldown > self.attack_speed):

                if self.target.current_health >= 0:
                    #if the target is a building, our damage are divided by 2
                    if type(self.target) in BUILDING_TYPES:
                        dmg = int((self.attack_dmg/2) - self.target.armor)
                    #else its normal damage
                    else:
                        dmg = int(self.attack_dmg - self.target.armor)
                    #if the damage is 0 or less, it is still 1
                    if dmg <= 0: dmg = 1
                    self.target.current_health -= dmg
                    self.attack_cooldown = self.now
                    self.strike += 1

                # else the unit is dead
                else:
                    tile = self.map.map[self.target.pos[0]][self.target.pos[1]]
                    tile["tile"] = ""
                    if type(self.target) == TownCenter:
                        self.target.owner.towncenter = None
                    tile["collision"] = False
                    self.map.collision_matrix[tile["grid"][1]][tile["grid"][0]] = 1
                    self.target = None
                    self.is_attacking = False
                    self.attack_animation.to_be_played = False
                    self.strike = 0

            if self.target is not None and type(self.target) == Villager and \
                    not self.target.is_attacking and self.strike > 1:
                self.target.target = self
                self.target.is_attacking = True
                self.target.attack()
        else:
            if self.target in GENERAL_UNIT_LIST:
                ind = GENERAL_UNIT_LIST.index(self.target)
                pos = GENERAL_UNIT_LIST[ind].pos
                self.go_to_attack(pos)
            elif self.target in GENERAL_BUILDING_LIST:
                ind = GENERAL_BUILDING_LIST.index(self.target)
                pos = GENERAL_BUILDING_LIST[ind].pos
                self.go_to_attack(pos)

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.move_timer > 400:
            if self.searching_for_path:
                # movement
                # for debug, because the first tile of our path is the pos of unit, not the first tile where we must go
                if self.path_index < len(self.path) and self.path[self.path_index] == self.pos:
                    self.path_index += 1
                #print("debug path index, path)", self.path_index, len(self.path))
                if len(self.path) > self.path_index:
                    new_pos = self.path[self.path_index]
                    #update position in the world
                    self.change_tile(new_pos)

                self.path_index += 1
                if self.path_index == len(self.path):
                    self.searching_for_path = False
                    self.is_on_tile = True
                    if self.is_moving_to_attack:
                        self.is_attacking = True
                        self.is_moving_to_attack = False
            else:
                ...

            #always at the end to reset the timer
            self.move_timer = self.now

        if self.is_attacking:
            self.attack()


class Dragon(Unit):

    # Training : 50 FOOD, 20s
    description = " Big. Deadly. Breath fire. What else ? "
    construction_tooltip = " Train a Dragon"
    name = "Black Dragon"
    attack_speed = 500

    construction_cost = [0, 10, 25, 0]
    construction_time = 5
    population_produced = 1

    def __init__(self, pos, player_owner_of_unit, map, angle=180):

        self.name = "Black Dragon"
        # DISPLAY
        # DATA
        self.max_health = 1000
        self.current_health = self.max_health
        self.attack_dmg = 150
        self.attack_speed = 1500
        self.movement_speed = 1.1
        # unit type : melee
        self.is_on_tile = True
        self.range = 0
        # used to gather ressources
        # between 0 and 360, 0 being top, 90 right, etc.... Only 0, 45, 90, 135, etc (up to 360 ofc) supported for now

        self.display_pos = pos

        #to attack
        self.is_moving_to_attack = False
        self.target = None
        self.strike = 0

        self.is_attacking = False


        #Training : 25 food and 10 gold, 2s
        self.construction_cost = [0, 25, 10, 0]
        self.construction_time = 5
        self.population_produced = 1
        self.now = 0

        super().__init__(pos, player_owner_of_unit, map, angle)
        self.owner.unit_occupied.append(0)
        #attack animation - None for now
       # self.attack_animation_group = pygame.sprite.Group()
        #self.attack_animation = VillagerAttackAnimation(self, map.hud.dragon_sprites[["Villager"]["sprites"][
        #    player_owner_of_unit.color])

        #idle animation
        self.idle_animation_group = pygame.sprite.Group()
        self.idle_animation = IdleDragonAnimation(self, map.hud.dragon_sprites["idle"])

        #death animation
       # self.death_animation_group = pygame.sprite.Group()
#        self.death_animation = DeathDragonAnimation(self, map.hud.dragon_sprites["death"])

    def go_to_attack(self, pos):
        if self.map.get_empty_adjacent_tiles(pos):
            unit_dest = self.map.get_empty_adjacent_tiles(pos)[0]
            self.move_to(self.map.map[unit_dest[0]][unit_dest[1]])
            self.is_moving_to_attack = True

            if self.map.map[pos[0]][pos[1]]["tile"] == "building":
                for b in GENERAL_BUILDING_LIST:
                    if b.pos == pos:
                        self.target = b
                        break
            else:
                for u in GENERAL_UNIT_LIST:
                    if u.pos == pos:
                        self.target = u
                        break

    def attack(self):
        if self.target is not None:
            if abs(self.pos[0] - self.target.pos[0]) <= 1 and abs(self.pos[1] - self.target.pos[1]) <= 1:
                possible_angles_list = (0, 90, 180, 270)
                if self.map.get_angle_between(self.pos, self.target.pos, self) in possible_angles_list:
                    self.angle = self.map.get_angle_between(self.pos, self.target.pos, self)

                if self.is_attacking and (self.now - self.attack_cooldown > self.attack_speed):
                    self.map.hud.boom_animation.play(self.map.grid_to_display_pos(self.target.pos))
                    if self.target.current_health >= 0:
                        #if the target is a building, our damage are divided by 2
                        if type(self.target) in BUILDING_TYPES:
                            dmg = int((self.attack_dmg/2) - self.target.armor)
                        #else its normal damage
                        else:
                            dmg = int(self.attack_dmg - self.target.armor)
                        #if the damage is 0 or less, it is still 1
                        if dmg <= 0: dmg = 1
                        self.target.current_health -= dmg
                        self.attack_cooldown = self.now
                        self.strike += 1

                    # else the unit is dead
                    else:
                        tile = self.map.map[self.target.pos[0]][self.target.pos[1]]
                        tile["tile"] = ""
                        if type(self.target) == TownCenter:
                            self.target.owner.towncenter = None
                        tile["collision"] = False
                        self.map.collision_matrix[tile["grid"][1]][tile["grid"][0]] = 1
                        self.target = None
                        self.is_attacking = False
                        #self.attack_animation.to_be_played = False
                        self.strike = 0

                if self.target is not None and type(self.target) == Villager and \
                        not self.target.is_attacking and self.strike > 1:
                    self.target.target = self
                    self.target.is_attacking = True
                    self.target.attack()
            else:
                ind = GENERAL_UNIT_LIST.index(self.target)
                pos = GENERAL_UNIT_LIST[ind].pos
                self.go_to_attack(pos)

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.move_timer > 400:
            if self.searching_for_path:

                # movement
                # for debug, because the first tile of our path is the pos of unit, not the first tile where we must go
                if self.path_index < len(self.path) and self.path[self.path_index] == self.pos:
                    self.path_index += 1
                #print("debug path index, path)", self.path_index, len(self.path))
                if len(self.path) > self.path_index:
                    new_pos = self.path[self.path_index]
                    #update position in the world
                    self.change_tile(new_pos)

                self.path_index += 1
                if self.path_index == len(self.path):
                    self.searching_for_path = False
                    self.is_on_tile = True
                    if self.is_moving_to_attack:
                        self.is_attacking = True
                        self.is_moving_to_attack = False

            #always at the end to reset the timer
            self.move_timer = self.now

        if self.is_attacking:
            self.attack()

    #modified change_tile fonction for dragon because we don't have 8 angles for our sprites but only 4.
    def change_tile(self, new_tile):
        # remove the unit from its current position on the map
        possible_angles_list = (0, 90, 180, 270)
        if self.pos != new_tile:
            if self.map.get_angle_between(self.pos, new_tile, self) in possible_angles_list:
                self.angle = self.map.get_angle_between(self.pos, new_tile, self)

        self.map.units[self.pos[0]][self.pos[1]] = None
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = ""
        #remove collision from old position
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 1
        # update the map
        self.map.units[new_tile[0]][new_tile[1]] = self
        self.pos = tuple(self.map.map[new_tile[0]][new_tile[1]]["grid"])
        #update collision for new tile
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 0
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = "unit"