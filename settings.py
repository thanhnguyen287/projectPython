import os
import pygame

TILE_SIZE = 64
#WIDTH = 1920
#HEIGHT = 1080
SHOW_GRID_SETTING = False


ENABLE_HEALTH_BARS = False

pygame.font.init()
myfont = pygame.font.SysFont("monospace", 14)

#path
current_path = os.path.dirname(__file__)  #current path of settings.py
resource_path = os.path.join(current_path, 'resources') 
common_path = os.path.join(resource_path, 'common')
assets_path = os.path.join(resource_path, 'assets')

top_menu_hd = pygame.image.load("resources/assets/NewUI_blank_resized.png")
bot_menu_building_hd = pygame.image.load("resources/assets/buildingmenuDE.png")
bot_complet_menu_building_hd = pygame.image.load("resources/assets/botuiDE.png")
action_menu = pygame.image.load("resources/assets/action_menu.png")
selection_panel = pygame.image.load("resources/assets/selection_panel.png")
minimap_panel = pygame.image.load("resources/assets/minimap_panel.png")
age_panel = pygame.image.load("resources/assets/age_panel.png")
resource_panel = pygame.image.load("resources/assets/resources_panel.png")

#resources icons
wood_icon = pygame.image.load("resources/assets/wood_icon.png")
food_icon = pygame.image.load("resources/assets/food_icon.png")
gold_icon = pygame.image.load("resources/assets/gold.png")
stone_icon = pygame.image.load("resources/assets/stone_icon.png")
pop_icon = pygame.image.load("resources/assets/pop_icon.png")

#ages icons
age_1 = pygame.image.load("resources/assets/age_1.png")
age_2 = pygame.image.load("resources/assets/age_2.png")
age_3 = pygame.image.load("resources/assets/age_3.png")
age_4 = pygame.image.load("resources/assets/age_4.png")





farm_icon = pygame.image.load("resources/assets/icons./farm_icon.png")
farm_icon_hd = pygame.image.load("resources/assets/icons./FarmDE.png")

town_center_icon = pygame.image.load("resources/assets/icons./town_center_icon_hd.png")
house_icon = pygame.image.load("resources/assets/icons/houseDE.png")
villager_icon = pygame.image.load("resources/assets/icons/villagerde.bmp")

#armor and attack classes icons
armor_icon = pygame.image.load("resources/assets/icons/normal_armor.png")
building_armor_icon = pygame.image.load("resources/assets/icons/building_armor.png")
melee_attack_icon = pygame.image.load("resources/assets/icons/melee_attack.png")
ranged_attack_icon = pygame.image.load("resources/assets/icons/ranged_attack.png")

stop_icon = pygame.image.load("resources/assets/icons/STOP.png")

#ressources icons
wood_cost = pygame.image.load("resources/assets/icons/wood_cost.png")
food_cost = pygame.image.load("resources/assets/icons/food_cost.png")
gold_cost = pygame.image.load("resources/assets/icons/gold_cost.png")
stone_cost = pygame.image.load("resources/assets/icons/stone_cost.png")
population_cost = pygame.image.load("resources/assets/icons/population_cost.png")

#construction progression
building_construction_1 = pygame.image.load("resources/assets/258_1.png")
building_construction_2 = pygame.image.load("resources/assets/258_2.png")
building_construction_3 = pygame.image.load("resources/assets/258_3.png")
building_construction_4 = pygame.image.load("resources/assets/258_4.png")

building_construction_1_2x2 = pygame.image.load("resources/assets/Models/Buildings/b_all_construction_2x2_x2_1.png")
building_construction_2_2x2 = pygame.image.load("resources/assets/Models/Buildings/b_all_construction_2x2_x2_2.png")
building_construction_3_2x2 = pygame.image.load("resources/assets/Models/Buildings/b_all_construction_2x2_x2_3.png")
building_construction_4_2x2 = pygame.image.load("resources/assets/Models/Buildings/b_all_construction_2x2_x2_4.png")



standard_cursor = pygame.image.load("resources/assets/standard_cursor.png")

destination_flag = pygame.image.load("resources/assets/dflag.png")
