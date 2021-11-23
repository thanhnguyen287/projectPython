import pygame, sys, os
import pygame.mouse

from settings import *
pygame.init()


class Animation(pygame.sprite.Sprite):

	def __init__(self, pos_x, pos_y):
		super().__init__()

		self.attack_animation = False
		self.sprites = []
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_0.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_1.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_2.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_3.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_4.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_5.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_6.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_7.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_8.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_9.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_10.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_11.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_12.png"))
		self.sprites.append(pygame.image.load("resources/assets/Boom/496_13.png"))


		#for i in range (14):
		#	self.sprites.append(pygame.image.load('"496_" + str(i)) '))

		self.current_sprite = 0
		self.image = self.sprites[self.current_sprite]

		self.rect = self.image.get_rect()
		self.rect.topleft = [pos_x,pos_y]

	def play(self):
		self.attack_animation = True


	def update(self,speed):
		if self.attack_animation:
			self.current_sprite += speed
			if int(self.current_sprite) >= len(self.sprites):
				self.current_sprite = 0
				self.attack_animation = False

		self.image = self.sprites[int(self.current_sprite)]


# Creating the sprites and groups


player = Animation(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
moving_sprites = pygame.sprite.Group()
moving_sprites.add(player)



