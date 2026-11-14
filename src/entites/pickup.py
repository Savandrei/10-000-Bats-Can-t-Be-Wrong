import pygame

class Exp_gem(pygame.sprite.Sprite):
	def __init__(self, pos, target_player, exp_value=10, color=(0, 200, 255), size=(10, 10)):
		super().__init__()
		self.image = pygame.Surface(size, pygame.SRCALPHA)
		pygame.draw.circle(self.image, color, (size[0] // 2, size[1] // 2), size[0] // 2)
		self.rect = self.image.get_rect(center=pos)

		self.pos = pygame.math.Vector2(pos)
		self.target = target_player
		self.exp_value = exp_value

		self.magnet_radius = 100
		self.speed = 6.0

	def update(self, *args, **kwargs):
		# move towards the player if close enough
		target_pos = pygame.math.Vector2(self.target.rect.center)
		direction = target_pos - self.pos
		distance = direction.length()

		if 0 < distance <= self.magnet_radius:
			self.pos += direction.normalize() * self.speed
			self.rect.center = (round(self.pos.x), round(self.pos.y))
