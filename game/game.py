import sys
from .camera import Camera
from .map import *
from .utils import draw_text
from .hud import Hud
from.animation import *
from units import *


class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        # hud
        self.hud = Hud(self.width, self.height)
        # entities list (units, buildings, etc...)
        self.entities = []
        # map
        self.map = Map(self.hud, self.entities, 50, 50, self.width, self.height)

        #start_unit = Villager(self.map.map[5][5], playerOne, self.map)
        #self.map.units[5][5] = start_unit
        #first villagers
        start_unit = Villager(self.map.map[5][5], playerOne, self.map)
        self.map.units[5][5] = start_unit
        self.map.collision_matrix[start_unit.pos["grid"][1]][start_unit.pos["grid"][0]] = 0
        self.map.map[start_unit.pos["grid"][0]][start_unit.pos["grid"][1]]["collision"] = True

        # camera
        self.camera = Camera(self.width, self.height)
        # on centre la camera au milieu de la carte
        #th_x = self.map.place_x
        th_x = 25
        #th_y = self.map.place_y
        th_y = 25
        cam_x = (iso_to_decarte(th_x*64, th_y*32)[0]) - 4050
        cam_y = (iso_to_decarte(th_x*64, th_y*32)[1]) - 1200
        self.camera.scroll = pygame.Vector2(cam_x, cam_y)
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
                    pass
                elif event.button == 3:  # RIGHT CLICK
                    #if testUnit1.is_alive:
                        #testUnit2.attack(testUnit1)
                    player.rect.topleft = [pygame.mouse.get_pos()[0]-60, pygame.mouse.get_pos()[1]-100]
                    player.play()
    def update(self):
        self.camera.update()
        self.hud.update(self.screen)
        self.map.update(self.camera, self.screen)
        for an_entity in self.entities:
            an_entity.update()
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
        draw_text(self.screen,'fps={}'.format(round(self.clock.get_fps())),20,(255,0,0),(5,40))
        pygame.display.flip()
