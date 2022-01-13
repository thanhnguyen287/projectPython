from .camera import Camera
from .map import *
from .utils import draw_text
from .hud import Hud
from .animation import *
from .AI import AI


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
        self.AI_1 = AI(playerTwo, self.map.map)
        self.AI_2 = AI(playerOne, self.map.map)

        # chat
        self.chat_color = (40, 40, 40, 150)
        self.input_box = pygame.Rect(self.width // 2 - 70, self.height // 2 - 16, 140, 45)

        self.is_chat_activated = False
        self.chat_enabled = True
        self.display_msg_flag = False
        self.chat_text = ""
        self.chat_text_color = get_color_code("WHITE")
        self.chat_display_timer = pygame.time.get_ticks()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(120)
            self.events()
            self.update()
            self.draw()
            self.AI_1.run()
            self.AI_2.run()

    def events(self):
        mouse_pos = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # USER PRESSED A KEY
            if event.type == pygame.KEYDOWN:
                # chat mode
                if self.is_chat_activated:
                    # if escape, we leave chat and clear what was written
                    if event.key == pygame.K_ESCAPE:
                        self.is_chat_activated = False

                    # if pressing backspace, we have to remote the last character of the message
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_text = self.chat_text[:-1]

                    # if press enter again, we display the message, do some stuff if cheatcode, and disable chat
                    elif event.key == pygame.K_RETURN:
                        self.display_msg_flag = True
                        self.is_chat_activated = False
                        if self.chat_text == "PICSOU":
                            MAIN_PLAYER.update_resource("WOOD", 10000)
                            MAIN_PLAYER.update_resource("FOOD", 10000)
                            MAIN_PLAYER.update_resource("GOLD", 10000)
                            MAIN_PLAYER.update_resource("STONE", 10000)
                            self.chat_text = "CHEAT CODE ACTIVATED : PICSOU"

                    # we store the letter
                    else:
                        self.chat_text += event.unicode

                # else if chat is not activated
                else:
                    if event.key == pygame.K_ESCAPE:
                        # Quit game if chat wasnt activated
                        pygame.quit()
                        sys.exit()

                    # Enable - Disable health bars
                    elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                        global ENABLE_HEALTH_BARS
                        ENABLE_HEALTH_BARS = not ENABLE_HEALTH_BARS

                    # if enter button is pressed, chat stuff happens (for cheatcodes)
                    elif event.key == pygame.K_RETURN and self.chat_enabled:
                        self.is_chat_activated = True

            # USER PRESSED A MOUSEBUTTON
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # the player left click to train a villager or build a building
                if event.button == 1 and self.hud.bottom_left_menu is not None:

                    #to have informations about the villager
                    if self.map.hud.examined_tile is not None and self.map.hud.examined_tile.name == "Villager":
                        villager_pos = self.map.hud.examined_tile.pos
                        this_villager = self.map.units[villager_pos[0]][villager_pos[1]]
                        #("Info about villager, print is in game, events")
                        #this_villager.print_state()

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
                    if 0 <= grid_pos[0] <= self.map.grid_length_x and 0 <= grid_pos[1] <= self.map.grid_length_y:

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

                            # ONLY MOVEMENT
                            if not self.map.map[grid_pos[0]][grid_pos[1]]["collision"] and \
                                    not this_villager.is_gathering and this_villager.targeted_ressource is None and \
                                    not this_villager.is_attacking:
                                this_villager.move_to(self.map.map[grid_pos[0]][grid_pos[1]])

                            # we check if the tile we right click on is a ressource and if its on an adjacent tile of
                            # the villager pos, and if the villager isnt moving if the tile next to him is a ressource
                            # and we right click on it and he is not moving, he will gather it
                            if not this_villager.searching_for_path \
                                    and (self.map.map[pos_x][pos_y]["tile"] in ["tree", "rock", "gold", "berrybush"])\
                                    and this_villager.gathered_ressource_stack < this_villager.stack_max and \
                                    (this_villager.stack_type is None or
                                     this_villager.stack_type == self.map.map[pos_x][pos_y]["tile"]):

                                this_villager.go_to_ressource((pos_x, pos_y))

                            if this_villager.gathered_ressource_stack >= this_villager.stack_max:
                                this_villager.go_to_townhall()

    def update(self):
        self.camera.update()
        self.hud.update(self.screen)
        self.map.update(self.camera, self.screen)
        for an_entity in self.entities:
            an_entity.update()


    # GAME DISPLAY
    def draw(self):
        now = pygame.time.get_ticks()
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
        # chat

        txt_surface = chatFont.render(self.chat_text, True, get_color_code("RED"))
        # Resize the box if the text is too long.
        if self.is_chat_activated:
            width = max(200, txt_surface.get_width() + 10)
            self.input_box.w = width
            # Blit the input_box rect outside.
            pygame.draw.rect(self.screen, get_color_code("GOLD"), self.input_box, 2)
            self.chat_surface = pygame.Surface((width, 44), pygame.SRCALPHA)
            self.chat_surface.fill(self.chat_color)
            self.chat_rect = self.chat_surface.get_rect(topleft=(0, 0))
            # display grey rectangle
            self.screen.blit(self.chat_surface, (self.input_box.x, self.input_box.y + 1))

            # Blit the text.
            self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))

        # message written and pressed enter again, it displays a message on the screen for a few seconds
        if self.display_msg_flag:
            self.chat_enabled = False
            draw_text(self.screen, self.chat_text, 30, get_color_code("WHITE"), (10, 130))
            # if message has been displayed more than 5 secs, we make it disappear
            if now - self.chat_display_timer > 5000:
                self.display_msg_flag = False
                self.chat_text = ""
                self.chat_display_timer = now
                self.chat_enabled = True

        #Boom animation
        #Draw FPS, must be the last to shown -> put it right on top of the display.flip
        draw_text(self.screen,'fps={}'.format(round(self.clock.get_fps())),20,(255,0,0),(5,55))
        pygame.display.flip()
