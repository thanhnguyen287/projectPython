from units import *


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
