from game.game import Game as g
from settings import *
#from .settings import WIDTH
#from .settings import HEIGHT

# to force push : git push -f origin branch_name (our branch name is name)

#intialize pygame
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

#create the screen
#screen = pygame.display.set_mode((1920,1080))
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) #Full screen for many type of screen
#screen = pygame.display.set_mode((WIDTH,HEIGHT)) #Adjustable in Settings.py


#Title and Icon
pygame.display.set_caption("Age of Empire: Homemade Edition")
icon = pygame.image.load(os.path.join(common_path,'icon.png'))
pygame.display.set_icon(icon)
game = g(screen, clock)

def main():


#Exit game
    running = True
    playing = True
    while running:

        # Add start menu here

        while playing:



            # Start game loop
            game.run()



if __name__ == "__main__":
    main()

