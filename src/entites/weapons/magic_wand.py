import pygame
from .base_weapon import BaseWeapon
from src.entites.projectiles import BlastVisual

class MagicWand(BaseWeapon):
	def __init__(self, player):
		super().__init__(player, cooldown=0.75) 
		self.damage = 25

	def attack(self, all_sprites, projectile_group, enemy_group):
		if not enemy_group:
			return

		# locate the closest enemy relative to the player
		closest_enemy = min(
			enemy_group.sprites(),
			key=lambda e: pygame.math.Vector2(self.player.rect.center).distance_to(e.rect.center)
		)

		closest_enemy.take_damage(self.damage)

		# calculate the firing trajectory
		direction = pygame.math.Vector2(closest_enemy.rect.center) - self.player.rect.center

		# spawn the bullet and assign it to the groups
		# bullet = Bullet(pos=self.player.rect.center, direction=direction)
		# all_sprites.add(bullet)
		# projectile_group.add(bullet)
		
		blast = BlastVisual(pos=closest_enemy.rect.center, radius=30)
		
		all_sprites.add(blast)
		# projectile_group.add(blast)