from settings import *


class Player:

    ressources = [0, 0, 0, 0]   # wood, food, gold , stone

    def __init__(self, name, controller, starting_ressources, civilization):

        self.name = name

        # True = Human, False = AI
        self.controller = controller

        self.ressources = starting_ressources

        self.current_population = 0
        self.max_population = 0

        self.civilization = civilization

    def increaseRessources(self, ressource_type, amount):
        # 0 for WOOD, 1 for FOOD, 2 for GOLD, 3 for STONE
        if ressource_type == 4:
            self.current_population += amount

        elif ressource_type == 5:
            self.max_population += amount

        else:
            self.ressources[ressource_type] += amount

    def update_ressources_bar(self, screen):
        # ressources display
        screen.blit(top_menu, (0, 0))

        #position of display slightly varies depending on the number of digits of the corresponding resource

        # WOOD
        if self.ressources[0] < 10:
            screen.blit(display_wood, (60, 2))
            # 2 digits
        elif self.ressources[0] < 100:
            screen.blit(display_wood, (53, 2))
            # 3 digits
        elif self.ressources[0] < 1000:
            screen.blit(display_wood, (46, 2))
            # 4 digits
        elif self.ressources[0] < 10000:
            screen.blit(display_wood, (39, 2))
            # 5 digits : max
        else:
            screen.blit(display_wood, (32, 2))

        # FOOD
        if self.ressources[1] < 10:
            screen.blit(display_food, (128, 2))
            # 2 digits
        elif self.ressources[1] < 100:
            screen.blit(display_food, (121, 2))
            # 3 digits
        elif self.ressources[1] < 1000:
            screen.blit(display_food, (114, 2))
            # 4 digits
        elif self.ressources[1] < 10000:
            screen.blit(display_food, (107, 2))
            # 5 digits : max
        else:
            screen.blit(display_gold, (167, 2))

        # GOLD
        if self.ressources[2] < 10:
            screen.blit(display_gold, (195, 2))
            # 2 digits
        elif self.ressources[2] < 100:
            screen.blit(display_gold, (188, 2))
            # 3 digits
        elif self.ressources[2] < 1000:
            screen.blit(display_gold, (181, 2))
            # 4 digits
        elif self.ressources[2] < 10000:
            screen.blit(display_gold, (174, 2))
            # 5 digits : max
        else:
            screen.blit(display_gold, (167, 2))

        # STONE
        if self.ressources[3] < 10:
            screen.blit(display_stone, (263, 2))
            # 2 digits
        elif self.ressources[3] < 100:
            screen.blit(display_stone, (256, 2))
            # 3 digits
        elif self.ressources[3] < 1000:
            screen.blit(display_stone, (249, 2))
            # 4 digits
        elif self.ressources[3] < 10000:
            screen.blit(display_stone, (242, 2))
            # 5 digits : max
        else:
            screen.blit(display_stone, (235, 2))


playerOne = Player("Tristan", True, [500, 750, 250, 1000], "GREEK")
players = [playerOne
           ]
#  INIT FOR RESSOURCES DISPLAY

display_wood = myfont.render(str(playerOne.ressources[0]), True, (255, 255, 255))
display_food = myfont.render(str(playerOne.ressources[1]), True, (255, 255, 255))
display_gold = myfont.render(str(playerOne.ressources[2]), True, (255, 255, 255))
display_stone = myfont.render(str(playerOne.ressources[3]), True, (255, 255, 255))
