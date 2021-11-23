import pygame, sys
from pygame.locals import *
from pygame import mixer
from settings import assets_path
import os

pygame.init()

#create screen
pygame.display.set_caption('Start Menu')
screen = pygame.display.set_mode((1200,675))
#COLOR
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (30, 30, 30)
#add icon
pygame.display.set_caption("AOE 2")
icon = pygame.image.load(os.path.join(assets_path,'AOE 2.jpg'))
pygame.display.set_icon(icon)

font = pygame.font.SysFont('Corbel', 50)

background = pygame.image.load(os.path.join(assets_path,'EV0qwWIXQAA8qpN.jpg'))

pygame.display.set_caption('AOE 2: Homemade Edition')

#background music
mixer.music.load((os.path.join(assets_path,'Age of Empires II- Definitive Edition - Main Menu Soundtrack (audio-extractor.net).wav')))

mixer.music.play(-1)
pygame.display.update()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

click = False

def main_menu():
    clock =pygame.time.Clock()
    while True:
        screen.fill((0,0,0))
        screen.blit(background,(0,0))
        draw_text('MENU', font, GRAY, screen, 50 ,150 )

        mx, my = pygame.mouse.get_pos()
        text2 = font.render('Options', True, BLACK)
        text1 = font.render('Start ', True, BLACK)
        button_1 = pygame.Rect(50, 250, 100, 50)
        button_2 = pygame.Rect(50, 400, 160, 50)

        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                options()
        pygame.draw.rect(screen, (150, 75, 0), button_1)
        pygame.draw.rect(screen, (150, 75, 0), button_2)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        screen.blit(text1, (50,250))
        screen.blit(text2, (50,400))
        pygame.display.update()

        clock.tick(30)

def game():
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_text('game', font, (255, 255, 255), screen, 20, 20)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        pygame.display.update()

def options():
    running = True
    while running:
        screen.fill((0, 0, 0))

        draw_text('options', font, (255, 255, 255), screen, 20, 20)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        pygame.display.update()
main_menu()