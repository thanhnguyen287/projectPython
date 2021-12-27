from player import *


# classes for the ressources on the map

class Ressource:

    def __init__(self, tile_x, tile_y):
    
        self.quantity = 0
        self.type = ""
        self.x = tile_x
        self.y = tile_y

        self.max_health = 100
        self.current_health = self.max_health
        self.is_standing = True

        self.sprite_standing = pygame.image.load("resources/assets/tree.png")
        self.sprite_fallen = pygame.image.load("resources/assets/rock.png")

        self.image_select = pygame.image.load("resources/assets/image_select.png")
        self.selected = False

    def update_quantity(self, amount):
        self.quantity += amount

    #we return the "real" x and y position to display the building on the map
    def get_position(self):
        return 908+(self.x-self.y)*64, 188+(self.y+self.x)*32

    def get_position_select(self):
        return 894+(self.x-self.y)*64, 202+(self.y+self.x)*32

    def select(self):
        if (self.x, self.y) == self.pos_mouse():
            self.selected = not self.selected

    def pos_mouse(self):
        mousex = int(((1 / 2) * pygame.mouse.get_pos()[0] + pygame.mouse.get_pos()[1] - 672) // 64)
        mousey = int((pygame.mouse.get_pos()[1] - (1 / 2) * pygame.mouse.get_pos()[0] + 288) // 64)
        return mousex, mousey

    def display(self, screen):
        if self.selected:
            screen.blit(self.image_select, self.get_position_select())
            self.display_life(screen)

        #depending on if the tree is standing or fallen we display different models
        if self.is_standing:
            screen.blit(self.sprite_standing, self.get_position())
        else:
            screen.blit(self.sprite_fallen, self.get_position())

    def display_life(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.get_position()[0]-15, self.get_position()[1]-15, self.current_health * 3, 10))
        pygame.draw.rect(screen, (25, 25, 25), (self.get_position()[0]-15, self.get_position()[1]-15, self.max_health * 3, 10), 4)

