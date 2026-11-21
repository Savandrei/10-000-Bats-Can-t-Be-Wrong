import random
import pygame
from .base_enemy import BaseEnemy
from .batling import Batling

class Plaguewing(BaseEnemy):
	def __init__(self, pos, target_player, all_sprites=None, pickup_group=None):
		super().__init__(
			pos=pos,
			target_player=target_player,
			speed=135,
			health=85,
			damage=14,
			color=(95, 175, 85),
			size=(32, 32),
			exp_value=12,
			all_sprites=all_sprites,
			pickup_group=pickup_group,
		)

		frames = self.load_sprite_sheet(
			"assets/images/plaguewing.png", 32, 32, columns=4, rows=4
		)
		self.animations = {
			"down": frames[0:4],
			"up": frames[4:8],
			"left": frames[8:12],
			"right": frames[12:16],
		}

		# frame animation default state
		self.facing = "down"
		self.frame_index = 0
		self.frame_timer = 0.0
		self.image = self.animations[self.facing][self.frame_index]
		self.rect = self.image.get_rect(center=self.rect.center)

	def update(self, dt, *args, **kwargs):
		super().update(dt, *args, **kwargs)

		direction = pygame.math.Vector2(self.target.rect.center) - self.pos
		# determine which way it should face
		if direction.length_squared() > 0:
			if abs(direction.x) > abs(direction.y):
				if direction.x > 0:
					self.facing = "right"
				else:
					self.facing = "left"
			else:
				if direction.y > 0:
					self.facing = "down"
				else:
					self.facing = "up"

		self.frame_timer += dt
		while self.frame_timer >= 0.12:
			self.frame_timer -= 0.12
			self.frame_index = (self.frame_index + 1) % 4

		self.image = self.animations[self.facing][self.frame_index]
		self.rect = self.image.get_rect(center=self.rect.center)

	def take_damage(self, amount):
		if not self.alive():
			return

		# check if it will die
		will_die = (self.health - amount) <= 0
		active_groups = self.groups()
		spawn_center = pygame.math.Vector2(self.rect.center)

		super().take_damage(amount)

		# if it dies, spawn 2 Batlings
		if will_die:
			for i in range(2):
				offset = pygame.math.Vector2(
					random.uniform(-14, 14),
					random.uniform(-14, 14),
				)
				batling = Batling(
					pos=spawn_center + offset,
					target_player=self.target,
					all_sprites=self.all_sprites,
					pickup_group=self.pickup_group,
				)
				for group in active_groups:
					group.add(batling)