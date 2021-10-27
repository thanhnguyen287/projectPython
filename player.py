from settings import *


class Player:


    def __init__(self, name, controller, starting_resources, civilization):

        self.name = name

        # True = Human, False = AI
        self.is_human = controller
        #self.resources = {"wood": 0, "food": 0, "gold": 0, "stone": 0}
        self.resources = starting_resources

        self.current_population = 0
        self.max_population = 0

        self.civilization = civilization

        self.building_costs = {
            "Farm": {"wood": 100, "stone": 0, "food": 0, "gold": 0},
            "House": {"wood": 600, "stone": 0, "food": 0, "gold": 0},
            "Town center": {"wood": 1000, "stone": 0, "food": 0, "gold": 0}

        }

    def update_resource(self, resource_type, amount):
        # 0 for WOOD, 1 for FOOD, 2 for GOLD, 3 for STONE
        if resource_type == 4:
            self.current_population += amount

        elif resource_type == 5:
            self.max_population += amount

        else:
            self.resources[resource_type] += amount

    def can_afford(self, building):
        affordable = True
        i = 0
        for ressource_type, cost in self.building_costs[building].items():
            if cost > self.resources[i]:
                affordable = False
            i += 1
        return affordable

    def pay_construction_cost(self, building):
        for resource_type in range(4):
            self.resources[resource_type] -= building.construction_cost[resource_type]

    def update_resources_bar(self, screen):
        # resources display
        screen.blit(top_menu, (0, 0))
        resource_text_pos = 35
        for resource_type in range(4):
            screen.blit(myfont.render(str(playerOne.resources[resource_type]), True, (255, 255, 255)), (resource_text_pos, 2))
            resource_text_pos += 65

"""
    def is_affordable(self, building):
        affordable = True
        for resource, cost in self.building_costs[building].items():
            if cost > self.resources[resource]:
                affordable = False
        return affordable
"""

"""
    def can_afford(self, building):
        affordable = True
        for resource_type in range(4):
            if building.construction_cost[resource_type] > self.resources[resource_type]:
                affordable = False
        return affordable
"""

playerOne = Player("Tristan", True, [500, 750, 250,1000], "GREEK")
players = [playerOne]
#  INIT FOR RESSOURCES DISPLAY

"""
display_wood = myfont.render(str(playerOne.resources[0]), True, (255, 255, 255))
display_food = myfont.render(str(playerOne.resources[1]), True, (255, 255, 255))
display_gold = myfont.render(str(playerOne.resources[2]), True, (255, 255, 255))
display_stone = myfont.render(str(playerOne.resources[3]), True, (255, 255, 255))
"""
