import pygame, sys, os
import pygame.mouse
from math import floor

from settings import *

pygame.init()
pygame.mixer.init()


# for unit
class Animation(pygame.sprite.Sprite):
    # change this to make the animation quicker or slower

    def __init__(self, pos_x=0, pos_y=0, sprites=[], animation_speed=0.15):
        super().__init__()

        self.sprites = sprites
        self.current_sprite = 0

        self.selected_sprites_list = self.sprites["BLUE"]["0"][self.current_sprite]
        # used to know if we must use the angle stuff (only for units, no need for buildings)
        self.angle = "0"
        self.color = "BLUE"
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
            self.image = self.sprites[self.current_sprite]

        else:
            self.image = self.sprites["BLUE"]["0"][self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        # old stuff, will maybe be used one day. Kinda a file with offset for every sprite.
        # self.anchor_list = None

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0), anchor_list=None, color="BLUE", angle="0"):
        self.color = color
        self.angle = angle
        if angle == 360: angle = 0
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # self.image = self.sprites["BLUE"][0][self.current_sprite]

        # we determine which sprites list to use with angle, color and age arguments
        # sprites list go from 0 to 3 for ages, not 1 to 4, hence the -1
        self.selected_sprites_list = self.sprites[self.color][str(angle)]

        if anchor_list is not None:
            self.anchor_list = anchor_list
        self.rect.topleft = [pos[0], pos[1]]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.selected_sprites_list):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.selected_sprites_list[int(self.current_sprite)]


class BoomAnimation(pygame.sprite.Sprite):
    # change this to make the animation quicker or slower

    def __init__(self, sprites_list, animation_speed=0.10):
        super().__init__()

        self.sprites = sprites_list
        self.current_sprite = 0

        # used to know if we must use the angle stuff (only for units, no need for buildings)
        self.angle = "0"
        self.color = "BLUE"
        self.index = 0
        self.current_frame = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [0, 0]

        # old stuff, will maybe be used one day. Kinda a file with offset for every sprite.
        # self.anchor_list = None

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0)):
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        self.rect.topleft = [pos[0], pos[1]]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]


class BuildingAnimation(pygame.sprite.Sprite):
    # change this to make the animation quicker or slower

    def __init__(self, pos_x=0, pos_y=0, sprites=[], animation_speed=0.15):
        super().__init__()

        self.sprites = sprites
        self.selected_sprites_list = []
        self.age = 1
        # used to know if we must use the angle stuff (only for units, no need for buildings)
        self.color = "BLUE"
        self.index = 0
        self.current_frame = 0
        self.current_sprite = 0
        self.animation_speed = animation_speed

        self.to_be_played = False

        self.image = self.sprites["BLUE"]["1"][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        # old stuff, will maybe be used one day. Kinda a file with offset for every sprite.
        # self.anchor_list = None

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0), age=1, color="BLUE"):
        self.age = age
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # we determine which sprites list to use with color and age arguments

        self.selected_sprites_list = self.sprites[self.color][str(self.age)]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.selected_sprites_list):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.selected_sprites_list[int(self.current_sprite)]


# sprites dic containing 4 lists with death animation sprites for every age
class BuildingDeathAnimation(pygame.sprite.Sprite):

    def __init__(self, unit, images, pos_x=0, pos_y=0, animation_speed=0.15):
        super().__init__()

        self.unit = unit
        self.color = self.unit.owner.color
        self.age = 1
        self.sprites = images
        # age will be updated when we call the death method display to match the unit's owner age.

        self.index = 0
        self.current_frame = 0
        self.current_sprite = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        # image is the image we blit, we change it quickly to create the animation
        self.image = self.sprites[str(self.age)][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.unit.death_animation_group.add(self)

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0)):
        self.age = self.unit.owner.age
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # we determine which sprites list to use with color and age arguments

        self.sprites = self.sprites[str(self.age)]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]


# sprites dic containing 8 lists with angles of attack animation
class VillagerAttackAnimation(pygame.sprite.Sprite):

    def __init__(self, unit, images, pos_x=0, pos_y=0, animation_speed=0.2):
        super().__init__()

        self.unit = unit
        self.color = self.unit.owner.color
        self.angle = 0
        self.sprites = images
        self.selected_angle_sprites = []
        # age will be updated when we call the death method display to match the unit's owner age.

        self.index = 0
        self.current_frame = 0
        self.current_sprite = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        # image is the image we blit, we change it quickly to create the animation
        self.image = self.sprites[str(self.angle)][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.unit.attack_animation_group.add(self)

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0)):
        self.angle = self.unit.angle
        if self.angle == 360: self.angle = 0
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # we determine which sprites list to use with color and age arguments
        # self.sprites = self.sprites[str(self.angle)]
        self.selected_angle_sprites = self.sprites[str(self.angle)]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.selected_angle_sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.selected_angle_sprites[int(self.current_sprite)]


class VillagerMiningAnimation(pygame.sprite.Sprite):

    def __init__(self, unit, images, pos_x=0, pos_y=0, animation_speed=0.4):
        super().__init__()

        self.unit = unit
        self.color = self.unit.owner.color
        self.angle = 0
        self.sprites = images
        self.selected_angle_sprites = []
        # age will be updated when we call the death method display to match the unit's owner age.

        self.index = 0
        self.current_frame = 0
        self.current_sprite = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        # image is the image we blit, we change it quickly to create the animation
        self.image = self.sprites[str(self.angle)][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.unit.mining_animation_group.add(self)

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0)):
        self.angle = self.unit.angle
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # we determine which sprites list to use with color and age arguments
        # self.sprites = self.sprites[str(self.angle)]
        self.selected_angle_sprites = self.sprites[str(self.angle)]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.selected_angle_sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.selected_angle_sprites[int(self.current_sprite)]


class IdleDragonAnimation(pygame.sprite.Sprite):

    def __init__(self, unit, images, pos_x=0, pos_y=0, animation_speed=0.10):
        super().__init__()

        self.unit = unit
        self.angle = 180
        self.sprites = images
        self.selected_angle_sprites = []
        # age will be updated when we call the death method display to match the unit's owner age.

        self.index = 0
        self.current_frame = 0
        self.current_sprite = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        # image is the image we blit, we change it quickly to create the animation
        self.image = self.sprites[str(self.angle)][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.unit.idle_animation_group.add(self)

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0)):
        self.angle = self.unit.angle
        if self.angle == 360: self.angle = 0

        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # we determine which sprites list to use with color and age arguments
        # self.sprites = self.sprites[str(self.angle)]
        self.selected_angle_sprites = self.sprites[str(self.angle)]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.selected_angle_sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.selected_angle_sprites[int(self.current_sprite)]


# sprites dic containing 8 lists with angles of attack animation
class DeathDragonAnimation(pygame.sprite.Sprite):

    def __init__(self, unit, images, pos_x=0, pos_y=0, animation_speed=0.2):
        super().__init__()

        self.unit = unit
        self.angle = 270
        self.sprites = images
        self.selected_angle_sprites = []
        # age will be updated when we call the death method display to match the unit's owner age.

        self.index = 0
        self.current_frame = 0
        self.current_sprite = 0
        self.animation_speed = animation_speed

        self.to_be_played = False
        # image is the image we blit, we change it quickly to create the animation
        self.image = self.sprites[self.angle][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.unit.death_animation_group.add(self)

    #######################################################################################################
    # pos : render_pos_x, render_pos_y. This is what you call in map or hud or game to display an animation#
    # example : play(render_pos_0, render_pos_1, age=3, color="YELLOW", angle = 180)                      #
    #######################################################################################################
    def play(self, pos=(0, 0)):
        self.angle = self.unit.angle
        if self.angle == 360: self.angle = 0
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos[0], pos[1]]
        # we determine which sprites list to use with color and age arguments
        # self.sprites = self.sprites[str(self.angle)]
        self.selected_angle_sprites = self.sprites[str(self.angle)]
        self.to_be_played = True

    def update(self):
        if self.to_be_played:
            self.current_sprite += self.animation_speed
        if floor(self.current_sprite) >= len(self.selected_angle_sprites):
            self.to_be_played = False
            self.current_sprite = 0
        self.image = self.selected_angle_sprites[int(self.current_sprite)]


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
