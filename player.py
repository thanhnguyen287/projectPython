import pygame

class Player:

    # stone, gold, lumber, food
    ressources = [0, 0, 0, 0]

    def __init__(self, name, controller, starting_ressources, civilization):

        self.name = name

        # True = Human, False = AI
        self.controller = controller

        self.ressources = starting_ressources

        self.civilization = civilization

    def increaseRessources(self, ressource_type, amount):
        # 0 for STONE, 1 for GOLD, 2 for LUMBER, 3 for FOOD
        self.ressources[ressource_type] += amount


playerOne = Player("Tristan", True, [250, 1000, 500, 100], "GREEK")