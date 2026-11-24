import math
import pygame


def _load_sound_safe(path, volume=0.6):
	try:
		sound = pygame.mixer.Sound(path)
		sound.set_volume(volume)
		return sound
	except (pygame.error, FileNotFoundError):
		return None


def _get_entity_pos(entity):
	if hasattr(entity, "pos"):
		return pygame.math.Vector2(entity.pos)
	return pygame.math.Vector2(entity.rect.center)


class WoodenStake(pygame.sprite.Sprite):
	def __init__(self, pos, angle_deg, damage=45, speed=780.0, pierce=3, lifetime=1.6):
		super().__init__()
		self.pos = pygame.math.Vector2(pos)
		self.angle_deg = angle_deg
		self.damage = damage
		self.pierce = pierce
		self.lifesteal = 0
		self.lifetime = lifetime
		self.timer = 0.0

		# Pygame rotates counter-clockwise, so negate angle_deg for screen-space Y-down vectors
		rad = math.radians(-angle_deg)
		self.velocity = pygame.math.Vector2(math.cos(rad), math.sin(rad)) * speed

		base_surf = self._build_stake_surface()
		self.image = pygame.transform.rotate(base_surf, self.angle_deg)
		self.rect = self.image.get_rect(center=self.pos)

	@staticmethod
	def _build_stake_surface():
		surf = pygame.Surface((34, 10), pygame.SRCALPHA)

		pygame.draw.rect(surf, (70, 74, 82), pygame.Rect(0, 2, 5, 6), border_radius=1)
		pygame.draw.line(surf, (130, 136, 148), (1, 2), (1, 7), 1)

		pygame.draw.rect(surf, (139, 90, 43), pygame.Rect(5, 2, 18, 6))
		pygame.draw.line(surf, (166, 114, 62), (6, 3), (21, 3), 1)
		pygame.draw.line(surf, (98, 60, 26), (7, 6), (22, 6), 1)

		tip_points = [(23, 1), (34, 5), (23, 9)]
		pygame.draw.polygon(surf, (205, 165, 110), tip_points)
		pygame.draw.line(surf, (232, 198, 148), (23, 2), (32, 5), 1)

		return surf

	def hit_enemy(self):
		self.pierce -= 1
		if self.pierce <= 0:
			self.kill()

	def update(self, dt, all_sprites, projectile_group, sorted_enemies):
		self.timer += dt
		if self.timer >= self.lifetime:
			self.kill()
			return

		self.pos += self.velocity * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))


class CrucifixSentry(pygame.sprite.Sprite):
	CANVAS_SIZE = 116

	def __init__(
		self,
		pos,
		damage=45,
		fire_interval=0.55,
		duration=12.0,
		detection_range=520.0,
		angular_range=260.0,
		pierce=3,
	):
		super().__init__()
		self.pos = pygame.math.Vector2(pos)
		self.damage = damage
		self.fire_interval = fire_interval
		self.duration = duration
		self.detection_range = detection_range
		self.angular_range = angular_range
		self.pierce = pierce

		self.fire_sound = _load_sound_safe("assets/sounds/stake_fire.mp3", volume=0.55)
		self.deploy_sound = _load_sound_safe("assets/sounds/sentry_deploy.mp3", volume=0.65)
		if self.deploy_sound:
			self.deploy_sound.play()

		self.frame_surf = self._build_mounting_frame()
		self.barrel_surf = self._build_cross_barrel()

		self.aim_angle = 0.0
		self.turn_speed = 420.0
		self.fire_timer = 0.15
		self.life_timer = 0.0
		self.recoil_offset = 0.0
		self.muzzle_flash_timer = 0.0

		self.image = pygame.Surface((self.CANVAS_SIZE, self.CANVAS_SIZE), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=self.pos)
		self._compose_sprite()

	@staticmethod
	def _build_mounting_frame():
		surf = pygame.Surface((76, 76), pygame.SRCALPHA)
		cx, cy = 38, 38

		pygame.draw.ellipse(surf, (15, 15, 20, 95), pygame.Rect(10, 14, 56, 52))

		leg_angles = [90, 210, 330]
		for deg in leg_angles:
			rad = math.radians(deg)
			foot_x = cx + math.cos(rad) * 28
			foot_y = cy + math.sin(rad) * 28

			pygame.draw.line(surf, (42, 45, 52), (cx, cy), (foot_x, foot_y), 7)
			pygame.draw.line(surf, (88, 94, 106), (cx, cy), (foot_x, foot_y), 3)

			pad_rect = pygame.Rect(0, 0, 12, 12)
			pad_rect.center = (round(foot_x), round(foot_y))
			pygame.draw.rect(surf, (55, 58, 66), pad_rect, border_radius=3)
			pygame.draw.rect(surf, (135, 142, 156), pad_rect, width=1, border_radius=3)
			pygame.draw.circle(surf, (185, 155, 90), pad_rect.center, 2)

		brace_pts = [
			(cx + math.cos(math.radians(a)) * 16, cy + math.sin(math.radians(a)) * 16)
			for a in leg_angles
		]
		pygame.draw.polygon(surf, (62, 66, 74), brace_pts, width=3)

		pygame.draw.circle(surf, (36, 38, 44), (cx, cy), 15)
		pygame.draw.circle(surf, (112, 118, 130), (cx, cy), 15, width=2)
		pygame.draw.circle(surf, (175, 140, 72), (cx, cy), 9, width=2)

		return surf

	@staticmethod
	def _build_cross_barrel():
		surf = pygame.Surface((82, 58), pygame.SRCALPHA)
		cy = 29

		crossbar_x = 46
		crossbar_w = 11
		crossbar_h = 52
		bar_top = cy - crossbar_h // 2

		pygame.draw.rect(
			surf,
			(58, 62, 70),
			pygame.Rect(crossbar_x, bar_top, crossbar_w, crossbar_h),
			border_radius=2,
		)
		pygame.draw.rect(
			surf,
			(122, 128, 140),
			pygame.Rect(crossbar_x, bar_top, crossbar_w, crossbar_h),
			width=1,
			border_radius=2,
		)
		for cap_y in (bar_top, bar_top + crossbar_h - 6):
			pygame.draw.rect(surf, (182, 146, 74), pygame.Rect(crossbar_x - 1, cap_y, crossbar_w + 2, 6), border_radius=1)
			pygame.draw.rect(surf, (150, 38, 44), pygame.Rect(crossbar_x + 2, cap_y + 1, crossbar_w - 4, 4))

		pygame.draw.rect(surf, (48, 52, 60), pygame.Rect(8, cy - 7, 16, 14), border_radius=3)
		pygame.draw.rect(surf, (115, 120, 132), pygame.Rect(8, cy - 7, 16, 14), width=1, border_radius=3)

		pygame.draw.rect(surf, (74, 79, 88), pygame.Rect(22, cy - 6, 52, 12))
		pygame.draw.line(surf, (148, 154, 168), (22, cy - 5), (73, cy - 5), 1)
		pygame.draw.line(surf, (32, 34, 40), (24, cy), (74, cy), 2)

		pygame.draw.polygon(surf, (196, 152, 96), [(74, cy - 3), (81, cy), (74, cy + 3)])

		pygame.draw.rect(surf, (176, 140, 70), pygame.Rect(69, cy - 7, 5, 14), border_radius=1)
		junction = pygame.Rect(0, 0, 15, 16)
		junction.center = (crossbar_x + crossbar_w // 2, cy)
		pygame.draw.rect(surf, (88, 94, 106), junction, border_radius=2)
		pygame.draw.rect(surf, (182, 146, 74), junction, width=1, border_radius=2)
		pygame.draw.circle(surf, (175, 40, 48), junction.center, 3)

		return surf

	def _find_target(self, sorted_enemies):
		if not sorted_enemies:
			return None

		best_angular_pos = None
		best_angular_score = None
		best_distance_pos = None
		best_distance_score = None

		max_range_sq = self.detection_range ** 2
		angular_range_sq = self.angular_range ** 2

		for enemy in sorted_enemies:
			if hasattr(enemy, "alive") and not enemy.alive():
				continue
			if getattr(enemy, "hp", 1) <= 0:
				continue

			enemy_pos = _get_entity_pos(enemy)
			direction = enemy_pos - self.pos
			dist_sq = direction.length_squared()
			if dist_sq > max_range_sq:
				continue

			if dist_sq > 0:
				target_angle = -math.degrees(math.atan2(direction.y, direction.x))
				angle_diff = abs((target_angle - self.aim_angle + 180) % 360 - 180)
			else:
				angle_diff = 0.0

			if dist_sq <= angular_range_sq:
				score = (angle_diff, dist_sq)
				if best_angular_score is None or score < best_angular_score:
					best_angular_score = score
					best_angular_pos = enemy_pos
			elif best_angular_pos is None:
				score = (dist_sq, angle_diff)
				if best_distance_score is None or score < best_distance_score:
					best_distance_score = score
					best_distance_pos = enemy_pos

		return best_angular_pos if best_angular_pos is not None else best_distance_pos

	def _fire_stake(self, all_sprites, projectile_group):
		rad = math.radians(-self.aim_angle)
		aim_dir = pygame.math.Vector2(math.cos(rad), math.sin(rad))
		muzzle_pos = self.pos + aim_dir * 38

		stake = WoodenStake(
			pos=muzzle_pos,
			angle_deg=self.aim_angle,
			damage=self.damage,
			pierce=self.pierce,
		)
		all_sprites.add(stake)
		projectile_group.add(stake)

		self.recoil_offset = 6.0
		self.muzzle_flash_timer = 0.06
		if self.fire_sound:
			self.fire_sound.play()

	def _compose_sprite(self):
		self.image.fill((0, 0, 0, 0))
		center = pygame.math.Vector2(self.CANVAS_SIZE // 2, self.CANVAS_SIZE // 2)

		frame_rect = self.frame_surf.get_rect(center=center)
		self.image.blit(self.frame_surf, frame_rect)

		rotated_barrel = pygame.transform.rotate(self.barrel_surf, self.aim_angle)
		rad = math.radians(-self.aim_angle)
		aim_dir = pygame.math.Vector2(math.cos(rad), math.sin(rad))
		barrel_center = center - aim_dir * self.recoil_offset

		barrel_rect = rotated_barrel.get_rect(center=(round(barrel_center.x), round(barrel_center.y)))
		self.image.blit(rotated_barrel, barrel_rect)

		if self.muzzle_flash_timer > 0:
			flash_pos = barrel_center + aim_dir * 42
			fx, fy = round(flash_pos.x), round(flash_pos.y)
			pygame.draw.circle(self.image, (255, 220, 130, 210), (fx, fy), 7)
			pygame.draw.circle(self.image, (255, 250, 220, 240), (fx, fy), 3)

		remaining = self.duration - self.life_timer
		if 0 < remaining < 1.5 and int(remaining * 10) % 2 == 0:
			self.image.set_alpha(120)
		else:
			self.image.set_alpha(255)

	def update(self, dt, all_sprites, projectile_group, sorted_enemies):
		self.life_timer += dt
		if self.life_timer >= self.duration:
			self.kill()
			return

		if self.recoil_offset > 0:
			self.recoil_offset = max(0.0, self.recoil_offset - 36.0 * dt)
		if self.muzzle_flash_timer > 0:
			self.muzzle_flash_timer = max(0.0, self.muzzle_flash_timer - dt)

		self.fire_timer -= dt
		target_pos = self._find_target(sorted_enemies)

		if target_pos is not None:
			direction = target_pos - self.pos
			if direction.length_squared() > 0:
				target_angle = -math.degrees(math.atan2(direction.y, direction.x))
				angle_diff = (target_angle - self.aim_angle + 180) % 360 - 180
				max_step = self.turn_speed * dt

				if abs(angle_diff) <= max_step:
					self.aim_angle = target_angle
				else:
					self.aim_angle += math.copysign(max_step, angle_diff)

				if abs(angle_diff) <= 12.0 and self.fire_timer <= 0:
					self._fire_stake(all_sprites, projectile_group)
					self.fire_timer = self.fire_interval

		self._compose_sprite()