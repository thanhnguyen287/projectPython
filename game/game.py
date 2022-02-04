from .camera import Camera
from .map import *
from .utils import draw_text, find_owner, IA_MODE
from .hud import Hud
from .animation import *
#from .AI import AI
from.new_AI import new_AI
from time import sleep


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
        self.camera = Camera(self.width, self.height, self.map)
        self.hud.camera = self.camera

        self.timer = self.map.timer


        # on centre la camera au milieu de la carte
        #th_x = self.map.place_x
        th_x = 25
        #th_y = self.map.place_y
        th_y = 25
        cam_x = (iso_to_decarte(th_x*64, th_y*32)[0]) - 4050
        cam_y = (iso_to_decarte(th_x*64, th_y*32)[1]) - 1200
        self.camera.scroll = pygame.Vector2(cam_x, cam_y)

        # IA
        if IA_MODE:
            # we chose a behaviour between all the behaviours we defined
            self.behaviour_possible = ["neutral", "defensive", "aggressive", "pacifist"]

            if TEST_MODE or MAIN_PLAYER != playerOne:
                self.AI_1 = new_AI(playerOne, self.map, self.behaviour_possible[2])

            if TEST_MODE or MAIN_PLAYER != playerTwo:
                self.AI_2 = new_AI(playerTwo, self.map, self.behaviour_possible[0])

            if TEST_MODE or MAIN_PLAYER != playerThree:
                self.AI_3 = new_AI(playerThree, self.map, self.behaviour_possible[3])

        #defeated player
        self.defeated_player = None

        # chat
        self.chat_color = (40, 40, 40, 150)
        self.input_box = pygame.Rect(self.width // 2 - 70, self.height // 2 - 16, 140, 45)

        self.is_chat_activated = False
        self.chat_enabled = True
        self.display_msg_flag = False
        self.chat_text = ""
        self.chat_text_color = get_color_code("WHITE")
        self.chat_display_timer = pygame.time.get_ticks()

        self.victory = pygame.image.load("resources/assets/Images_for_in_game_menu_Oussama/Victory.png")
        self.defeat = pygame.image.load("resources/assets/Images_for_in_game_menu_Oussama/defeat.png")

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(120)
            self.events()
            self.update()
            self.draw()
            if IA_MODE:
                if TEST_MODE or MAIN_PLAYER != playerOne:
                    self.AI_1.run()

                if TEST_MODE or MAIN_PLAYER != playerTwo:
                    self.AI_2.run()

                if TEST_MODE or MAIN_PLAYER != playerThree:
                    self.AI_3.run()

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
                        elif self.chat_text == "BIGDADDY":
                            self.map.spawn_dragon(MAIN_PLAYER, self.camera)
                            self.chat_text = "CHEAT CODE ACTIVATED : BIGDADDY"
                        elif self.chat_text == "DESTROY":
                            for u in GENERAL_UNIT_LIST:
                                u.attack_dmg *= 5
                                u.max_health *= 10
                                u.current_health *= 10
                            self.chat_text = "CHEAT CODE ACTIVATED : DESTROY"



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

                #if we left click on the display tech tree button
                if event.button == 1:
                    if self.map.hud.tech_tree_rect.collidepoint(mouse_pos):
                        self.map.hud.tech_tree_display_flag = False if self.map.hud.tech_tree_display_flag else True

                # if we left click on the action panel and a building/unit is selected
                if self.hud.bottom_left_menu is not None and self.map.hud.examined_tile is not None:
                    entity = self.map.hud.examined_tile
                    # if the examined entity belongs to us (or we are in debug mode)
                    #if entity.owner == MAIN_PLAYER or TEST_MODE:
                    if True:
                        # for every button in action panel
                        for button in self.hud.bottom_left_menu:
                            #if the button is pressed
                            if button["rect"].collidepoint(mouse_pos):
                                #STOP BUTTON
                                if button["name"] == "STOP":
                                    entity.owner.refund_entity_cost(entity.unit_type_currently_trained)
                                    entity.queue -= 1
                                    # no more units to create
                                    if entity.queue == 0:
                                        entity.is_working = False
                                        entity.unit_type_currently_trained = None
                                else:
                                    # we only do the actions corresponding to the button if player has enough resources/requirements are met
                                    if button["affordable"]:
                                        # if it was villager button, we train one
                                        if button["name"] == "Villager" and not self.hud.examined_tile.is_being_built:
                                            entity.train(Villager)
                                        elif button["name"] == "Clubman" and not self.hud.examined_tile.is_being_built:
                                            entity.train(Clubman)
                                        # if it was an advancement research, we... research it. Makes sense right ?
                                        elif button["name"] == "Advance to Feudal Age" \
                                                or button["name"] == "Advance to Castle Age"\
                                                or button["name"] == "Advance to Imperial Age" \
                                                or button["name"] == "Research Improved Masonry" \
                                                or button["name"] == "Research Reinforced Masonry" \
                                                or button["name"] == "Research Imbued Masonry" \
                                                or button["name"] == "Research Iron Swords" \
                                                or button["name"] == "Research Steel Swords" \
                                                or button["name"] == "Research Mithril Swords" \
                                                or button["name"] == "Research Iron Armors" \
                                                or button["name"] == "Research Steel Armors" \
                                                or button["name"] == "Research Mithril Armors" \
                                                or button["name"] == "Research Iron Arrows" \
                                                or button["name"] == "Research Iron Horseshoes" \
                                                or button["name"] == "Research Super Cows":
                                            entity.research_tech(button["name"])
                                        # else it is a building
                                        else:
                                            self.hud.selected_tile = button

                    #to have informations about the villager if he is selected
                    if type(entity) == Villager:
                        this_villager = self.map.units[entity.pos[0]][entity.pos[1]]
                        #("Info about villager, print is in game, events")
                        this_villager.print_state()

                #BOOM WHEN RIGHT CLICKING
                if event.button == 3:  # RIGHT CLICK
                    # right click, gathering and moving units (fighting in future)
                    grid_pos = self.map.mouse_to_grid(mouse_pos[0], mouse_pos[1], self.camera.scroll)
                    if 0 <= grid_pos[0] < self.map.grid_length_x and 0 <= grid_pos[1] < self.map.grid_length_y:

                        # There is a bug with collecting ressources on the side of the map !!!

                        if self.map.hud.examined_tile is not None and (self.map.hud.examined_tile.name == "Villager" or
                                                                       self.map.hud.examined_tile.name == "Clubman" or
                                                                       self.map.hud.examined_tile.name == "Black Dragon"):
                            villager_pos = self.map.hud.examined_tile.pos
                            this_villager = self.map.units[villager_pos[0]][villager_pos[1]]

                            print(this_villager.owner, MAIN_PLAYER)
                            if this_villager.owner == MAIN_PLAYER or TEST_MODE:
                                pos_mouse = self.map.mouse_to_grid(mouse_pos[0], mouse_pos[1], self.camera.scroll)
                                pos_x = pos_mouse[0]
                                pos_y = pos_mouse[1]
                                # ATTACK
                                if (self.map.units[pos_x][pos_y] is not None
                                    or self.map.buildings[pos_x][pos_y] is not None) \
                                        and not this_villager.owner == find_owner([pos_x, pos_y]):
                                    # attack !
                                    this_villager.go_to_attack((pos_x, pos_y))

                                # ONLY MOVEMENT
                                if isinstance(this_villager, Villager) and self.map.collision_matrix[grid_pos[1]][grid_pos[0]] and \
                                        not this_villager.is_gathering and this_villager.targeted_ressource is None and \
                                        not this_villager.is_attacking:
                                    this_villager.move_to(self.map.map[grid_pos[0]][grid_pos[1]])
                                elif isinstance(this_villager, Clubman) and self.map.collision_matrix[grid_pos[1]][grid_pos[0]] and \
                                        not this_villager.is_attacking:
                                    this_villager.move_to(self.map.map[grid_pos[0]][grid_pos[1]])
                                elif isinstance(this_villager, Dragon) and self.map.collision_matrix[grid_pos[1]][
                                    grid_pos[0]] and \
                                     not this_villager.is_attacking:
                                    this_villager.move_to(self.map.map[grid_pos[0]][grid_pos[1]])

                                # we check if the tile we right click on is a ressource and if its on an adjacent tile of
                                # the villager pos, and if the villager isnt moving if the tile next to him is a ressource
                                # and we right click on it and he is not moving, he will gather it
                                if isinstance(this_villager, Villager) and not this_villager.searching_for_path \
                                        and (self.map.map[pos_x][pos_y]["tile"] in ["tree", "rock", "gold", "berrybush"])\
                                        and this_villager.gathered_ressource_stack < this_villager.stack_max and \
                                        (this_villager.stack_type is None or
                                         this_villager.stack_type == self.map.map[pos_x][pos_y]["tile"]):

                                    this_villager.go_to_ressource((pos_x, pos_y))

                                if isinstance(this_villager, Villager) and this_villager.gathered_ressource_stack >= this_villager.stack_max \
                                        or (this_villager.owner.towncenter.pos[0] <= pos_x <=
                                        this_villager.owner.towncenter.pos[0]+1
                                            and this_villager.owner.towncenter.pos[1] <= pos_y <=
                                        this_villager.owner.towncenter.pos[1]-1):
                                    this_villager.go_to_townhall()


    def update(self):
        self.camera.update()
        self.hud.update(self.screen)
        self.map.update(self.camera, self.screen)
        for an_entity in self.entities:
            an_entity.update()

        for p in player_list:
            if p.towncenter is None:
                self.is_chat_activated = False
                self.display_msg_flag = True
                self.chat_text = str(p.name) + " has been defeated"

                player_list.remove(p)
                self.timer = self.map.timer
                self.defeated_player =  p

        time = pygame.time.get_ticks()
        if time - self.timer > 3000:
            if self.defeated_player is not None and self.defeated_player == MAIN_PLAYER:
                print("DEFEAT")
                self.screen.fill((0, 0, 0))
                pos_x = (self.width - self.defeat.get_width())/2
                pos_y = (self.height - self.defeat.get_height())/2

                pos_text_x = (self.width - self.defeat.get_width()*0.35)/2
                pos_text_y = (self.height - self.defeat.get_height()*0.2)/2

                self.screen.blit(self.defeat, (pos_x, pos_y))

                draw_text(self.screen, "DEFEAT", 110, get_color_code("DARK_GRAY"), (pos_text_x, pos_text_y))

                pygame.display.flip()
                sleep(3)

                pygame.quit()
                sys.exit()
            else:
                if len(player_list) == 1:
                    player_list[0].victory()
                    print("VICTORY")

                    self.screen.fill((0, 0, 0))
                    pos_x = (self.width - self.defeat.get_width()) / 2
                    pos_y = (self.height - self.defeat.get_height()) / 2

                    pos_text_x = (self.width - self.defeat.get_width() * 0.4) / 2
                    pos_text_y = (self.height - self.defeat.get_height() * 0.2) / 2

                    self.screen.blit(self.victory, (pos_x, pos_y))

                    draw_text(self.screen, "VICTORY", 110, get_color_code("GOLD"), (pos_text_x, pos_text_y))

                    pygame.display.flip()
                    sleep(3)

                    pygame.quit()
                    sys.exit()
                self.defeated_player = None


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

        #Draw FPS, must be the last to shown -> put it right on top of the display.flip
        draw_text(self.screen,'fps={}'.format(round(self.clock.get_fps())),20,(255,0,0),(5,55))
        pygame.display.flip()
