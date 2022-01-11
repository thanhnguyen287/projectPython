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
        self.hud = Hud(self.width, self.height, self.screen)

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
            #self.IA.run()

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
                    ENABLE_HEALTH_BARS = not ENABLE_HEALTH_BARS

            # USER PRESSED A MOUSEBUTTON
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # the player left click to train a villager or build a building
                if event.button == 1 and self.hud.bottom_left_menu is not None:

                    #to have informations about the villager
                    if self.map.hud.examined_tile is not None and self.map.hud.examined_tile.name == "Villager":
                        villager_pos = self.map.hud.examined_tile.pos
                        this_villager = self.map.units[villager_pos[0]][villager_pos[1]]
                        print("Info about villager, print is in game, events")
                        this_villager.print_state()

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
                                        self.hud.examined_tile.train(Villager)

                                    elif button["name"] == "Advance to Feudal Age" or button["name"] == "Advance to Castle Age" or button["name"] == "Advance to Imperial Age":
                                        self.hud.examined_tile.research_tech(button["name"])
                                    else:
                                        self.hud.selected_tile = button
                #BOOM WHEN RIGHT CLICKING
                elif event.button == 3:  # RIGHT CLICK
                    #player.rect.topleft = [pygame.mouse.get_pos()[0]-60, pygame.mouse.get_pos()[1]-100]
                    #player.play()
                    # right click, gathering and moving units (fighting in future)
                    grid_pos = self.map.mouse_to_grid(mouse_pos[0], mouse_pos[1], self.camera.scroll)
                    if 0 <= grid_pos[0] <= self.map.grid_length_x and 0 <= grid_pos[
                        1] <= self.map.grid_length_y:

                        # There is a bug with collecting ressources on the side of the map !!!

                        if self.map.hud.examined_tile is not None and self.map.hud.examined_tile.name == "Villager":
                            villager_pos = self.map.hud.examined_tile.pos
                            this_villager = self.map.units[villager_pos[0]][villager_pos[1]]

                            pos_mouse = self.map.mouse_to_grid(mouse_pos[0], mouse_pos[1], self.camera.scroll)
                            pos_x = pos_mouse[0]
                            pos_y = pos_mouse[1]
                            # ATTACK
                            if self.map.units[pos_x][pos_y] is not None or self.map.buildings[pos_x][pos_y] is not None:
                                # si les deux unites sont adjacentes:
                                this_villager.go_to_attack((pos_x, pos_y))
                                """target_to_attack = self.map.units[pos_x][pos_y] if \
                                    self.map.units[pos_x][pos_y] is not None else self.map.buildings[pos_x][pos_y]
                                this_villager.target = target_to_attack

                                if self.map.map[pos_x][pos_y]["tile"] != "" and \
                                        self.map.map[pos_x][pos_y]["tile"] != "building" and \
                                        self.map.map[pos_x][pos_y]["tile"] != "unit":
                                    this_villager.targeted_ressource = (pos_x, pos_y)

                                if this_villager.is_adjacent_to(target_to_attack):
                                    this_villager.is_attacking = True
                                else:
                                    this_villager_dest = self.map.get_empty_adjacent_tiles((pos_x, pos_y))[0]
                                    this_villager.move_to(self.map.map[this_villager_dest[0]][this_villager_dest[1]])
                                    this_villager.is_moving_to_attack = True"""

                            # ONLY MOVEMENT
                            if not self.map.map[grid_pos[0]][grid_pos[1]]["collision"] and \
                                    not this_villager.is_gathering and this_villager.targeted_ressource is None:
                                this_villager.move_to(self.map.map[grid_pos[0]][grid_pos[1]])

                            # we check if the tile we right click on is a ressource and if its on an adjacent tile of the villager pos, and if the villager isnt moving
                            # if the tile next to him is a ressource and we right click on it and he is not moving, he will gather it
                            if not this_villager.searching_for_path \
                                    and (self.map.map[pos_x][pos_y]["tile"] in ["tree", "rock", "gold", "berrybush"]):
                                this_villager.go_to_ressource((pos_x, pos_y))

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
        #Draw FPS, must be the last to shown -> put it right on top of the display.flip
        draw_text(self.screen,'fps={}'.format(round(self.clock.get_fps())),20,(255,0,0),(5,55))
        pygame.display.flip()
