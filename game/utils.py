import pygame


def draw_text(screen, text, size, color, pos):
#create a Font object from the system fonts
#SysFont(name, size, bold=False, italic=False)

    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color )
    text_rect = text_surface.get_rect(topleft=pos)

    screen.blit(text_surface, text_rect)
