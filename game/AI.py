from player import player_list
from .utils import tile_founding, better_look_around, RESSOURCE_LIST
from units import Villager
from random import randint


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

        # a list of tiles to manage the gathering of ressources with the multiple units
        self.targeted_tiles = []

        # a list of the tiles where buildings are being built, to not build more on it
        self.in_building_tiles = []

        # number of each ressource needed for every villager
        self.limit = 150

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
                    if abs(self.tc_pos[0] - u.pos[0]) < 10 and abs(self.tc_pos[1] - u.pos[1]) < 10:  # in tiles
                        self.behaviour = "defense"
                        break
        # if we are the strongest we attack !
        if self.is_stronger():
            self.behaviour = "attack"
        # if we dont attack not defend, we are neutral
        else:
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
        elif self.behaviour == "neutral":
            ressources_available = []
            for r in self.needed_ressource:
                tiles_to_gather = tile_founding(1, 1, self.range, self.map, self.player, r)
                if tiles_to_gather:
                    ressources_available.append(True)
                else:
                    ressources_available.append(False)

            if True not in ressources_available:
                self.range += 1

    def run(self):
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
                        not self.dev_pop:
                    self.gathering_routine(u)

                # if we dont need ressources or when the villager is building, we are using the building routine
                elif isinstance(u, Villager) and (not self.dev_pop or u.building_to_create is not None):
                    self.building_routine(u)

        self.free_tiles()
        self.dev_pop = False

    def defense_routine(self):
        for p in player_list:
            if p != self.player:
                for u in p.unit_list:
                    if abs(self.tc_pos[0] - u.pos[0]) < 10 and abs(self.tc_pos[1] - u.pos[1]) < 10:  # in tiles
                        pos_unit_to_attack = u.pos

                        focused = False

                        for my_u in self.player.unit_list:
                            # et rajouter si le type de l'unité n'est pas un villageois
                            if my_u.building_to_create is None and my_u.targeted_ressource is None and \
                                    my_u.target is None and not focused:
                                my_u.go_to_attack(pos_unit_to_attack)
                                focused = True
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

    def building_routine(self, unit):
        # if we have more than 90% of our pop capacity occupied, we build a house
        if self.player.current_population >= 0.9 * self.player.max_population:
            # we check if the player has enough ressource to build
            can_afford = []
            for r in range(len(self.player.resources)):
                if self.player.resources[r] >= self.player.entity_costs["House"][RESSOURCE_LIST[r]]:
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
                            unit.go_to_build(tiles_to_build[random_number], "House")
                            self.in_building_tiles.append(tiles_to_build[random_number])


        # /!\ with the "elif" we can only build 1 building after 1 building
        # if we have more than 50% of our pop capacity occupied, we build a farm
        #elif self.player.current_population >= 0.5 * self.player.max_population:

        #we are currently always trying to build a farm if we are in the building routine
        else:
            # we check if the player has enough ressource to build
            can_afford = []
            for r in range(len(self.player.resources)):
                if self.player.resources[r] >= self.player.entity_costs["Farm"][RESSOURCE_LIST[r]]:
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

    def population_developpement_routine(self):
        self.player.towncenter.train(Villager)

    # ==================================================================================================================
    # ---------------------------------------------USEFUL FUNCTIONS-----------------------------------------------------
    # ==================================================================================================================

    def planning_gathering(self):
        for i in range(4):
            if self.player.resources[i] <= len(self.player.unit_list) * self.limit and \
                    RESSOURCE_LIST[i] not in self.needed_ressource:
                self.needed_ressource.append(RESSOURCE_LIST[i])
            elif self.player.resources[i] > len(self.player.unit_list) * self.limit and \
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
