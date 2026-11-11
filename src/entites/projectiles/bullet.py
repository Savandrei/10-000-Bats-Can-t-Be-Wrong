import pygame

class Bullet(pygame.sprite.Sprite):
	def __init__(self, pos, direction):
		super().__init__()

		self.speed=600
		self.damage=15
		self.pierce=1
		self.lifetime=120
		self.color=(255, 220, 50)
		size=(40, 20)

		self.image = pygame.Surface(size, pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=pos)
		self.pos = pygame.math.Vector2(pos)
		self.direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(1, 0)

		# outer layer
		pygame.draw.rect(self.image, (0, 0, 0, 100), (0, 0, 40, 20))
		# inner layer(with color)
		pygame.draw.rect(self.image, (255, 220, 50), (5, 5, 30, 10))

		# rotation
		if self.direction != (0,0):
			# as_polar returns (length, angle_in_degrees)
			# pygame's Y-axis is inverted (0 is at the top)
			angle = -self.direction.as_polar()[1]
			self.image = pygame.transform.rotate(self.image, angle)
			self.rect = self.image.get_rect(center=self.rect.center)

		self.rotated_image = self.image.copy()

	def update(self, dt, *args, **kwargs):
		self.pos += self.direction * self.speed * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))

		self.image = self.rotated_image

		self.lifetime -= dt
		if self.lifetime <= 0:
			self.kill()

	def hit_enemy(self):
		self.pierce -= 1
		if self.pierce <= 0:
			self.kill()

