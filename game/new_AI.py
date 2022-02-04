from player import player_list, str_to_entity_class
from .utils import tile_founding, better_look_around, RESSOURCE_LIST
from units import Villager, Barracks, Clubman, Market, Wall, Tower, House, Farm, Dragon
from random import randint, random
from settings import MAP_SIZE_X, MAP_SIZE_Y


class new_AI:

    def __init__(self, player, map, behaviour):
        self.player = player
        self.map = map
        self.tc_pos = self.player.towncenter_pos

        self.behaviour = behaviour


        # the range (in layers) that the AI will go to. It increase when the AI becomes stronger
        # or is lacking ressources
        self.range = 3

        # this will be used to know if the AI needs to gather or not, and to expand or not
        self.ressource_to_gather = []

        # number of each ressource needed
        self.base_quantity_of_each_ressource = [400, 150, 150, 300]
        self.quantity_of_each_ressource = self.base_quantity_of_each_ressource

        self.needed_ressource = [0, 0, 0, 0]

        #for attack
        self.has_barracks = False
        self.has_second_barracks = False
        self.barracks = None
        self.second_barracks = None

        #for technologies
        self.has_market = False
        self.market = None

        #the building queue for the building we want to build
        self.nb_ferme = 0
        self.building_queue = []
        self.training_queue = []

        self.army = []

        self.poking_unit = None
        self.in_poking_player = None

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

    # this needs a little correction, it is too... confident
    def expand(self):
        # the idea is that the AI will check if she is stronger to know if she can expand
        if self.is_stronger():
            self.range += 1

        # WARNING i will modify this so the AI expand only if a ressource she needs is lacking
        # or if she is neutral but lacking ressources to gather
        elif self.range < MAP_SIZE_X and self.range < MAP_SIZE_Y:
            ressources_available = []
            for r in self.ressource_to_gather:
                ressources_available = []
                tiles_to_gather = tile_founding(len(self.player.unit_list), 1, self.range, self.map.map, self.player, r)
                if len(tiles_to_gather) >= len(self.player.unit_list):
                    ressources_available.append(True)
                else:
                    ressources_available.append(False)

            if self.ressource_to_gather and True not in ressources_available:
                self.range += 1
                print(self.range)


    def run(self):
        # to update the tower
        if self.player.tower is not None and self.player.tower not in self.player.building_list:
            self.player.tower = None
        if self.player.second_tower is not None and self.player.second_tower not in self.player.building_list:
            self.player.second_tower = None

        #print(self.barracks, self.second_barracks)

        if self.player.towncenter is not None:

            #we update the army
            for u in self.player.unit_list:
                if isinstance(u, Clubman) and u not in self.army:
                    self.army.append(u)

            #we execute a different routine for each behaviour that exists
            self.routine()

            # at the end, we try to expand (go to expand method to see the conditions)
            self.expand()


    # ==================================================================================================================
    # ------------------------------------------------MAIN ROUTINES-----------------------------------------------------
    # ==================================================================================================================

    # gather, build, spawn villagers
    def routine(self):

        #to know if we need to gather ressources
        self.planning_gathering()

        #the defense
        if self.behaviour != "pacifist":
            self.defense_routine()

        # the poke
        if self.army and self.behaviour == "aggressive":
            self.poking_routine()

        # if we dont need ressources, we are not training units, we have free pop space and we have at least as many
        # buildings as units, then we can train a new unit
        if not self.ressource_to_gather and self.player.towncenter.queue == 0 and  \
                self.player.current_population < self.player.max_population and \
                (self.count_villagers() < 5 or (self.barracks is not None and self.barracks.queue == 0)):
            #print("dev pop")

            self.population_developpement_routine()
            self.dev_pop = True

        # if we dont train unit, we will try to gather or to build
        else:
            for u in self.player.unit_list:

                # if we need ressources and the unit is a villager and he is free, he will go gather
                if self.ressource_to_gather and isinstance(u, Villager) and u.building_to_create is None \
                        and not u.is_moving_to_attack and u.target is None and not u.is_building:
                    #print("gathering")
                    if u.gathered_ressource_stack < u.stack_max:
                        self.gathering_routine(u)
                    else:
                        u.go_to_townhall()

                # if we dont need ressources the villager is going to build
                elif isinstance(u, Villager) and not u.is_moving_to_attack and u.target is None:
                    #print("building")
                    self.building_routine(u)

        #to reset frozen villagers
        for u in self.player.unit_list:
            if isinstance(u, Villager) and u.is_moving_to_gather and not u.searching_for_path:
                u.is_moving_to_gather = False
                print(u, "reseted")

        #to free tiles and to reset dev pop var
        self.free_tiles()
        self.dev_pop = False

    def defense_routine(self):
        for p in player_list:
            if p != self.player:
                for u in p.unit_list:
                    if abs(self.tc_pos[0] - u.pos[0]) <= 1 and abs(self.tc_pos[1] - u.pos[1]) <= 1 \
                            and not u in self.units_focused and not isinstance(u, Dragon):  # in tiles

                        if len(self.army) > 1:
                            for my_u in self.army:
                                if my_u != self.poking_unit:
                                    my_u.go_to_attack(u.pos)
                                    if my_u.target is None and not u in self.units_focused:
                                        my_u.go_to_attack(u.pos)
                                        self.units_focused.append(u)
                        else:
                            for my_u in self.player.unit_list:
                                self.reset_villager(my_u)

                                if my_u.target is None and not u in self.units_focused:
                                    my_u.go_to_attack(u.pos)
                                    self.units_focused.append(u)

                    if u in self.units_focused:
                        for my_u in self.player.unit_list:
                            if my_u.target == u:
                                if u.current_health > 0:
                                    my_u.attack()
                                else:
                                    my_u.target = None
                                    my_u.is_attacking = False
                                    self.units_focused.remove(u)


        #creer une routine de repli des villageois près de l'hotel de ville


    def attack_routine(self):
        #TODO
        if self.army:
            for u in self.army:
                pass


    # ==================================================================================================================
    # -------------------------------------------------SUB ROUTINES-----------------------------------------------------
    # ==================================================================================================================

    def gathering_routine(self, unit):
        for r in self.ressource_to_gather:
            if unit.targeted_ressource is None:
                ressource = None
                if r == "wood": ressource = "tree"
                elif r == "stone": ressource = "rock"
                elif r == "gold": ressource = "gold"
                elif r == "berrybush": ressource = "food"

                if unit.gathered_ressource_stack == 0 or unit.stack_type == ressource:
                    tiles_to_gather = tile_founding(10, 1, self.range, self.map.map, self.player, r)
                    found = False
                    for i in range(len(tiles_to_gather)):
                        if tiles_to_gather:
                            pos_x = tiles_to_gather[i][0]
                            pos_y = tiles_to_gather[i][1]
                            if better_look_around(unit.pos, (pos_x, pos_y), self.map.map) and not found and \
                                    (pos_x, pos_y) not in self.targeted_tiles:
                                unit.go_to_ressource(tiles_to_gather[i])
                                self.targeted_tiles.append((pos_x, pos_y))
                                found = True

                else:
                    unit.go_to_townhall()

    def building_routine(self, u):
        #print(self.building_queue)
        if u.building_to_create is None:
            # first we try to build what's on the queue
            if self.building_queue:
                if self.check_price(self.building_queue[0][0]):
                    to_build = self.building_queue[0][0]
                    pos = self.building_queue[0][1]
                    u.go_to_build(pos, to_build)
                    self.map.collision_matrix[pos[1]][pos[0]] = 0
                    self.building_queue.remove(self.building_queue[0])

            #if there is nothing in the queue, we build a house if we have more than 70% of the pop
            elif self.player.current_population >= 0.7 * self.player.max_population:
                tiles_to_build = tile_founding(5, 2, self.range, self.map.map, self.player, "", self.map)
                if tiles_to_build:
                    r = randint(0, len(tiles_to_build)-1)
                    pos = tiles_to_build[r]
                    if pos not in self.in_building_tiles and self.let_a_path(pos):
                        self.building_queue.append(("House", pos))
                        self.in_building_tiles.append(pos)

            #TECHNOLOGY NOT IMPLEMENTED YET
            #elif not self.has_market and self.player.tower is not None and \
                    #(self.behaviour == "neutral" or self.behaviour == "pacifist"):
                #while not self.has_market and not self.ressource_to_gather:
                    #tiles_to_build = tile_founding(10, 3, self.range+1, self.map.map, self.player, "", self.map)
                    #if tiles_to_build:
                        #r = randint(0, len(tiles_to_build) - 1)
                        #pos = tiles_to_build[r]
                        #if self.check_matrix_and_in_building_tiles(pos) and pos not in self.in_building_tiles and \
                                #self.let_a_path(pos) and self.let_a_path((pos[0], pos[1]+1)):
                            #self.building_queue.append(("Market", pos))
                            #self.in_building_tiles.append(pos)
                            #self.in_building_tiles.append((pos[0], pos[1] - 1))
                            #self.in_building_tiles.append((pos[0] + 1, pos[1]))
                            #self.in_building_tiles.append((pos[0] + 1, pos[1] - 1))
                            #self.has_market = True


            #else we try to build a barracks if we dont have one and we have 5 villagers
            elif self.count_villagers() >= 5 and not self.has_barracks and \
                    (self.player.tower is not None or self.behaviour == "aggressive") and self.behaviour != "pacifist":
                while not self.has_barracks and not self.ressource_to_gather:
                    tiles_to_build = tile_founding(20, 2, self.range+1, self.map.map, self.player, "", self.map)
                    if tiles_to_build:
                        r = randint(0, len(tiles_to_build) - 1)
                        pos = tiles_to_build[r]
                        if self.check_matrix_and_in_building_tiles(pos) and pos not in self.in_building_tiles and \
                                self.let_a_path(pos) and self.let_a_path((pos[0], pos[1]+1)) and \
                                self.check_constructor_pos(pos):
                            self.building_queue.append(("Barracks", pos))
                            self.in_building_tiles.append(pos)
                            self.in_building_tiles.append((pos[0], pos[1] - 1))
                            self.in_building_tiles.append((pos[0] + 1, pos[1]))
                            self.in_building_tiles.append((pos[0] + 1, pos[1] - 1))
                            self.has_barracks = True

            # else we try to build a defense if we dont have one
            elif self.player.tower is None and self.behaviour != "pacifist" and self.behaviour != "aggressive":
                self.build_defense()


            #else we just build a farm
            else:
                tiles_to_build = tile_founding(5, 2, self.range, self.map.map, self.player, "", self.map)
                if tiles_to_build:
                    r = randint(0, len(tiles_to_build)-1)
                    pos = tiles_to_build[r]
                    if pos not in self.in_building_tiles and self.let_a_path(pos) and self.nb_ferme < 5:
                        self.building_queue.append(("Farm", pos))
                        self.in_building_tiles.append(pos)
                        self.nb_ferme += 1

        if self.behaviour == "aggressive" and self.has_barracks and not self.has_second_barracks and \
                self.barracks is not None:
            self.has_barracks = False
            self.has_second_barracks = True
            self.second_barracks = self.barracks
            self.barracks = None

        # to make the villager able to build other buildings after he buildt a building, we release him
        if u.building_to_create is not None:
            pos_x = u.building_to_create["pos"][0]
            pos_y = u.building_to_create["pos"][1]

            for b in u.owner.building_list:
                if b.pos[0] == pos_x and b.pos[1] == pos_y and not u.is_moving_to_build:
                    if not b.is_being_built:
                        self.in_building_tiles.remove(u.building_to_create["pos"])
                        for i in range(4):
                            self.needed_ressource[i] -= \
                            str_to_entity_class(u.building_to_create["name"]).construction_cost[i]
                        u.building_to_create = None
                        u.is_building = False
                        #print(u, "freed")
                        if isinstance(b, Barracks):
                            self.barracks = b
                        if isinstance(b, Market):
                            self.market = b
                        if isinstance(b, Tower) and self.player.second_tower is None and self.behaviour == "defensive":
                            self.player.second_tower = b
                        elif isinstance(b, Tower) and self.player.tower is None:
                            self.player.tower = b

        self.lock_tiles()

    def population_developpement_routine(self):
        #if we can afford it and if we have less than 5 villagers, we create a villager
        if self.count_villagers() < 5 and self.check_price(Villager):
            self.player.towncenter.train(Villager)
            for i in range(4):
                self.needed_ressource[i] -= Villager.construction_cost[i]

        elif self.check_price(Clubman) and \
                self.player.current_population+len(self.training_queue) < self.player.max_population and \
                self.behaviour != "pacifist" and \
                (len(self.army) < 5 or (self.behaviour == "aggressive" and len(self.army) < 10)) and self.has_barracks:
            self.barracks.train(Clubman)
            for i in range(4):
                self.needed_ressource[i] -= Clubman.construction_cost[i]

        if self.behaviour == "aggressive" and self.check_price(Clubman) and \
                self.player.current_population+len(self.training_queue) < self.player.max_population \
            and len(self.army) < 10 and self.has_second_barracks:
            self.second_barracks.train(Clubman)
            for i in range(4):
                self.needed_ressource[i] -= Clubman.construction_cost[i]

    def poking_routine(self):
        #in case the unit get killed
        if self.poking_unit not in self.player.unit_list:
            self.poking_unit = None

        if self.poking_unit is not None and self.in_poking_player is not None and \
                self.in_poking_player.tower is None and self.poking_unit.target is None:
            self.poking_unit.go_to_attack(self.in_poking_player.towncenter_pos)

        if self.in_poking_player is not None and self.in_poking_player.towncenter is None:
            self.in_poking_player = None
            self.poking_unit.is_attacking = False
            self.poking_unit = None

        if self.poking_unit is None:
            for u in self.army:
                for p in player_list:
                    if p != self.player:
                        if not u.is_moving_to_attack and u.target is None and self.poking_unit is None:
                            self.poking_unit = u
                            self.in_poking_player = p
                            if self.in_poking_player.tower is not None:
                                self.poking_unit.go_to_attack(self.in_poking_player.tower_pos)
                            elif self.in_poking_player.second_tower is not None:
                                self.poking_unit.go_to_attack(self.in_poking_player.second_tower_pos)
                            else:
                                self.poking_unit.go_to_attack(p.towncenter.pos)


        else:
            self.poking_unit.attack()

    # ==================================================================================================================
    # ---------------------------------------------USEFUL FUNCTIONS-----------------------------------------------------
    # ==================================================================================================================

    def planning_gathering(self):
        for i in range(4):
            if self.player.resources[i] < self.quantity_of_each_ressource[i] and \
                    RESSOURCE_LIST[i] not in self.ressource_to_gather:
                self.ressource_to_gather.append(RESSOURCE_LIST[i])
            elif self.player.resources[i] >= self.quantity_of_each_ressource[i] and \
                self.player.resources[i] >= self.needed_ressource[i] and \
                    RESSOURCE_LIST[i] in self.ressource_to_gather:
                self.ressource_to_gather.remove(RESSOURCE_LIST[i])

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
            if self.map.map[tile[0]][tile[1]]["tile"] == "":
                self.targeted_tiles.remove(tile)

    def lock_tiles(self):
        for b in self.player.building_list:
            self.map.collision_matrix[b.pos[1]][b.pos[0]] = 0

            if isinstance(b, Market) or isinstance(b, Barracks):
                self.map.collision_matrix[b.pos[1]-1][b.pos[0]] = 0
                self.map.collision_matrix[b.pos[1]][b.pos[0]+1] = 0
                self.map.collision_matrix[b.pos[1]-1][b.pos[0]+1] = 0

    def count_villagers(self):
        nb_of_villagers = 0
        for u in self.player.unit_list:
            if isinstance(u, Villager):
                nb_of_villagers +=1
        return nb_of_villagers

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
        #we find a place to build the tower
        pos = (-1, -1) #we initialize it even if it is always modified
        nb_tiles = 1
        while self.player.tower_pos is None:
            tiles_to_build = tile_founding(nb_tiles, 3, self.range, self.map.map, self.player, "", self.map)
            if tiles_to_build:
                r = randint(0, len(tiles_to_build)-1)
                pos = tiles_to_build[r]
                if self.player.side == "top" and pos[0] >= self.player.towncenter_pos[0] and pos[1] >= self.player.towncenter_pos[1]-1:
                    self.building_queue.append(("Tower", pos))
                    self.in_building_tiles.append(pos)

                    self.player.tower_pos = pos

                elif self.player.side == "bot" and pos[0] <= self.player.towncenter_pos[0]+1 and pos[1] <= self.player.towncenter_pos[1]:
                    self.building_queue.append(("Tower", pos))
                    self.in_building_tiles.append(pos)

                    self.player.tower_pos = pos

                elif self.player.side == "left" and pos[0] >= self.player.towncenter_pos[0] and pos[1] <= self.player.towncenter_pos[1]:
                    self.building_queue.append(("Tower", pos))
                    self.in_building_tiles.append(pos)

                    self.player.tower_pos = pos

                elif self.player.side == "right" and pos[0] <= self.player.towncenter_pos[0]+1 and pos[1] >= self.player.towncenter_pos[1]:
                    self.building_queue.append(("Tower", pos))
                    self.in_building_tiles.append(pos)

                    self.player.tower_pos = pos
            nb_tiles += 1


        #we look for the eight surrounding position if we can build walls
        eight_pos = [(pos[0]+1, pos[1]-1), (pos[0]+1, pos[1]), (pos[0]+1, pos[1]+1), (pos[0], pos[1]+1),
                     (pos[0]-1, pos[1]+1), (pos[0]-1, pos[1]), (pos[0]-1, pos[1]-1), (pos[0], pos[1]-1)]
        """
        for i in range(8):
            pos = eight_pos[i]
            if self.map.collision_matrix[pos[1]][pos[0]]:
                self.building_queue.append(("Wall", pos))
                self.in_building_tiles.append(pos)
        """

        if self.behaviour == "defensive" and self.player.second_tower is None:
            self.player.second_tower = self.player.tower
            self.player.tower = None
            self.player.second_tower_pos = self.player.tower_pos
            self.player.tower_pos = None


    def let_a_path(self, pos):
        if self.player.side == "top" or self.player.side == "left":
            if pos[1] == self.player.towncenter_pos[1] and pos[0] >= self.player.towncenter_pos[0]+2:
                return False
            else:
                return True
        elif self.player.side == "bot" or self.player.side == "right":
            if pos[1] == self.player.towncenter_pos[1] and pos[0] <= self.player.towncenter_pos[0]-1:
                return False
            else:
                return True

    # update self.needed_ressource and return False if we need ressource and else True
    def check_price(self, entity_class):
        if type(entity_class) == str:
            entity_class = str_to_entity_class(entity_class)
        can_build = True
        for i in range(4):
            if self.player.resources[i] < entity_class.construction_cost[i] and \
                    self.player.resources[i] < self.needed_ressource[i]:
                if RESSOURCE_LIST[i] not in self.ressource_to_gather:
                    self.ressource_to_gather.append(RESSOURCE_LIST[i])
                can_build = False

            self.needed_ressource[i] += entity_class.construction_cost[i]
        return can_build

    def check_matrix_and_in_building_tiles(self, pos):
        pos1 = (pos[0], pos[1]-1)
        pos2 = (pos[0]+1, pos[1])
        pos3 = (pos[0]+1, pos[1] - 1)
        if self.map.collision_matrix[pos[1] - 1][pos[0]] and self.map.collision_matrix[pos[1]][
            pos[0] + 1] and self.map.collision_matrix[pos[1] - 1][pos[0] + 1] and pos not in self.in_building_tiles and \
                pos1 not in self.in_building_tiles and pos2 not in self.in_building_tiles and pos3 not in self.in_building_tiles:
            return True
        else:
            return False

    def check_constructor_pos(self, pos):
        villager_pos = (pos[0] - 1, pos[1] - 1)
        if self.map.collision_matrix[villager_pos[1]][villager_pos[0]] and villager_pos not in self.in_building_tiles:
            return True
        else:
            return False