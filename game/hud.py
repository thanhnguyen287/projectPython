from settings import *
import pygame
from math import floor
from .utils import draw_text, scale_image, get_color_code
from player import playerOne
from units import Villager, TownCenter, House, Farm, Building
# from buildings import TownCenter, House, Farm, Building
from .ActionMenu import *
from tech import Age_II, Age_III, Age_IV
from .animation import load_images_better, Animation, moving_sprites


class Hud:

    def __init__(self, width, height, screen):

        self.width = width
        self.height = height
        self.hud_color = (198, 155, 93, 175)
        self.screen = screen

        # bottom hud
        self.bottom_hud_surface = pygame.Surface((887, 182), pygame.SRCALPHA)
        self.bottom_hud_surface.fill((0, 0, 0, 100))
        self.bottom_hud_rect = self.bottom_hud_surface.get_rect(topleft=(0, self.height - 182))

        # tooltip hud
        self.tooltip_surface = pygame.Surface((width * 0.2, height * 0.15), pygame.SRCALPHA)
        # grey
        self.tooltip_color = (40, 40, 40, 150)
        self.tooltip_surface.fill(self.tooltip_color)
        self.tooltip_rect = self.tooltip_surface.get_rect(topleft=(0, self.height * 0.65))

        # unit_description_hud
        self.icon_size = (50, 50)
        self.trained_unit_icon_pos = (action_menu.get_width() + 290, self.height * 0.8 + 10)
        self.trained_unit_icon_surface = pygame.Surface(self.icon_size, pygame.SRCALPHA)
        self.trained_unit_icon_rect = self.tooltip_surface.get_rect(topleft=self.trained_unit_icon_pos)

        self.images = self.load_images()
        self.town_hall_menu = self.create_train_menu_town_hall()
        self.villager_menu = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None

        self.bottom_left_menu = None
        self.is_cancel_button_present = False

        # buildings sprites

        self.first_age_building_sprites = self.load_first_age_building_images()
        self.second_age_building_sprites = self.load_second_age_building_images()
        self.third_age_building_sprites = self.load_third_age_building_images()
        self.fourth_age_building_sprites = self.load_fourth_age_building_images()

        # resources sprites
        self.resources_sprites = self.load_resources_images()
        self.house_death_animation = None
        self.house_death_animation_group = None
        self.temp_bool = True

        # animations. contains stuff like : self.death_animations["house"]["animation"]
        self.death_animations = self.create_all_death_animations()
        self.villager_sprites = load_images_better("Resources/assets/Models/Units/Villager/Idle/fixed")
        self.villager_attack_animations = self.create_all_attack_animations()
        self.villager_idle_animations = self.create_all_idle_animations()
#        self.villager_walk_animations = self.create_all_walk_animations()


    def create_train_menu_town_hall(self):
        render_pos = [25, self.height - action_menu.get_height() + 40]
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
        # advancing age
        render_pos = [25, self.height - action_menu.get_height() + 125]
        tiles.append(
            {
                "name": "Advance to Feudal Age",
                "icon": advance_to_second_age_icon,
                "image": None,
                "rect": advance_to_second_age_icon.get_rect(topleft=render_pos),
                "affordable": True
            }
        )
        return tiles

    def create_build_hud(self):

        render_pos = [0 + 25, self.height * 0.8 + 10]

        tiles = []
        for image_name, image in self.images.items():

            pos = render_pos.copy()
            if image_name == "Farm":
                image_scale = farm_icon_hd

            elif image_name == "TownCenter":
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

        # building action_menu
        if self.bottom_left_menu is not None:
            for button in self.bottom_left_menu:
                if button["name"] != "STOP":
                    if playerOne.can_afford(button["name"]):
                        button["affordable"] = True
                    else:
                        button["affordable"] = False
                # we remove the advance to x age tech if it has been researched, and add the next one
                if self.examined_tile is not None and isinstance(self.examined_tile, TownCenter):
                    if button["name"] == "Advance to Feudal Age" and self.examined_tile.owner.age == 2:
                        self.bottom_left_menu.remove(button)
                        # adding next advancing age
                        self.bottom_left_menu.append(
                            {
                                "name": "Advance to Castle Age",
                                "icon": advance_to_third_age_icon,
                                "image": None,
                                "rect": advance_to_third_age_icon.get_rect(
                                    topleft=[25, self.height - action_menu.get_height() + 125]),
                                "affordable": True
                            })
                    elif button["name"] == "Advance to Castle Age" and self.examined_tile.owner.age == 3:
                        self.bottom_left_menu.remove(button)
                        # adding next advancing age
                        self.bottom_left_menu.append(
                            {
                                "name": "Advance to Imperial Age",
                                "icon": advance_to_fourth_age_icon,
                                "image": None,
                                "rect": advance_to_fourth_age_icon.get_rect(
                                    topleft=[25, self.height - action_menu.get_height() + 125]),
                                "affordable": True
                            })
                    elif button["name"] == "Advance to Imperial Age" and self.examined_tile.owner.age == 4:
                        self.bottom_left_menu.remove(button)
                    # if button is STOP
                    else:
                        # if town center is not working, we have to remove the cancel button as there is nothing to cancel
                        if self.is_cancel_button_present:
                            if not self.examined_tile.is_working:
                                self.bottom_left_menu.pop()
                                self.is_cancel_button_present = False

            if self.examined_tile is not None and isinstance(self.examined_tile, TownCenter):

                if self.examined_tile.is_working and not self.is_cancel_button_present:
                    stop_icon_pos = [action_menu.get_width() - 90, self.height * 0.8 + 52 * 2]
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

    def draw(self, screen, map, camera):
        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        #entity is string corresponding to class unit/building name
        for entity in self.death_animations:
            if entity == "Villager":
                #8 possible angles for villager
                for angle in range(0,8):
                    if self.death_animations[entity]["animation"][str(int(45*angle))].to_be_played:
                        self.death_animations[entity]["group"][str(int(45*angle))].draw(screen)
                        self.death_animations[entity]["animation"][str(int(45*angle))].update()
            else:
                if self.death_animations[entity]["animation"].to_be_played:
                    self.death_animations[entity]["group"].draw(screen)
                    self.death_animations[entity]["animation"].update()
        for angle in self.villager_attack_animations:
            if self.villager_attack_animations[angle]["animation"].to_be_played:
                self.villager_attack_animations[str(angle)]["group"].draw(screen)
                self.villager_attack_animations[angle]["animation"].update()
        for angle in self.villager_idle_animations:
            if self.villager_idle_animations[angle]["animation"].to_be_played:
                self.villager_idle_animations[str(angle)]["group"].draw(screen)
                self.villager_idle_animations[angle]["animation"].update()


        # resources bar
        playerOne.update_resources_bar(screen)
        # bottom menu

        if self.examined_tile is not None:
            # Draw minimap
            screen.blit(minimap_panel,
                        (self.width - minimap_panel.get_width(), self.height - selection_panel.get_height()))
            #map.draw_minimap(screen, camera)
            screen.blit(action_menu, (0, self.height - action_menu.get_height()))
            screen.blit(selection_panel, (action_menu.get_width(), self.height - selection_panel.get_height()))

            self.display_entity_description(screen, map)

            # if the town center is creating villager, we display the corresponding progression bar
            if type(self.examined_tile) == TownCenter and self.examined_tile.is_working:
                self.display_progress_bar(screen, Villager, self.examined_tile)
            # we display progression bar if a building is currently being built
            elif issubclass(type(self.examined_tile), Building) and self.examined_tile.is_being_built:
                self.display_progress_bar(screen, "Non_meaningful arg 1", "Non_meaningful arg 2", self.examined_tile)

            # building selection inside the build menu
            if self.bottom_left_menu is not None:
                # if it is not a building in construction
                if not issubclass(type(self.examined_tile), Building) or not self.examined_tile.is_being_built:
                    for tile in self.bottom_left_menu:
                        icon = tile["icon"].copy()
                        # if player cant affort to build/train entity, we make the icon transparent
                        if tile["name"] != "STOP" and not playerOne.can_afford(tile["name"]):
                            icon.set_alpha(100)
                        screen.blit(icon, tile["rect"].topleft)
                        if tile["rect"].collidepoint(mouse_pos) and tile["name"] != "STOP":
                            self.display_construction_tooltip(screen, tile["name"])
                        if tile["rect"].collidepoint(mouse_pos) and (
                                tile["name"] == "STOP" and tile["name"] != "Advance to Feudal Age" and tile[
                            "name"] != "Advance to Castle Age" and tile["name"] != "Advance to Imperial Age"):
                            self.display_construction_tooltip(screen, tile)

    def load_images(self):
        town_center = pygame.image.load(
            "Resources/assets/Models/Buildings/Town_Center/town_center_x1.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/house_1.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png").convert_alpha()

        # villager = pygame.image.load("resources/assets/villager.png").convert_alpha()
        villager = None
        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm,
            "Villager": villager
        }
        return images

    # display life of entity inside mid bottom menu (when examining smth)
    # if below 25 pourcent, life bar in red, 25-40 : orange , 40-60 : yellow, 60-100 : light or dark green
    def display_life_bar(self, screen, entity, map, for_hud=True, camera=None, for_resource=False):
        if for_hud:
            # health bar
            # to get the same health bar size and not have huge ones, we use a ratio
            health_bar_length = 100
            hp_displayed = (entity.current_health / entity.max_health * health_bar_length)
            # from 1 to 100% of max health, used to know which color we use for the health bar
            unit_pourcentage_of_max_hp = (entity.current_health / entity.max_health) * 100
            bar_info = (action_menu.get_width() + 30, self.height * 0.9 + 43, hp_displayed, 6)

            if 0 < unit_pourcentage_of_max_hp <= 25:
                pygame.draw.rect(screen, get_color_code("RED"), bar_info)

            elif 25 < unit_pourcentage_of_max_hp <= 40:
                pygame.draw.rect(screen, get_color_code("ORANGE"), bar_info)

            elif 40 < unit_pourcentage_of_max_hp <= 60:
                pygame.draw.rect(screen, get_color_code("YELLOW"), bar_info)

            elif 60 < unit_pourcentage_of_max_hp <= 85:
                pygame.draw.rect(screen, get_color_code("GREEN"), bar_info)

            else:
                pygame.draw.rect(screen, get_color_code("DARK_GREEN"), bar_info)

            # outer rectangle for the shape of life bar, never changes
            pygame.draw.rect(screen, get_color_code("BLACK"),
                             (action_menu.get_width() + 30, self.height * 0.9 + 43, health_bar_length, 6), 2)

            # health text
            health_text = str(entity.current_health) + " / " + str(entity.max_health)
            draw_text(screen, health_text, 16, (255, 255, 255), (action_menu.get_width() + 45, self.height * 0.92 + 33))

        # if for_hud is False, it means we must display the life bar above the entity
        elif not for_hud and not for_resource:

            # health bar size depends on the entity size : 1x1 tile, 2x2 tile, etc...
            # for 2x2 entities
            if type(entity) == TownCenter:
                health_bar_length = 200
                # bar_display_pos
                display_pos_x = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[
                                    0] + map.grass_tiles.get_width() / 2 + camera.scroll.x + 10

                display_pos_y = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[1] - 55 + camera.scroll.y

                hp_displayed = (entity.current_health / entity.max_health * health_bar_length)
                # from 1 to 100% of max health, used to know which color we use for the health bar
                unit_pourcentage_of_max_hp = (entity.current_health / entity.max_health) * 100
                bar_info = (display_pos_x, display_pos_y, hp_displayed, 6)  # change this line to make it above the unit

                if 0 < unit_pourcentage_of_max_hp <= 25:
                    pygame.draw.rect(screen, get_color_code("RED"), bar_info)

                elif 25 < unit_pourcentage_of_max_hp <= 40:
                    pygame.draw.rect(screen, get_color_code("ORANGE"), bar_info)

                elif 40 < unit_pourcentage_of_max_hp <= 60:
                    pygame.draw.rect(screen, get_color_code("YELLOW"), bar_info)

                elif 60 < unit_pourcentage_of_max_hp <= 85:
                    pygame.draw.rect(screen, get_color_code("GREEN"), bar_info)

                else:
                    pygame.draw.rect(screen, get_color_code("DARK_GREEN"), bar_info)

                # outer rectangle for the shape of life bar, never changes
                pygame.draw.rect(screen, get_color_code("BLACK"),
                                 (display_pos_x, display_pos_y, health_bar_length, 6), 2)  # change this too
            # for 1x1 entities
            else:
                health_bar_length = 90
                # bar_display_pos
                display_pos_x = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[
                                    0] + map.grass_tiles.get_width() / 2 + camera.scroll.x + 10
                if type(entity) == Villager:
                    display_pos_y = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[1] + camera.scroll.y - 40
                else:
                    display_pos_y = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[1] + camera.scroll.y

                hp_displayed = (entity.current_health / entity.max_health * health_bar_length)
                # from 1 to 100% of max health, used to know which color we use for the health bar
                unit_pourcentage_of_max_hp = (entity.current_health / entity.max_health) * 100
                bar_info = (display_pos_x, display_pos_y, hp_displayed, 6)  # change this line to make it above the unit

                if 0 < unit_pourcentage_of_max_hp <= 25:
                    pygame.draw.rect(screen, get_color_code("RED"), bar_info)

                elif 25 < unit_pourcentage_of_max_hp <= 40:
                    pygame.draw.rect(screen, get_color_code("ORANGE"), bar_info)

                elif 40 < unit_pourcentage_of_max_hp <= 60:
                    pygame.draw.rect(screen, get_color_code("YELLOW"), bar_info)

                elif 60 < unit_pourcentage_of_max_hp <= 85:
                    pygame.draw.rect(screen, get_color_code("GREEN"), bar_info)

                else:
                    pygame.draw.rect(screen, get_color_code("DARK_GREEN"), bar_info)

                # outer rectangle for the shape of life bar, never changes
                pygame.draw.rect(screen, get_color_code("BLACK"),
                                 (display_pos_x, display_pos_y, health_bar_length, 6), 2)

        elif for_resource:
            health_bar_length = 100
            # bar_display_pos
            display_pos_x = map.grid_to_renderpos(entity["grid"][0], entity["grid"][1])[
                                0] + map.grass_tiles.get_width() / 2 + camera.scroll.x + 10

            display_pos_y = map.grid_to_renderpos(entity["grid"][0], entity["grid"][1])[1] + camera.scroll.y - 20

            hp_displayed = (entity["health"] / entity["max_health"] * health_bar_length)
            # from 1 to 100% of max health, used to know which color we use for the health bar
            resource_pourcentage_of_max_hp = (entity["health"] / entity["max_health"]) * 100
            bar_info = (display_pos_x, display_pos_y, hp_displayed, 6)  # change this line to make it above the unit

            if 0 < resource_pourcentage_of_max_hp <= 25:
                pygame.draw.rect(screen, get_color_code("RED"), bar_info)

            elif 25 < resource_pourcentage_of_max_hp <= 40:
                pygame.draw.rect(screen, get_color_code("ORANGE"), bar_info)

            elif 40 < resource_pourcentage_of_max_hp <= 60:
                pygame.draw.rect(screen, get_color_code("YELLOW"), bar_info)

            elif 60 < resource_pourcentage_of_max_hp <= 85:
                pygame.draw.rect(screen, get_color_code("GREEN"), bar_info)

            else:
                pygame.draw.rect(screen, get_color_code("DARK_GREEN"), bar_info)

            # outer rectangle for the shape of life bar, never changes
            pygame.draw.rect(screen, get_color_code("BLACK"),
                             (display_pos_x, display_pos_y, health_bar_length, 6), 2)  # change this too

    # used for bottom mid menu
    def display_description(self, screen, entity):
        # warning - for now, you cannot render multiples lines
        draw_text(screen, entity.description, 15, (255, 255, 255), (self.width * 0.38 + 85, self.height * 0.92 - 70))

    def display_entity_description(self, screen, map):
        # selection (bottom middle menu)
        w, h = self.bottom_hud_rect.width, self.bottom_hud_rect.height
        img = None
        # as we are scaling it, we make a copy
        if isinstance(self.examined_tile, Building):
            if self.examined_tile.owner.age == 1:
                img = self.first_age_building_sprites[self.examined_tile.__class__.__name__].copy()
            elif self.examined_tile.owner.age == 2:
                img = self.second_age_building_sprites[self.examined_tile.__class__.__name__].copy()
            elif self.examined_tile.owner.age == 3:
                if isinstance(self.examined_tile, Building):
                    img = self.third_age_building_sprites[self.examined_tile.__class__.__name__].copy()
            elif self.examined_tile.owner.age == 4:
                if isinstance(self.examined_tile, Building):
                    img = self.fourth_age_building_sprites[self.examined_tile.__class__.__name__].copy()
        else:
            img = self.examined_tile.sprite.copy()

        if type(self.examined_tile) == Farm:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 85))

        elif type(self.examined_tile) == House:
            img_scaled = scale_image(img, h * 0.50)
            screen.blit(img_scaled, (action_menu.get_width() + 30, self.height - selection_panel.get_height() + 85))

        elif type(self.examined_tile) == TownCenter:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 75))
        # villager
        else:
            img_scaled = scale_image(img, h * 0.28)
            screen.blit(img_scaled, (action_menu.get_width() + 50, self.height - selection_panel.get_height() + 70))

        # for now, we display the picture of the object and its name
        # name
        temp_pos = (action_menu.get_width() + 30, self.height * 0.79 + 20)
        if isinstance(self.examined_tile, Villager):
            temp_pos = temp_pos[0] + 13, temp_pos[1]
        elif isinstance(self.examined_tile, Farm) or isinstance(self.examined_tile, House):
            temp_pos = temp_pos[0] + 16, temp_pos[1]
        draw_text(screen, self.examined_tile.name, 20, (255, 255, 255), temp_pos)
        temp_pos = (action_menu.get_width() + 20 + 120, self.height * 0.79 + 16)
        pygame.draw.line(screen, (155, 155, 155), temp_pos,
                         (temp_pos[0], temp_pos[1] + 145), 2)

        # attack and armor display
        temp_pos = (action_menu.get_width() + 20 + 175, self.height * 0.79 + 107)
        text = "Armor : "
        draw_text(screen, text, 15, (255, 201, 14), temp_pos)
        temp_pos = (action_menu.get_width() + 20 + 178, self.height * 0.79 + 128)
        draw_text(screen, str(self.examined_tile.armor), 12, (255, 255, 255), temp_pos)

        # buildings
        if issubclass(type(self.examined_tile), Building):
            temp_pos = (action_menu.get_width() + 20 + 130, self.height * 0.79 + 110)
            screen.blit(building_armor_icon, temp_pos)
        # units
        else:
            temp_pos = (action_menu.get_width() + 20 + 130, self.height * 0.79 + 45)
            screen.blit(melee_attack_icon, temp_pos)
            temp_pos = (action_menu.get_width() + 20 + 130, self.height * 0.79 + 110)
            screen.blit(armor_icon, temp_pos)

            temp_pos = (action_menu.get_width() + 20 + 175, self.height * 0.79 + 45)
            text = "Damage : "
            draw_text(screen, text, 15, (255, 201, 14), temp_pos)
            temp_pos = (action_menu.get_width() + 20 + 178, self.height * 0.79 + 65)
            draw_text(screen, str(self.examined_tile.attack_dmg) + " - " + str(self.examined_tile.attack_dmg + 1),
                      12, (255, 255, 255), temp_pos)

        # lifebar and numbers
        self.display_life_bar(screen, self.examined_tile, map)

    # display progress bar and icon of trained unit
    def display_progress_bar(self, screen, trained_entity, training_entity, building_built=None):
        # if we get building_arg, it means we must display the construction progress, else it is units training
        if building_built is not None:
            progress_bar_length = 120
            # to get the same health bar size and not have huge ones, we use a ratio
            progress_displayed = ((building_built.now - building_built.resource_manager_cooldown) / (
                    building_built.construction_time * 1000) * progress_bar_length)

            pygame.draw.rect(screen, (255, 201, 14),
                             (action_menu.get_width() + 350, self.height * 0.8 + 34, progress_displayed, 6))
            pygame.draw.rect(screen, (25, 25, 25),
                             (action_menu.get_width() + 350, self.height * 0.8 + 34, progress_bar_length, 6), 2)

            temp_text = "Construction progress..."
            draw_text(screen, temp_text, 13, (255, 255, 255), (action_menu.get_width() + 354, self.height * 0.8 + 17))

            # progress_time in secs
            progress_time = ((building_built.now - building_built.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / building_built.construction_time
            progress_text = str(floor(progress_time_pourcent)) + "%"
            draw_text(screen, progress_text, 12, (255, 255, 255),
                      (action_menu.get_width() + 400, self.height * 0.8 + 42))

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
                             (action_menu.get_width() + 350, self.height * 0.8 + 34, progress_displayed, 6))
            pygame.draw.rect(screen, (55, 55, 55),
                             (action_menu.get_width() + 350, self.height * 0.8 + 34, progress_bar_length, 6), 2)

            temp_text = "Training a " + str(trained_entity.name) + "..."
            draw_text(screen, temp_text, 13, (255, 255, 255), (action_menu.get_width() + 354, self.height * 0.8 + 17))

            # progress %
            health_text = str(int((training_entity.now - training_entity.resource_manager_cooldown) / 1000) * 20) + "%"
            draw_text(screen, health_text, 12, (255, 255, 255), (action_menu.get_width() + 400, self.height * 0.8 + 42))

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
        display_tooltip_for_tech = False
        if entity == "Villager":
            entity = Villager
        elif entity == "Farm":
            entity = Farm
        elif entity == "House":
            entity = House
        elif entity == "TownCenter":
            entity = TownCenter
        else:
            display_tooltip_for_entity = False

        if entity == "Advance to Feudal Age":
            display_tooltip_for_tech = True
            entity = Age_II

        elif entity == "Advance to Castle Age":
            display_tooltip_for_tech = True
            entity = Age_III

        elif entity == "Advance to Imperial Age":
            display_tooltip_for_tech = True
            entity = Age_IV

        # display grey rectangle
        screen.blit(self.tooltip_surface, (0, self.height - action_menu.get_height() - self.tooltip_rect.height))
        pygame.draw.rect(self.tooltip_surface, (255, 201, 14),
                         pygame.Rect(0, 0, self.tooltip_rect.width, self.tooltip_rect.height), 2)

        if display_tooltip_for_entity:
            # construction/training resources costs icons
            screen.blit(wood_cost, (8, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(food_cost, (0 + 60, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(gold_cost, (0 + 115, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(stone_cost, (0 + 170, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(population_cost,
                        (0 + 225, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))

            # order text such as "train a villager" or "build xxx"
            tooltip_text = entity.construction_tooltip + " (" + str(entity.construction_time) + "s)"
            draw_text(screen, tooltip_text, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0],
                       self.height - action_menu.get_height() - self.tooltip_rect.height + 5))

            # cost values. Displayed in red if not enough resources, else in gold
            display_color = "WHITE"
            temp_pos = (30, self.height - action_menu.get_height() - self.tooltip_rect.height + 35)
            # resources
            for resource_type in range(0, 4):
                if entity.construction_cost[resource_type] > playerOne.resources[resource_type]:
                    display_color = "RED"
                else:
                    display_color = "GOLD"
                draw_text(screen, str(entity.construction_cost[resource_type]), 12, display_color, temp_pos)
                temp_pos = temp_pos[0] + 55, temp_pos[1]
            # pop cost
            if playerOne.current_population + entity.population_produced > playerOne.max_population:
                display_color = "RED"
            else:
                display_color = "GOLD"
            draw_text(screen, str(entity.population_produced), 12, display_color, temp_pos)

            # description
            draw_text(screen, entity.description, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

            # grey line
            temp_pos = (7, self.height - action_menu.get_height() - self.tooltip_rect.height + 60)
            pygame.draw.line(screen, (192, 192, 192), temp_pos,
                             (temp_pos[0] + self.tooltip_rect.width - 20, temp_pos[1]))

        elif display_tooltip_for_tech:
            # construction/training resources costs icons
            screen.blit(wood_cost, (8, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(food_cost, (0 + 60, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(gold_cost,
                        (0 + 115, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))
            screen.blit(stone_cost,
                        (0 + 170, self.height - action_menu.get_height() - self.tooltip_rect.height + 30))

            # order text such as "train a villager" or "build xxx"
            tooltip_text = entity.name + " (" + str(entity.research_time) + "s )"
            draw_text(screen, tooltip_text, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0] + 5,
                       self.height - action_menu.get_height() - self.tooltip_rect.height + 5))

            # cost values. Displayed in red if not enough resources, else in gold
            display_color = "WHITE"
            temp_pos = (30, self.height - action_menu.get_height() - self.tooltip_rect.height + 35)
            # resources
            for resource_type in range(0, 4):
                if entity.construction_costs[resource_type] > playerOne.resources[resource_type]:
                    display_color = "RED"
                else:
                    display_color = "GOLD"
                draw_text(screen, str(entity.construction_costs[resource_type]), 12, display_color, temp_pos)
                temp_pos = temp_pos[0] + 55, temp_pos[1]

            # description
            draw_text(screen, entity.description, 14, (255, 255, 255),
                      (self.tooltip_rect.topleft[0], temp_pos[1] + 30))

            # grey line
            temp_pos = (7, self.height - action_menu.get_height() - self.tooltip_rect.height + 60)
            pygame.draw.line(screen, (192, 192, 192), temp_pos,
                             (temp_pos[0] + self.tooltip_rect.width - 20, temp_pos[1]))

        # not tooltip for building/unit but for order
        else:
            # text
            tooltip_text = entity["tooltip"]
            draw_text(screen, tooltip_text, 14, (255, 0, 0),
                      (self.tooltip_rect.topleft[0],
                       self.height - action_menu.get_height() - self.tooltip_rect.height + 5))
            # grey line
            temp_pos = (7, self.height - action_menu.get_height() - self.tooltip_rect.height + 60)
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

    def load_first_age_building_images(self):
        town_center = pygame.image.load(
            "Resources/assets/Models/Buildings/Town_Center/town_center_x1.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/house_1.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png").convert_alpha()

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm
        }
        return images

    def load_second_age_building_images(self):
        town_center = pygame.image.load(
            "Resources/assets/Models/Buildings/Town_Center/town_center_x2.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/house_2.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png").convert_alpha()

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm
        }
        return images

    def load_third_age_building_images(self):
        town_center = pygame.image.load(
            "Resources/assets/Models/Buildings/Town_Center/town_center_x3.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/house_3.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png").convert_alpha()

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm
        }
        return images

    def load_fourth_age_building_images(self):
        town_center = pygame.image.load(
            "Resources/assets/Models/Buildings/Town_Center/town_center_x4.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/house_4.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png").convert_alpha()

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm
        }
        return images

    def load_resources_images(self):

        rock_1 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/1.png")).convert_alpha()
        rock_2 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/2.png")).convert_alpha()
        rock_3 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/3.png")).convert_alpha()
        rock_4 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/4.png")).convert_alpha()
        rock_5 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/5.png")).convert_alpha()
        rock_6 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/6.png")).convert_alpha()
        rock_7 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/7.png")).convert_alpha()

        rock_sprites = {"1": rock_1, "2": rock_2, "3": rock_3, "4": rock_4, "5": rock_5, "6": rock_6, "7": rock_7}

        gold_1 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/1.png")).convert_alpha()
        gold_2 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/2.png")).convert_alpha()
        gold_3 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/3.png")).convert_alpha()
        gold_4 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/4.png")).convert_alpha()
        gold_5 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/5.png")).convert_alpha()
        gold_6 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/6.png")).convert_alpha()
        gold_7 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/7.png")).convert_alpha()

        gold_sprites = {"1": gold_1, "2": gold_2, "3": gold_3, "4": gold_4, "5": gold_5, "6": gold_6, "7": gold_7}

        berry_bush_1 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Berrybush/1.png")).convert_alpha()
        berry_bush_2 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Berrybush/2.png")).convert_alpha()
        berry_bush_3 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Berrybush/3.png")).convert_alpha()

        berry_bush_sprites = {"1": berry_bush_1, "2": berry_bush_2, "3": berry_bush_3}

        tree_1 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Trees/1.png")).convert_alpha()
        tree_2 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Trees/2.png")).convert_alpha()
        tree_3 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Trees/3.png")).convert_alpha()
        tree_4 = pygame.image.load(os.path.join("Resources/assets/Models/Map/Trees/4.png")).convert_alpha()

        tree_sprites = {"1": tree_1, "2": tree_2, "3": tree_3, "4": tree_4}

        resources_sprites = {"rock": rock_sprites, "gold": gold_sprites, "berrybush": berry_bush_sprites,
                             "tree": tree_sprites}

        return resources_sprites

    def create_all_death_animations(self):
        #HOUSE
        house_death_animation = Animation(300, 300, sprites=load_images_better(
            "resources/assets/Models/Buildings/House/House_death_animation"))
        house_death_animation_group = pygame.sprite.Group()
        house_death_animation_group.add(house_death_animation)
        house = {"animation": house_death_animation,
                 "group": house_death_animation_group
                 }
        #TOWN CENTER
        town_center_1_death_animation = Animation(300, 300, sprites=load_images_better(
            "resources/assets/Models/Buildings/Town_Center/town_center_1_death_animation"))
        town_center_1_death_animation_group = pygame.sprite.Group()
        town_center_1_death_animation_group.add(town_center_1_death_animation)

        town_center_1 = {"animation": town_center_1_death_animation,
                         "group": town_center_1_death_animation_group
                         }
        #VILLAGER - 8 different deaths animation, varies with angle
        villager_death_sprites = {}
        villager_death_animation = {}
        villager_death_animation_group = {}
        villager_death ={}
        villager_death["animation"] = {}
        villager_death["group"] = {}

        for folder in range(0, 8):
            villager_death_sprites[str(folder*45)] = load_images_better("resources/assets/Models/Units/Villager/death/" + str(int(folder*45)))
            villager_death_animation[str(folder*45)] = Animation(sprites=villager_death_sprites[str(str(folder*45))])

            villager_death_animation_group[str(int(folder*45))] = pygame.sprite.Group()
            villager_death_animation_group[str(int(folder*45))].add(villager_death_animation[str(int(folder*45))])

            villager_death["animation"][str(int(folder*45))] = villager_death_animation[str(int(folder*45))]
            villager_death["group"] = villager_death_animation_group

        dic = {"House": house,
               "Town Center 1": town_center_1,
               "Villager": villager_death}
        return dic

    def create_all_attack_animations(self):

        anim_speed = 0.65
        villager_attack_animation_0 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/0"), animation_speed=anim_speed)
        villager_attack_animation_1 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/45"), animation_speed=anim_speed)
        villager_attack_animation_2 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/90"), animation_speed=anim_speed)
        villager_attack_animation_3 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/135"), animation_speed=anim_speed)
        villager_attack_animation_4 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/180"), animation_speed=anim_speed)
        villager_attack_animation_5 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/225"), animation_speed=anim_speed)
        villager_attack_animation_6 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/270"), animation_speed=anim_speed)
        villager_attack_animation_7 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/attack/315"), animation_speed=anim_speed)

        villager_attack_animation_0_group = pygame.sprite.Group()
        villager_attack_animation_0_group.add(villager_attack_animation_0)
        attack_animation_0 = {"animation": villager_attack_animation_0,
                 "group": villager_attack_animation_0_group
                 }
        villager_attack_animation_1_group = pygame.sprite.Group()
        villager_attack_animation_1_group.add(villager_attack_animation_1)
        attack_animation_1 = {"animation": villager_attack_animation_1,
                              "group": villager_attack_animation_1_group
                              }
        villager_attack_animation_2_group = pygame.sprite.Group()
        villager_attack_animation_2_group.add(villager_attack_animation_2)
        attack_animation_2 = {"animation": villager_attack_animation_2,
                              "group": villager_attack_animation_2_group
                              }
        villager_attack_animation_3_group = pygame.sprite.Group()
        villager_attack_animation_3_group.add(villager_attack_animation_3)
        attack_animation_3 = {"animation": villager_attack_animation_3,
                              "group": villager_attack_animation_3_group
                              }
        villager_attack_animation_4_group = pygame.sprite.Group()
        villager_attack_animation_4_group.add(villager_attack_animation_4)
        attack_animation_4 = {"animation": villager_attack_animation_4,
                              "group": villager_attack_animation_4_group
                              }
        villager_attack_animation_5_group = pygame.sprite.Group()
        villager_attack_animation_5_group.add(villager_attack_animation_5)
        attack_animation_5 = {"animation": villager_attack_animation_5,
                              "group": villager_attack_animation_5_group
                              }
        villager_attack_animation_6_group = pygame.sprite.Group()
        villager_attack_animation_6_group.add(villager_attack_animation_6)
        attack_animation_6 = {"animation": villager_attack_animation_6,
                              "group": villager_attack_animation_6_group
                              }
        villager_attack_animation_7_group = pygame.sprite.Group()
        villager_attack_animation_7_group.add(villager_attack_animation_7)
        attack_animation_7 = {"animation": villager_attack_animation_7,
                              "group": villager_attack_animation_7_group
                              }

        dic = {"0": attack_animation_0,
               "45": attack_animation_1,
               "90": attack_animation_2,
               "135": attack_animation_3,
               "180": attack_animation_4,
               "225": attack_animation_5,
               "270": attack_animation_6,
               "315": attack_animation_7,
}

        return dic

    def create_all_idle_animations(self):

        anim_speed = 0.15
        villager_idle_animation_0 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/0"), animation_speed=anim_speed)
        villager_idle_animation_1 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/45"), animation_speed=anim_speed)
        villager_idle_animation_2 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/90"), animation_speed=anim_speed)
        villager_idle_animation_3 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/135"), animation_speed=anim_speed)
        villager_idle_animation_4 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/180"), animation_speed=anim_speed)
        villager_idle_animation_5 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/225"), animation_speed=anim_speed)
        villager_idle_animation_6 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/270"), animation_speed=anim_speed)
        villager_idle_animation_7 = Animation(300, 300, sprites=load_images_better("Resources/assets/Models/Units/Villager/Idle/315"), animation_speed=anim_speed)

        villager_idle_animation_0_group = pygame.sprite.Group()
        villager_idle_animation_0_group.add(villager_idle_animation_0)
        idle_animation_0 = {"animation": villager_idle_animation_0,
                 "group": villager_idle_animation_0_group
                 }
        villager_idle_animation_1_group = pygame.sprite.Group()
        villager_idle_animation_1_group.add(villager_idle_animation_1)
        idle_animation_1 = {"animation": villager_idle_animation_1,
                              "group": villager_idle_animation_1_group
                              }
        villager_idle_animation_2_group = pygame.sprite.Group()
        villager_idle_animation_2_group.add(villager_idle_animation_2)
        idle_animation_2 = {"animation": villager_idle_animation_2,
                              "group": villager_idle_animation_2_group
                              }
        villager_idle_animation_3_group = pygame.sprite.Group()
        villager_idle_animation_3_group.add(villager_idle_animation_3)
        idle_animation_3 = {"animation": villager_idle_animation_3,
                              "group": villager_idle_animation_3_group
                              }
        villager_idle_animation_4_group = pygame.sprite.Group()
        villager_idle_animation_4_group.add(villager_idle_animation_4)
        idle_animation_4 = {"animation": villager_idle_animation_4,
                              "group": villager_idle_animation_4_group
                              }
        villager_idle_animation_5_group = pygame.sprite.Group()
        villager_idle_animation_5_group.add(villager_idle_animation_5)
        idle_animation_5 = {"animation": villager_idle_animation_5,
                              "group": villager_idle_animation_5_group
                              }
        villager_idle_animation_6_group = pygame.sprite.Group()
        villager_idle_animation_6_group.add(villager_idle_animation_6)
        idle_animation_6 = {"animation": villager_idle_animation_6,
                              "group": villager_idle_animation_6_group
                              }
        villager_idle_animation_7_group = pygame.sprite.Group()
        villager_idle_animation_7_group.add(villager_idle_animation_7)
        idle_animation_7 = {"animation": villager_idle_animation_7,
                              "group": villager_idle_animation_7_group
                              }

        dic = {"0": idle_animation_0,
               "45": idle_animation_1,
               "90": idle_animation_2,
               "135": idle_animation_3,
               "180": idle_animation_4,
               "225": idle_animation_5,
               "270": idle_animation_6,
               "315": idle_animation_7,
}

        return dic

print(
    #work in progress, not finished
   """ def create_all_walking_animations(self):
        anim_speed = 0.15
        villager_walking_animation_1 = Animation(300, 300, sprites=load_images_better(
            "Resources/assets/Models/Units/Villager/Idle/45"), animation_speed=anim_speed)
       
        villager_walking_animation_3 = Animation(300, 300, sprites=load_images_better(
            "Resources/assets/Models/Units/Villager/Idle/135"), animation_speed=anim_speed)

        villager_walking_animation_5 = Animation(300, 300, sprites=load_images_better(
            "Resources/assets/Models/Units/Villager/Idle/225"), animation_speed=anim_speed)

        villager_walking_animation_7 = Animation(300, 300, sprites=load_images_better(
            "Resources/assets/Models/Units/Villager/Idle/315"), animation_speed=anim_speed)

        villager_walking_animation_1_group = pygame.sprite.Group()
        villager_walking_animation_1_group.add(villager_idle_animation_1)
        walking_animation_1 = {"animation": villager_idle_animation_1,
                            "group": villager_idle_animation_1_group
                            }
 
        villager_idle_animation_3_group = pygame.sprite.Group()
        villager_idle_animation_3_group.add(villager_idle_animation_3)
        walking_animation_3 = {"animation": villager_idle_animation_3,
                            "group": villager_idle_animation_3_group
                            }

        villager_idle_animation_5_group = pygame.sprite.Group()
        villager_idle_animation_5_group.add(villager_idle_animation_5)
        walking_animation_5 = {"animation": villager_idle_animation_5,
                            "group": villager_idle_animation_5_group
                            }

        villager_idle_animation_7_group = pygame.sprite.Group()
        villager_idle_animation_7_group.add(villager_walking_animation_7)
        walking_animation_7 = {"animation": villager_walking_animation_7,
                            "group": villager_walking_animation_7_group
                            }

        dic = {
               "45": walking_animation_1,
               "135": walking_animation_3,
               "225": walking_animation_5,
               "315": walking_animation_7,
               }

        return dic
""") if False else...