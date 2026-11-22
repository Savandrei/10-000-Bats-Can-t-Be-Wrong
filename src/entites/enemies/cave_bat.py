import pygame
from .base_enemy import BaseEnemy

class CaveBat(BaseEnemy):
	def __init__(self, pos, target_player, all_sprites=None, pickup_group=None):
		super().__init__(
			pos=pos,
			target_player=target_player,
			speed=220,
			health=35,
			damage=8,
			size=(24, 24),
			exp_value=5,
			all_sprites=all_sprites,
			pickup_group=pickup_group,
		)

		frames = self.load_sprite_sheet(
			"assets/images/cave_bat.png", 24, 24, columns=4, rows=4
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