import pygame


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
        return 0, 128, 0

    elif color == "RED":
        return 255, 0, 0

    elif color == "DARK_RED":
        return 138, 3, 3

    elif color == "ORANGE":
        return 255, 127, 0

    elif color == "YELLOW":
        return 255, 255, 0

    elif color == "GOLD":
        return 255, 201, 14
