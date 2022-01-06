from player import player_list
from .utils import tile_founding

class IA:

    def __init__(self, player, map):
        self.player = player
        self.behaviour = "neutral"
        self.mode = "neutral"
        self.map = map

        self.tc_pos = self.player.towncenter_pos

    def chose_behaviour(self):
        for p in player_list:
            if p != self.player:
                if self.mode == "defense":
                    break
                for u in p.unit_list:
                    if self.mode == "defense":
                        break
                    # if a enemy unit is in a 10 tiles range of the towncenter
                    if abs(self.tc_pos[0] - u.pos[0]) < 10 and abs(self.tc_pos[1] - u.pos[1]) < 10:  # in tiles
                        self.mode = "defense"
                        break
        if self.is_stronger():
            self.mode = "attack"

        else:
            self.mode = "neutral"

    def is_stronger(self):
        for p in player_list:
            if p != self.player:
                # we have at least 25% more units, only works without fog of war because we are looking at all enemy units
                if len(self.player.unit_list) >= 1.25 * len(p.unit_list):
                    return True
                else:
                    return False

    def run(self):
        """self.chose_behaviour()  # looking at state of the game to chose mode (we should look every 5 seconds or so)
        if self.mode == "neutral":
            self.neutral_routine()
        elif self.mode == "defense":
            self.defense_routine()
        elif self.mode == "attack":
            self.attack_routine()"""
        self.gathering_routine()

    def neutral_routine(self):
        ressources = []
        for r in self.player.resources:
            if r >= 1250:
                ressources.append(True)
            else:
                ressources.append(False)

        if False in ressources:
            self.gathering_routine()
        else:
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
        found = False
        for r in ["wood", "food", "gold", "stone"]:
            if self.player.resources[i] < 9999:
                for j in range(len(self.player.unit_list)):
                    u = self.player.unit_list[j]
                    if u is not None and self.player.unit_occupied[j] == 0 and u.name == "Villager":
                        tile_to_gather = tile_founding(1, 1, 5, self.map, self.player, r)
                        if tile_to_gather:
                            u.go_to_ressource(tile_to_gather)
                            found = True

                    if found: break
                    # we go out of the for because we found a villager that will gather

    def building_routine(self):
        # if we have more than 90% of our pop capacity that is occupied, we build a house
        if self.player.current_population - self.player.max_population <= 0.1 * self.player.max_population:
            pass
            # build a house on the nearest free tile (near the townhall)

        if self.player.current_population >= 0.5 * self.player.max_population:
            pass
            # build a farm on the nearest free tile (near the townhall)


