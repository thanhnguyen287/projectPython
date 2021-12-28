from settings import *
from units import Villager
from math import floor, ceil

############################################################################################
#  DUE TO CIRCULAR IMPORTING ERROR I HAD TO MOVE THE BUILDINGS RELATED CODE TO UNITS.PY   #
############################################################################################

"""
class Building:
    population_produced = 0
    is_being_built = True
    construction_progress = 0

    def __init__(self, pos, map, player_owner_of_unit, ):
        self.owner = player_owner_of_unit
        self.rect = self.sprite.get_rect(topleft=pos)
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        self.map = map

        # will be used in the timer to increase resources of the player
        self.resource_manager_cooldown = pygame.time.get_ticks()

        self.current_health = 1
        self.is_alive = True

        self.image_select = pygame.image.load(os.path.join(assets_path, "image_select.png"))
        self.selected = False

        self.resource_manager_cooldown = pygame.time.get_ticks()
        #self.owner.pay_entity_cost(self)
        self.now = 0

    def update(self):
        pass


class TownCenter(Building):
    description = " Used to create villagers."
    construction_tooltip = " Build a Town Center"
    construction_cost = [1000, 0, 0, 100]
    construction_time = 8
    armor = 3

    def __init__(self, pos, map, player_owner_of_unit):

        self.name = "Town center"
        self.sprite = pygame.image.load(os.path.join(assets_path, "town_center.png"))

        self.construction_cost = [0, 0, 0, 0]

        self.max_health = 100
        #becomes true when you create villagers
        self.is_working = False
        #class of unit being trained
        self.unit_type_currently_trained = None
        player_owner_of_unit.max_population += 5
        #used when you order the creation of multiples units
        self.queue = 0
        self.resource_manager_cooldown = 0

        super().__init__(pos, map, player_owner_of_unit)

    # to create villagers, research techs and upgrade to second age
    def update(self):
        self.now = pygame.time.get_ticks()
        # add a button to stop the current action if the town center is working
        if self.is_working and not self.is_being_built:
            # if a villager is being created since 5 secs :
            if self.now - self.resource_manager_cooldown > 5000:
                self.resource_manager_cooldown = self.now
                # we determine the nearest free tile and spawn a villager on it
                self.check_collision_and_spawn_villager_where_possible()
                # decrease the queue
                self.queue -= 1
                # if there are no more villagers to train, we can stop there
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

    # we determine the nearest free tile, collision matrix has a 1 if the tile is free
    # we try the 4 tiles under the town center, then the ones on the sides, then the ones above
    # we also check if we stay in the map boundaries
    def check_collision_and_spawn_villager_where_possible(self):
        # UNDER
        #check if the tile is in the map boundaries and if tile is empty
        if 0 <= self.pos[0] < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and self.map.collision_matrix[self.pos[1] + 1][self.pos[0]] == 1:
            # new villager
            self.map.units[self.pos[0]][self.pos[1] + 1] = Villager((self.pos[0], self.pos[1] + 1), self.owner,
                                                                    self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0]] = 0

        elif 0 <= self.pos[0] + 1 < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and self.map.collision_matrix[self.pos[1] + 1][
            self.pos[0] + 1] == 1:
            # new villager
            self.map.units[self.pos[0] + 1][self.pos[1] + 1] = Villager((self.pos[0] + 1, self.pos[1] + 1),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0] + 1] = 0

        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] + 1][self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1] + 1] = Villager((self.pos[0] - 1, self.pos[1] + 1),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] + 1][self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1] + 1] = Villager((self.pos[0] + 2, self.pos[1] + 1),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0] + 2] = 0

        # SIDES
        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] < self.map.grid_length_y and self.map.collision_matrix[self.pos[1]][
            self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1]] = Villager((self.pos[0] - 1, self.pos[1]),
                                                                    self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1]][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] < self.map.grid_length_y and self.map.collision_matrix[self.pos[1]][
            self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1]] = Villager((self.pos[0] + 2, self.pos[1]),
                                                                    self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1]][self.pos[0] + 2] = 0

        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] - 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 1][self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1] - 1] = Villager((self.pos[0] - 1, self.pos[1] - 1),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 1][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] - 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 1][self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1] - 1] = Villager((self.pos[0] + 2, self.pos[1] - 1),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 1][self.pos[0] + 2] = 0


        # ABOVE
        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 2][self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1] - 2] = Villager((self.pos[0] - 1, self.pos[1] - 2),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and self.map.collision_matrix[self.pos[1] - 2][
            self.pos[0]] == 1:
            # new villager
            self.map.units[self.pos[0]][self.pos[1] - 2] = Villager((self.pos[0], self.pos[1] - 2),
                                                                    self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0]] = 0

        elif 0 <= self.pos[0] + 1 < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 1] == 1:
            # new villager
            self.map.units[self.pos[0] + 1][self.pos[1] - 2] = Villager((self.pos[0] + 1, self.pos[1] - 2),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1] - 2] = Villager((self.pos[0] + 2, self.pos[1] - 2),
                                                                        self.owner, self.map)
            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 2] = 0


class Farm(Building):
    description = " Provides 50 food every 5 seconds."
    construction_tooltip = " Build a Farm"
    construction_cost = [100, 0, 0, 0]
    construction_time = 4
    armor = 0

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = " Farm"
        self.sprite = pygame.image.load(os.path.join(assets_path, "Farm.png"))

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


class House(Building):
    description = " Each House increases the maximum population by 5."
    construction_tooltip = " Build a House"
    construction_cost = [600, 0, 0, 0]
    construction_time = 4
    armor = -2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "House"
        self.sprite = pygame.image.load(os.path.join(assets_path, "House.png"))

        self.construction_cost = [600, 0, 0, 0]
        self.max_health = 50
        player_owner_of_unit.max_population += 5

        super().__init__(pos, map, player_owner_of_unit)

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)
            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if self.now - self.resource_manager_cooldown > House.construction_time * 1000:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif self.now - self.resource_manager_cooldown > House.construction_time * 750:
                self.construction_progress = 75
            elif self.now - self.resource_manager_cooldown > House.construction_time * 500:
                self.construction_progress = 50
            elif self.now - self.resource_manager_cooldown > House.construction_time * 250:
                self.construction_progress = 25
"""