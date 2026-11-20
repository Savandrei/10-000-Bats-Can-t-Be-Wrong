import pygame

class Bullet(pygame.sprite.Sprite):
	def __init__(self, pos, direction):
		super().__init__()

		self.speed = 600
		self.damage = 15
		self.pierce = 1
		self.lifetime = 120
		self.color = (210, 215, 225) # Metallic silver
		size = (44, 18)

		self.image = pygame.Surface(size, pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=pos)
		self.pos = pygame.math.Vector2(pos)
		self.direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(1, 0)

		# --- Draw Silver Bullet (pointing right) ---
		# 1. Dark metallic outline/shadow base
		outline_points = [(2, 2), (28, 2), (43, 9), (28, 16), (2, 16)]
		pygame.draw.polygon(self.image, (60, 65, 75), outline_points)

		# 2. Main silver body and pointed tip
		body_points = [(4, 4), (27, 4), (40, 9), (27, 14), (4, 14)]
		pygame.draw.polygon(self.image, self.color, body_points)

		# 3. Specular highlight along the upper half for a 3D metallic shine
		highlight_points = [(5, 5), (27, 5), (37, 8), (27, 8), (5, 8)]
		pygame.draw.polygon(self.image, (245, 248, 255), highlight_points)

		# 4. Crimp/groove line separating the casing from the pointed head
		pygame.draw.line(self.image, (120, 125, 135), (24, 3), (24, 14), 2)

		# 5. Rim at the very back of the bullet
		pygame.draw.rect(self.image, (160, 165, 175), (2, 3, 3, 12))

		# Rotation
		if self.direction.length() > 0:
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