import pygame

# WORK IN PROGRESS


class Unit:
    def __init__(self, starting_tile):
        self.tile = starting_tile
        self.current_health = self.max_health
        self.is_alive = True

    def move_to(self, location):
        ...

    def attack(self, targeted_unit):

        targeted_unit.current_health -= self.attack_dmg
        #pour tester
        #print("hp de unit :", targeted_unit.current_health, " / ", targeted_unit.max_health)

        # if target has less than 0 hp after attack, she dies
        if targeted_unit.current_health < 0:
            #print pour tester
            #print(" unit DIED")
            targeted_unit.is_alive = False
            #del units_group[units_group.index(targeted_unit)]


class Villager(Unit):

    def __init__(self, starting_tile):

        self.name = "Villager"

        # DISPLAY
        self.sprite = pygame.image.load("resources/assets/Villager.bmp")

        # DATA
        self.max_health = 25
        self.attack_dmg = 3
        self.attack_speed = 1.5
        self.movement_speed = 1.1

        # unit type : melee
        self.range = 0

        #Training : 50 FOOD, 20s
        self.training_cost = [0, 50, 0, 0]
        self.training_time = 20
        self.population_produced = 1

        super().__init__(starting_tile)

    def build(self, tile,):
        ...

    def repair(self, building):
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

    def __init__(self, starting_tile):
        super().__init__(starting_tile)

        #DISPLAY
        self.sprite = None

        # DATA
        self.max_health = 35
        self.current_health = 35
        self.attack = 3
        self.attack_speed = 1.4
        self.movement_speed = 1.2
        # unit type : distance
        self.range = 5

        #Training : 20 WOOD, 40 FOOD, 30s
        self.training_cost = [20, 40, 0, 0]
        self.training_time = 30
        self.population_produced = 1


class Clubman(Unit):

    def __init__(self, starting_tile):
        super().__init__(starting_tile)

        #DISPLAY
        self.sprite = None

        # DATA
        self.max_health = 40
        self.current_health = 40
        self.attack = 3
        self.attack_speed = 1.5
        self.movement_speed = 1.2

        # unit type : melee
        self.range = 0

        #Training : 50 FOOD, 26s
        self.training_cost = [0, 50, 0, 0]
        self.training_time = 26
        self.population_produced = 1
