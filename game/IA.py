from player import player_list
from .utils import tile_founding
from units import Villager


class IA:

    def __init__(self, player, map):
        self.player = player
        self.map = map
        self.tc_pos = self.player.towncenter_pos

        self.behaviour = "neutral"

        # the range (in layers) that the AI will go to. It increase when the AI becomes stronger
        # or is lacking ressources
        self.range = 1

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


        # or if she is neutral but lacking ressources to gather
        elif self.behaviour == "neutral":
            ressources = ["wood", "food", "gold", "stone"]
            ressources_available = []
            for r in ressources:
                tiles_to_gather = tile_founding(1, 1, self.range, self.map, self.player, r)
                if tiles_to_gather:
                    ressources_available.append(True)
                else:
                    ressources_available.append(False)

            if False in ressources_available:
                self.range += 1

        print(self.range)

    def is_stronger(self):
        for p in player_list:
            if p != self.player:
                # we have at least 25% more units, only works without fog of war because we are looking at all enemy units
                if len(self.player.unit_list) >= 1.25 * len(p.unit_list):
                    return True
                else:
                    return False
        return False

    def run(self):
        self.chose_behaviour()  # looking at state of the game to chose mode (we should look every 5 seconds or so)
        if self.behaviour == "neutral":
            self.neutral_routine()
        elif self.behaviour == "defense":
            self.defense_routine()
        elif self.behaviour == "attack":
            self.attack_routine()

    def neutral_routine(self):
        ressources = []
        for r in self.player.resources:
            if r >= 1250:
                ressources.append(True)
            else:
                ressources.append(False)

        if False in ressources:
            self.gathering_routine()

        self.building_routine()

    # TODO

    def defense_routine(self):
        pass

    # TODO

    def attack_routine(self):
        pass

    # TODO

    def gathering_routine(self):
        i = 0
        for u in self.player.unit_list:
            if isinstance(u, Villager) and u.target is None:
                for indice in range(len(["wood", "food", "gold", "stone"])):
                    r = ["wood", "food", "gold", "stone"][indice]
                    if self.player.resources[indice] < 150:
                        tiles_to_gather = tile_founding(1, 1, self.range, self.map, self.player, r)
                        if tiles_to_gather:
                            u.go_to_ressource(tiles_to_gather[0])

    def building_routine(self):
        # if we have more than 90% of our pop capacity occupied, we build a house
        if self.player.current_population - self.player.max_population <= 0.1 * self.player.max_population:
            for u in self.player.unit_list:
                if isinstance(u, Villager) and u.target is None:
                    tiles_to_build = tile_founding(1, 2, self.range, self.map, self.player, "")
                    # u.build(tiles_to_build[0], "House")


        # /!\ with the "elif" we can only build 1 building after 1 building
        # if we have more than 50% of our pop capacity occupied, we build a farm
        elif self.player.current_population >= 0.5 * self.player.max_population:
            for u in self.player.unit_list:
                if isinstance(u, Villager) and u.target is None:
                    tiles_to_build = tile_founding(1, 2, self.range, self.map, self.player, "")
                    # u.build(tiles_to_build[0], "House")
