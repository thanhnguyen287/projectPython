import pygame
from settings import MAP_SIZE_X, MAP_SIZE_Y

RESSOURCE_LIST = ["wood", "food", "gold", "stone"]

GENERAL_UNIT_LIST = []
GENERAL_BUILDING_LIST = []

UNIT_TYPES = []
BUILDING_TYPES = []


#Global parameters of the game

TEST_MODE = True
IA_MODE = True
SPEED_OF_GAME = 3

def draw_text(screen, text, size, color, pos):
    # create a Font object from the system fonts
    # SysFont(name, size, bold=False, italic=False)

    # font = pygame.font.SysFont(None, size)

    font = pygame.font.SysFont('Times New Roman', size)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=pos)

    screen.blit(text_surface, text_rect)


# 2D -> 2.5D
def decarte_to_iso(x, y):
    iso_x = x - y
    iso_y = (x + y) / 2
    return iso_x, iso_y


def iso_to_decarte(iso_x, iso_y):
    y = (2 * iso_y - iso_x) / 2
    x = (2 * iso_y + iso_x) / 2
    return x, y


def scale_image(image, w=None, h=None):
    if (w is None) and (h is None):
        pass
    elif h is None:
        scale = w / image.get_width()
        h = scale * image.get_height()
        image = pygame.transform.scale(image, (int(w), int(h)))
    elif w is None:
        scale = h / image.get_height()
        w = scale * image.get_width()
        image = pygame.transform.scale(image, (int(w), int(h)))
    else:
        image = pygame.transform.scale(image, (int(w), int(h)))

    return image


    #returns RGB_code corresponding to the color argument(red,green,blue)
    #red, green, blue going from 0 to 255, with 255 being the closer to full color and 0 to none/black
def get_color_code(color: str):

    if color == "WHITE":
        return 255, 255, 255

    elif color == "BLACK":
        return 0, 0, 0

    elif color == "GREY":
        return 60, 60, 60

    elif color == "BLUE":
        return 0, 0, 255

    elif color == "GREEN":
        return 0, 255, 0

    elif color == "DARK_GREEN":
        return 0, 190, 20

    elif color == "RED":
        return 255, 0, 0

    elif color == "DARK_RED":
        return 138, 3, 3

    elif color == "DEFEAT_RED":
        return 158, 43, 43

    elif color == "DARK_GRAY":
        return 25, 25, 25

    elif color == "ORANGE":
        return 255, 127, 0

    elif color == "YELLOW":
        return 255, 255, 0

    elif color == "GOLD":
        return 255, 201, 14


#def str_to_entity_class(name: str):
 #   if name == "TownCenter":
  #      return TownCenter
   # elif name == "House":
    #    return House
    #elif name == "Farm":
     #   return Farm

    #elif name == "Villager":
     #   return Villager
    #elif name == "Clubman":
     #   return Clubman
    #elif name == "Bowman":
     #   return Bowman

# this methode return a list of the x nearest free tiles
def tile_founding(x, first_layer, layer_max, map, player, tile_type, MAP=None):
    #here we convert the ressource we want to the corresponding ressource type on the map
    if tile_type == "wood": tile_type = "tree"
    if tile_type == "stone": tile_type = "rock"
    if tile_type == "food": tile_type = "berrybush"

    list_of_tile = []
    nb_of_tile_left_to_found = x
    layer = first_layer
    tc_pos = player.towncenter_pos

    # while we dont have all the tiles we want or the layer max is reached, we keep going
    while nb_of_tile_left_to_found > 0 and layer <= layer_max:
        # we look at the top and bot side of the square formed by the tile of the
        for j in range(layer * 2 + 2):
            # if the tile is empty we add it to the list and we decrease the nb of tile left to found
            pos_x = tc_pos[0] - layer + j
            pos_y = tc_pos[1] - layer - 1
            if 0 <= pos_x < MAP_SIZE_X and 0 <= pos_y < MAP_SIZE_Y and map[pos_x][pos_y]["tile"] == tile_type and \
                    nb_of_tile_left_to_found > 0:
                if tile_type != "" or MAP is None:
                    list_of_tile.append((pos_x, pos_y))
                    nb_of_tile_left_to_found -= 1
                else:
                    if MAP is not None and MAP.collision_matrix[pos_y][pos_x]:
                        list_of_tile.append((pos_x, pos_y))
                        nb_of_tile_left_to_found -= 1

            pos_x = tc_pos[0] - layer + j
            pos_y = tc_pos[1] + layer
            if 0 <= pos_x < MAP_SIZE_X and 0 <= pos_y < MAP_SIZE_Y and map[pos_x][pos_y]["tile"] == tile_type and \
                    nb_of_tile_left_to_found > 0:
                if tile_type != "" or MAP is None:
                    list_of_tile.append((pos_x, pos_y))
                    nb_of_tile_left_to_found -= 1
                else:
                    if MAP is not None and MAP.collision_matrix[pos_y][pos_x]:
                        list_of_tile.append((pos_x, pos_y))
                        nb_of_tile_left_to_found -= 1

        for k in range(1, layer * 2 + 1):
            pos_x = tc_pos[0] - layer
            pos_y = tc_pos[1] - layer - 1 + k
            if 0 <= pos_x < MAP_SIZE_X and 0 <= pos_y < MAP_SIZE_Y and map[pos_x][pos_y]["tile"] == tile_type and \
                    nb_of_tile_left_to_found > 0:
                if tile_type != "" or MAP is None:
                    list_of_tile.append((pos_x, pos_y))
                    nb_of_tile_left_to_found -= 1
                else:
                    if MAP is not None and MAP.collision_matrix[pos_y][pos_x]:
                        list_of_tile.append((pos_x, pos_y))
                        nb_of_tile_left_to_found -= 1

            pos_x = tc_pos[0] + layer + 1
            pos_y = tc_pos[1] - layer - 1 + k
            if 0 <= pos_x < MAP_SIZE_X and 0 <= pos_y < MAP_SIZE_Y and map[pos_x][pos_y]["tile"] == tile_type and \
                    nb_of_tile_left_to_found > 0:
                if tile_type != "" or MAP is None:
                    list_of_tile.append((pos_x, pos_y))
                    nb_of_tile_left_to_found -= 1
                else:
                    if MAP is not None and MAP.collision_matrix[pos_y][pos_x]:
                        list_of_tile.append((pos_x, pos_y))
                        nb_of_tile_left_to_found -= 1

        layer += 1
    return list_of_tile


def look_around(pos, map):
    list = []
    if 0 <= pos[0]+1 < MAP_SIZE_X and map[pos[0]+1][pos[1]]["tile"] == "":
        list.append(True)
    else:
        list.append(False)

    if 0 <= pos[0]-1 < MAP_SIZE_X and map[pos[0]-1][pos[1]]["tile"] == "":
        list.append(True)
    else:
        list.append(False)

    if 0 <= pos[1]+1 < MAP_SIZE_Y and map[pos[0]][pos[1] + 1]["tile"] == "":
        list.append(True)
    else:
        list.append(False)

    if 0 <= pos[1]-1 < MAP_SIZE_Y and map[pos[0]][pos[1]-1]["tile"] == "":
        list.append(True)
    else:
        list.append(False)

    return True if any(list) else False

def better_look_around(villager_pos, ressource_pos, map):
    list = []
    if 0 <= ressource_pos[0] + 1 < MAP_SIZE_X and map[ressource_pos[0] + 1][ressource_pos[1]]["tile"] == "" and \
            villager_pos[0] >= ressource_pos[0]:
        list.append(True)
    else:
        list.append(False)

    if 0 <= ressource_pos[0] - 1 < MAP_SIZE_X and map[ressource_pos[0] - 1][ressource_pos[1]]["tile"] == "" and \
            villager_pos[0] <= ressource_pos[0]:
        list.append(True)
    else:
        list.append(False)

    if 0 <= ressource_pos[1] + 1 < MAP_SIZE_Y and map[ressource_pos[0]][ressource_pos[1] + 1]["tile"] == "" and \
            villager_pos[1] >= ressource_pos[1]:
        list.append(True)
    else:
        list.append(False)

    if 0 <= ressource_pos[1] - 1 < MAP_SIZE_Y and map[ressource_pos[0]][ressource_pos[1] - 1]["tile"] == "" and \
            villager_pos[1] <= ressource_pos[1]:
        list.append(True)
    else:
        list.append(False)

    return True if any(list) else False


def is_adjacent_to(pos1, pos2):
    if 0 <= pos1[0] < MAP_SIZE_X and 0 <= pos2[0] < MAP_SIZE_X and 0 <= pos1[1] < MAP_SIZE_Y and \
            0 <= pos2[1] < MAP_SIZE_Y:
        if (abs(pos1[0] - pos2[0]) <= 1 and pos1[1] == pos2[1]) or \
                (abs(pos1[1] - pos2[1]) <= 1 and pos1[0] == pos2[0]):
            return True

        else:
            return False

def find_owner(pos):
    for u in GENERAL_UNIT_LIST:
        unit_pos = list(u.pos)
        if unit_pos == pos:
            return u.owner

    for b in GENERAL_BUILDING_LIST:
        bat_pos= list(b.pos)
        if bat_pos == pos:
            return b.owner