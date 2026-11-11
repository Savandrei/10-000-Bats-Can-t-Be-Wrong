import pygame

class BaseEnemy(pygame.sprite.Sprite):
	def __init__(self, pos, target_player, speed, health, damage, color, size=(24, 24)):
		super().__init__()
		self.image = pygame.Surface(size, pygame.SRCALPHA)
		pygame.draw.circle(self.image, color, (size[0] // 2, size[1] // 2), size[0] // 2)
		self.rect = self.image.get_rect(center=pos)
		
		self.pos = pygame.math.Vector2(pos)
		self.target = target_player
		self.speed = speed
		self.health = health
		self.max_health = health
		self.damage = damage

	def update(self, dt, *args, **kwargs):
		# go towards the player
		target_pos = pygame.math.Vector2(self.target.rect.center)
		direction = target_pos - self.pos

		if direction.length_squared() > 0:
			self.pos += direction.normalize() * self.speed * dt
			self.rect.center = (round(self.pos.x), round(self.pos.y))

	def take_damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			self.kill()