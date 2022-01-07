from settings import *
from units import House
from game.utils import str_to_entity_class, draw_text


class Player:

    def __init__(self, name, controller, starting_resources, civilization):

        self.name = name

        # True = Human, False = AI
        self.is_human = controller
        #self.resources = {"wood": 0, "food": 0, "gold": 0, "stone": 0}
        self.resources = starting_resources
        self.age = 1
        self.current_population = 0
        self.max_population = 5

        self.unit_list = []

        self.unit_occupied = []

        self.building_list = []

        self.towncenter_pos = None

        self.civilization = civilization

        self.entity_costs = {
            "Farm": {"wood": 100, "stone": 0, "food": 0, "gold": 0},
            "House": {"wood": 600, "stone": 0, "food": 0, "gold": 0},
            "TownCenter": {"wood": 1000, "stone": 0, "food": 0, "gold": 0},

            "Villager": {"wood": 0, "stone": 0, "food": 10, "gold": 25}

        }

        self.entity_population_cost = {
            "Farm": 0,
            "House": 0,
            "TownCenter": 0,

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
        if entity_class == "House":
            entity_class = House
        elif type(entity_class) == str:
            entity_class = str_to_entity_class(entity_class)
        for resource_type in range(4):
            self.resources[resource_type] -= entity_class.construction_cost[resource_type]
        self.current_population += entity_class.population_produced

    def refund_entity_cost(self, entity_class):
        for resource_type in range(4):
            self.resources[resource_type] += entity_class.construction_cost[resource_type]
        self.current_population -= entity_class.population_produced

    def update_resources_bar_hd(self, screen):
        # resources display
        #screen.blit(top_menu_hd, (0, 0))
        screen.blit(resource_panel, (0, 0))
        screen.blit(wood_icon, (35, 11))
        screen.blit(food_icon, (35+82, 11))
        screen.blit(gold_icon, (35+162, 11))
        screen.blit(stone_icon, (35+242, 11))
        screen.blit(pop_icon, (35+330, 11))

        resource_text_pos = 70
        for resource_type in range(4):
            screen.blit(myfont.render(str(playerOne.resources[resource_type]), True, (255, 255, 255)),
                        (resource_text_pos, 17))
            resource_text_pos += 83

        #population
        population_text = str(playerOne.current_population) + "/" + str(playerOne.max_population)

        screen.blit(myfont.render(population_text, True, (255, 255, 255)), (resource_text_pos, 17))
        # age
        screen.blit(age_panel, (screen.get_size()[0]-age_panel.get_width(), 0))
        screen.blit(age_1, (screen.get_size()[0] - age_panel.get_width() + 12, 9))
        population_text = str(playerOne.current_population) + "/" + str(playerOne.max_population)
        if self.age == 1:
            screen.blit(age_1, (screen.get_size()[0] - age_panel.get_width() + 12, 9))
            age_text = "Dark Age"

        elif self.age == 2:
            screen.blit(age_2, (screen.get_size()[0] - age_panel.get_width() + 12, 9))
            age_text = "Feudal Age"

        elif self.age == 3:
            screen.blit(age_3, (screen.get_size()[0] - age_panel.get_width() + 12, 9))
            age_text = "Castle Age"

        else:
            screen.blit(age_4, (screen.get_size()[0] - age_panel.get_width() + 12, 9))
            age_text = "Imperial Age"

        draw_text(screen, age_text, 18, "WHITE", (screen.get_size()[0] - age_panel.get_width() + 90, 17))

playerOne = Player("Tristan", True, [1000, 5000, 250, 1000], "GREEK")
playerOne.age = 3
players = [playerOne]
player_list = [playerOne]
#  INIT FOR RESSOURCES DISPLAY
