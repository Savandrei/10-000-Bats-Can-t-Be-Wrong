import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
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
		# calculates a random coordinate outside the screen boundaries
		side = random.choice(["top", "bottom", "left", "right"])
		offset = 50  # spawn 50 pixels off-screen so they don't pop in

		if side == "top":
			return random.randint(0, SCREEN_WIDTH), -offset
		elif side == "bottom":
			return random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + offset
		elif side == "left":
			return -offset, random.randint(0, SCREEN_HEIGHT)
		else: # right
			return SCREEN_WIDTH + offset, random.randint(0, SCREEN_HEIGHT)

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
