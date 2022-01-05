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

        self.unit_list = []
        self.unit_occupied = []

        self.towncenter_pos = None

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

    def update_resource(self, resource_type: str, amount):

        if resource_type == "WOOD":
            self.resources[0] += amount
        elif resource_type == "FOOD":
            self.resources[1] += amount
        elif resource_type == "GOLD":
            self.resources[2] += amount
        elif resource_type == "STONE":
            self.resources[3] += amount
        elif resource_type == "CURRENT_POP":
            self.current_population += amount
        elif resource_type == "MAX_POP":
            self.max_population += amount

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

    def pay_entity_cost_bis(self, entity_class):
        for resource_type in range(4):
            self.resources[resource_type] -= entity_class.construction_cost[resource_type]
        self.current_population += entity_class.population_produced

    def refund_entity_cost(self, entity_class):
        for resource_type in range(4):
            self.resources[resource_type] += entity_class.construction_cost[resource_type]
        self.current_population -= entity_class.population_produced

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


playerOne = Player("Tristan", True, [5000, 5000, 250, 1000], "GREEK")
player_list = [playerOne]
#  INIT FOR RESSOURCES DISPLAY
