import pygame

class BaseWeapon:
	def __init__(self, player, cooldown=0.75, projectile_number=1):
		self.player = player
		self.cooldown = cooldown
		self.timer = 0.0
		self.level = 1
		self.projectile_number = projectile_number
		self.pierce = 1

	def update(self, dt, all_sprites, projectile_group, sorted_enemies):
		self.timer += dt
		if self.timer >= self.cooldown:
			self.timer = 0.0
			self.attack(all_sprites, projectile_group, sorted_enemies)

	def attack(self, all_sprites, projectile_group, enemy_group):
		raise NotImplementedError("Implement the attack() function boss")

	def level_up(self):
		raise NotImplementedError("Implement the level_up() function boss")