from settings import *
import pygame
from math import floor
from .utils import draw_text, scale_image, get_color_code, TEST_MODE
from player import playerOne, playerTwo, player_list, MAIN_PLAYER
from units import Villager, TownCenter, House, Farm, Building, Barracks, Clubman, Dragon, Tower, Wall, Market
# from buildings import TownCenter, House, Farm, Building
from .ActionMenu import *
from tech import Age_II, Age_III, Age_IV, horseshoe_tech, arrow_tech, iron_sword_tech, steel_sword_tech, mithril_sword_tech, iron_armor_tech, steel_armor_tech, mithril_armor_tech, improved_masonry_tech, reinforced_masonry_tech, imbued_masonry_tech, food_production_tech
from .animation import load_images_better, Animation, BuildingAnimation


class Hud:

    def __init__(self, width, height, screen):
        self.camera = None
        self.tech_tree_display_flag = False
        self.width = width
        self.height = height
        self.hud_color = (198, 155, 93, 175)
        self.screen = screen
        # self.camera = camera

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


        #tech sprites
        self.tech_sprites = self.load_tech_icons()
        self.tech_sprites_disabled = self.load_tech_icons_disabled()
        self.tech_tree_button_surface = pygame.Surface((tech_tree_icon.get_width(), tech_tree_icon.get_height()), pygame.SRCALPHA)
        self.tech_tree_rect = self.tech_tree_button_surface.get_rect(topleft=(screen.get_size()[0] - tech_tree_icon.get_width() - 5, age_panel.get_height() + 10))

        #action_panel for all units/buildings
        self.images = self.load_buildings_icons()
        self.town_hall_panel = self.create_train_menu_town_hall()
        self.villager_panel = self.create_villager_action_panel()
        self.barracks_panel = self.create_action_menu_barracks()
        self.market_panel = self.create_market_action_panel()

        self.selected_tile = None
        self.examined_tile = None

        self.bottom_left_menu = None
        self.is_cancel_button_present = False

        # buildings sprites
        self.first_age_building_sprites = self.load_first_age_building_images()

        #destination flags
        self.destination_flags_sprites = self.load_destination_flags()

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

        #self.villager_walk_animations = self.create_all_walk_animations()
        self.all_buildings_death_animations = self.create_all_building_death_animations()
        self.mining_sprites_villager = self.load_mining_sprites_villager()
        self.tech_tree_images = self.load_tech_tree()

        #dragon
        self.dragon_sprites = self.load_dragon_sprites()

    #town_hall has 2 buttons in its action panel : train Villager and Advance to Second Age
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
                tiles.append(
                    {
                        "name": image_name,
                        "icon": image,
                        "image": self.images[image_name],
                        "rect": image.get_rect(topleft=pos),
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

    def create_action_menu_barracks(self):
        render_pos = [25, self.height - action_menu.get_height() + 40]
        object_width = 50

        tiles = []
        image_scale = None
        image_name = None
        rect = None

        for image_name, image in self.images.items():
            pos = render_pos.copy()

            if image_name == "Clubman":
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
        return tiles

    def create_market_action_panel(self):
        render_pos = [25, self.height - action_menu.get_height() + 40]
        object_width = 50

        tiles = []
        image_scale = None
        image_name = None
        rect = None

        for image_name, image in self.tech_sprites.items():
            if image_name == "Swords" or image_name == "Armor" or image_name == "Masonry":
                pos = render_pos.copy()
                name = image_name
                if image_name == "Swords":
                    name = "Research Iron Swords"

                elif image_name == "Armor":
                    name = "Research Iron Armors"

                elif image_name == "Masonry":
                    name = "Research Improved Masonry"

                tiles.append(
                    {
                        "name": name,
                        "icon": image,
                        "image": image,
                        "rect": image.get_rect(topleft=render_pos),
                        "affordable": True
                    }
                )
                render_pos[0] += image.get_width() + 5
        return tiles

    def create_villager_action_panel(self):

        render_pos = [0 + 25, self.height * 0.8 + 10]

        tiles = []
        compteur = 0
        for image_name, image in self.images.items():
            if image_name != "Villager" and image_name != "Clubman":
                compteur += 1
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
                # if more than 5 icons, we go to the line below in action panel
                if compteur > 5:
                    #position reseted to line below
                    render_pos = [0 + 25 - image.get_width() - 5, self.height * 0.8 + 65]
                    compteur = 0
                render_pos[0] += image.get_width() + 5



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

                # we remove the advance to x age tech if it has been researched, and add the next one
                if self.examined_tile is not None and isinstance(self.examined_tile, Market):
                    if (button["name"] == "Research Iron Swords" and self.examined_tile.owner.iron_swords_unlocked)\
                            or (button["name"] == "Research Steel Swords" and self.examined_tile.owner.steel_swords_unlocked) \
                            or (button["name"] == "Research Mithril Swords" and self.examined_tile.owner.mithril_swords_unlocked) \
                            or (button["name"] == "Research Iron Armors" and self.examined_tile.owner.iron_armors_unlocked) \
                            or (button["name"] == "Research Steel Armors" and self.examined_tile.owner.steel_armors_unlocked) \
                            or (button["name"] == "Research Mithril Armors" and self.examined_tile.owner.mithril_armors_unlocked) \
                            or (button["name"] == "Research Iron Arrows" and self.examined_tile.owner.iron_arrows_unlocked)\
                            or (button["name"] == "Research Iron Horseshoes" and self.examined_tile.owner.iron_horseshoes_unlocked) \
                            or (button["name"] == "Research Improved Masonry" and self.examined_tile.owner.improved_masonry_unlocked) \
                            or (button["name"] == "Research Reinforced Masonry" and self.examined_tile.owner.reinforced_masonry_unlocked) \
                            or (button["name"] == "Research Imbued Masonry" and self.examined_tile.owner.imbued_masonry_unlocked) \
                            or (button["name"] == "Research Super Cows" and self.examined_tile.owner.super_cows_unlocked):
                        self.bottom_left_menu.remove(button)

                        if button["name"] == "Research Iron Swords":
                        #adding next tech tier
                            self.bottom_left_menu.append(
                            {
                                "name": "Research Steel Swords",
                                "icon": steel_sword_icon,
                                "image": steel_sword_icon,
                                "rect": button["rect"],
                                "affordable": True
                            })
                        elif button["name"] == "Research Steel Swords":
                        #adding next tech tier
                            self.bottom_left_menu.append(
                            {
                                "name": "Research Mithril Swords",
                                "icon": mithril_sword_icon,
                                "image": mithril_sword_icon,
                                "rect": button["rect"],
                                "affordable": True
                            })
                        elif button["name"] == "Research Iron Armors":
                        #adding next tech tier
                            self.bottom_left_menu.append(
                            {
                                "name": "Research Steel Armors",
                                "icon": steel_armor_icon,
                                "image": steel_armor_icon,
                                "rect": button["rect"],
                                "affordable": True
                            })
                        elif button["name"] == "Research Steel Armors":
                        #adding next tech tier
                            self.bottom_left_menu.append(
                            {
                                "name": "Research Mithril Armors",
                                "icon": mithril_armor_icon,
                                "image": mithril_armor_icon,
                                "rect": button["rect"],
                                "affordable": True
                            })
                        elif button["name"] == "Research Improved Masonry":
                        #adding next tech tier
                            self.bottom_left_menu.append(
                            {
                                "name": "Research Reinforced Masonry",
                                "icon": fortified_masonry_icon,
                                "image": fortified_masonry_icon,
                                "rect": button["rect"],
                                "affordable": True
                            })
                        elif button["name"] == "Research Reinforced Masonry":
                        #adding next tech tier
                            self.bottom_left_menu.append(
                            {
                                "name": "Research Imbued Masonry",
                                "icon": imbued_masonry_icon,
                                "image": imbued_masonry_icon,
                                "rect": button["rect"],
                                "affordable": True
                            })


            # to remove the stop action button if it is no longer useful
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

    def draw(self, screen, map, camera, the_player=MAIN_PLAYER):
        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        # entity is string corresponding to class unit/building name
        for entity in self.death_animations:
                if not isinstance(entity, Dragon) and self.death_animations[entity]["animation"].to_be_played:
                    self.death_animations[entity]["group"].draw(screen)
                    self.death_animations[entity]["animation"].update()

        for player in player_list:
            for unit in player.unit_list:
                if not isinstance(unit, Dragon) and unit.attack_animation.to_be_played:
                    unit.attack_animation_group.draw(screen)
                    unit.attack_animation.update()
                if type(unit) == Dragon and unit.idle_animation.to_be_played:
                    unit.idle_animation_group.draw(screen)
                    unit.idle_animation.update()

        # resources bar
        the_player.update_resources_bar(screen)
        # bottom menu

        if self.examined_tile is not None:
            # Draw minimap
            screen.blit(minimap_panel,
                        (self.width - minimap_panel.get_width(), self.height - selection_panel.get_height()))
            map.draw_minimap(screen, self.camera)
            screen.blit(action_menu, (0, self.height - action_menu.get_height()))
            screen.blit(selection_panel, (action_menu.get_width(), self.height - selection_panel.get_height()))

            self.display_entity_description(screen, map)

            entity_class = type(self.examined_tile)
            # if the town center is creating villager, we display the corresponding progression bar
            if (entity_class == TownCenter or entity_class == Barracks) and self.examined_tile.is_working:
                self.display_progress_bar(screen, self.examined_tile.unit_type_currently_trained, self.examined_tile)
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
                        #if tile["rect"].collidepoint(mouse_pos) and (
                         #       tile["name"] == "STOP" and tile["name"] != "Advance to Feudal Age" and tile[
                        #    "name"] != "Advance to Castle Age" and tile["name"] != "Advance to Imperial Age" and tile["name"] != "Research Iron Swords" and tile["name"] != "Research Iron Arrows" and tile["name"] != "Research Iron Horseshoes" and tile["name"] != "Research Super Cows"):
                        elif tile["rect"].collidepoint(mouse_pos) and tile["name"] == "STOP":
                            self.display_construction_tooltip(screen, tile)
        if self.tech_tree_display_flag:
            self.display_tech_tree(screen)


    def load_buildings_icons(self):

        town_center = pygame.image.load("resources/assets/icons/town_center_icon_hd.png").convert_alpha()
        house = pygame.image.load("Resources/assets/icons/houseDE.png").convert_alpha()
        farm = pygame.image.load("resources/assets/icons/farmDE.png").convert_alpha()
        barracks = pygame.image.load("resources/assets/icons/barracks_icon.png").convert_alpha()
        market = pygame.image.load("resources/assets/icons/market_icon.png").convert_alpha()


        tower_1 = pygame.image.load("resources/assets/icons/tower_1_icon.png").convert_alpha()
        #tower_2 = pygame.image.load("resources/assets/icons/tower_2_icon.png").convert_alpha()
        #tower_4 = pygame.image.load("resources/assets/icons/tower_4_icon.png").convert_alpha()

        wall_1 = pygame.image.load("resources/assets/icons/weak_wall_icon.png").convert_alpha()
        #wall_2 = pygame.image.load("resources/assets/icons/med_wall_icon.png").convert_alpha()
        #wall_4 = pygame.image.load("resources/assets/icons/strong_wall_icon.png").convert_alpha()

        villager = pygame.image.load("resources/assets/icons/villagerde.bmp").convert_alpha()
        clubman = pygame.image.load("resources/assets/icons/Clubman_icon.png").convert_alpha()

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm,
            "Barracks": barracks,
            "Market": market,

            "Villager": villager,
            "Clubman": clubman,
            "Tower": tower_1,
            #"Tower_2": tower_2,
            #"Tower_4": tower_4,
            "Wall": wall_1,
            #"Wall_2": wall_2,
            #"Wall_4": wall_4
        }
        return images

    def load_tech_icons(self):
        Advance_age_II = pygame.image.load("resources/assets/icons/tech/advance_2_age.png").convert_alpha()
        Advance_age_III = pygame.image.load("resources/assets/icons/tech/advance_3_age.png").convert_alpha()
        Advance_age_IV = pygame.image.load("resources/assets/icons/tech/advance_4_age.png").convert_alpha()

        iron_swords = iron_sword_icon
        iron_armor = iron_armor_icon
        masonry = improved_masonry_icon
        iron_arrows = pygame.image.load("resources/assets/icons/tech/arrow_tech.png").convert_alpha()
        iron_horse_shoe = pygame.image.load("resources/assets/icons/tech/horse_tech.png").convert_alpha()
        cow = pygame.image.load("resources/assets/icons/tech/cow_tech.png").convert_alpha()
        images = {
            "Advance_age_2": Advance_age_II,
            "Advance_age_3": Advance_age_III,
            "Advance_age_4": Advance_age_IV,
            "Swords": iron_swords,
            "Arrows": iron_arrows,
            "Horseshoe": iron_horse_shoe,
            "Cow": cow,
            "Armor": iron_armor,
            "Masonry": masonry
        }
        return images
    #list of disabled icons. 0,1,2 for masonry, 3,4,5 for swords, 6,7,8 for armor
    def load_tech_icons_disabled(self):
        return load_images_better("resources/assets/icons/tech/disabled")



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
            if type(entity) == TownCenter or type(entity) == Barracks or type(entity) == Market:
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
                    display_pos_y = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[1] + camera.scroll.y - 43
                elif type(entity) == Clubman:
                    display_pos_y = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[1] + camera.scroll.y - 56
                    display_pos_x = map.grid_to_renderpos(entity.pos[0], entity.pos[1])[
                                        0] + map.grass_tiles.get_width() / 2 + camera.scroll.x + 10
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
            if self.examined_tile.__class__.__name__ == "Farm":
                img = self.first_age_building_sprites[self.examined_tile.__class__.__name__][self.examined_tile.owner.color].copy()

            elif self.examined_tile.__class__.__name__ == "Tower":
                img = scale_image(self.first_age_building_sprites[self.examined_tile.__class__.__name__][self.examined_tile.owner.color][0].copy(), w= 80)

            elif self.examined_tile.__class__.__name__ == "Wall":
                img = scale_image(self.first_age_building_sprites[self.examined_tile.__class__.__name__][
                                      self.examined_tile.owner.color][0].copy(), w=90)
            else:
                img = self.first_age_building_sprites[self.examined_tile.__class__.__name__][self.examined_tile.owner.color][self.examined_tile.owner.age - 1].copy()


        # if unit, display unit with 270 degree (index : 4)
        else:
            if isinstance(self.examined_tile, Villager):
                img = self.villager_sprites[self.examined_tile.owner.color][4].copy()
                img_scaled = scale_image(img, h * 0.20)
                screen.blit(img_scaled, (action_menu.get_width() + 50, self.height - selection_panel.get_height() + 70))
            elif isinstance(self.examined_tile, Clubman):
                img = self.clubman_sprites[self.examined_tile.owner.color][4].copy()
                img_scaled = scale_image(img, h * 0.40)
                screen.blit(img_scaled, (action_menu.get_width() + 40, self.height - selection_panel.get_height() + 70))

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

        elif type(self.examined_tile) == Tower:
            img_scaled = scale_image(img, h * 0.50)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 75))

        elif type(self.examined_tile) == Wall:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 75))

        elif type(self.examined_tile) == Market:
            img_scaled = scale_image(img, h * 0.60)
            screen.blit(img_scaled, (action_menu.get_width() + 20, self.height - selection_panel.get_height() + 85))

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
                icon = self.images["Villager"]
                str_name = "Villager"
            elif trained_entity == Clubman:
                icon = self.images["Clubman"]
                str_name = "Clubman"

            else:
                icon = None
            # health bar
            # to get the same progress bar size and not have huge ones, we use a ratio
            progress_bar_length = 120
            progress_secs = training_entity.now - training_entity.resource_manager_cooldown
            max_progress = (trained_entity.construction_time * 1000)
            progress_displayed = progress_secs / max_progress * progress_bar_length

            # from 1 to 100% of max health, used to know which color we use for the health bar
            ratio = (progress_secs / max_progress) * 100

            pygame.draw.rect(screen, (255, 201, 14),
                             (action_menu.get_width() + 350, self.height * 0.8 + 34, progress_displayed, 6))
            pygame.draw.rect(screen, (55, 55, 55),
                             (action_menu.get_width() + 350, self.height * 0.8 + 34, progress_bar_length, 6), 2)

            temp_text = "Training a " + str_name + "..."
            draw_text(screen, temp_text, 13, (255, 255, 255), (action_menu.get_width() + 354, self.height * 0.8 + 17))

            # progress %
            health_text = str(int(ratio)) + "%"
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
        elif entity == "Clubman":
            entity = Clubman
        elif entity == "Farm":
            entity = Farm
        elif entity == "House":
            entity = House
        elif entity == "TownCenter":
            entity = TownCenter
        elif entity == "Barracks":
            entity = Barracks
        elif entity == "Tower":
            entity = Tower
        elif entity == "Wall":
            entity = Wall
        elif entity == "Market":
            entity = Market
        else:
            display_tooltip_for_entity = False

        if entity == "Advance to Feudal Age" or entity == "Advance to Castle Age" or \
                entity == "Advance to Imperial Age" or entity == "Research Improved Masonry" or \
                entity == "Research Reinforced Masonry" or entity == "Research Imbued Masonry" or \
                entity == "Research Iron Swords" or entity == "Research Steel Swords" or \
                entity == "Research Mithril Swords" or entity == "Research Iron Armors" or \
                entity == "Research Steel Armors" or entity == "Research Mithril Armors" or \
                entity == "Research Iron Arrows" or entity == "Research Iron Horseshoes":
            display_tooltip_for_tech = True

        if entity == "Advance to Feudal Age":
            entity = Age_II
        elif entity == "Advance to Castle Age":
            entity = Age_III
        elif entity == "Advance to Imperial Age":
            entity = Age_IV

        elif entity == "Research Iron Swords":
            entity = iron_sword_tech
        elif entity == "Research Steel Swords":
            entity = steel_sword_tech
        elif entity == "Research Mithril Swords":
            entity = mithril_sword_tech

        elif entity == "Research Iron Armors":
            entity = iron_armor_tech
        elif entity == "Research Steel Armors":
            entity = steel_armor_tech
        elif entity == "Research Mithril Armors":
            entity = mithril_armor_tech

        elif entity == "Research Improved Masonry":
            entity = improved_masonry_tech
        elif entity == "Research Reinforced Masonry":
            entity = reinforced_masonry_tech
        elif entity == "Research Imbued Masonry":
            entity = imbued_masonry_tech

        elif entity == "Research Iron Arrows":
            entity = arrow_tech
        elif entity == "Research Iron Horseshoes":
            entity = horseshoe_tech
        elif entity == "Research Super Cows":
            entity = food_production_tech

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

        market = {"BLUE": load_images_better("Resources/assets/Models/Buildings/Market/BLUE/"),
                 "RED": load_images_better("Resources/assets/Models/Buildings/Market/RED/"),
                 "GREEN": load_images_better("Resources/assets/Models/Buildings/Market/GREEN/"),
                 "YELLOW": load_images_better("Resources/assets/Models/Buildings/Market/YELLOW/")}
        # to resize
        for x in range(0, 4):
            market["BLUE"][x] = scale_image(market["BLUE"][x], w=200)
            market["RED"][x] = scale_image(market["RED"][x], w=200)
            market["GREEN"][x] = scale_image(market["GREEN"][x], w=200)
            market["YELLOW"][x] = scale_image(market["YELLOW"][x], w=200)

        tower = {"BLUE": load_images_better("Resources/assets/Models/Buildings/Tower/BLUE/"),
                    "RED": load_images_better("Resources/assets/Models/Buildings/Tower/RED/"),
                    "GREEN": load_images_better("Resources/assets/Models/Buildings/Tower/GREEN/"),
                    "YELLOW": load_images_better("Resources/assets/Models/Buildings/Tower/YELLOW/")}
        # to resize
        for x in range (0,4):
            tower["BLUE"][x] = scale_image(tower["BLUE"][x], w= 180)
            tower["RED"][x] = scale_image(tower["RED"][x], w= 180)
            tower["GREEN"][x] = scale_image(tower["GREEN"][x], w= 180)
            tower["YELLOW"][x] = scale_image(tower["YELLOW"][x], w= 180)


        wall = {"BLUE": load_images_better("Resources/assets/Models/Buildings/Wall/BLUE/Left/"),
                    "RED": load_images_better("Resources/assets/Models/Buildings/Wall/RED/Left"),
                    "GREEN": load_images_better("Resources/assets/Models/Buildings/Wall/GREEN/Left"),
                    "YELLOW": load_images_better("Resources/assets/Models/Buildings/Wall/YELLOW/Left")}

        for x in range (0,4):
            wall["BLUE"][x] = scale_image(wall["BLUE"][x], w= 100)
            wall["RED"][x] = scale_image(wall["RED"][x], w= 100)
            wall["GREEN"][x] = scale_image(wall["GREEN"][x], w= 100)
            wall["YELLOW"][x] = scale_image(wall["YELLOW"][x], w= 100)

        images = {
            "TownCenter": town_center,
            "House": house,
            "Barracks": barracks,
            "Farm": farm,
            "Market": market,
            "Tower": tower,
            "Wall": wall
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

    # flags that are displayed to show the unit's destination
    def load_destination_flags(self):
        dic = {"BLUE": load_images_better("Resources/assets/Models/Units/dest_flag/BLUE"),
               "RED": load_images_better("Resources/assets/Models/Units/dest_flag/RED"),
               "GREEN": load_images_better("Resources/assets/Models/Units/dest_flag/GREEN"),
               "YELLOW": load_images_better("Resources/assets/Models/Units/dest_flag/YELLOW")
               }
        return dic

    def load_dragon_sprites(self):
        dragon_sprites_dic = {"idle": {}, "death": []}
        # loop for the 8 angles. folder * 45 because angles are 0, 45, 90, 135, etc... up to 315 for max.
        for folder in range(0, 3):
            dragon_sprites_dic["idle"][str(int(folder * 90))] = load_images_better("resources/assets/Models/Units/Dragon/idle/" + str(int(folder * 90)))
        dragon_sprites_dic["death"] = load_images_better("resources/assets/Models/Units/Dragon/death")

        return dragon_sprites_dic

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

    def load_tech_tree(self):
        return load_images_better("resources/assets/tech_tree")

    def display_tech_tree(self, screen):
        tech_tree_width = self.tech_tree_images[0].get_width() + self.tech_tree_images[1].get_width() + self.tech_tree_images[2].get_width()
        tech_tree_height = self.tech_tree_images[0].get_height()
        init_pos = ((self.width - tech_tree_width) // 2, (self.height - tech_tree_height ) // 2)
        screen.blit(self.tech_tree_images[0], init_pos)
        screen.blit(self.tech_tree_images[1], (init_pos[0] + self.tech_tree_images[0].get_width(), init_pos[1]))
        screen.blit(self.tech_tree_images[2], (init_pos[0] + self.tech_tree_images[0].get_width() + self.tech_tree_images[1].get_width(), init_pos[1]))

        # player name
        draw_text(screen, MAIN_PLAYER.name, 30, "GOLD", (init_pos[0] + 150, init_pos[1] + 30))
        #rows
        first_age_height = init_pos[1] + 125
        second_age_height = first_age_height + 150
        third_age_height = second_age_height + 150
        fourth_age_height = third_age_height + 150
        #columns
        first_column = init_pos[0] + 600
        second_column = first_column + 150
        third_column = second_column + 150

        #**************************************** masonry tech
        if MAIN_PLAYER.improved_masonry_unlocked:
            screen.blit(improved_masonry_icon, (third_column, second_age_height))
            screen.blit(scale_image(tech_line, w=30), (third_column + 10, second_age_height + 55))

        # else blit disabled version of icon
        else:
            screen.blit(self.tech_sprites_disabled[0], (third_column, second_age_height))

        if MAIN_PLAYER.reinforced_masonry_unlocked:
            screen.blit(fortified_masonry_icon, (third_column, third_age_height))
            screen.blit(scale_image(tech_line, w=30), (third_column + 10, third_age_height + 55))

        else:
            screen.blit(self.tech_sprites_disabled[1], (third_column, third_age_height))

        if MAIN_PLAYER.imbued_masonry_unlocked:
            screen.blit(imbued_masonry_icon, (third_column, fourth_age_height))
        else:
            screen.blit(self.tech_sprites_disabled[2], (third_column, fourth_age_height))

        # *****************************************sword tech
        if MAIN_PLAYER.iron_swords_unlocked:
            screen.blit(iron_sword_icon, (first_column, second_age_height))
            screen.blit(scale_image(tech_line, w=30), (first_column + 10, second_age_height + 55))
        # else blit disabled version of icon
        else:
            screen.blit(self.tech_sprites_disabled[3], (first_column, second_age_height))

        if MAIN_PLAYER.steel_swords_unlocked:
            screen.blit(steel_sword_icon, (first_column, third_age_height))
            screen.blit(scale_image(tech_line, w=30), (first_column + 10, third_age_height + 55))
        else:
            screen.blit(self.tech_sprites_disabled[4], (first_column, third_age_height))

        if MAIN_PLAYER.mithril_swords_unlocked:
            screen.blit(mithril_sword_icon, (first_column, fourth_age_height))
        else:
            screen.blit(self.tech_sprites_disabled[5], (first_column, fourth_age_height))

        #*******************************armor tech
        if MAIN_PLAYER.iron_armors_unlocked:
            screen.blit(iron_armor_icon, (second_column, second_age_height))
            screen.blit(scale_image(tech_line, w=30), (second_column + 10, second_age_height + 55))
        #else blit disabled version of icon
        else:
            screen.blit(self.tech_sprites_disabled[6], (second_column, second_age_height))

        if MAIN_PLAYER.steel_armors_unlocked:
            screen.blit(steel_armor_icon, (second_column, third_age_height))
            screen.blit(scale_image(tech_line, w=30), (second_column + 10, third_age_height + 55))
        else:
            screen.blit(self.tech_sprites_disabled[7], (second_column, third_age_height))

        if MAIN_PLAYER.mithril_armors_unlocked:
            screen.blit(mithril_armor_icon, (second_column, fourth_age_height))
        else:
            screen.blit(self.tech_sprites_disabled[8], (second_column, fourth_age_height))
