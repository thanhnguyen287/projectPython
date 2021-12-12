import pygame


def draw_text(screen, text, size, color, pos):
#create a Font object from the system fonts
#SysFont(name, size, bold=False, italic=False)

    #font = pygame.font.SysFont(None, size)


    font = pygame.font.SysFont('Times New Roman', size)

    text_surface = font.render(text, True, color )
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

