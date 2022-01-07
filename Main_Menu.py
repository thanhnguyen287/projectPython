from pygame.locals import *
import pygame
from pygame import *
import os
from pygame import mixer
from main import *
import pygame


pygame.init()

pygame.init()

# create screen
pygame.display.set_caption('Start Menu')
screen = pygame.display.set_mode((1200, 675))

# add icon
pygame.display.set_caption("AOE 2")
icon = pygame.image.load(os.path.join(assets_path, 'AOE 2.jpg'))
pygame.display.set_icon(icon)
font = pygame.font.SysFont('Tarjan', 50)

font = pygame.font.Font("resources/this.otf", 50)

textsurface = font.render("text", False, (0, 0, 0))  # "text", antialias, color


background = pygame.image.load(os.path.join(assets_path, 'EV0qwWIXQAA8qpN.jpg'))
pygame.display.set_caption('AOE 2: Homemade Edition')

mixer.music.load(os.path.join(assets_path,'Age of Empires II- Definitive Edition - Main Menu Soundtrack (audio-extractor.net).wav'))
mixer.music.play(-1)

# define colours
bg = (204, 102, 0)
red = (255, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
GRAY = (30, 30, 30)
BROWN=(88, 41, 0)

# define global variable
clicked = False
counter = 0

screen.blit(background, (0, 0))


class Button():
    # colours for button and text
    button_col = (88, 41, 0)
    hover_col = (30, 30, 30)
    click_col = (30, 30, 30)
    text_col = (0, 0, 0)
    width = 220
    height = 70

    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def draw_button(self):

        global clicked
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # create pygame Rect object for the button
        button_rect = Rect(self.x, self.y, self.width, self.height)

        # check mouseover and clicked conditions
        if button_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = True
                pygame.draw.rect(screen, self.click_col, button_rect)
            elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
                clicked = False
                action = True
            else:
                pygame.draw.rect(screen, self.hover_col, button_rect)
        else:
            pygame.draw.rect(screen, self.button_col, button_rect)

        # add shading to button
        pygame.draw.line(screen, white, (self.x, self.y), (self.x + self.width, self.y), 2)
        pygame.draw.line(screen, white, (self.x, self.y), (self.x, self.y + self.height), 2)
        pygame.draw.line(screen, black, (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 2)
        pygame.draw.line(screen, black, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 2)

        # add text to button
        text_img = font.render(self.text, True, self.text_col)
        text_len = text_img.get_width()
        screen.blit(text_img, (self.x + int(self.width /2) - int(text_len /2), self.y + 10))
        return action

newGame_button = Button(50, 250, 'NewGame')
loadGame_button = Button(50, 350, 'LoadGame')
option_button = Button(50, 450, 'Option')
exit_button = Button(50, 550, 'Exit')


run = True
while run:

    screen.blit(background, ( 0, 0))

    if newGame_button.draw_button():
        main()
    if exit_button.draw_button():
        exit_button.quit()
    if option_button.draw_button():
        options()
    if loadGame_button.draw_button():
        print('Load Game')

    counter_img = font.render(str(counter), True, red)
    screen.blit(counter_img, (2000, 1000))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    def draw_text(text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)


    click = True


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

pygame.quit()
