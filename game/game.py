from .camera import Camera
from .map import *
from .utils import draw_text
from .hud import Hud
from .animation import *
from .IA import IA
from settings import SHOW_GRID_SETTING


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

        # IA
        self.IA = IA(playerOne, self.map.map)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(120)
            self.events()
            self.update()
            self.draw()
            self.IA.run()

    def events(self):
        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
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
                # the player left click to train a villager or build a building
                if event.button == 1 and self.hud.bottom_left_menu is not None:
                    for button in self.hud.bottom_left_menu:
                        if button["rect"].collidepoint(mouse_pos):
                            if button["name"] == "STOP":
                                unit_type_trained = self.hud.examined_tile.unit_type_currently_trained
                                self.hud.examined_tile.owner.refund_entity_cost(unit_type_trained)
                                self.hud.examined_tile.queue -= 1
                                #no more units to create
                                if self.hud.examined_tile.queue == 0:
                                    self.hud.examined_tile.is_working = False
                                    self.hud.examined_tile.unit_type_currently_trained = None
                            else:
                                if button["affordable"]:
                                    if button["name"] == "Villager" and not self.hud.examined_tile.is_being_built:
                                        self.hud.examined_tile.queue += 1
                                        #if the town center is not working
                                        if not self.hud.examined_tile.is_working:
                                            self.hud.examined_tile.unit_type_currently_trained = Villager
                                            self.hud.examined_tile.is_working = True
                                            self.hud.examined_tile.resource_manager_cooldown = pygame.time.get_ticks()
                                        #pay training cost
                                        unit_type_trained = self.hud.examined_tile.unit_type_currently_trained
                                        self.hud.examined_tile.owner.pay_entity_cost_bis(unit_type_trained)

                                    else:
                                        self.hud.selected_tile = button
                #BOOM WHEN RIGHT CLICKING
                elif event.button == 3:  # RIGHT CLICK
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
        self.hud.draw(self.screen, self.map, self.camera)
        # MOUSE CURSOR - we disable the default one and create a new one at the current position of the mouse
        # MUST BE LAST TO SEE IT AND NOT BE HIDDEN BEHIND OTHER THINGS
        #pygame.mouse.set_visible(False)
        #standard_cursor_rect = standard_cursor.get_rect()
        #standard_cursor_rect.center = pygame.mouse.get_pos()  # update position
        #self.screen.blit(standard_cursor, standard_cursor_rect)  # draw the cursor
        #Boom animation
        moving_sprites.draw(self.screen)
        moving_sprites.update(0.25)
        #Draw minimap
        self.map.draw_minimap(self.screen, self.camera)
        #Draw FPS, must be the last to shown -> put it right on top of the display.flip
        draw_text(self.screen,'fps={}'.format(round(self.clock.get_fps())),20,(255,0,0),(5,40))
        pygame.display.flip()
