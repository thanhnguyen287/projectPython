import pygame

pygame.init()

set_index = 0
frame_set_start = set_index*1
frame_set_end = frame_set_start+9

speed = 0
dwell = 8 #number frames to spend on each image

move_up, move_left, move_down, move_right = 350,170, 390,  570
idle_up, idle_left, idle_down,  idle_right = 100, 121, 139, 320
attack_up,attack_left, attack_down, attack_right = 0, 19, 40, 219
die = 50



class AnimatedSprite:
    def __init__(self, screen, x, y, frames):
        self.screen = screen
        self.x = x
        self.y = y
        self.index = 0
        self.frames = frames
        self.rect = self.frames[self.index].get_rect()
        self.dwell_countdown = dwell

    def advanceImage(self):
        self.dwell_countdown -= 1
        if self.dwell_countdown < 0:
            self.dwell_countdown = dwell
            self.index = (self.index+1)%(frame_set_end+1)
            if self.index<frame_set_start:
                self.index = frame_set_start
            #print(self.index)

    def draw(self):
        self.screen.blit(self.frames[self.index],
                     ( int(self.x-self.rect.width/2),
                       int(self.y-self.rect.height/2) ))



def strip_from_sheet():
    '''Strips individual frames from specific sprite sheet.'''
    sheet = pygame.image.load('C:\\Users\\MS\\Desktop\\study stuff\\3A\\Projet AOE\\Test2.0\\resources\\units\\scout.png' ).convert()

    r = sheet.get_rect()
    rows = 4
    columns = 50
    img_width = r.width/columns
    img_height = r.height/rows

    frames = []
    for row in range(rows):
        for col in range(columns):
            rect = pygame.Rect(col * img_width, row * img_height, img_width, img_height)
            frames.append(sheet.subsurface(rect))

        # Now load all the images also facing the other direction
    for row in range(rows):
        for col in range(columns):
            rect = pygame.Rect(col * img_width, row * img_height, img_width, img_height)
            frames.append(pygame.transform.flip(sheet.subsurface(rect), True, False))

    return frames


clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))

frames = strip_from_sheet()

dimensions = frames[0].get_rect()
#Reminder: this is how you resize the image if you want.
scaling = 1
dimensions = (int(dimensions.w*scaling),int(dimensions.h*scaling))
for i in range(len(frames)):
    frames[i] = pygame.transform.scale( frames[i], dimensions)

sprite = AnimatedSprite(screen, 400, 300, frames)


#TODO TESTING
image = pygame.image.load('C:\\Users\\MS\\Desktop\\study stuff\\3A\\Projet AOE\\Test2.0\\resources\\units\\scout.png' )
rect = pygame.Rect(0,0,8,8)
random_image = image.subsurface(rect)




#Draw all images on the screen
done = False
while not done:
    #Detect held down keys:
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT]:
        sprite.x-=speed
    if pressed[pygame.K_RIGHT]:
        sprite.x+=speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            #print(event.key) #Print value of key press
            if event.key == pygame.K_ESCAPE:
                done = True
            # elif event.key == pygame.K_RIGHT:
            #     set_index = move_right
            elif event.key == pygame.K_LEFT:
                set_index = move_left
            elif event.key == pygame.K_UP:
                set_index = move_up
            elif event.key == pygame.K_DOWN:
                set_index = move_down
            elif event.key == pygame.K_w:
                set_index = attack_up
            elif event.key == pygame.K_s:
                set_index = attack_down
            elif event.key == pygame.K_a:
                set_index = attack_left
            elif event.key == pygame.K_d:
                set_index = attack_right
            elif event.key == pygame.K_DELETE:
                set_index = die

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                set_index = idle_left
            elif event.key == pygame.K_RIGHT:
                set_index = idle_right
            elif event.key == pygame.K_UP:
                set_index = idle_up
            elif event.key == pygame.K_DOWN:
                set_index = idle_down
        #Since set index has usually just been adjusted,
        #update the frame starts and ends.
        frame_set_start = set_index*1
        frame_set_end = frame_set_start+9

    screen.fill((0,0,0)) #fill screen with black
    sprite.draw()
    sprite.advanceImage()

    #TODO TESTING
    screen.blit(random_image, (0,0))

    pygame.display.flip()
    #Delay to get 30 fps
    clock.tick(60)
pygame.quit()