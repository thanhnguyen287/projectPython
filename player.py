from settings import *
from units import House, TownCenter,Farm, Villager, Clubman, Bowman
from game.utils import draw_text


class Player:

    def __init__(self, name, controller, starting_resources,color="RED"):

        self.name = name
        self.color = color
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
        self.towncenter = None
        self.townhall_placed = False

        self.entity_costs = {
            "Farm": {"wood": 100, "food": 0, "gold": 0, "stone": 0},
            "House": {"wood": 300, "food": 0, "gold": 0, "stone": 50},
            "TownCenter": {"wood": 1000, "food": 0, "gold": 0, "stone": 100},

            "Villager": {"wood": 0, "food": 10, "gold": 25, "stone": 0},
            "Advance to Feudal Age": {"wood": 0, "food": 500, "gold": 0, "stone": 0},
            "Advance to Castle Age": {"wood": 0, "food": 800, "gold": 200, "stone": 0},
            "Advance to Imperial Age": {"wood": 0, "food": 1000, "gold": 800, "stone": 0}

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

        if entity != "Advance to Feudal Age" and entity != "Advance to Castle Age" and entity != "Advance to Imperial Age" and self.current_population + self.entity_population_cost[entity] > self.max_population:
            affordable = False
        return affordable

    def pay_entity_cost(self, entity):
        for resource_type in range(4):
            self.resources[resource_type] -= entity.construction_cost[resource_type]

    def pay_entity_cost_bis(self, entity_class):
        if type(entity_class) == str:
            entity_class = str_to_entity_class(entity_class)
        for resource_type in range(4):
            self.resources[resource_type] -= entity_class.construction_cost[resource_type]
        #self.current_population += entity_class.population_produced

    def refund_entity_cost(self, entity_class):
        for resource_type in range(4):
            self.resources[resource_type] += entity_class.construction_cost[resource_type]
        self.current_population -= entity_class.population_produced

    def update_resources_bar(self, screen):
        # resources display
        screen.blit(resource_panel, (0, 0))
        screen.blit(wood_icon, (35, 11))
        screen.blit(food_icon, (35+82, 11))
        screen.blit(gold_icon, (35+162, 11))
        screen.blit(stone_icon, (35+242, 11))
        screen.blit(pop_icon, (35+330, 11))

        resource_text_pos = 70
        for resource_type in range(4):
            screen.blit(myfont.render(str(MAIN_PLAYER.resources[resource_type]), True, (255, 255, 255)),
                        (resource_text_pos, 17))
            resource_text_pos += 83

        #population
        population_text = str(MAIN_PLAYER.current_population) + "/" + str(MAIN_PLAYER.max_population)

        screen.blit(myfont.render(population_text, True, (255, 255, 255)), (resource_text_pos, 17))
        # age
        screen.blit(age_panel, (screen.get_size()[0]-age_panel.get_width(), 0))
        screen.blit(age_1, (screen.get_size()[0] - age_panel.get_width() + 12, 9))
        population_text = str(MAIN_PLAYER.current_population) + "/" + str(MAIN_PLAYER.max_population)
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


playerOne = Player("Lucien", True, [1000, 10000, 10000, 10000], color="BLUE")
playerOne.age = 1

playerTwo = Player("AI", True, [1000, 1000, 1000, 1000], color="RED")
playerTwo.age = 1
player_list = [playerOne, playerTwo]
#  INIT FOR RESSOURCES DISPLAY

#define which player is controlled by us
MAIN_PLAYER = playerOne

def str_to_entity_class(name: str):
    if name == "TownCenter":
        return TownCenter
    elif name == "House":
        return House
    elif name == "Farm":
        return Farm
    elif name == "Villager":
        return Villager
    elif name == "Clubman":
        return Clubman
    elif name == "Bowman":
        return Bowman
