import os
import pygame

TILE_SIZE = 64
#WIDTH = 1920
#HEIGHT = 1080


ENABLE_HEALTH_BARS = False

pygame.font.init()
myfont = pygame.font.SysFont("monospace", 14)

#path
current_path = os.path.dirname(__file__)  #current path of settings.py
resource_path = os.path.join(current_path, 'resources') 
common_path = os.path.join(resource_path, 'common')
assets_path = os.path.join(resource_path, 'assets')

top_menu = pygame.image.load("resources/assets/ressource_bar_ui.png")
top_menu_hd = pygame.image.load("resources/assets/NewUI_blank_resized.png")
bot_menu_building_hd = pygame.image.load("resources/assets/buildingmenuDE.png")
bot_complet_menu_building_hd = pygame.image.load("resources/assets/botuiDE.png")


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



#ressources icons
wood_cost = pygame.image.load("resources/assets/icons/wood_cost.png")
food_cost = pygame.image.load("resources/assets/icons/food_cost.png")
gold_cost = pygame.image.load("resources/assets/icons/gold_cost.png")
stone_cost = pygame.image.load("resources/assets/icons/stone_cost.png")
population_cost = pygame.image.load("resources/assets/icons/population_cost.png")

standard_cursor = pygame.image.load("resources/assets/standard_cursor.png")

destination_flag = pygame.image.load("resources/assets/dflag.png")
