import pygame
from src.entites.weapons.base_weapon import BaseWeapon
from src.entites.projectiles.incense_aura import IncenseAuraEffect


class CenserAura(BaseWeapon):
	def __init__(self, player):
		super().__init__(player)
		self.name = "CenserAura"
		self.damage = 10
		self.radius = 300
		self.cooldown = 0.5
		self.knockback = 25

		self.aura_sprite = None

	def attack(self, all_sprites, projectile_group, sorted_enemies):
		if self.aura_sprite is None or not self.aura_sprite.alive():
			self.aura_sprite = IncenseAuraEffect(self.player, radius=self.radius)
			all_sprites.add(self.aura_sprite)

		self.aura_sprite.set_radius(self.radius)
		self.aura_sprite.trigger_pulse()

		player_pos = pygame.math.Vector2(self.player.rect.center)
		radius_sq = self.radius * self.radius

		for enemy in sorted_enemies:
			enemy_pos = pygame.math.Vector2(enemy.rect.center)
			offset = enemy_pos - player_pos
			dist_sq = offset.length_squared()

			if dist_sq <= radius_sq:
				if hasattr(enemy, "take_damage"):
					enemy.take_damage(self.damage)
				elif hasattr(enemy, "hp"):
					enemy.hp -= self.damage

				if self.knockback > 0 and dist_sq > 0 and hasattr(enemy, "pos"):
					enemy.pos += offset.normalize() * self.knockback * 0.1