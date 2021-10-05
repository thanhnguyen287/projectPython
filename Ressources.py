import pygame
from settings import *
from player import *


#créer une classe qui représente les ressources


class Ressource

  def  __init__(self):
    
    self.nbRessources = 0
    self.typeRessource = ""
    
  def __init__(self, nbRess, laRess):
    self.nbRessources = nbRess
    self.typeRessource = laRess

  def getTypeRessource(self):
    return self.typeRessource

  def getNbRessources(self):
    return self.nbRessources

  def setTypeRessource(self, typeRess):
    self.typeRessource = typeRess
   
  def setNbRessources(self, nbRess):
    self.nbRessources = nbRess

# Writing style
myfont = pygame.font.SysFont("monospace", 20)

  def update_ressources_bar(self,screen):
    #  INIT FOR RESSOURCES DISPLAY
    self.display_stone = myfont.render(str(playerOne.ressources[0]), True, (10, 10, 10))
    self.display_gold = myfont.render(str(playerOne.ressources[1]), True, (10, 10, 10))
    self.display_lumber = myfont.render(str(playerOne.ressources[2]), True, (10, 10, 10))
    self.display_food = myfont.render(str(playerOne.ressources[3]), True, (10, 10, 10))

    self.screen.blit(top_menu, (180, 95))
    self.screen.blit(myfont.render(str(playerOne.ressources[0]), True, (10, 10, 10), (300, 130))
    self.screen.blit(myfont.render(str(playerOne.ressources[1]), True, (10, 10, 10), (500, 130))
    self.screen.blit(myfont.render(str(playerOne.ressources[2]), True, (10, 10, 10), (700, 130))
    self.screen.blit(myfont.render(str(playerOne.ressources[3]), True, (10, 10, 10), (900, 130))


