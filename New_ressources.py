import pygame

def display_health(screen, x, y, health, max_health):
    pygame.draw.rect(screen, (0, 255, 0), (x, y, health * 10, 10))
    pygame.draw.rect(screen, (25, 25, 25), (x, y, max_health * 10, 10), 4)
