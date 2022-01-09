import pygame, sys, os
import pygame.mouse
from math import floor

from settings import *

pygame.init()
pygame.mixer.init()


class Animation(pygame.sprite.Sprite):
    # change this to make the animation quicker or slower

    def __init__(self, pos_x, pos_y, sprites=[], animation_speed=0.15):
        super().__init__()

        self.sprites = sprites
        self.index = 0
        self.current_frame = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        if not sprites:
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_0.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_1.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_2.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_3.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_4.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_5.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_6.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_7.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_8.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_9.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_10.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_11.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_12.png"))
            self.sprites.append(pygame.image.load("resources/assets/Boom/496_13.png"))

        # for i in range (14):
        #	self.sprites.append(pygame.image.load('"496_" + str(i)) '))

        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]
        self.anchor_list = None

    #pos : render_pos_x, render_pos_y
    def play(self, pos=(0,0), anchor_list=None):
        if anchor_list is not None:
            self.anchor_list = anchor_list
        self.rect.topleft = [ pos[0], pos[1]]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]


player = Animation(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
moving_sprites = pygame.sprite.Group()
moving_sprites.add(player)


def load_images_better(path):
    """
    Loads all images in directory. The directory must only contain images.

    Args:
        path: The relative or absolute path to the directory to load images from.

    Returns:
        List of images.
    """

    images = []
    for file_name in os.listdir(path):
        image = pygame.image.load(path + os.sep + file_name).convert_alpha()
        images.append(image)
    return images
