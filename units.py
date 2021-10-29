import pygame
from player import playerOne
default_unit_model = pygame.image.load ("resources/assets/tree.png")


# WORK IN PROGRESS

class Unit:
    def __init__(self, x, y,owner_of_unit):
        self.sprite = default_unit_model
        self.x = x
        self.y = y
        self.owner = owner_of_unit

        self.max_health = 10
        self.current_health = self.max_health
        self.attack_dmg = 0
        self.attack_speed = 0.0
        self.range = 0
        self.movement_speed = 0

        self.is_alive = True

        # TRAINING
        self.training_cost = [0, 0, 0, 0]         # GOLD, LUMBER, STONE, FOOD
        self.training_time = 0
        self.population_produced = 1

    def display(self, screen):
        screen.blit(self.sprite, self.get_position())

    def display_life(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x-15, self.y - 15, self.current_health * 3, 10))
        pygame.draw.rect(screen, (25, 25, 25), (self.x -15, self.y - 15, self.max_health * 3, 10), 4)


    def select(self, event, real_x, real_y):
        ...

    def move_to(self, location ):
        ...

    def get_position(self):
        return (self.x, self.y)


    def attack(self, targeted_unit):

        targeted_unit.current_health-=self.attack_dmg
        #pour tester
        #print("hp de unit :", targeted_unit.current_health, " / ", targeted_unit.max_health)

        # if target has less than 0 hp after attack, she dies
        if targeted_unit.current_health < 0:
            #print pour tester
            #print(" unit DIED")
            targeted_unit.is_alive = False
            #del units_group[units_group.index(targeted_unit)]


class Villager(Unit):

    def __init__(self,x,y,player_owner_of_unit):
        super().__init__(x, y, player_owner_of_unit)

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
        self.population_produced = 1

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

class Bowman(Unit):

    def __init__(self,x,y):
        super().__init__(x, y)

        #DISPLAY
        self.model = default_unit_model

        # DATA
        self.max_health = 35
        self.current_health = 35
        self.attack = 3
        self.attack_speed = 1.4
        self.movement_speed = 1.2
        # unit type : distance
        self.range = 5

        #Training : 20 WOOD, 40 FOOD, 30s
        self.training_cost = [0,20,0,40]
        self.training_time = 30
        self.population_produced = 1


class Clubman(Unit):

    def __init__(self,x,y):
        super().__init__(x, y)

        #DISPLAY
        self.model = default_unit_model

        # DATA
        self.max_health = 40
        self.current_health = 40
        self.attack = 3
        self.attack_speed = 1.5
        self.movement_speed = 1.2
        # unit type : melee
        self.range = 0

        #Training : 50 FOOD, 26s
        self.training_cost = [0,0,0,50]
        self.training_time = 26
        self.population_produced = 1


testUnit1 = Villager(800,500,playerOne)
testUnit2 = Villager(500, 500, playerOne)

#units alive are put in this group
units_group = [testUnit1, testUnit2]


