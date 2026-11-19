import math
import random
import pygame


class IncenseAuraEffect(pygame.sprite.Sprite):
	def __init__(self, owner, radius=110):
		super().__init__()
		self.owner = owner
		self.radius = radius
		self.timer = 0.0
		self.pulse_timer = 0.0
		self.last_owner_pos = pygame.math.Vector2(self.owner.rect.center)

		self.padding = 16
		self.surface_size = (
			(self.radius + self.padding) * 2,
			(self.radius + self.padding) * 2,
		)
		self.image = pygame.Surface(self.surface_size, pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=self.owner.rect.center)

		# Pre-generate 3 distinct, compact smoke textures
		self.textures = self._generate_smoke_textures()
		self.particles = [self._spawn_particle(random_progress=True) for _ in range(30)]

	def _generate_smoke_textures(self):
		"""Creates three distinct small smoke shapes: ribbons, curls, and wispy streaks."""
		textures = {"ribbon": [], "curl": [], "streak": []}

		# 1. Wavy vertical incense ribbons (S-curve filaments)
		for _ in range(3):
			low = pygame.Surface((20, 36), pygame.SRCALPHA)
			freq = random.uniform(4.5, 6.5)
			phase = random.uniform(0, math.tau)
			for step in range(14):
				t = step / 13.0
				# Taper alpha at top and bottom ends
				end_fade = math.sin(t * math.pi)
				alpha = int(155 * end_fade)
				x = 10 + math.sin(phase + t * freq) * 4.5
				y = 32 - t * 28
				r = 2 if step % 3 == 0 else 3
				pygame.draw.circle(low, (238, 238, 245, alpha), (int(x), int(y)), r)
			textures["ribbon"].append(pygame.transform.smoothscale(low, (32, 56)))

		# 2. Compact curling smoke swirls (C-shaped / comma spirals)
		for _ in range(3):
			low = pygame.Surface((28, 28), pygame.SRCALPHA)
			start_angle = random.uniform(0, math.tau)
			arc_len = random.uniform(3.2, 4.6)
			for step in range(14):
				t = step / 13.0
				ang = start_angle + t * arc_len
				rad = 3.0 + t * 6.5
				x = 14 + math.cos(ang) * rad
				y = 14 + math.sin(ang) * rad
				alpha = int(145 * math.sin(t * math.pi))
				size = max(1, int(3.2 * (1.0 - t * 0.45)))
				pygame.draw.circle(low, (225, 225, 235, alpha), (int(x), int(y)), size)
			textures["curl"].append(pygame.transform.smoothscale(low, (42, 42)))

		# 3. Tight horizontal vapor streaks
		for _ in range(3):
			low = pygame.Surface((32, 16), pygame.SRCALPHA)
			for _ in range(4):
				bx = random.randint(7, 24)
				by = random.randint(6, 10)
				rx = random.randint(4, 7)
				ry = random.randint(2, 3)
				pygame.draw.ellipse(
					low, (215, 215, 225, 95), (bx - rx, by - ry, rx * 2, ry * 2)
				)
			textures["streak"].append(pygame.transform.smoothscale(low, (48, 24)))

		return textures

	def _spawn_particle(self, random_progress=False):
		kind = random.choices(
			["ribbon", "curl", "streak"],
			weights=[0.4, 0.35, 0.25],
		)[0]

		angle = random.uniform(0, math.tau)
		# Distribute evenly inside the circle area using sqrt
		spawn_dist = math.sqrt(random.random()) * (self.radius * 0.78)
		max_age = random.uniform(1.1, 2.0)
		age = random.uniform(0, max_age) if random_progress else 0.0

		if kind == "ribbon":
			vx = random.uniform(-5.0, 5.0)
			vy = random.uniform(-22.0, -12.0)  # Rises upward like stick incense
			rot = random.uniform(-12.0, 12.0)
			rot_speed = random.uniform(-18.0, 18.0)
			scale = random.uniform(0.45, 0.72)
			max_alpha = random.randint(135, 185)
		elif kind == "curl":
			vx = math.cos(angle) * random.uniform(4.0, 12.0)
			vy = math.sin(angle) * random.uniform(4.0, 12.0) - 8.0
			rot = random.uniform(0, 360)
			rot_speed = random.choice([-1, 1]) * random.uniform(45.0, 95.0)
			scale = random.uniform(0.42, 0.68)
			max_alpha = random.randint(125, 175)
		else:  # streak
			vx = random.choice([-1, 1]) * random.uniform(8.0, 16.0)
			vy = random.uniform(-10.0, -4.0)
			rot = random.uniform(-15.0, 15.0)
			rot_speed = random.uniform(-10.0, 10.0)
			scale = random.uniform(0.45, 0.75)
			max_alpha = random.randint(115, 160)

		return {
			"kind": kind,
			"x": math.cos(angle) * spawn_dist,
			"y": math.sin(angle) * spawn_dist,
			"vx": vx,
			"vy": vy,
			"rot": rot,
			"rot_speed": rot_speed,
			"sway_phase": random.uniform(0, math.tau),
			"scale": scale,
			"max_alpha": max_alpha,
			"age": age,
			"max_age": max_age,
			"tex": random.choice(self.textures[kind]),
		}

	def trigger_pulse(self):
		"""Subtly pulses the outline and fill when damage ticks."""
		self.pulse_timer = 1.0

	def set_radius(self, new_radius):
		if new_radius != self.radius:
			self.radius = new_radius
			self.surface_size = (
				(self.radius + self.padding) * 2,
				(self.radius + self.padding) * 2,
			)
			self.image = pygame.Surface(self.surface_size, pygame.SRCALPHA)
			self.rect = self.image.get_rect(center=self.owner.rect.center)

	def update(self, dt, *args, **kwargs):
		if not self.owner.alive():
			self.kill()
			return

		self.timer += dt
		if self.pulse_timer > 0:
			self.pulse_timer = max(0.0, self.pulse_timer - dt * 4.0)

		current_pos = pygame.math.Vector2(self.owner.rect.center)
		move_delta = current_pos - self.last_owner_pos
		self.last_owner_pos = current_pos

		self.rect.center = self.owner.rect.center
		self._update_and_draw(dt, move_delta)

	def _draw_zone_circle(self, cx, cy):
		"""Draws the transparent grey zone fill and crisp outer boundary."""
		fill_alpha = int(42 + 14 * self.pulse_timer)
		outline_alpha = int(145 + 75 * self.pulse_timer)
		inner_alpha = int(55 + 35 * self.pulse_timer)

		# Transparent grey fill
		pygame.draw.circle(
			self.image,
			(130, 130, 138, fill_alpha),
			(cx, cy),
			int(self.radius),
		)

		# Crisp outer border at exact damage radius
		pygame.draw.circle(
			self.image,
			(220, 220, 228, outline_alpha),
			(cx, cy),
			int(self.radius),
			2,
		)

		# Subtle inner ring
		if self.radius > 10:
			pygame.draw.circle(
				self.image,
				(200, 200, 208, inner_alpha),
				(cx, cy),
				int(self.radius - 4),
				1,
			)

	def _update_and_draw(self, dt, move_delta):
		self.image.fill((0, 0, 0, 0))
		cx = self.surface_size[0] // 2
		cy = self.surface_size[1] // 2

		# 1. Draw the grey transparent circle and crisp outline first
		self._draw_zone_circle(cx, cy)

		# 2. Update and draw small, distinct smoke effects inside the zone
		surviving = []
		max_inner_r = self.radius * 0.86

		for p in self.particles:
			p["age"] += dt
			if p["age"] >= p["max_age"]:
				surviving.append(self._spawn_particle(random_progress=False))
				continue

			# Slight lag when player moves
			p["x"] -= move_delta.x * 0.45
			p["y"] -= move_delta.y * 0.45

			sway = math.sin(self.timer * 3.2 + p["sway_phase"]) * 10.0
			p["x"] += (p["vx"] + sway) * dt
			p["y"] += p["vy"] * dt
			p["rot"] += p["rot_speed"] * dt

			# Fade smoothly before touching the outer circle border
			dist = math.hypot(p["x"], p["y"])
			if dist > max_inner_r:
				surviving.append(self._spawn_particle(random_progress=False))
				continue

			border_fade = 1.0
			if dist > self.radius * 0.65:
				border_fade = max(
					0.0, 1.0 - (dist - self.radius * 0.65) / (max_inner_r - self.radius * 0.65)
				)

			life = p["age"] / p["max_age"]
			if life < 0.22:
				life_fade = life / 0.22
			else:
				life_fade = (1.0 - (life - 0.22) / 0.78) ** 1.3

			alpha = int(p["max_alpha"] * life_fade * border_fade)
			if alpha <= 2:
				surviving.append(p)
				continue

			current_scale = p["scale"] * (0.85 + 0.3 * life)
			sprite = pygame.transform.rotozoom(p["tex"], p["rot"], current_scale)
			sprite.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)

			draw_x = int(cx + p["x"] - sprite.get_width() // 2)
			draw_y = int(cy + p["y"] - sprite.get_height() // 2)
			self.image.blit(sprite, (draw_x, draw_y))
			surviving.append(p)

		self.particles = surviving