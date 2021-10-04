import pygame

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


playerOne = Player("Tristan", True, [250, 1000, 500, 100], "GREEK")