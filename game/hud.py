from settings import *
import pygame
from math import floor
from .utils import draw_text, scale_image, get_color_code
from player import playerOne
from units import Villager, TownCenter, House, Farm, Building
#from buildings import TownCenter, House, Farm, Building


class Hud:

    def __init__(self, width, height):

        self.width = width
        self.height = height
        self.hud_color = (198, 155, 93, 175)

        # bottom hud
        self.bottom_hud_surface = pygame.Surface((887, 182), pygame.SRCALPHA)
        self.bottom_hud_surface.fill((0, 0, 0, 75))
        self.bottom_hud_rect = self.bottom_hud_surface.get_rect(topleft=(0, self.height - 182))

        # tooltip hud
        self.tooltip_surface = pygame.Surface((width * 0.2, height * 0.15), pygame.SRCALPHA)
        # grey
        self.tooltip_color = (60, 60, 60, 150)
        self.tooltip_surface.fill(self.tooltip_color)
        self.tooltip_rect = self.tooltip_surface.get_rect(topleft=(0, self.height * 0.65))

        # unit_description_hud
        self.icon_size = (50, 50)
        self.trained_unit_icon_pos = (self.width * 0.30 + 65, self.height * 0.8 + 20)
        self.trained_unit_icon_surface = pygame.Surface(self.icon_size, pygame.SRCALPHA)
        self.trained_unit_icon_rect = self.tooltip_surface.get_rect(topleft=self.trained_unit_icon_pos)

        self.images = self.load_images()
        self.town_hall_menu = self.create_train_menu_town_hall()
        self.villager_menu = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None

        self.bottom_left_menu = None
        self.is_cancel_button_present = False

    def create_train_menu_town_hall(self):
        render_pos = [0 + 15, self.height * 0.8 + 10]
        object_width = 50

        tiles = []
        image_scale = None
        image_name = None
        rect = None

        for image_name, image in self.images.items():
            pos = render_pos.copy()

            if image_name == "Villager":
                image_scale = villager_icon
                rect = image_scale.get_rect(topleft=pos)

        tiles.append(
            {
                "name": image_name,
                "icon": image_scale,
                "image": self.images[image_name],
                "rect": rect,
                "affordable": True
            }
        )
        return tiles

    def create_build_hud(self):

        render_pos = [0 + 15, self.height * 0.8 + 10]

        tiles = []
        for image_name, image in self.images.items():

            pos = render_pos.copy()
            if image_name == "Farm":
                image_scale = farm_icon_hd

            elif image_name == "Town center":
                image_scale = town_center_icon

            elif image_name == "House":
                image_scale = house_icon

            elif image_name == "Villager":
                image_scale = villager_icon

            else:
                image_tmp = image.copy()
                image_scale = scale_image(image_tmp, w=40)  # a modifier pour s'adapter a l'ecran
            rect = image_scale.get_rect(topleft=pos)

            tiles.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.images[image_name],
                    "rect": rect,
                    "affordable": True
                }
            )

            render_pos[0] += image_scale.get_width() + 5  # modifier le 20 pour que ça marche pour tout ecran
        tiles.pop()

        return tiles

    def update(self, screen):

        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        mouse_action = pygame.mouse.get_pressed()
        # deselection by right-clicking
        if mouse_action[2]:
            self.selected_tile = None

        # building selection inside the build menu
        if self.bottom_left_menu is not None:
            for button in self.bottom_left_menu:
                if button["name"] != "STOP":
                    if playerOne.can_afford(button["name"]):
                        button["affordable"] = True
                    else:
                        button["affordable"] = False
                else:
                    #if town center is not working, we have to remove the cancel button as there is nothing to cancel
                    if self.examined_tile is not None and self.examined_tile.name == "Town center" and not self.examined_tile.is_working:
                        self.bottom_left_menu.pop()
                        self.is_cancel_button_present = False

            if self.examined_tile is not None and self.examined_tile.name == "Town center":
                if self.examined_tile.is_working and not self.is_cancel_button_present:
                    stop_icon_pos = [0 + 52 * 4, self.height * 0.8 + 52 * 2]
                    icon = stop_icon
                    rect = icon.get_rect(topleft=stop_icon_pos)
                    self.bottom_left_menu.append(
                        {
                            "name": "STOP",
                            "icon": stop_icon,
                            "image": None,
                            "rect": rect,
                            "tooltip": " Cancel",
                            "description": " Cancel the current action."
                        })
                    self.is_cancel_button_present = True

        # display

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]

        # resources bar
        playerOne.update_resources_bar_hd(screen)
        # bottom menu
        if self.examined_tile is not None:
            screen.blit(bot_complet_menu_building_hd, (0, self.height - 182))
            self.display_entity_description(screen)

            #if the town center is creating villager, we display the corresponding progression bar
            if type(self.examined_tile) == TownCenter and self.examined_tile.is_working:
                self.display_progress_bar(screen, Villager, self.examined_tile)
            #we display progression bar if a building is currently being built
            elif issubclass(type(self.examined_tile), Building) and self.examined_tile.is_being_built:
                self.display_progress_bar(screen, "Non_meaningful arg 1", "Non_meaningful arg 2", self.examined_tile)

            # building selection inside the build menu
            if self.bottom_left_menu is not None:
                #if it is not a building in construction
                if not issubclass(type(self.examined_tile), Building) or not self.examined_tile.is_being_built:
                    for tile in self.bottom_left_menu:
                        icon = tile["icon"].copy()
                        #if player cant affort to build/train entity, we make the icon transparent
                        if tile["name"] != "STOP" and not playerOne.can_afford(tile["name"]):
                            icon.set_alpha(100)
                        screen.blit(icon, tile["rect"].topleft)
                        if tile["rect"].collidepoint(mouse_pos) and tile["name"] != "STOP" and tile["affordable"]:
                            self.display_construction_tooltip(screen, tile["name"])
                        if tile["rect"].collidepoint(mouse_pos) and tile["name"] == "STOP":
                            self.display_construction_tooltip(screen, tile)

    def load_images(self):
        town_center = pygame.image.load("Resources/assets/town_center.png").convert_alpha()
        house = pygame.image.load("Resources/assets/House.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/farm.png").convert_alpha()

        villager = pygame.image.load("resources/assets/Villager.bmp").convert_alpha()

        images = {
            "Town center": town_center,
            "House": house,
            "Farm": farm,
            "Villager": villager
        }
        return images

    #display life of entity inside mid bottom menu (when examining smth)
     #if below 25 pourcent, life bar in red, 25-40 : orange , 40-60 : yellow, 60-100 : light or dark green
    def display_life_hud(self, screen, entity):
        # health bar
        # to get the same health bar size and not have huge ones, we use a ratio
        health_bar_length = 100
        hp_displayed = (entity.current_health / entity.max_health * health_bar_length)
        #from 1 to 100% of max health, used to know which color we use for the health bar
        unit_pourcentage_of_max_hp = (entity.current_health / entity.max_health) * 100

        if 0 < unit_pourcentage_of_max_hp <= 25:
            pygame.draw.rect(screen, get_color_code("RED"), (self.width * 0.185, self.height * 0.9 + 43, hp_displayed, 6))

        elif 25 < unit_pourcentage_of_max_hp <= 40:
            pygame.draw.rect(screen, get_color_code("ORANGE"), (self.width * 0.185, self.height * 0.9 + 43, hp_displayed, 6))

        elif 40 < unit_pourcentage_of_max_hp <= 60:
            pygame.draw.rect(screen, get_color_code("YELLOW"), (self.width * 0.185, self.height * 0.9 + 43, hp_displayed, 6))

        elif 60 < unit_pourcentage_of_max_hp <= 85:
            pygame.draw.rect(screen, get_color_code("GREEN"), (self.width * 0.185, self.height * 0.9 + 43, hp_displayed, 6))

        else:
            pygame.draw.rect(screen, get_color_code("DARK_GREEN"), (self.width * 0.185, self.height * 0.9 + 43, hp_displayed, 6))

        #outer rectangle for the shape of life bar, never changes
        pygame.draw.rect(screen, get_color_code("BLACK"), (self.width * 0.185, self.height * 0.9 + 43, health_bar_length, 6), 2)

        # health text
        health_text = str(entity.current_health) + " / " + str(entity.max_health)
        draw_text(screen, health_text, 16, (255, 255, 255), (self.width * 0.185 + 28, self.height * 0.92 + 33))

    # used for bottom mid menu
    def display_description(self, screen, entity):
        # warning - for now, you cannot render multiples lines
        draw_text(screen, entity.description, 15, (255, 255, 255), (self.width * 0.38 + 85, self.height * 0.92 - 70))

    # No longer used. Display which entity, its costs, and a brief description. Kept because why not
    def display_construction_tooltip_old(self, screen, entity):

        w, h = self.tooltip_rect.width, self.tooltip_rect.height
        screen.blit(self.tooltip_surface, (0, self.height * 0.64))
        pygame.draw.rect(self.tooltip_surface, (255, 201, 14),
                         pygame.Rect(0, 0, self.tooltip_rect.width, self.tooltip_rect.height), 2)
        # tooltip
        if entity == "Villager":
            draw_text(screen, Villager.construction_tooltip, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], self.tooltip_rect.topleft[1] - 4))
            # resources cost
            temp_pos = (27, self.height * 0.64 + 30)
            draw_text(screen, str(Villager.construction_cost[0]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55, self.height * 0.64 + 30)
            draw_text(screen, str(Villager.construction_cost[1]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 2, self.height * 0.64 + 30)
            draw_text(screen, str(Villager.construction_cost[2]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 3, self.height * 0.64 + 30)
            draw_text(screen, str(Villager.construction_cost[3]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 4, self.height * 0.64 + 30)
            draw_text(screen, str(Villager.population_produced), 12, (255, 201, 14), temp_pos)

            # description
            draw_text(screen, Villager.description, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

        elif entity == "Town center":
            draw_text(screen, TownCenter.construction_tooltip, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], self.tooltip_rect.topleft[1] - 4))
            # ressources cost display
            temp_pos = (27, self.height * 0.64 + 30)
            draw_text(screen, str(TownCenter.construction_cost[0]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55, self.height * 0.64 + 30)
            draw_text(screen, str(TownCenter.construction_cost[1]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 2, self.height * 0.64 + 30)
            draw_text(screen, str(TownCenter.construction_cost[2]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 3, self.height * 0.64 + 30)
            draw_text(screen, str(TownCenter.construction_cost[3]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 4, self.height * 0.64 + 30)
            draw_text(screen, str(TownCenter.population_produced), 12, (255, 201, 14), temp_pos)
            # short description
            draw_text(screen, TownCenter.description, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

        elif entity == "House":
            draw_text(screen, House.construction_tooltip, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], self.tooltip_rect.topleft[1] - 4))
            temp_pos = (27, self.height * 0.64 + 30)
            draw_text(screen, str(House.construction_cost[0]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55, self.height * 0.64 + 30)
            draw_text(screen, str(House.construction_cost[1]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 2, self.height * 0.64 + 30)
            draw_text(screen, str(House.construction_cost[2]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 3, self.height * 0.64 + 30)
            draw_text(screen, str(House.construction_cost[3]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 4, self.height * 0.64 + 30)
            draw_text(screen, str(House.population_produced), 12, (255, 201, 14), temp_pos)

            # description
            draw_text(screen, House.description, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

        elif entity == "Farm":
            draw_text(screen, Farm.construction_tooltip, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], self.tooltip_rect.topleft[1] - 4))
            temp_pos = (27, self.height * 0.64 + 30)
            draw_text(screen, str(Farm.construction_cost[0]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55, self.height * 0.64 + 30)
            draw_text(screen, str(Farm.construction_cost[1]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 2, self.height * 0.64 + 30)
            draw_text(screen, str(Farm.construction_cost[2]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 3, self.height * 0.64 + 30)
            draw_text(screen, str(Farm.construction_cost[3]), 12, (255, 201, 14), temp_pos)

            temp_pos = (27 + 55 * 4, self.height * 0.64 + 30)
            draw_text(screen, str(Farm.population_produced), 12, (255, 201, 14), temp_pos)

            # description
            draw_text(screen, Farm.description, 14, (220, 220, 220),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

        # construction/training resources costs icons
        screen.blit(wood_cost, (5, self.height * 0.64 + 25))
        screen.blit(food_cost, (0 + 55, self.height * 0.64 + 25))
        screen.blit(gold_cost, (0 + 110, self.height * 0.64 + 25))
        screen.blit(stone_cost, (0 + 165, self.height * 0.64 + 25))
        screen.blit(population_cost, (0 + 220, self.height * 0.64 + 25))

        # grey line
        temp_pos = (5, self.height * 0.64 + 55)
        pygame.draw.line(screen, (192, 192, 192), temp_pos, (temp_pos[0] + self.tooltip_rect.width - 20, temp_pos[1]))

    def display_entity_description(self, screen):
        # selection (bottom middle menu)
        w, h = self.bottom_hud_rect.width, self.bottom_hud_rect.height
        screen.blit(self.bottom_hud_surface, (0, self.height * 0.79))
        # as we are scaling it, we make a copy
        img = self.examined_tile.sprite.copy()
        if type(self.examined_tile) == Farm:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (self.width * 0.185 - 10, self.height * 0.79 + 58))
        elif type(self.examined_tile) == House:
            img_scaled = scale_image(img, h * 0.50)
            screen.blit(img_scaled, (self.width * 0.185 - 10, self.height * 0.79 + 43))

        elif type(self.examined_tile) == TownCenter:
            img_scaled = scale_image(img, h * 0.55)
            screen.blit(img_scaled, (self.width * 0.185 - 10, self.height * 0.79 + 48))
        # villager
        else:
            img_scaled = scale_image(img, h * 0.3)
            screen.blit(img_scaled, (self.width * 0.185 + 10, self.height * 0.79 + 33))

        # for now, we display the picture of the object and its name
        # name
        temp_pos = (self.width * 0.185 + 10, self.height * 0.79 + 20)
        draw_text(screen, self.examined_tile.name, 20, (255, 255, 255), temp_pos)
        temp_pos = (self.width * 0.185 + 120, self.height * 0.79 + 16)
        pygame.draw.line(screen, (50, 50, 50), temp_pos,
                         (temp_pos[0], temp_pos[1] + 150), 2)

        # attack and armor display
        temp_pos = (self.width * 0.185 + 175, self.height * 0.79 + 107)
        text = "Armor : "
        draw_text(screen, text, 15, (255, 201, 14), temp_pos)
        temp_pos = (self.width * 0.185 + 178, self.height * 0.79 + 128)
        draw_text(screen, str(self.examined_tile.armor), 12, (255, 255, 255), temp_pos)

        # buildings
        if issubclass(type(self.examined_tile), Building):
            temp_pos = (self.width * 0.185 + 130, self.height * 0.79 + 110)
            screen.blit(building_armor_icon, temp_pos)
        # units
        else:
            temp_pos = (self.width * 0.185 + 130, self.height * 0.79 + 45)
            screen.blit(melee_attack_icon, temp_pos)
            temp_pos = (self.width * 0.185 + 130, self.height * 0.79 + 110)
            screen.blit(armor_icon, temp_pos)

            temp_pos = (self.width * 0.185 + 175, self.height * 0.79 + 45)
            text = "Damage : "
            draw_text(screen, text, 15, (255, 201, 14), temp_pos)
            temp_pos = (self.width * 0.185 + 178, self.height * 0.79 + 65)
            draw_text(screen, str(self.examined_tile.attack_dmg) + " - " + str(self.examined_tile.attack_dmg + 1),
                      12, (255, 255, 255), temp_pos)

        # lifebar and numbers
        self.display_life_hud(screen, self.examined_tile)

    # display progress bar and icon of trained unit
    def display_progress_bar(self, screen, trained_entity, training_entity, building_built=None):
        # if we get building_arg, it means we must display the construction progress, else it is units training
        if building_built is not None:
            progress_bar_length = 120
            # to get the same health bar size and not have huge ones, we use a ratio
            progress_displayed = ((building_built.now - building_built.resource_manager_cooldown) / (
                    building_built.construction_time * 1000) * progress_bar_length)

            pygame.draw.rect(screen, (255, 201, 14),
                             (self.width * 0.30 + 120, self.height * 0.8 + 43, progress_displayed, 6))
            pygame.draw.rect(screen, (25, 25, 25),
                             (self.width * 0.30 + 120, self.height * 0.8 + 43, progress_bar_length, 6), 2)

            temp_text = "Construction progress..."
            draw_text(screen, temp_text, 13, (255, 255, 255), (self.width * 0.30 + 120, self.height * 0.8 + 27))

            # progress_time in secs
            progress_time = ((building_built.now - building_built.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time*100 / building_built.construction_time
            progress_text = str(floor(progress_time_pourcent)) + "%"
            draw_text(screen, progress_text, 12, (255, 255, 255), (self.width * 0.30 + 170, self.height * 0.8 + 53))

        # no building_built, which means we have to display a training unit progress bar
        else:
            if trained_entity == Villager:
                icon = villager_icon
            else:
                icon = None
            # health bar
            # to get the same health bar size and not have huge ones, we use a ratio
            progress_bar_length = 120
            progress_displayed = ((training_entity.now - training_entity.resource_manager_cooldown) / (
                        trained_entity.construction_time * 1000) * progress_bar_length)

            pygame.draw.rect(screen, (255, 201, 14),
                             (self.width * 0.30 + 120, self.height * 0.8 + 43, progress_displayed, 6))
            pygame.draw.rect(screen, (25, 25, 25),
                             (self.width * 0.30 + 120, self.height * 0.8 + 43, progress_bar_length, 6), 2)

            temp_text = "Training a " + str(trained_entity.name) + "..."
            draw_text(screen, temp_text, 13, (255, 255, 255), (self.width * 0.30 + 130, self.height * 0.8 + 27))

            # progress %
            health_text = str(int((training_entity.now - training_entity.resource_manager_cooldown) / 1000) * 20) + "%"
            draw_text(screen, health_text, 12, (255, 255, 255), (self.width * 0.30 + 170, self.height * 0.8 + 53))

            # icon and number of units being trained
            screen.blit(icon, self.trained_unit_icon_pos)
            black_color = (0, 0, 0)
            # Drawing little black rectangle to make it easier to read number of entities to train
            little_black_square_surface = pygame.Surface((7, 11), pygame.SRCALPHA)
            little_black_square_surface.fill(black_color)
            screen.blit(little_black_square_surface,
                        (self.trained_unit_icon_pos[0] + 42, self.trained_unit_icon_pos[1] + 38))

            draw_text(screen, str(training_entity.queue), 12, (255, 255, 255),
                      (self.trained_unit_icon_pos[0] + 43, self.trained_unit_icon_pos[1] + 37))

    # display what entity, its costs, and a brief description
    def display_construction_tooltip(self, screen, entity):
        display_tooltip_for_entity = True
        if entity == "Villager":
            entity = Villager
        elif entity == "Farm":
            entity = Farm
        elif entity == "House":
            entity = House
        elif entity == "Town center":
            entity = TownCenter
        else:
            display_tooltip_for_entity = False

        # display grey rectangle
        screen.blit(self.tooltip_surface, (0, self.height * 0.64))
        pygame.draw.rect(self.tooltip_surface, (255, 201, 14),
                         pygame.Rect(0, 0, self.tooltip_rect.width, self.tooltip_rect.height), 2)

        if display_tooltip_for_entity:
            # construction/training resources costs icons
            screen.blit(wood_cost, (5, self.height * 0.64 + 25))
            screen.blit(food_cost, (0 + 55, self.height * 0.64 + 25))
            screen.blit(gold_cost, (0 + 110, self.height * 0.64 + 25))
            screen.blit(stone_cost, (0 + 165, self.height * 0.64 + 25))
            screen.blit(population_cost, (0 + 220, self.height * 0.64 + 25))

            # text
            tooltip_text = entity.construction_tooltip + " (" + str(entity.construction_time) + "s)"
            draw_text(screen, tooltip_text, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0], self.tooltip_rect.topleft[1] - 4))
            # cost values
            temp_pos = (27, self.height * 0.64 + 30)
            draw_text(screen, str(entity.construction_cost[0]), 12, (255, 201, 14), temp_pos)
            temp_pos = (27 + 55, self.height * 0.64 + 30)
            draw_text(screen, str(entity.construction_cost[1]), 12, (255, 201, 14), temp_pos)
            temp_pos = (27 + 55 * 2, self.height * 0.64 + 30)
            draw_text(screen, str(entity.construction_cost[2]), 12, (255, 201, 14), temp_pos)
            temp_pos = (27 + 55 * 3, self.height * 0.64 + 30)
            draw_text(screen, str(entity.construction_cost[3]), 12, (255, 201, 14), temp_pos)
            temp_pos = (27 + 55 * 4, self.height * 0.64 + 30)
            draw_text(screen, str(entity.population_produced), 12, (255, 201, 14), temp_pos)

            # description
            draw_text(screen, entity.description, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

            # grey line
            temp_pos = (5, self.height * 0.64 + 55)
            pygame.draw.line(screen, (192, 192, 192), temp_pos,
                             (temp_pos[0] + self.tooltip_rect.width - 20, temp_pos[1]))

        # not tooltip for building/unit but for order
        else:
            # text
            tooltip_text = entity["tooltip"]
            draw_text(screen, tooltip_text, 14, (255, 0, 0),
                      (self.tooltip_rect.topleft[0], self.tooltip_rect.topleft[1] - 4))
            # grey line
            temp_pos = (5, self.height * 0.64 + 55)
            pygame.draw.line(screen, (192, 192, 192), temp_pos,
                             (temp_pos[0] + self.tooltip_rect.width - 20, temp_pos[1]))
            # description
            temp_pos = (27 + 55 * 4, self.height * 0.64 + 30)
            description_text = entity["description"]
            draw_text(screen, description_text, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

    def display_resources_health(self, screen, x, y, health, max_health):
        pygame.draw.rect(screen, (0, 255, 0), (x, y, health * 10, 10))
        pygame.draw.rect(screen, (25, 25, 25), (x, y, max_health * 10, 10), 4)

    def display_building(self, screen, building, scroll, render_pos):
        # we either display the building fully constructed or being built ( 4 possible states )
        if not building.is_being_built:
            screen.blit(building.sprite, (
                render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                        )
        else:
            if building.construction_progress == 0:
                if type(building) == TownCenter:
                    screen.blit(building_construction_1_2x2, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )
                else:
                    screen.blit(building_construction_1, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )

            elif building.construction_progress == 25:
                if type(building) == TownCenter:
                    screen.blit(building_construction_2_2x2, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )
                else:
                    screen.blit(building_construction_2, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )
            elif building.construction_progress == 50:
                if type(building) == TownCenter:
                    screen.blit(building_construction_3_2x2, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )
                else:
                    screen.blit(building_construction_3, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )
            elif building.construction_progress == 75:
                if type(building) == TownCenter:
                    screen.blit(building_construction_4_2x2, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                                )
                else:
                    screen.blit(building_construction_4, (
                        render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                        render_pos[1] - (building.sprite.get_height() - TILE_SIZE) + scroll.y)
                            )
