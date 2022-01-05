from player import player_list

class IA:


    def __init__(self, player):
        self.player = player
        self.behaviour = "neutral"
        self.mode = "neutral"


    def chose_behaviour(self):
        for p in player_list:
            if p != self.player:
                if self.mode == "defense":
                    break
                for u in p.unit_list:
                    if self.mode == "defense":
                        break
                    # if a enemy unit is in a 10 tiles range of the towncenter
                    if abs(p.towncenter_pos[0] - u.pos[0]) < 10 and abs(p.towncenter_pos[1] - u.pos[1]) < 10:  # in tiles
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
        self.chose_behaviour()  # looking at state of the game to chose mode (we should look every 5 seconds or so)
        if self.mode == "neutral":
            self.neutral_routine()
        elif self.mode == "defense":
            self.defense_routine()
        elif self.mode == "attack":
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
            if self.player.resources[i] < 1250:
                for j in range(len(self.player.unit_list)):
                    u = self.player.unit_list[j]
                    if u is not None and self.player.unit_occupied[j] == 0 and u.name == "Villager":
                        pass
                        #the unit needs to gather the nearest ressource of the type r
                        found = True

                    if found: break
                    #we go out of the for because we found a villager that will gather

    def building_routine(self):
        pass
        #TODO