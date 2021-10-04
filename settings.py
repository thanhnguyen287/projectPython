import os
import pygame
TILE_SIZE = 64
WIDTH = 800
HEIGHT = 600

ENABLE_HEALTH_BARS = False

#path
current_path = os.path.dirname(__file__) #current path of settings.py
resource_path = os.path.join(current_path, 'resources') 
common_path = os.path.join(resource_path, 'common')
assets_path = os.path.join(resource_path, 'assets')
top_menu = pygame.image.load ("resources/assets/top_menu.png")
standard_cursor = pygame.image.load ("resources/assets/standard_cursor.png")

def decarte_to_iso(x, y):
    iso_x = x - y
    iso_y = (x + y) / 2
    return iso_x, iso_y


