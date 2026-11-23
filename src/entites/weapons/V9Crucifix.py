import math
import pygame
from .base_weapon import BaseWeapon
from src.entites.projectiles.crucifix_sentry import CrucifixSentry


class V9Crucifix(BaseWeapon):
	def __init__(self, player):
		super().__init__(player, cooldown=14.0, projectile_number=1)
		self.name = "V-9 Crucifix"
		self.damage = 45
		self.sentry_duration = 12.0
		self.fire_interval = 0.05
		self.detection_range = 520.0
		self.angular_range = 260.0
		self.pierce = 3

	def attack(self, all_sprites, projectile_group, sorted_enemies):
		origin = pygame.math.Vector2(self.player.pos)
		count = max(1, int(getattr(self, "projectile_number", 1)))

		for i in range(count):
			if count == 1:
				spawn_pos = origin
			else:
				angle = (2 * math.pi / count) * i
				offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 42
				spawn_pos = origin + offset

			sentry = CrucifixSentry(
				pos=spawn_pos,
				damage=self.damage,
				fire_interval=self.fire_interval,
				duration=self.sentry_duration,
				detection_range=self.detection_range,
				angular_range=self.angular_range,
				pierce=self.pierce,
			)
			all_sprites.add(sentry)