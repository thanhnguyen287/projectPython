import sys

from House import *
from TownHall import *
from .camera import Camera
from .map import *
from .utils import draw_text
from .hud import Hud
from.animation import *

buildings = [town1, house1]


class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()

        # camera
        self.camera = Camera(self.width, self.height)

        # hud
        self.hud = Hud(self.width, self.height)

        # map
        self.map = Map(self.hud, 50, 50, self.width, self.height)




    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(120)
            self.events()
            self.update()
            self.draw()



    def events(self):

        for event in pygame.event.get():

            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # USER PRESSED A KEY
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    # Quit to menu screen instead maybe
                    pygame.quit()
                    sys.exit()

                # Enable - Disable health bars
                if event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    global ENABLE_HEALTH_BARS
                    if ENABLE_HEALTH_BARS == False:
                        ENABLE_HEALTH_BARS = True
                    else:
                        ENABLE_HEALTH_BARS = False



            # USER PRESSED A MOUSEBUTTON
            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:  #  LEFT CLICK
                    # we check the clicks for every building
                    for b in buildings:
                        b.select()

                elif event.button == 3:  # RIGHT CLICK
                    #if testUnit1.is_alive:
                        #testUnit2.attack(testUnit1)
                    player.rect.topleft = [pygame.mouse.get_pos()[0]-60, pygame.mouse.get_pos()[1]-100]
                    player.play()

    def update(self):
        self.camera.update()
        self.hud.update()
        self.map.update(self.camera)

    # GAME DISPLAY
    def draw(self):

        # BLACK BACKGROUND
        self.screen.fill((0,0,0))
        #the map display was moved inside the hud class
        self.map.draw(self.screen, self.camera)
        # drawing the hud, must be last but before fps and cursor
        self.hud.draw(self.screen)

        # MOUSE CURSOR - we disable the default one and create a new one at the current position of the mouse
        # MUST BE LAST TO SEE IT AND NOT BE HIDDEN BEHIND OTHER THINGS
        #pygame.mouse.set_visible(False)
        #standard_cursor_rect = standard_cursor.get_rect()
        #standard_cursor_rect.center = pygame.mouse.get_pos()  # update position
        #self.screen.blit(standard_cursor, standard_cursor_rect)  # draw the cursor

        #Boom animation
        moving_sprites.draw(self.screen)
        moving_sprites.update(0.25)

        #Draw FPS, must be the last to shown -> put it right on top of the display.flip
        draw_text(self.screen,'fps={}'.format(round(self.clock.get_fps())),25,(255,0,0),(5,80))
        pygame.display.flip()

