from settings import *
###################OLD CODE, WE ARE NOT WORKING WITH IT ANYMORE. SEE builds to see buildings relevant code
class Building:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.name = "none"
        self.max_health = 100
        self.current_health = self.max_health
        self.is_alive = True

        self.construction_time = 1
        self.construction_cost = [0,0,0,0]
        self.max_population_bonus = 0

        self.sprite = pygame.image.load(os.path.join(assets_path,"town_center.png"))

        self.image_select = pygame.image.load(os.path.join(assets_path,"image_select.png"))
        self.selected = False



    def display(self, screen):
        if self.selected:
            screen.blit(self.image_select, self.get_position_select())
            self.display_life(screen)

        screen.blit(self.sprite, self.get_position())


    def display_life(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.get_position()[0] - 8,self.get_position()[1]-15, self.current_health * 1, 10))
        pygame.draw.rect(screen, (25, 25, 25), (self.get_position()[0] - 8,self.get_position()[1]-15, self.max_health * 1, 10), 4)



    #we return the position to display the select blue rectangle
    def get_position_select(self):
        return 894+(self.x-self.y)*64, 202+(self.y+self.x)*32

    #we change the parameter selected
    def select(self):
        if (self.x, self.y) == self.pos_mouse():
            self.selected = not(self.selected)

