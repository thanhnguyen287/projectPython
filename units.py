import pygame
from villager import *
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


