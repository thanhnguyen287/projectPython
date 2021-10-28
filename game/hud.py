import os
from settings import *
import pygame
from .utils import draw_text
from player import playerOne
from math import ceil

class Hud:

    def __init__(self, width, height):

        self.width = width
        self.height = height
        self.hud_color = (198, 155, 93, 175)

        #building hud - 3rd line is for collision
        self.build_surface = pygame.Surface((width * 0.15, height * 0.25), pygame.SRCALPHA)

        self.build_surface.fill(self.hud_color)
        self.build_rect = self.build_surface.get_rect(topleft=(0, self.height * 0.75))

        #select hud - same for collision
        self.select_surface = pygame.Surface((width * 0.3, height * 0.2), pygame.SRCALPHA)
        self.select_surface.fill(self.hud_color)
        self.select_rect = self.select_surface.get_rect(topleft =(self.width * 0.35, self.height * 0.8))

        self.images = self.load_images()
        self.tiles = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None

    def create_build_hud(self):

        render_pos = [0 + 15, self.height * 0.8 + 10]
        object_width = self.build_surface.get_width()

        tiles = []

        for image_name, image in self.images.items():

            pos = render_pos.copy()
            if image_name == "Farm":
                image_scale = farm_icon_hd
            elif image_name == "Town center":
                image_scale = town_center_icon
            elif image_name == "House":
                image_scale = house_icon

            else:
                image_tmp = image.copy()
                image_scale = self.scale_image(image_tmp, w=40) #a modifier pour s'adapter a l'ecran
            rect = image_scale.get_rect(topleft=pos)

            tiles.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.images[image_name],
                    "rect": rect,
                    "affordable" : True
                }
            )

            render_pos[0] += image_scale.get_width() + 5 #modifier le 20 pour que ça marche pour tout ecran

        return tiles

    def update(self):

        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        mouse_action = pygame.mouse.get_pressed()

        #deselection by right-clicking
        if mouse_action[2]:
            self.selected_tile = None

        # building selection inside the build menu
        for tile in self.tiles:
            if playerOne.can_afford(tile["name"]):
                tile["affordable"] = True
            else:
                tile["affordable"] = False

            if tile["rect"].collidepoint(mouse_pos) and tile["affordable"]:
                if mouse_action[0]:
                    self.selected_tile = tile

    # display
    def draw(self, screen):

        # resources bar
        playerOne.update_resources_bar_hd(screen)

        # build menu

        # old display
        #screen.blit(self.build_surface, (0, self.height * 0.75))
        #new one
        screen.blit(bot_menu_building_hd, (0, self.height - 182))
        # display of the buildings icons inside the build menu
        for tile in self.tiles:
            icon = tile["icon"].copy()
            if not tile["affordable"]:
                icon.set_alpha(100)
            screen.blit(icon, tile["rect"].topleft)

        # selection (bottom middle menu)
        if self.examined_tile is not None:
            w, h = self.select_rect.width, self.select_rect.height
            screen.blit(self.select_surface, (self.width * 0.35, self.height * 0.79))
            # as we are scaling it, we make a copy
            img = self.examined_tile.sprite.copy()
            img_scaled = self.scale_image(img, h*0.7)
            # for now, we display the picture of the object and its name
            screen.blit(img_scaled, (self.width * 0.35, self.height * 0.79 + 30))
            #name
            draw_text(screen, self.examined_tile.name, 40, (255, 255, 255), self.select_rect.midtop)

            #lifebar and numbers
            self.display_life(screen, self.examined_tile)

    def load_images(self):
        town_center = pygame.image.load("Resources/assets/town_center.png").convert_alpha()
        house = pygame.image.load("Resources/assets/House.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/farm.png").convert_alpha()

        images = {
            "Town center": town_center,
            "House": house,
            "Farm": farm
        }
        return images

    def scale_image(self, image, w=None, h=None):

        if (w == None) and (h == None):
            pass
        elif h == None:
            scale = w/image.get_width()
            h = scale * image.get_height()
            image = pygame.transform.scale(image, (int(w), int(h)))
        elif w == None:
            scale = h/image.get_height()
            w = scale * image.get_width()
            image = pygame.transform.scale(image, (int(w), int(h)))
        else:
            image = pygame.transform.scale(image, (int(w), int(h)))

        return image

    def display_life(self, screen, building):
        #health bar
        # to get the same health bar size and not have huge ones, we use a ratio
        health_bar_length = 100
        hp_displayed = (building.current_health / building.max_health * health_bar_length)

        pygame.draw.rect(screen, (255, 0, 0), (self.width * 0.36, self.height * 0.9 + 30, hp_displayed, 6))
        pygame.draw.rect(screen, (25, 25, 25), (self.width*0.36, self.height * 0.9 + 30, health_bar_length, 6),2)

        # health text
        health_text = str(building.current_health) + " / " + str(building.max_health)
        draw_text(screen, health_text, 20, (255, 255, 255), (self.width*0.38, self.height*0.92 +30))