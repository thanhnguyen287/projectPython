import os
from settings import *
import pygame
from .utils import draw_text
from player import players



class Hud:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.hud_color = (198, 155, 93, 175)

        #resources hud

        #self.resources_surface = pygame.Surface((width, height * 0.025), pygame.SRCALPHA)
        #self.resources_surface.fill(self.hud_color)

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

        render_pos = [0 + 10, self.height * 0.75 + 10]
        object_width = self.build_surface.get_width()

        tiles = []

        for image_name, image in self.images.items():

            pos = render_pos.copy()
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, w=40) #a modifier pour s'adapter a l'ecran
            rect = image_scale.get_rect(topleft=pos)

            tiles.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.images[image_name],
                    "rect": rect
                }
            )

            render_pos[0] += image_scale.get_width() + 20 #modifier le 20 pour que ça marche pour tout ecran

        return tiles

    def update(self):

        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        mouse_action = pygame.mouse.get_pressed()

        #deselection by right-clicking
        if mouse_action[2]:
            self.selected_tile = None

        #parcours de liste pour voir quelle tile est selectionnée
        for tile in self.tiles:
            if tile["rect"].collidepoint(mouse_pos):
                if mouse_action[0]:
                    self.selected_tile = tile

    # display
    def draw(self, screen):

        # resources bar
        for a_player in players:
            if a_player.is_human:
                a_player.update_ressources_bar(screen)

        # build menu
        screen.blit(self.build_surface, (0, self.height * 0.75))

        # selection (bottom middle menu)
        if self.examined_tile is not None:
            w, h = self.select_rect.width, self.select_rect.height
            screen.blit(self.select_surface, (self.width * 0.35, self.height * 0.79))
            # as we are scaling it, we make a copy
            img = self.images[self.examined_tile["tile"]].copy()
            img_scaled = self.scale_image(img, h*0.9)
            # for now, we display the picture of the object and its name
            screen.blit(img_scaled, (self.width * 0.35 - 10, self.height * 0.79 + 10 ))
            draw_text(screen, self.examined_tile["tile"], 40, (255, 255, 255), self.select_rect.midtop)


        #display of the buildings icons inside the build menu
        for tile in self.tiles:
            screen.blit(tile["icon"], tile["rect"].topleft)

        # resources
        #pos = self.width - 400
        #for resource in ["wood :", "stone :", "gold :"]:
            #draw_text(screen, resource, 30, (255, 255, 255), (pos, 0))
            #pos += 100

    def load_images(self):
        tree = pygame.image.load(os.path.join(assets_path, "tree.png")).convert_alpha()
        rock = pygame.image.load(os.path.join(assets_path, "rock.png")).convert_alpha()

        building1 = pygame.image.load("Resources/assets/town_center.png").convert_alpha()
        building2 = pygame.image.load("Resources/assets/House_sprite.png").convert_alpha()

        images = {
            "building1": building1,
            "building2": building2,
            "tree": tree,
            "rock": rock,
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



