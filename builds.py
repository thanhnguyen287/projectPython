import pygame
import Buildings
from settings import *


class Farm:

    def __init__(self, starting_pos, player_owner_of_unit):
        self.name = "Farm"
        self.owner = player_owner_of_unit
        self.sprite = pygame.image.load(os.path.join(assets_path, "Farm.png"))
        self.rect = self.sprite.get_rect(topleft=starting_pos)
        self.construction_cost = [10, 0, 0, 0]
        self.owner.pay_construction_cost(self)
        self.resource_manager_cooldown = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        # every 5 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.owner.resources[0] += 100
            self.resource_manager_cooldown = now


class Town_center:

    def __init__(self, starting_pos, player_owner_of_unit):
        self.name = "Town center"
        self.owner = player_owner_of_unit
        self.sprite = pygame.image.load(os.path.join(assets_path, "town_center.png"))
        self.rect = self.sprite.get_rect(topleft=starting_pos)
        self.resource_manager_cooldown = pygame.time.get_ticks()
        self.construction_cost = [1000, 0, 0, 100]
        self.owner.pay_construction_cost(self)



    def update(self):
        now = pygame.time.get_ticks()
        # every 2 secs :
        if now - self.resource_manager_cooldown > 2000:
            self.resource_manager_cooldown = now

class House:

    def __init__(self, starting_pos, player_owner_of_unit):
        self.name = "House"
        self.owner = player_owner_of_unit
        self.sprite = pygame.image.load(os.path.join(assets_path, "House.png"))
        self.rect = self.sprite.get_rect(topleft=starting_pos)
        self.resource_manager_cooldown = pygame.time.get_ticks()
        self.construction_cost = [600, 0, 0, 0]
        self.owner.pay_construction_cost(self)




    def update(self):
        now = pygame.time.get_ticks()
        # every 2 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.resource_manager_cooldown = now
