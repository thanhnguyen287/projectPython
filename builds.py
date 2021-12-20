from settings import *
from units import Villager


class Building:
    population_produced = 0
    

    def __init__(self, pos, map, player_owner_of_unit,):
        self.owner = player_owner_of_unit
        self.rect = self.sprite.get_rect(topleft=pos)
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        self.map = map

        # will be used in the timer to increase resources of the player
        self.resource_manager_cooldown = pygame.time.get_ticks()

        self.current_health = self.max_health
        self.is_alive = True

        self.image_select = pygame.image.load(os.path.join(assets_path, "image_select.png"))
        self.selected = False

        self.resource_manager_cooldown = pygame.time.get_ticks()
        self.owner.pay_entity_cost(self)

    def update(self):
        pass


class Town_center(Building):
    description = " Used to create villagers."
    construction_tooltip = " Build a Town Center"
    construction_cost = [1000, 0, 0, 100]
    construction_time = 150
    armor = 3

    def __init__(self, pos, map,  player_owner_of_unit):

        self.name = "Town center"
        self.sprite = pygame.image.load(os.path.join(assets_path, "town_center.png"))

        self.construction_cost = [0, 0, 0, 0]
        self.construction_time = 150

        self.max_health = 100
        self.is_working = False
        player_owner_of_unit.max_population += 5
        self.queue = 0
        self.now = 0
        self.resource_manager_cooldown = 0

        super().__init__(pos, map, player_owner_of_unit)

    #to create villagers, research techs and upgrade to second age
    def update(self):
        self.now = pygame.time.get_ticks()
        #add a button to stop the current action if the town center is working
        if self.is_working:
            # if a villager is being created since 5 secs :
            if self.now - self.resource_manager_cooldown > 5000:
                self.resource_manager_cooldown = self.now
                #create a new villager
                self.map.units[self.pos[0]][self.pos[1] + 1] = Villager((self.pos[0], self.pos[1] + 1), self.owner, self.map)
                # update collision for new villager
                self.map.collision_matrix[self.pos[1] + 1][self.pos[0]] = 0
                # decrease the queue
                self.queue -= 1
                #if there are now more villagers to train, we can stop there
                if self.queue <= 0:
                    self.is_working = False


class Farm(Building):
    description = " Provides 50 food every 5 seconds."
    construction_tooltip = " Build a Farm"
    construction_cost = [100, 0, 0, 0]
    construction_time = 1
    armor = 0

    def __init__(self, pos, map,  player_owner_of_unit):

        self.name = " Farm"
        self.sprite = pygame.image.load(os.path.join(assets_path, "Farm.png"))

        self.construction_cost = [100, 0, 0, 0]
        self.construction_time = 1

        self.max_health = 10
        self.max_population_bonus = 0

        super().__init__(pos, map, player_owner_of_unit)

    def update(self):
        now = pygame.time.get_ticks()
        # every 5 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.owner.resources[2] += 50
            self.resource_manager_cooldown = now


class House(Building):
    description = " Each House increases the maximum population by 5."
    construction_tooltip = " Build a House"
    construction_cost = [600, 0, 0, 0]
    construction_time = 1
    armor = -2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "House"
        self.sprite = pygame.image.load(os.path.join(assets_path, "House.png"))

        self.construction_cost = [600, 0, 0, 0]
        self.construction_time = 1

        self.max_health = 50
        player_owner_of_unit.max_population += 5

        super().__init__(pos, map, player_owner_of_unit)

    def update(self):
        now = pygame.time.get_ticks()
        # every 5 secs :
        if now - self.resource_manager_cooldown > 5000:
            self.resource_manager_cooldown = now


