from units import *


class Villager(Unit):

    def __init__(self,x,y):
        super().__init__(x, y)

        #DISPLAY
        self.sprite = pygame.image.load ("resources/assets/Villager.bmp")


        # DATA
        self.max_health = 25
        self.current_health = 25
        self.attack_dmg = 3
        self.attack_speed = 1.5
        self.movement_speed = 1.1
        # unit type : melee
        self.range = 0

        #Training : 50 FOOD, 20s
        self.training_cost = [0,0,0,50]
        self.training_time = 20

    def build(self, tile,):
        ...

    def repair (self, building):
        if building.current_health != building.max_health:
            ...
        else:
            ...

"""
    def gatherRessources(self, ressource):
        if (ressource.type = BERRY_BUSH):
            ...
        elif (ressource.type = TREE):
            ...
        elif (ressource.type = GOLD_MINE):
            ...
        elif (ressource.type = STONE_MINE):
            ...
        elif (ressource.type = SHORE_FISH):
            ...
        elif (ressource.type = ANIMALS):
            ...
"""

testUnit1 = Villager(800,500)
testUnit2 = Villager(500, 500)

#units alive are put in this group
units_group = [testUnit1, testUnit2]
