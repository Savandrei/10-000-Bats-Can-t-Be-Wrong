import pygame
from src.entites.pickup import Exp_gem

class CollisionManager:

	def __init__(self, player, all_sprites, enemy_group, projectile_group, pickup_group):
		self.player = player
		self.all_sprites = all_sprites
		self.enemy_group = enemy_group
		self.projectile_group = projectile_group
		self.pickup_group = pickup_group

	def update(self):
		self.handle_combat_collisions()
		self.handle_pickups()

	def handle_combat_collisions(self):
		# projectiles vs enemies
		# returns a dict: {Projectile: [hit_Enemy_1, hit_Enemy_2, ...]}
		hits = pygame.sprite.groupcollide(self.projectile_group, self.enemy_group, False, False)

		for bullet, hit_enemies in hits.items():
			for enemy in hit_enemies:
				# deal damage to the enemy
				enemy.take_damage(bullet.damage)

				# reduce bullet pierce count
				bullet.hit_enemy()

				# if the bullet was destroyed (pierce depleted), stop checking it against others
				if not bullet.alive():
					break

		# enemies and player
		if not self.player.is_invincible:
			collided_enemies = pygame.sprite.spritecollide(self.player, self.enemy_group, False)

			for enemy in collided_enemies:
				self.player.take_damage(enemy.damage)

	def handle_pickups(self):
		collected_gems = pygame.sprite.spritecollide(self.player, self.pickup_group, True)
		for gem in collected_gems:
			self.player.gain_exp(gem.exp_value)