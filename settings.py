import os
import pygame

TILE_SIZE = 64
WIDTH = 1920
HEIGHT = 1080

ENABLE_HEALTH_BARS = False

pygame.font.init()

#path
current_path = os.path.dirname(__file__) #current path of settings.py
resource_path = os.path.join(current_path, 'resources') 
common_path = os.path.join(resource_path, 'common')
assets_path = os.path.join(resource_path, 'assets')
top_menu = pygame.image.load ("resources/assets/top_menu.png").convert_alphas()
standard_cursor = pygame.image.load ("resources/assets/standard_cursor.png").convert_alpha()

myfont = pygame.font.SysFont("monospace", 20)

