import pygame
pygame.init()
import math
import game

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()



#à modifier selon la taille de l'écran
screen = pygame.display.set_mode()



#afficher la bannière
background_menu = pygame.image.load("resources/assets/start_screen.jpg")
logo= pygame.image.load('resources/assets/AOE.jpg')
logo= pygame.transform.scale(logo,(400,400))
logo_rect= logo.get_rect()
logo_rect.x = math.ceil(screen.get_width() / 3)


#case login
login_button= pygame.image.load('assets/login.png')
login_button= pygame.transform.scale(login_button,(300,150))
login_button_rect= login_button.get_rect()
login_button_rect.x = math.ceil(screen.get_width()/ 2.33)
login_button_rect.y=math.ceil(screen.get_height()/ 1,5)

#under while running acant le démarrage du jeu ajout le menu
screen.blit(login_button,login_button.rec)
screen.blit(logo,(logo_rect)
#login_button_rect.collidepoint(event.pos)




#Password





