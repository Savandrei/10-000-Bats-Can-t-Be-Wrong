import random
import pygame
from src.entites.enemies import Bat, Zombie, Slime

class Spawner:
	# spawns off-screen at set intervals
	def __init__(self, all_sprites, enemy_group, pickup_group, target_player):
		self.all_sprites = all_sprites
		self.enemy_group = enemy_group
		self.pickup_group = pickup_group
		self.target = target_player

		# timing and progression
		self.timer = 0
		self.spawn_interval = 0.15  # seconds

	def get_perimeter_pos(self):
		screen_width, screen_height = pygame.display.get_surface().get_size()
		# calculates a random coordinate outside the screen boundaries
		side = random.choice(["top", "bottom", "left", "right"])
		offset = 50

		if side == "top":
			return random.randint(0, screen_width), -offset
		elif side == "bottom":
			return random.randint(0, screen_width), screen_height + offset
		elif side == "left":
			return -offset, random.randint(0, screen_height)
		else: # right
			return screen_width + offset, random.randint(0, screen_height)

	def update(self, dt):
		# ticks the spawn timer and creates enemies
		self.timer += dt

		if self.timer >= self.spawn_interval:
			self.timer = 0
			pos = self.get_perimeter_pos()

			# for now, random choice
			enemy_class = random.choices([Bat, Zombie, Slime], weights=[50, 30, 20])[0]

			# instantiate the chosen enemy and add to groups
			enemy = enemy_class(pos = pos, target_player = self.target, all_sprites = self.all_sprites, pickup_group = self.pickup_group,)
			self.all_sprites.add(enemy)
			self.enemy_group.add(enemy)
