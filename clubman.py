from units import *


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