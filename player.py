from settings import *


class Player:

    ressources = [0, 0, 0, 0]   # stone, gold, lumber, food

    def __init__(self, name, controller, starting_ressources, civilization):

        self.name = name

        # True = Human, False = AI
        self.controller = controller

        self.ressources = starting_ressources

        self.current_population = 0
        self.max_population = 0

        self.civilization = civilization

    def increaseRessources(self, ressource_type, amount):
        # 0 for STONE, 1 for GOLD, 2 for LUMBER, 3 for FOOD
        if ressource_type == 4:
            self.current_population += amount

        elif ressource_type == 5:
            self.max_population += amount

        else:
            self.ressources[ressource_type] += amount

    def update_ressources_bar(self, screen):
        # ressources display
        screen.blit(top_menu, (0, 0))
        screen.blit(display_stone, (125, 35))
        screen.blit(display_gold, (320, 35))
        screen.blit(display_lumber, (535, 35))
        screen.blit(display_food, (715, 35))


playerOne = Player("Tristan", True, [250, 1000, 500, 100], "GREEK")
players = [playerOne
           ]
#  INIT FOR RESSOURCES DISPLAY

display_stone = myfont.render(str(playerOne.ressources[0]), True, (10, 10, 10))
display_gold = myfont.render(str(playerOne.ressources[1]), True, (10, 10, 10))
display_lumber = myfont.render(str(playerOne.ressources[2]), True, (10, 10, 10))
display_food = myfont.render(str(playerOne.ressources[3]), True, (10, 10, 10))
