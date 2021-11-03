import os
import pygame
from pygame import *

pygame.init()

os.environ['SDL_VIDEO_CENTERED'] = '1'

screen_width=800
screen_height=500
screen=pygame.display.set_mode((screen_width, screen_height))

def text_format(message, textFont, textSize, textColor):
    newFont=pygame.font.Font(textFont, textSize)
    newText=newFont.render(message, 0, textColor)
    return newText

white=(255, 255, 255)
black=(0, 0, 0)
gray=(50, 50, 50)
red=(255, 0, 0)
green=(0, 255, 0)
blue=(0, 0, 255)
yellow=(255, 255, 0)

font = None

clock = pygame.time.Clock()
FPS=30
background = transform.scale(image.load("resources/assets/start_screen.jpg"), (800, 500))
def main_menu():

    menu=True
    selected="start"
    while menu:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    selected="start"
                elif event.key==pygame.K_DOWN:
                    selected="quit"
                if event.key==pygame.K_RETURN:
                    if selected=="start":
                        if _name_ == '_main_':
                             pygame.init()
                             game = Game()
                             game.run()
                    if selected=="quit":
                        pygame.quit()
                        quit()

        # Main Menu UI
        screen.blit(background, (0, 0))
        title=text_format("AGE OF EMPIRE", font, 90, yellow)
        if selected=="start":
            text_start=text_format("START", font, 75, black)
        else:
            text_start = text_format("START", font, 75, black)
        if selected=="quit":
            text_quit=text_format("QUIT", font, 75, red)
        else:
            text_quit = text_format("QUIT", font, 75, red)

        title_rect=title.get_rect()
        start_rect=text_start.get_rect()
        quit_rect=text_quit.get_rect()

        # Main Menu Text
        screen.blit(title, (screen_width/2 - (title_rect[2]/2), 80))
        screen.blit(text_start, (screen_width/2 - (start_rect[2]/2), 300))
        screen.blit(text_quit, (screen_width/2 - (quit_rect[2]/2), 360))
        pygame.display.update()
        clock.tick(FPS)
        pygame.display.set_caption(" AOE START SCREEN TEST")
# window settings
game = True
logiks = 100

tolkaninfo = False

game__over = False
main_menu()
pygame.quit()
quit()



# Game

# game menu
res = (800, 500)
screen = pygame.display.set_mode(res)

color = (255,255,255)

width = screen.get_width()
height = screen.get_height()
smallfont = pygame.font.SysFont('Arial', 35)

text = smallfont.render('quit' , True , color)

while game:
    # quit
    for ev in pygame.event.get():

        if ev.type == pygame.QUIT:
            game = False

    pygame.display.update()