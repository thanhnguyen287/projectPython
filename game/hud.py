from settings import *
import pygame
from math import floor
from .utils import draw_text, scale_image, get_color_code, TEST_MODE
from player import playerOne, playerTwo, player_list, MAIN_PLAYER
from units import Villager, TownCenter, House, Farm, Building, Barracks
# from buildings import TownCenter, House, Farm, Building
from .ActionMenu import *
from tech import Age_II, Age_III, Age_IV
from .animation import load_images_better, Animation, BuildingAnimation


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

        self.images = self.load_buildings_icons()
        self.town_hall_menu = self.create_train_menu_town_hall()
        self.villager_menu = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None

        self.bottom_left_menu = None
        self.is_cancel_button_present = False

        # buildings sprites

        self.first_age_building_sprites = self.load_first_age_building_images()

        # resources sprites
        self.resources_sprites = self.load_resources_images()
        self.resources_sprites_offsets = [(-15, -5),(-20,-5),(-20,-5),(-28,-15),(-70, -115),(-60,-45),(-65,-40),(-100, -145),(-70, -110), (-40,-70)]
        self.house_death_animation = None
        self.house_death_animation_group = None
        self.temp_bool = True

        # animations. contains stuff like : self.death_animations["house"]["animation"]
        self.death_animations = self.create_all_death_animations()
        self.villager_sprites = self.load_villager_idle_fixed_sprites()
        self.clubman_sprites = self.load_clubman_idle_fixed_sprites()
        self.villager_attack_animations = self.create_all_attack_animations()

    #        self.villager_walk_animations = self.create_all_walk_animations()
        self.all_buildings_death_animations = self.create_all_building_death_animations()
        self.mining_sprites_villager = self.load_mining_sprites_villager()

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
            if image_name != "Villager":
                pos = render_pos.copy()
                rect = image.get_rect(topleft=pos)

                tiles.append(
                    {
                        "name": image_name,
                        "icon": image,
                        "image": self.images[image_name],
                        "rect": rect,
                        "affordable": True
                    }
                )

                render_pos[0] += image.get_width() + 5  # modifier le 20 pour que ça marche pour tout ecran

        return tiles

    def update(self, screen, the_player=MAIN_PLAYER):

        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        mouse_action = pygame.mouse.get_pressed()
        # deselection by right-clicking
        if mouse_action[2]:
            self.selected_tile = None

        # building action_menu
        if self.bottom_left_menu is not None:
            for button in self.bottom_left_menu:
                if button["name"] != "STOP":
                    if the_player.can_afford(button["name"]):
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

    def draw(self, screen, map, camera, the_player=MAIN_PLAYER):
        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        # entity is string corresponding to class unit/building name
        for entity in self.death_animations:
                if self.death_animations[entity]["animation"].to_be_played:
                    self.death_animations[entity]["group"].draw(screen)
                    self.death_animations[entity]["animation"].update()

        for player in player_list:
            for unit in player.unit_list:
                if unit.attack_animation.to_be_played:
                    unit.attack_animation_group.draw(screen)
                    unit.attack_animation.update()

        # resources bar
        the_player.update_resources_bar(screen)
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
                        if tile["name"] != "STOP" and not the_player.can_afford(tile["name"]):
                            icon.set_alpha(100)
                        screen.blit(icon, tile["rect"].topleft)
                        if tile["rect"].collidepoint(mouse_pos) and tile["name"] != "STOP":
                            self.display_construction_tooltip(screen, tile["name"])
                        if tile["rect"].collidepoint(mouse_pos) and (
                                tile["name"] == "STOP" and tile["name"] != "Advance to Feudal Age" and tile[
                            "name"] != "Advance to Castle Age" and tile["name"] != "Advance to Imperial Age"):
                            self.display_construction_tooltip(screen, tile)

    def load_buildings_icons(self):

        town_center = pygame.image.load("resources/assets/icons/town_center_icon_hd.png").convert_alpha()
        house = pygame.image.load("Resources/assets/icons/houseDE.png").convert_alpha()
        farm = pygame.image.load("resources/assets/icons/farmDE.png").convert_alpha()
        barracks = pygame.image.load("resources/assets/icons/barracks_icon.png").convert_alpha()
        # villager = pygame.image.load("resources/assets/icons/villagerde.bmp").convert_alpha()

        villager = None
        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm,
            "Barracks": barracks,
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
            if type(entity) == TownCenter or type(entity) == Barracks:
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
            if self.examined_tile.__class__.__name__ != "Farm":
                img = self.first_age_building_sprites[self.examined_tile.__class__.__name__][self.examined_tile.owner.color][self.examined_tile.owner.age - 1].copy()
            else:
                img = self.first_age_building_sprites[self.examined_tile.__class__.__name__][
                    self.examined_tile.owner.color].copy()
        # if unit, display unit with 270 degree (index : 4)
        else:
            img = self.villager_sprites[self.examined_tile.owner.color][4].copy()

        if type(self.examined_tile) == Farm:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 85))

        elif type(self.examined_tile) == House:
            img_scaled = scale_image(img, h * 0.50)
            screen.blit(img_scaled, (action_menu.get_width() + 30, self.height - selection_panel.get_height() + 85))

        elif type(self.examined_tile) == TownCenter:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 75))

        elif type(self.examined_tile) == Barracks:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 75))

        # villager
        else:
            img_scaled = scale_image(img, h * 0.20)
            screen.blit(img_scaled, (action_menu.get_width() + 50, self.height - selection_panel.get_height() + 70))

        # for now, we display the picture of the object and its name
        # name
        temp_pos = (action_menu.get_width() + 30, self.height * 0.79 + 20)
        if isinstance(self.examined_tile, Villager):
            villager = self.examined_tile
            temp_pos = temp_pos[0] + 13, temp_pos[1]
            # resources carried display if he has gathered smth
            if villager.gathered_ressource_stack > 0:
                if villager.stack_type == "tree":
                    screen.blit(scale_image(BIG_wood_icon,w=40), (action_menu.get_width() + selection_panel.get_width() -200, self.height * 0.79 + 50))
                    #self.gathered_ressource_stack = 0

                elif villager.stack_type == "rock":
                    screen.blit(scale_image(BIG_stone_icon,w=40), (action_menu.get_width() + selection_panel.get_width() -200, self.height * 0.79 + 50))

                elif villager.stack_type == "berrybush":
                    screen.blit(scale_image(BIG_food_icon,w=40), (action_menu.get_width() + selection_panel.get_width() -200, self.height * 0.79 + 50))

                elif villager.stack_type == "gold":
                    screen.blit(scale_image(BIG_gold_icon,w=40), (action_menu.get_width() + selection_panel.get_width() -200, self.height * 0.79 + 50))
                draw_text(screen, "Carried resources : ", 15, get_color_code("GOLD"), (action_menu.get_width() + selection_panel.get_width() -150,  self.height - selection_panel.get_height() + 65))

                draw_text(screen, str(villager.gathered_ressource_stack), 14, (255, 255, 255), (action_menu.get_width() + selection_panel.get_width() -120, self.height - selection_panel.get_height() + 90))

        elif isinstance(self.examined_tile, Farm) or isinstance(self.examined_tile, House) or \
                isinstance(self.examined_tile, Barracks):
            temp_pos = temp_pos[0] + 16, temp_pos[1]
        draw_text(screen, self.examined_tile.name, 20, (255, 255, 255), temp_pos)
        temp_pos = (action_menu.get_width() + 20 + 120, self.height * 0.79 + 16)
        pygame.draw.line(screen, (155, 155, 155), temp_pos,
                         (temp_pos[0], temp_pos[1] + 145), 2)

        # attack and armor display
        temp_pos = (action_menu.get_width() + 20 + 175, self.height * 0.79 + 107)
        text = "Armor : "
        draw_text(screen, text, 15, get_color_code("GOLD"), temp_pos)
        temp_pos = (action_menu.get_width() + 20 + 178, self.height * 0.79 + 128)
        draw_text(screen, str(self.examined_tile.armor), 12, (255, 255, 255), temp_pos)

        # buildings
        if issubclass(type(self.examined_tile), Building):
            temp_pos = (action_menu.get_width() + 20 + 130, self.height * 0.79 + 100)
            screen.blit(building_armor_icon, temp_pos)
        # units
        else:
            temp_pos = (action_menu.get_width() + 20 + 130, self.height * 0.79 + 50)
            screen.blit(melee_attack_icon, temp_pos)
            temp_pos = (action_menu.get_width() + 20 + 130, self.height * 0.79 + 105)
            screen.blit(armor_icon, temp_pos)

            temp_pos = (action_menu.get_width() + 20 + 175, self.height - selection_panel.get_height() + 66)
            text = "Damage : "
            draw_text(screen, text, 15, (255, 201, 14), temp_pos)
            temp_pos = (action_menu.get_width() + 20 + 178, self.height - selection_panel.get_height() + 86)
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
    def display_construction_tooltip(self, screen, entity, the_player=MAIN_PLAYER):
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
        elif entity == "Barracks":
            entity = Barracks
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
                if entity.construction_cost[resource_type] > the_player.resources[resource_type]:
                    display_color = "RED"
                else:
                    display_color = "GOLD"
                draw_text(screen, str(entity.construction_cost[resource_type]), 12, display_color, temp_pos)
                temp_pos = temp_pos[0] + 55, temp_pos[1]
            # pop cost
            if the_player.current_population + entity.population_produced > the_player.max_population:
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
                if entity.construction_costs[resource_type] > the_player.resources[resource_type]:
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

    # returns dic containing images of First age Buildings; Need to specify the player's color. Uses like that : images["House"]["RED"]
    def load_first_age_building_images(self):
        town_center = {"BLUE": load_images_better("Resources/assets/Models/Buildings/Town_Center/BLUE/"),
                       "RED": load_images_better("Resources/assets/Models/Buildings/Town_Center/RED/"),
                       "GREEN": load_images_better("Resources/assets/Models/Buildings/Town_Center/GREEN/"),
                       "YELLOW": load_images_better("Resources/assets/Models/Buildings/Town_Center/YELLOW/")}

        # pygame.image.load("Resources/assets/Models/Buildings/Town_Center/town_center_x1.png").convert_alpha()
        house = {"BLUE": load_images_better("Resources/assets/Models/Buildings/House/BLUE/"),
                 "RED": load_images_better("Resources/assets/Models/Buildings/House/RED/"),
                 "GREEN": load_images_better("Resources/assets/Models/Buildings/House/GREEN/"),
                 "YELLOW": load_images_better("Resources/assets/Models/Buildings/House/YELLOW/")}

        farm = {"BLUE": pygame.image.load("Resources/assets/Models/Buildings/Farm/farmBLUE.png").convert_alpha(),
                "RED": pygame.image.load("Resources/assets/Models/Buildings/Farm/farmRED.png").convert_alpha(),
                "GREEN": pygame.image.load("Resources/assets/Models/Buildings/Farm/farmGREEN.png").convert_alpha(),
                "YELLOW": pygame.image.load("Resources/assets/Models/Buildings/Farm/farmYELLOW.png").convert_alpha()}

        barracks = {"BLUE": load_images_better("Resources/assets/Models/Buildings/Barracks/BLUE/"),
                 "RED": load_images_better("Resources/assets/Models/Buildings/Barracks/RED/"),
                 "GREEN": load_images_better("Resources/assets/Models/Buildings/Barracks/GREEN/"),
                 "YELLOW": load_images_better("Resources/assets/Models/Buildings/Barracks/YELLOW/")}

        images = {
            "TownCenter": town_center,
            "House": house,
            "Barracks": barracks,
            "Farm": farm
        }

        return images

    def load_resources_images(self):

        rock_sprites = load_images_better("Resources/assets/Models/Map/Stones")
        gold_sprites = load_images_better("Resources/assets/Models/Map/Gold")
        berry_bush_sprites = load_images_better("Resources/assets/Models/Map/Berrybush")
        tree_sprites = load_images_better("Resources/assets/Models/Map/Trees")
        grass_sprites = load_images_better("resources/assets/Models/Map/grass")

        resources_sprites = {"rock": rock_sprites, "gold": gold_sprites, "berrybush": berry_bush_sprites,
                             "tree": tree_sprites, "grass": grass_sprites}

        return resources_sprites

    def create_all_death_animations(self):

        # HOUSE - RED, BLUE, GREEN and YELLOW available, need to specify the current age too.
        house_death_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 4 ages
        for folder in range(1, 5):
            house_death_sprites_list["BLUE"][str(folder)] = load_images_better("resources/assets/Models/Buildings/House/death/BLUE/" + str(folder))
            house_death_sprites_list["RED"][str(folder)] = load_images_better("resources/assets/Models/Buildings/House/death/RED/" + str(folder))
            house_death_sprites_list["GREEN"][str(folder)] = load_images_better("resources/assets/Models/Buildings/House/death/GREEN/" + str(folder))
            house_death_sprites_list["YELLOW"][str(folder)] = load_images_better("resources/assets/Models/Buildings/House/death/YELLOW/" + str(folder))

        house_death_animation = BuildingAnimation(sprites=house_death_sprites_list)
        house_death_animation_group = pygame.sprite.Group()
        house_death_animation_group.add(house_death_animation)

        house = {"animation": house_death_animation,
                 "group": house_death_animation_group
                 }


        # TOWN CENTER
        town_center_death_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 4 ages
        for folder in range(1, 5):
            town_center_death_sprites_list["BLUE"][str(folder)] = load_images_better("resources/assets/Models/Buildings/Town_Center/death/BLUE/" + str(folder))
            town_center_death_sprites_list["RED"][str(folder)] = load_images_better("resources/assets/Models/Buildings/Town_Center/death/RED/" + str(folder))
            town_center_death_sprites_list["GREEN"][str(folder)] = load_images_better("resources/assets/Models/Buildings/Town_Center/death/GREEN/" + str(folder))
            town_center_death_sprites_list["YELLOW"][str(folder)] = load_images_better("resources/assets/Models/Buildings/Town_Center/death/YELLOW/" + str(folder))

        town_center_death_animation = BuildingAnimation(sprites=town_center_death_sprites_list)
        town_center_death_animation_group = pygame.sprite.Group()
        town_center_death_animation_group.add(town_center_death_animation)

        town_center = {"animation": town_center_death_animation,
                       "group": town_center_death_animation_group
                       }

        # VILLAGER - 8 different deaths animation, varies with angle, not with age. Available for RED, BLUE, GREEN and YELLOW players
        villager_death_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 8 angles. folder * 45 because angles are 0, 45, 90, 135, etc... up to 315 for max.
        for folder in range(0, 8):
            villager_death_sprites_list["BLUE"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/BLUE/death/" + str(int(folder * 45)))
            villager_death_sprites_list["RED"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/RED/death/" + str(int(folder * 45)))
            villager_death_sprites_list["GREEN"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/GREEN/death/" + str(int(folder * 45)))
            villager_death_sprites_list["YELLOW"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/YELLOW/death/" + str(int(folder * 45)))

        villager_death_animation = Animation(sprites=villager_death_sprites_list)
        villager_death_animation_group = pygame.sprite.Group()
        villager_death_animation_group.add(villager_death_animation)
        villager = {"animation": villager_death_animation,
                    "group": villager_death_animation_group
                       }

        # CLUBMAN - 8 different deaths animation, varies with angle, not with age. Available for RED, BLUE, GREEN and YELLOW players
        clubman_death_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 8 angles. folder * 45 because angles are 0, 45, 90, 135, etc... up to 315 for max.
        for folder in range(0, 8):
            clubman_death_sprites_list["BLUE"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/BLUE/death/" + str(int(folder * 45)))
            clubman_death_sprites_list["RED"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/RED/death/" + str(int(folder * 45)))
            clubman_death_sprites_list["GREEN"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/GREEN/death/" + str(int(folder * 45)))
            clubman_death_sprites_list["YELLOW"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/YELLOW/death/" + str(int(folder * 45)))

        clubman_death_animation = Animation(sprites=villager_death_sprites_list)
        clubman_death_animation_group = pygame.sprite.Group()
        clubman_death_animation_group.add(clubman_death_animation)
        clubman = {"animation": clubman_death_animation,
                    "group": clubman_death_animation_group
                    }


        dic = {"House": house,
               "Town Center": town_center,
               "Villager": villager}
        return dic

    def create_all_attack_animations(self):
        anim_speed = 0.50

        # VILLAGER - 8 different attacks animation, varies with angle, not with age. Available for RED, BLUE, GREEN and YELLOW players
        villager_attack_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 8 angles. folder * 45 because angles are 0, 45, 90, 135, etc... up to 315 for max.
        for folder in range(0, 8):
            villager_attack_sprites_list["BLUE"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/BLUE/attack/" + str(int(folder * 45)))
            villager_attack_sprites_list["RED"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/RED/attack/" + str(int(folder * 45)))
            villager_attack_sprites_list["GREEN"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/GREEN/attack/" + str(int(folder * 45)))
            villager_attack_sprites_list["YELLOW"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/YELLOW/attack/" + str(int(folder * 45)))

        villager_attack_animation = Animation(sprites=villager_attack_sprites_list, animation_speed=anim_speed)
        villager_attack_animation_group = pygame.sprite.Group()
        villager_attack_animation_group.add(villager_attack_animation)
        villager = {"animation": villager_attack_animation,
                    "group": villager_attack_animation_group,
                    "sprites": villager_attack_sprites_list
                    }
        # Clubman - 8 different attacks animation, varies with angle, not with age. Available for RED, BLUE, GREEN and YELLOW players
        clubman_attack_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 8 angles. folder * 45 because angles are 0, 45, 90, 135, etc... up to 315 for max.
        for folder in range(0, 8):
            clubman_attack_sprites_list["BLUE"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/BLUE/attack/" + str(int(folder * 45)))
            clubman_attack_sprites_list["RED"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/RED/attack/" + str(int(folder * 45)))
            clubman_attack_sprites_list["GREEN"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/GREEN/attack/" + str(int(folder * 45)))
            clubman_attack_sprites_list["YELLOW"][str(int(folder * 45))] = load_images_better(
                "resources/assets/Models/Units/Clubman/YELLOW/attack/" + str(int(folder * 45)))

        clubman_attack_animation = Animation(sprites=clubman_attack_sprites_list, animation_speed=anim_speed)
        clubman_attack_animation_group = pygame.sprite.Group()
        clubman_attack_animation_group.add(clubman_attack_animation)
        clubman = {"animation": clubman_attack_animation,
                    "group": clubman_attack_animation_group,
                    "sprites": clubman_attack_sprites_list
                    }

        dic = {"Villager": villager, "Clubman": clubman}
        return dic

    def load_mining_sprites_villager(self):

        # VILLAGER - 8 different attacks animation, varies with angle, not with age. Available for RED, BLUE, GREEN and YELLOW players
        villager_mining_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 8 angles. folder * 45 because angles are 0, 45, 90, 135, etc... up to 315 for max.
        for folder in range(0, 8):
            villager_mining_sprites_list["BLUE"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/BLUE/mine/" + str(int(folder * 45)))
            villager_mining_sprites_list["RED"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/RED/mine/" + str(int(folder * 45)))
            villager_mining_sprites_list["GREEN"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/GREEN/mine/" + str(int(folder * 45)))
            villager_mining_sprites_list["YELLOW"][str(int(folder * 45))] = load_images_better("resources/assets/Models/Units/Villager/YELLOW/mine/" + str(int(folder * 45)))
        return villager_mining_sprites_list


    def load_villager_idle_fixed_sprites(self):
        dic = {"BLUE": load_images_better("Resources/assets/Models/Units/Villager/BLUE/Idle/static"),
               "RED": load_images_better("Resources/assets/Models/Units/Villager/RED/Idle/static"),
               "GREEN": load_images_better("Resources/assets/Models/Units/Villager/GREEN/Idle/static"),
               "YELLOW": load_images_better("Resources/assets/Models/Units/Villager/YELLOW/Idle/static")
               }
        return dic

    def load_clubman_idle_fixed_sprites(self):
        dic = {"BLUE": load_images_better("Resources/assets/Models/Units/Clubman/BLUE/Idle/static"),
               "RED": load_images_better("Resources/assets/Models/Units/Clubman/RED/Idle/static"),
               "GREEN": load_images_better("Resources/assets/Models/Units/Clubman/GREEN/Idle/static"),
               "YELLOW": load_images_better("Resources/assets/Models/Units/Clubman/YELLOW/Idle/static")
               }
        return dic

    # work in progress, not finished
    #def create_all_walking_animations(self):


    def create_all_building_death_animations(self):
        # HOUSE - RED, BLUE, GREEN and YELLOW available, need to specify the current age too.
        house_death_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 4 ages
        for folder in range(1, 5):
            house_death_sprites_list["BLUE"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/House/death/BLUE/" + str(folder))
            house_death_sprites_list["RED"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/House/death/RED/" + str(folder))
            house_death_sprites_list["GREEN"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/House/death/GREEN/" + str(folder))
            house_death_sprites_list["YELLOW"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/House/death/YELLOW/" + str(folder))

        # house_death_animation = BuildingAnimation(sprites=house_death_sprites_list)
        # house_death_animation_group = pygame.sprite.Group()
        # house_death_animation_group.add(house_death_animation)

        # TOWN CENTER
        town_center_death_sprites_list = {"BLUE": {}, "RED": {}, "GREEN": {}, "YELLOW": {}}
        # loop for the 4 ages
        for folder in range(1, 5):
            town_center_death_sprites_list["BLUE"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/Town_Center/death/BLUE/" + str(folder))
            town_center_death_sprites_list["RED"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/Town_Center/death/RED/" + str(folder))
            town_center_death_sprites_list["GREEN"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/Town_Center/death/GREEN/" + str(folder))
            town_center_death_sprites_list["YELLOW"][str(folder)] = load_images_better(
                "resources/assets/Models/Buildings/Town_Center/death/YELLOW/" + str(folder))

        # town_center_death_animation = BuildingAnimation(sprites=town_center_death_sprites_list)
        # town_center_death_animation_group = pygame.sprite.Group()
        # town_center_death_animation_group.add(town_center_death_animation)

        dic = {"House": house_death_sprites_list,
               "Town Center": town_center_death_sprites_list}
        return dic