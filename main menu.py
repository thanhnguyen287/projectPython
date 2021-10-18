import pygame
pygame.init()
import math

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

#à modifier selon la taille de l'écran
screen = pygame.display.set_mode((1920,1070))



#afficher la bannière
background_menu = pygame.image.load('assets/menu2.jpg')
logo= pygame.image.load('asstes/logo.png')
logo= pygame.transform.scale(logo,(400,400))
logo_rect= logo.get_rect()
logo_rect.x = math.ceil(screen.get_width() / 3)


#case login
login_button= pygame.image.load('assets/login.png')
login_button= pygame.transform.scale(login_button,(300,150))
login_button_rect= login_buuton.get_rect()
login_button_rect.x = math.ceil(screen.get_width()/ 2.33)
login_button_rect.y=math.ceil(screen.get_height()/ 1,5)

#under while running acant le démarrage du jeu ajout le menu
screen.blit(login_button,login_button.rec)
screen.blit(logo,(logo_rect)
login_button_rect.collidepoint(event.pos):
    game.is_plaing = True


#Password
def password_check(pass):
    num='0123456789'
    caps='ABCDEFGHIJKLMNOPQRSTUVWYZ'
    spec_chars='#@&<>'
    S=0
    x=0
    y=0
    z=0
    while S!=3:
        while len(pass) != 6:
            pass=input('Password:')

        for i in range(len(pass)):
            if pass[i] in num:
                x = 1
            elif pass[i] in caps:
                y = 1
            elif pass[i] in spec_chars:
                z = 1
        S = x + y + z
        if S != 3:
            pass=input('*invalid password *, enter correct password:')
         else:
            print('Valid Password')





