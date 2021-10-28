import pygame
import Buildings
from settings import *


class Building:
    def __init__(self, pos, player_owner_of_unit):
        self.owner = player_owner_of_unit
        self.rect = self.sprite.get_rect(topleft=pos)

        # will be used in the timer to increase resources of the player
        self.resource_manager_cooldown = pygame.time.get_ticks()

        self.current_health = self.max_health
        self.is_alive = True

        self.image_select = pygame.image.load(os.path.join(assets_path,"image_select.png"))
        self.selected = False

        self.resource_manager_cooldown = pygame.time.get_ticks()
        self.owner.pay_construction_cost(self)

    def update(self):
        pass


class Town_center(Building):

    def __init__(self, pos, player_owner_of_unit):

        self.name = "Town center"
        self.sprite = pygame.image.load(os.path.join(assets_path, "town_center.png"))

        self.construction_cost = [1000, 0, 0, 100]
        self.construction_time = 150

        self.max_health = 100
        player_owner_of_unit.max_population += 5

        self.description = "Used to create villagers."

        super().__init__(pos, player_owner_of_unit)

    def update(self):
        now = pygame.time.get_ticks()
        # every 5 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.current_health -= 5
            self.resource_manager_cooldown = now


class Farm(Building):
    def __init__(self, pos, player_owner_of_unit):

        self.name = "Farm"
        self.sprite = pygame.image.load(os.path.join(assets_path, "Farm.png"))

        self.construction_cost = [100, 0, 0, 0]
        self.construction_time = 1

        self.max_health = 10
        self.max_population_bonus = 0

        self.description = "Provides 50 food every 5 seconds."

        super().__init__(pos, player_owner_of_unit)

    def update(self):
        now = pygame.time.get_ticks()
        # every 5 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.owner.resources[0] += 50
            self.current_health-=1
            self.resource_manager_cooldown = now


class House(Building):

    def __init__(self, pos, player_owner_of_unit):
        self.name = "House"
        self.sprite = pygame.image.load(os.path.join(assets_path, "House.png"))

        self.construction_cost = [600, 0, 0, 0]
        self.construction_time = 1

        self.max_health = 50
        player_owner_of_unit.max_population += 5

        self.description = "Each House increases the maximum population by 5."

        super().__init__(pos, player_owner_of_unit)

    def update(self):
        now = pygame.time.get_ticks()
        # every 5 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.current_health-=2
            self.resource_manager_cooldown = now


