import pygame
import random
import math


class SlashLine:
	"""Individual line segment inside the AoE sphere."""
	def __init__(self, local_center, max_radius, primary_color):
		cx_local, cy_local = local_center
		
		# Pick a random midpoint inside radius
		r = random.uniform(0, max_radius * 0.85)
		angle = random.uniform(0, math.tau)
		cx = cx_local + r * math.cos(angle)
		cy = cy_local + r * math.sin(angle)

		# Random angle and line length
		slash_angle = random.uniform(0, math.pi)
		length = random.uniform(max_radius * 0.7, max_radius * 1.3)

		dx = (length / 2) * math.cos(slash_angle)
		dy = (length / 2) * math.sin(slash_angle)

		self.p1 = (cx - dx, cy - dy)
		self.p2 = (cx + dx, cy + dy)
		
		self.lifetime = random.uniform(0.08, 0.2)
		self.max_lifetime = self.lifetime
		self.primary_color = primary_color
		self.width = random.randint(2, 4)

	def update(self, dt):
		self.lifetime -= dt
		return self.lifetime > 0

	def draw(self, surface):
		fade_ratio = max(0, self.lifetime / self.max_lifetime)
		r, g, b = self.primary_color
		glow_color = (int(r * fade_ratio), int(g * fade_ratio), int(b * fade_ratio))
		core_color = (int(255 * fade_ratio), int(255 * fade_ratio), int(255 * fade_ratio))

		# Outer glow & bright core
		pygame.draw.line(surface, glow_color, self.p1, self.p2, self.width + 3)
		pygame.draw.line(surface, core_color, self.p1, self.p2, max(1, self.width - 1))


class JudgementCutArea(pygame.sprite.Sprite):
	"""AoE slash sphere entity compatible with Pygame Sprite Groups."""
	def __init__(self, pos, radius=110, duration=0.8, damage=15, color = (0, 180, 255)):
		super().__init__()
		self.radius = radius
		self.duration = duration
		self.timer = duration
		self.damage = damage
		self.pierce = 1000

		self.color = color

		size = radius * 2 + 40
		self.image = pygame.Surface((size, size), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=pos)
		self.center_local = (size // 2, size // 2)

		# 1. Create a circular mask surface (white inside circle, transparent outside)
		self.mask_surf = pygame.Surface((size, size), pygame.SRCALPHA)
		pygame.draw.circle(self.mask_surf, (255, 255, 255, 255), self.center_local, self.radius)

		self.slashes = []
		self.spawn_timer = 0
		self.spawn_interval = 0.015

	def update(self, dt=1/60, *args, **kwargs):
		self.timer -= dt
		self.spawn_timer -= dt

		# Spawn slashes while active
		if self.timer > 0 and self.spawn_timer <= 0:
			for _ in range(random.randint(2, 4)):
				self.slashes.append(SlashLine(self.center_local, self.radius, self.color))
			self.spawn_timer = self.spawn_interval

		# Update active slashes
		self.slashes = [s for s in self.slashes if s.update(dt)]

		# Clear main surface
		self.image.fill((0, 0, 0, 0))

		# 1. DRAW BLUE DOME BACKGROUND FIRST
		# Fades smoothly while active, retains slight glow while trailing slashes finish
		if self.timer > 0 or len(self.slashes) > 0:
			life_ratio = max(0.0, 2 * self.timer / self.duration) if self.timer > 0 else 0.15
			alpha = int(25 * life_ratio)
			r, g, b = self.color

			# Fill & boundary line drawn UNDER slashes
			pygame.draw.circle(self.image, (r, g, b, alpha // 3), self.center_local, self.radius)
			pygame.draw.circle(self.image, (r, g, b, alpha), self.center_local, self.radius, 2)

		# 2. DRAW SLASHES ON TOP OF THE DOME
		if self.slashes:
			slash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
			for slash in self.slashes:
				slash.draw(slash_surf)

			# Clip slashes at circle edge
			slash_surf.blit(self.mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

			# Blit clipped slashes ON TOP of the blue background
			self.image.blit(slash_surf, (0, 0))

		# 3. DESTROY SPRITE WHEN EVERYTHING FINISHES
		if self.timer <= 0 and len(self.slashes) == 0:
			self.kill()

	def hit_enemy(self):
		self.pierce -= 1
		if self.pierce <= 0:
			self.kill()