import pygame


class ZephyxEdgeSlash(pygame.sprite.Sprite):

	FACING_ANGLES = {
		'left': 0,
		'up_left': 45,
		'up': 90,
		'up_right': 135,
		'right': 180,
		'down_right': -135,
		'down': -90,
		'down_left': -45,
	}

	def __init__(self, player, frames, damage=9999, attack_sound=None, frame_duration=0.06):
		super().__init__()

		self.player = player
		self.frames = frames
		self.damage = damage
		self.pierce = 9999
		self.lifesteal = 1
		self.attack_sound = attack_sound

		self.facing_angle = self.FACING_ANGLES.get(getattr(self.player, 'facing', 'left'), 0)

		self.pivot_pos = pygame.math.Vector2(self.player.pos)
		self.offset = pygame.math.Vector2(50, -130)
		self.offset_frame2 = pygame.math.Vector2(-65, 130)

		self.current_frame = 0

		base_surf = self.frames[self.current_frame]
		self.image = pygame.transform.rotate(base_surf, -self.facing_angle)
		rotated_offset = self.offset.rotate(self.facing_angle)
		self.rect = self.image.get_rect(center=self.pivot_pos + rotated_offset)

		self.frame0_duration = 0.7
		self.frame1_duration = 0.2
		self.frame2_duration = 0.22
		self.timer = 0.0

	def hit_enemy(self):
		self.pierce -= 1
		if self.pierce <= 0:
			self.kill()

	def update(self, dt, all_sprites, projectile_group, sorted_enemies):
		self.timer += dt
		self.pivot_pos = pygame.math.Vector2(self.player.pos)

		if self.current_frame == 0:
			if self.timer >= self.frame0_duration:
				self.timer -= self.frame0_duration
				self.current_frame += 1
				if self.attack_sound:
					self.attack_sound.play()

		elif self.current_frame == 1:
			if self.timer >= self.frame1_duration:
				self.timer -= self.frame1_duration
				self.current_frame += 1

		elif self.timer >= self.frame2_duration:
			self.timer -= self.frame2_duration
			self.current_frame += 1

		if self.current_frame == 2:
			if not projectile_group.has(self):
				projectile_group.add(self)
		else:
			if projectile_group.has(self):
				projectile_group.remove(self)

		if self.current_frame < 3:
			base_surf = self.frames[self.current_frame]
		else:
			self.kill()
			return

		if self.current_frame == 1:
			t = min(max(self.timer / self.frame1_duration, 0.0), 1.0)
			ease = 0.75 * (t ** 3) - 0.5 * (t ** 4)
			rot_deg = 600 * ease

			total_vec_rot = rot_deg + self.facing_angle
			total_img_rot = -rot_deg - self.facing_angle

			self.image = pygame.transform.rotate(base_surf, total_img_rot)
			rotated_offset = self.offset.rotate(total_vec_rot)
			self.rect = self.image.get_rect(center=self.pivot_pos + rotated_offset)

		elif self.current_frame == 2:
			t = min(max(self.timer / self.frame2_duration, 0.0), 1.0)
			ease = 0.75 * (t ** 2) - 0.5 * (t ** 3)
			rot_deg = 1600 * ease

			total_vec_rot = -rot_deg - 50 + self.facing_angle
			total_img_rot = rot_deg + 50 - self.facing_angle

			self.image = pygame.transform.rotate(base_surf, total_img_rot)
			rotated_offset = self.offset_frame2.rotate(total_vec_rot)
			self.rect = self.image.get_rect(center=self.pivot_pos + rotated_offset)

		else:
			self.image = pygame.transform.rotate(base_surf, -self.facing_angle)
			rotated_offset = self.offset.rotate(self.facing_angle)
			self.rect = self.image.get_rect(center=self.pivot_pos + rotated_offset)