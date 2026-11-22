import pygame
from src.entites.pickup import Exp_gem
from src.managers.asset_loader import AssetLoader

class BaseEnemy(pygame.sprite.Sprite):
	def __init__(self, pos, target_player, speed, health, damage, size=(24, 24), exp_value=10, all_sprites = None, pickup_group = None):
		super().__init__()
		self.rect = pygame.Rect(0, 0, *size)
		self.rect.center = pos

		self.pos = pygame.math.Vector2(pos)
		self.target = target_player
		self.speed = speed
		self.health = health
		self.max_health = health
		self.damage = damage
		self.exp_value = exp_value
		self.all_sprites = all_sprites
		self.pickup_group = pickup_group

	@staticmethod
	def load_sprite_sheet(path, frame_width, frame_height, columns, rows):
		directional = AssetLoader.get_directional_frames(
			path,
			cols=columns,
			rows=rows,
			target_size=(frame_width, frame_height),
		)
		return [
			frame
			for direction in ("S", "N", "W", "E")
			for frame in directional[direction]
		]

	def update(self, dt, *args, **kwargs):
		# go towards the player
		target_pos = pygame.math.Vector2(self.target.rect.center)
		direction = target_pos - self.pos

		if direction.length_squared() > 0:
			self.pos += direction.normalize() * self.speed * dt
			self.rect.center = (round(self.pos.x), round(self.pos.y))

	def take_damage(self, amount):
		if not self.alive():
			return

		self.health -= amount
		if self.health <= 0:
			if self.all_sprites is not None and self.pickup_group is not None:
				gem = Exp_gem(
					pos=self.rect.center,
					target_player=self.target,
					exp_value=self.exp_value,
				)
				self.all_sprites.add(gem)
				self.pickup_group.add(gem)
			self.kill()
