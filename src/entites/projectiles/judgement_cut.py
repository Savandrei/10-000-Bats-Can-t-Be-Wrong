import pygame
import random
import math


class DimensionalSlash:
	"""Razor-sharp tapered slash leaning toward a crisp white core with a vivid colored edge."""
	def __init__(self, local_center, max_radius, primary_color):
		cx_local, cy_local = local_center

		# Pick a random chord/midpoint inside the sphere
		r = random.uniform(0, max_radius * 0.78)
		angle = random.uniform(0, math.tau)
		cx = cx_local + r * math.cos(angle)
		cy = cy_local + r * math.sin(angle)

		self.angle = random.uniform(0, math.pi)
		length = random.uniform(max_radius * 0.9, max_radius * 1.65)

		self.dx = math.cos(self.angle)
		self.dy = math.sin(self.angle)
		half_len = length * 0.5

		self.p1 = (cx - self.dx * half_len, cy - self.dy * half_len)
		self.p2 = (cx + self.dx * half_len, cy + self.dy * half_len)
		self.mid = (cx, cy)

		# Perpendicular vector for diamond width
		self.px = -self.dy
		self.py = self.dx

		self.lifetime = random.uniform(0.09, 0.19)
		self.max_lifetime = self.lifetime
		self.primary_color = primary_color
		self.max_width = random.uniform(2.6, 4.6)

	def update(self, dt):
		self.lifetime -= dt
		return self.lifetime > 0

	def _make_diamond(self, mid, end, half_width):
		return [
			self.p1,
			(mid[0] + self.px * half_width, mid[1] + self.py * half_width),
			end,
			(mid[0] - self.px * half_width, mid[1] - self.py * half_width),
		]

	def draw(self, surface):
		progress = 1.0 - max(0.0, self.lifetime / self.max_lifetime)
		fade = max(0.0, self.lifetime / self.max_lifetime)

		# Rapidly extend from p1 to p2 in the first 20% of lifetime
		extend = min(1.0, progress / 0.20)
		curr_p2 = (
			self.p1[0] + (self.p2[0] - self.p1[0]) * extend,
			self.p1[1] + (self.p2[1] - self.p1[1]) * extend,
		)
		curr_mid = (
			(self.p1[0] + curr_p2[0]) * 0.5,
			(self.p1[1] + curr_p2[1]) * 0.5,
		)

		r, g, b = self.primary_color

		# Colored glow is slightly wider and lingers a touch longer than the white core
		glow_scale = fade ** 1.4
		core_scale = fade ** 1.75

		glow_w = max(1.0, self.max_width * 2.6 * glow_scale)
		core_w = max(0.6, self.max_width * 0.57 * core_scale)

		# 1. Rich primary-color outer blade
		glow_alpha = int(235 * fade)
		pygame.draw.polygon(
			surface,
			(r, g, b, glow_alpha),
			self._make_diamond(curr_mid, curr_p2, glow_w),
		)

		# 2. Dominant white-hot razor core with a subtle 10% primary tint
		core_color = (
			int(255 * 0.90 + r * 0.10),
			int(255 * 0.90 + g * 0.10),
			int(255 * 0.90 + b * 0.10),
			int(255 * min(1.0, fade * 1.35)),
		)
		pygame.draw.polygon(
			surface,
			core_color,
			self._make_diamond(curr_mid, curr_p2, core_w),
		)

		# 3. Sharp white pinpoint flash with a tight colored rim
		if progress < 0.25:
			spark_t = 1.0 - (progress / 0.25)
			center = (int(curr_mid[0]), int(curr_mid[1]))
			spark_r = int(4.5 * spark_t)
			if spark_r > 0:
				pygame.draw.circle(surface, (r, g, b, int(160 * spark_t)), center, spark_r + 2)
				pygame.draw.circle(surface, (255, 255, 255, int(235 * spark_t)), center, spark_r)


class JudgementCutArea(pygame.sprite.Sprite):
	"""DMC-style Judgement Cut AoE sphere with spatial background distortion."""
	def __init__(self, pos, radius=110, duration=0.75, damage=15, color=(0, 195, 255)):
		super().__init__()
		self.base_radius = radius
		self.duration = duration
		self.timer = duration
		self.damage = damage
		self.pierce = 1000
		self.color = color
		self.pos = pos

		self.size = radius * 2 + 40
		self.center_local = (self.size // 2, self.size // 2)

		# Pre-allocate reusable surfaces to avoid per-frame memory allocation
		self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=pos)

		self.mask_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		self.slash_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		self.distort_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		self.bg_capture = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

		self.slashes = []
		self.fracture_offsets = []  # Stores (y_start, height, shift_x, shift_y)
		self.spawn_timer = 0.0
		self.spawn_interval = 0.014

		# Spawn an immediate initial cross-slash so frame 1 hits hard
		for _ in range(3):
			self.slashes.append(DimensionalSlash(self.center_local, self.base_radius, self.color))
		self._regenerate_fractures()

	def _regenerate_fractures(self):
		"""Creates horizontal/band slice offsets to simulate reality being cut into shards."""
		self.fracture_offsets.clear()
		num_bands = random.randint(4, 7)
		band_h = self.size // num_bands
		for i in range(num_bands):
			shift_x = random.randint(-12, 12)
			shift_y = random.randint(-5, 5)
			self.fracture_offsets.append((i * band_h, band_h + 2, shift_x, shift_y))

	def _get_current_radius(self):
		"""3-phase envelope: rapid expansion -> full dome -> final snap implosion."""
		elapsed = self.duration - max(0.0, self.timer)
		progress = min(1.0, elapsed / self.duration)

		if progress < 0.10:
			# Fast burst open (0.2x -> 1.05x)
			t = progress / 0.10
			scale = 0.2 + 0.85 * (1.0 - (1.0 - t) ** 3)
		elif progress > 0.88:
			# Final spatial snap inward (1.0x -> 0.05x)
			t = (progress - 0.88) / 0.12
			scale = max(0.05, 1.0 - (t ** 2) * 0.95)
		else:
			# Subtle high-tension vibration during the flurry
			scale = 1.0 + random.uniform(-0.02, 0.02)

		return max(4, int(self.base_radius * scale))

	def _build_distorted_background(self, bg_surface, current_radius):
		"""Captures the screen behind the sphere, zooms, fractures, and chromatic-shifts it."""
		self.bg_capture.fill((0, 0, 0, 0))
		self.distort_surf.fill((0, 0, 0, 0))

		# Safe blit even if sprite is partially off-screen
		self.bg_capture.blit(bg_surface, (-self.rect.x, -self.rect.y))

		# 1. Lens magnification inside the sphere (bends background geometry at the rim)
		zoom = 1.14
		zoomed_size = int(self.size * zoom)
		zoomed = pygame.transform.smoothscale(self.bg_capture, (zoomed_size, zoomed_size))
		offset = (self.size - zoomed_size) // 2
		self.distort_surf.blit(zoomed, (offset, offset))

		# 2. Slice and shift horizontal bands (the "shattered glass" spatial displacement)
		for y_start, band_h, sx, sy in self.fracture_offsets:
			band_rect = pygame.Rect(0, y_start, self.size, band_h)
			self.distort_surf.blit(zoomed, (offset + sx, offset + y_start + sy), area=band_rect)

		# 3. Subtle chromatic aberration (cyan/blue spatial tear)
		chroma = self.distort_surf.copy()
		chroma.fill((30, 120, 255, 255), special_flags=pygame.BLEND_RGB_MULT)
		self.distort_surf.blit(chroma, (4, -2), special_flags=pygame.BLEND_RGB_ADD)

		# 4. Clip distorted background to the current animated circle radius
		self.mask_surf.fill((0, 0, 0, 0))
		pygame.draw.circle(self.mask_surf, (255, 255, 255, 245), self.center_local, current_radius)
		self.distort_surf.blit(self.mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

		self.image.blit(self.distort_surf, (0, 0))

	def update(self, dt=1/60, bg_surface=None, *args, **kwargs):
		self.timer -= dt
		self.spawn_timer -= dt

		current_radius = self._get_current_radius()

		# Spawn slashes & refresh reality fracture offsets during active phase
		if self.timer > self.duration * 0.12 and self.spawn_timer <= 0:
			for _ in range(random.randint(2, 4)):
				self.slashes.append(DimensionalSlash(self.center_local, current_radius, self.color))
			if random.random() < 0.45:
				self._regenerate_fractures()
			self.spawn_timer = self.spawn_interval

		self.slashes = [s for s in self.slashes if s.update(dt)]
		self.image.fill((0, 0, 0, 0))

		if self.timer > 0 or len(self.slashes) > 0:
			# 1. BACKGROUND REFRACTION & FRACTURE (if screen/world surface is passed)
			if bg_surface is not None:
				self._build_distorted_background(bg_surface, current_radius)

			# 2. DEEP DIMENSIONAL VOID TINT & CRISP DOUBLE RIM
			life_ratio = max(0.0, min(1.0, self.timer / self.duration)) if self.timer > 0 else 0.15
			r, g, b = self.color

			# Dark indigo interior tint so white slashes pop dramatically
			void_alpha = int(95 * life_ratio)
			pygame.draw.circle(self.image, (8, 18, 48, void_alpha), self.center_local, current_radius)

			# Outer refraction ring + bright inner energy rim
			rim_alpha = int(220 * life_ratio)
			pygame.draw.circle(self.image, (r, g, b, rim_alpha // 2), self.center_local, current_radius, 4)
			pygame.draw.circle(self.image, (210, 245, 255, rim_alpha), self.center_local, max(1, current_radius - 1), 2)

		# 3. RAZOR-SHARP TAPERED SLASHES (Clipped to sphere)
		if self.slashes:
			self.slash_surf.fill((0, 0, 0, 0))
			for slash in self.slashes:
				slash.draw(self.slash_surf)

			self.mask_surf.fill((0, 0, 0, 0))
			pygame.draw.circle(self.mask_surf, (255, 255, 255, 255), self.center_local, current_radius)
			self.slash_surf.blit(self.mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

			self.image.blit(self.slash_surf, (0, 0))

		# 4. FINAL IMPLOSION FLASH RIGHT BEFORE END
		if 0 < self.timer <= self.duration * 0.12:
			flash_t = 1.0 - (self.timer / (self.duration * 0.12))
			flash_r = int(current_radius * (1.2 - flash_t * 0.8))
			if flash_r > 0:
				pygame.draw.circle(
					self.image,
					(220, 250, 255, int(180 * (1.0 - flash_t))),
					self.center_local,
					flash_r,
					2,
				)

		if self.timer <= 0 and len(self.slashes) == 0:
			self.kill()

	def hit_enemy(self):
		self.pierce -= 1
		if self.pierce <= 0:
			self.kill()