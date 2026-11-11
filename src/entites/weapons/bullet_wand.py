import pygame
from .base_weapon import BaseWeapon
from src.entites.projectiles import Bullet

class BulletWand(BaseWeapon):
	# auto-fires a bullet/blast at the nearest enemy on a set cooldown
	def __init__(self, player):
		super().__init__(player, cooldown=1.75, projectile_number=20) 

	def attack(self, all_sprites, projectile_group, sorted_enemies):

		enemy_expected_dmg = 0

		for x in range(1, self.projectile_number):
			if not sorted_enemies:
				return
			closest_enemy = sorted_enemies[0]
			direction = pygame.math.Vector2(closest_enemy.rect.center) - self.player.rect.center
			bullet = Bullet(pos=self.player.rect.center, direction=direction)

			# bullet eficiency
			enemy_expected_dmg += bullet.damage
			if closest_enemy.health <= enemy_expected_dmg:
				sorted_enemies.pop(0)
				enemy_expected_dmg = 0

			all_sprites.add(bullet)
			projectile_group.add(bullet)
