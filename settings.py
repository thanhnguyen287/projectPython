import os
TILE_SIZE = 64
WIDTH = 800
HEIGHT = 600

#path
current_path = os.path.dirname(__file__) #current path of settings.py
resource_path = os.path.join(current_path, 'resources') 
common_path = os.path.join(resource_path, 'common')
assets_path = os.path.join(resource_path, 'assets')