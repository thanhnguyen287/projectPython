import pygame
from .utils import draw_text

class Hud:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.hud_color = (198, 155, 93, 175)

        #resources hud

        self.resources_surface = pygame.Surface((width, height * 0.025), pygame.SRCALPHA)
        self.resources_surface.fill(self.hud_color)

        #building hud
        self.build_surface = pygame.Surface((width * 0.15, height * 0.25), pygame.SRCALPHA)
        self.build_surface.fill(self.hud_color)

        #select hud
        self.select_surface = pygame.Surface((width * 0.3, height * 0.2), pygame.SRCALPHA)
        self.select_surface.fill(self.hud_color)

        self.images = self.load_images()
        self.tiles = self.create_build_hud()

        self.selected_tile = None

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

        mouse_pos = pygame.mouse.get_pos()
        mouse_action = pygame.mouse.get_pressed()

        #deselction
        if mouse_action[2]:
            self.selected_tile = None

        #parcours de liste pour voir quelle tile est selectionnée
        for tile in self.tiles:

            if tile["rect"].collidepoint(mouse_pos):
                if mouse_action[0]:
                    self.selected_tile = tile

    def draw(self, screen):

        if self.selected_tile is not None:
            img = self.selected_tile["image"].copy()
            #transparency
            img.set_alpha(100)

            screen.blit(img, pygame.mouse.get_pos())

        #display
        screen.blit(self.resources_surface, (0, 0))

        screen.blit(self.build_surface, (0, self.height * 0.75))

        screen.blit(self.select_surface, (self.width * 0.35, self.height * 0.8))

        for tile in self.tiles:
            screen.blit(tile["icon"], tile["rect"].topleft)

        # resources
        pos = self.width - 400
        for resource in ["wood :", "stone :", "gold :"]:
            draw_text(screen, resource, 30, (255, 255, 255), (pos, 0))
            pos += 100

    def load_images(self):
        building1 = pygame.image.load("Resources/assets/town_center.png")
        building2 = pygame.image.load("Resources/assets/House_sprite.png")

        images = {
            "building1": building1,
            "building2": building2
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



