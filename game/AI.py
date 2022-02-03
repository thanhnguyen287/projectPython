from player import player_list
from .utils import tile_founding, better_look_around, RESSOURCE_LIST
from units import Villager
from random import randint, random
from settings import MAP_SIZE_X, MAP_SIZE_Y


class AI:

    def __init__(self, player, map):
        self.player = player
        self.map = map
        self.tc_pos = self.player.towncenter_pos

        self.behaviour = "neutral"

        # the range (in layers) that the AI will go to. It increase when the AI becomes stronger
        # or is lacking ressources
        self.range = 3

        # this will be used to know if the AI needs to gather or not, and to expand or not
        self.needed_ressource = []

        # number of each ressource needed per villager
        self.base_quantity_of_each_ressource = [150, 50, 25, 100]
        self.quantity_of_each_ressource = self.base_quantity_of_each_ressource

        # the building we are aiming to build
        self.goal_building = None

        # a list of tiles to manage the gathering of ressources with the multiple units
        self.targeted_tiles = []

        # a list of the tiles where buildings are being built, to not build more on it
        self.in_building_tiles = []

        # a list of enemy units focused
        self.units_focused = []

        # to know if we are developping pop or not to know if we can build a building or not
        self.dev_pop = False

    # ==================================================================================================================
    # ----------------------------------------CONTROL AND RUNNING FUNCTIONS---------------------------------------------
    # ==================================================================================================================

    def chose_behaviour(self):
        # welook at the enemy units within 10 tiles of our town center to know if we should go in defense mode
        for p in player_list:
            if p != self.player:
                if self.behaviour == "defense":
                    break
                for u in p.unit_list:
                    if self.behaviour == "defense":
                        break
                    # if a enemy unit is in a 10 tiles range of the towncenter
                    if abs(self.tc_pos[0] - u.pos[0]) <= 1 and abs(self.tc_pos[1] - u.pos[1]) <= 1:  # in tiles
                        self.behaviour = "defense"
                        break
        # if we are the strongest we attack !
        if self.is_stronger():
            self.behaviour = "attack"
        # if we dont attack not defend, we are neutral
        elif self.behaviour != "defense":
            self.behaviour = "neutral"

        # at the end, we try to expand (go to expand method to see the conditions)
        self.expand()

    # this needs a little correction, it is too... confident
    def expand(self):
        # the idea is that the AI will check if she is stronger to know if she can expand
        if self.is_stronger():
            self.range += 1

        # WARNING i will modify this so the AI expand only if a ressource she needs is lacking
        # or if she is neutral but lacking ressources to gather
        elif self.behaviour == "neutral" and self.range < MAP_SIZE_X and self.range < MAP_SIZE_Y:
            ressources_available = []
            for r in self.needed_ressource:
                ressources_available = []
                tiles_to_gather = tile_founding(len(self.player.unit_list), 1, self.range, self.map, self.player, r)
                if len(tiles_to_gather) >= len(self.player.unit_list):
                    ressources_available.append(True)
                else:
                    ressources_available.append(False)

            if self.needed_ressource and True not in ressources_available:
                self.range += 1
                print(self.range)


    def run(self):
        if self.player.towncenter is not None:
            # looking at state of the game to chose mode (we should look every 5 seconds or so)
            self.chose_behaviour()

            if self.behaviour == "neutral":
                self.neutral_routine()
            elif self.behaviour == "defense":
                self.defense_routine()
            elif self.behaviour == "attack":
                self.attack_routine()


    # ==================================================================================================================
    # ------------------------------------------------MAIN ROUTINES-----------------------------------------------------
    # ==================================================================================================================

    # gather, build, spawn villagers
    def neutral_routine(self):
        # we just send a unit randomly to try to destroy the enemy townhall, if everything is correct the enemy AI will
        #kill the unit
        #self.poking_routine()


        self.planning_gathering()

        # if we dont need ressources, we are not training units, we have free pop space and we have at least as many
        # buildings as units, then we can train a new unit
        if not self.needed_ressource and self.player.towncenter.queue == 0 and \
                self.player.current_population < self.player.max_population and \
                len(self.player.building_list) >= len(self.player.unit_list):

            self.population_developpement_routine()
            self.dev_pop = True

        # if we dont train unit, we will try to gather or to build
        else:
            for u in self.player.unit_list:

                # if we need ressources and the unit is a villager and he is free, he will go gather
                if self.needed_ressource and isinstance(u, Villager) and u.building_to_create is None and \
                        not self.dev_pop and not u.is_moving_to_attack and u.target is None:
                    if u.gathered_ressource_stack < u.stack_max:
                        self.gathering_routine(u)
                    else:
                        u.go_to_townhall()

                # if we dont need ressources or when the villager is building, we are using the building routine
                elif isinstance(u, Villager) and (not self.dev_pop or u.building_to_create is not None) \
                        and not u.is_moving_to_attack and u.target is None:
                    self.building_routine(u)

        for u in self.player.unit_list:
            if u.is_moving_to_gather and not u.searching_for_path:
                u.is_moving_to_gather = False
                print("reset")

        self.free_tiles()
        self.dev_pop = False

    def defense_routine(self):
        for p in player_list:
            if p != self.player:
                for u in p.unit_list:
                    if abs(self.tc_pos[0] - u.pos[0]) <= 1 and abs(self.tc_pos[1] - u.pos[1]) <= 1 \
                            and not u in self.units_focused:  # in tiles

                        for my_u in self.player.unit_list:
                            # et rajouter si le type de l'unité n'est pas un villageois
                            self.reset_villager(my_u)

                            if my_u.target is None and not u in self.units_focused:
                                my_u.go_to_attack(u.pos)
                            self.units_focused.append(u)
        #creer une routine de repli des villageois près de l'hotel de ville


    def attack_routine(self):
        pass

    # TODO

    # ==================================================================================================================
    # -------------------------------------------------SUB ROUTINES-----------------------------------------------------
    # ==================================================================================================================

    def gathering_routine(self, unit):
        for r in self.needed_ressource:
            if unit.targeted_ressource is None:
                ressource = None
                if r == "wood": ressource = "tree"
                elif r == "stone": ressource = "rock"
                elif r == "gold": ressource = "gold"
                elif r == "berrybush": ressource = "food"

                if unit.gathered_ressource_stack == 0 or unit.stack_type == ressource:
                    tiles_to_gather = tile_founding(10, 1, self.range, self.map, self.player, r)
                    found = False
                    for i in range(len(tiles_to_gather)):
                        if tiles_to_gather:
                            pos_x = tiles_to_gather[i][0]
                            pos_y = tiles_to_gather[i][1]
                            if better_look_around(unit.pos, (pos_x, pos_y), self.map) and not found and \
                                    (pos_x, pos_y) not in self.targeted_tiles:
                                unit.go_to_ressource(tiles_to_gather[i])
                                self.targeted_tiles.append((pos_x, pos_y))
                                found = True

                else:
                    unit.go_to_townhall()

    def building_routine(self, unit):
        #if we have a building we want to build, we wait until we have the ressources and we
        if self.goal_building is not None:
            print("in goal building")
            can_afford = []
            for r in range(len(self.player.resources)):
                if self.player.resources[r] >= self.player.entity_costs[self.goal_building][RESSOURCE_LIST[r]]:
                    can_afford.append(True)
                else:
                    can_afford.append(False)

            if unit.building_to_create is None and False not in can_afford:
                tiles_to_build = tile_founding(10, 2, self.range, self.map, self.player, "")
                for i in range(len(tiles_to_build)):
                    if tiles_to_build:
                        random_number = randint(0, len(tiles_to_build) - 1)
                        if len(tiles_to_build) >= 2 and tiles_to_build[random_number] not in self.in_building_tiles \
                                and unit.building_to_create is None:
                            unit.go_to_build(tiles_to_build[random_number], self.goal_building)
                            self.in_building_tiles.append(tiles_to_build[random_number])
                            self.goal_building = None
                            self.quantity_of_each_ressource = self.base_quantity_of_each_ressource

        # if we have more than 90% of our pop capacity occupied, we build a house
        elif self.player.current_population >= 0.8 * self.player.max_population:
            # we check if the player has enough ressource to build
            can_afford = []
            for r in range(len(self.player.resources)):
                if self.player.resources[r] >= self.player.entity_costs["House"][RESSOURCE_LIST[r]]:
                    can_afford.append(True)
                elif self.quantity_of_each_ressource[r] < self.player.entity_costs["House"][RESSOURCE_LIST[r]]:
                    can_afford.append(False)
                    self.quantity_of_each_ressource[r] = self.player.entity_costs["House"][RESSOURCE_LIST[r]]
                    self.goal_building = "House"
                else:
                    can_afford.append(False)

            if unit.building_to_create is None and False not in can_afford:
                tiles_to_build = tile_founding(10, 2, self.range, self.map, self.player, "")
                for i in range(len(tiles_to_build)):
                    if tiles_to_build:
                        random_number = randint(0, len(tiles_to_build) - 1)
                        if len(tiles_to_build) >= 2 and tiles_to_build[random_number] not in self.in_building_tiles \
                                and unit.building_to_create is None:
                            unit.go_to_build(tiles_to_build[random_number], "House")
                            self.in_building_tiles.append(tiles_to_build[random_number])


        # /!\ with the "elif" we can only build 1 building after 1 building

        #we are currently always trying to build a farm if we are in the building routine
        else:
            # we check if the player has enough ressource to build
            can_afford = []
            for r in range(len(self.player.resources)):
                if self.player.resources[r] >= self.player.entity_costs["Farm"][RESSOURCE_LIST[r]]:
                    can_afford.append(True)
                elif self.quantity_of_each_ressource[r] < self.player.entity_costs["House"][RESSOURCE_LIST[r]]:
                    can_afford.append(False)
                    self.quantity_of_each_ressource[r] = self.player.entity_costs["House"][RESSOURCE_LIST[r]]
                else:
                    can_afford.append(False)

            if unit.building_to_create is None and False not in can_afford:
                tiles_to_build = tile_founding(10, 2, self.range, self.map, self.player, "")
                for i in range(len(tiles_to_build)):
                    if tiles_to_build:
                        random_number = randint(0, len(tiles_to_build) - 1)
                        if len(tiles_to_build) >= 2 and tiles_to_build[random_number] not in self.in_building_tiles \
                                and unit.building_to_create is None:
                            unit.go_to_build(tiles_to_build[random_number], "Farm")
                            self.in_building_tiles.append(tiles_to_build[random_number])

        # THAT IS A TEST, DONT ACTIVATE IT BUT DONT DELETE IT
        """if unit.building_to_create is None:
            tiles_to_build = tile_founding(10, 2, self.range, self.map, self.player, "")
            for i in range(len(tiles_to_build)):
                if tiles_to_build:
                    random_number = randint(0, len(tiles_to_build) - 1)
                    if len(tiles_to_build) >= 2 and tiles_to_build[random_number] not in self.in_building_tiles and \
                            unit.building_to_create is None:
                        unit.go_to_build(tiles_to_build[random_number], "Farm")
                        self.in_building_tiles.append(tiles_to_build[random_number])"""

        # to make the villager able to build other buildings after he buildt a building
        if unit.building_to_create is not None:
            pos_x = unit.building_to_create["pos"][0]
            pos_y = unit.building_to_create["pos"][1]

            for b in unit.owner.building_list:
                if b.pos[0] == pos_x and b.pos[1] == pos_y and not unit.is_moving_to_build:
                    if not b.is_being_built:
                        self.in_building_tiles.remove(unit.building_to_create["pos"])
                        unit.building_to_create = None
                        unit.is_building = False
                        print(unit, "freed")

    def population_developpement_routine(self):
        nb_of_villagers = 0
        for u in self.player.unit_list:
            if isinstance(u, Villager):
                nb_of_villagers +=1
        if nb_of_villagers < 5:
            self.player.towncenter.train(Villager)
        else:
            pass
            #military unit training


    def poking_routine(self):
        for u in self.player.unit_list:
            for p in player_list:
                if p != self.player:
                    if u.building_to_create is None and not u.is_moving_to_gather and not u.is_moving_to_attack \
                            and u.targeted_ressource is None and not u.is_gathering and u.target is None:
                        r = random()
                        if r <= 0.001:
                            u.go_to_attack(p.towncenter.pos)

    # ==================================================================================================================
    # ---------------------------------------------USEFUL FUNCTIONS-----------------------------------------------------
    # ==================================================================================================================

    def planning_gathering(self):
        for i in range(4):
            if self.player.resources[i] <= len(self.player.unit_list) * self.quantity_of_each_ressource[i] and \
                    RESSOURCE_LIST[i] not in self.needed_ressource:
                self.needed_ressource.append(RESSOURCE_LIST[i])
            elif self.player.resources[i] > len(self.player.unit_list) * self.quantity_of_each_ressource[i] and \
                    RESSOURCE_LIST[i] in self.needed_ressource:
                self.needed_ressource.remove(RESSOURCE_LIST[i])

    def is_stronger(self):
        #we count the number of attack unit we get
        number_of_my_attack_unit = 0
        for u in self.player.unit_list:
            if type(u) != Villager:
                number_of_my_attack_unit += 1


    # for each enemy player we count the number of their enemy attack unit to know if we are stronger
        for p in player_list:
            number_of_their_attack_unit = 0
            if p != self.player:
                # we have at least 25% more units, only works without fog of war because we are looking at all
                # enemy units
                for u in p.unit_list:
                    if type(u) != Villager:
                        number_of_their_attack_unit += 1

                if number_of_my_attack_unit != 0 and number_of_my_attack_unit >= 1.25 * number_of_their_attack_unit:
                    return True
                else:
                    return False
        return False

    def free_tiles(self):
        for tile in self.targeted_tiles:
            if self.map[tile[0]][tile[1]]["tile"] == "":
                self.targeted_tiles.remove(tile)

    def free_villagers(self):
        pass

    def reset_villager(self, u):
        u.is_moving_to_gather = False
        u.is_moving_to_attack = False
        u.is_moving_to_build = False

        u.building_to_create = None
        u.targeted_ressource = None
        u.target = None

        u.is_building = False
        u.is_gathering = False
        u.is_attacking = False

    def build_defense(self):
        if self.player.side == "top":
            pass
        elif self.player.side == "bot":
            pass
        elif self.player.side == "right":
            pass
        elif self.player.side == "left":
            pass