from settings import *

class Player:

    def __init__(self, name, controller, starting_resources, civilization):

        self.name = name

        # True = Human, False = AI
        self.is_human = controller
        #self.resources = {"wood": 0, "food": 0, "gold": 0, "stone": 0}
        self.resources = starting_resources

        self.current_population = 0
        self.max_population = 5

        self.civilization = civilization

        self.entity_costs = {
            "Farm": {"wood": 100, "stone": 0, "food": 0, "gold": 0},
            "House": {"wood": 600, "stone": 0, "food": 0, "gold": 0},
            "Town center": {"wood": 1000, "stone": 0, "food": 0, "gold": 0},

            "Villager": {"wood": 0, "stone": 0, "food": 10, "gold": 25}

        }

        self.entity_population_cost = {
            "Farm": 0,
            "House": 0,
            "Town center": 0,

            "Villager": 1

        }

    def update_resource(self, resource_type, amount):
        # 0 for WOOD, 1 for FOOD, 2 for GOLD, 3 for STONE
        if resource_type == 4:
            self.current_population += amount

        elif resource_type == 5:
            self.max_population += amount

        else:
            self.resources[resource_type] += amount

    def can_afford(self, entity):
        affordable = True
        i = 0
        for ressource_type, cost in self.entity_costs[entity].items():
            if cost > self.resources[i]:
                affordable = False
            i += 1

        if self.current_population + self.entity_population_cost[entity] > self.max_population:
            affordable = False
        return affordable

    def pay_entity_cost(self, entity):
        for resource_type in range(4):
            self.resources[resource_type] -= entity.construction_cost[resource_type]



    def update_resources_bar(self, screen):
        # resources display
        screen.blit(top_menu, (0, 0))
        resource_text_pos = 35
        for resource_type in range(4):
            screen.blit(myfont.render(str(playerOne.resources[resource_type]), True, (255, 255, 255)), (resource_text_pos, 2))
            resource_text_pos += 65

    def update_resources_bar_hd(self, screen):
        # resources display
        screen.blit(top_menu_hd, (0, 0))
        resource_text_pos = 34
        for resource_type in range(4):
            screen.blit(myfont.render(str(playerOne.resources[resource_type]), True, (255, 255, 255)),
                        (resource_text_pos, 11))
            resource_text_pos += 68

        #population
        population_text = str(playerOne.current_population) + "/" + str(playerOne.max_population)

        screen.blit(myfont.render(population_text, True, (255, 255, 255)), (resource_text_pos, 11))


playerOne = Player("Tristan", True, [5000, 750, 250, 1000], "GREEK")
players = [playerOne]
#  INIT FOR RESSOURCES DISPLAY
