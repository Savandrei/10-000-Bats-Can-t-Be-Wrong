import pygame
from .base_weapon import BaseWeapon

class ZephyxEdgeSlash(pygame.sprite.Sprite):
	"""Animated sprite for the Scythe attack sequence."""

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

	def __init__(self, player, spritesheet_path="assets/images/phase2_spritesheet.png", frame_duration=0.06):
		super().__init__()

		self.player = player
		self.pierce = 9999
		self.attack_sound = pygame.mixer.Sound("assets/sounds/scythe_attack.mp3")
		self.attack_sound.set_volume(0.7)

		self.facing_angle = self.FACING_ANGLES.get(getattr(self.player, 'facing', 'left'), 0)

		self.pivot_pos = pygame.math.Vector2(self.player.pos)
		self.offset = pygame.math.Vector2(50, -130)
		self.offset_frame2 = pygame.math.Vector2(-65, 130)

		sheet = pygame.image.load(spritesheet_path).convert_alpha()
		sheet_w, sheet_h = sheet.get_size()
		frame_w, frame_h = sheet_w // 4, sheet_h // 2

		self.frames = []
		for row in range(2):
			for col in range(4):
				rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
				frame_surf = sheet.subsurface(rect)
				self.frames.append(frame_surf)

		self.frames[2] = pygame.transform.flip(self.frames[2], True, False)

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
		"""Updates animation frame based on delta time (dt)."""
		self.timer += dt
		self.pivot_pos = pygame.math.Vector2(self.player.pos)

		if self.current_frame == 0:
			if self.timer >= self.frame0_duration:
				self.timer -= self.frame0_duration
				self.current_frame += 1
				self.attack_sound.play()

		elif self.current_frame == 1:
			if self.timer >= self.frame1_duration:
				self.timer -= self.frame1_duration
				self.current_frame += 1

		elif self.timer >= self.frame2_duration:
			self.timer -= self.frame2_duration
			self.current_frame += 1

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


class ZephyxEdge(BaseWeapon):
	"""Scythe weapon that spawns a full slash animation relative to the player or target."""

	def __init__(self, player):
		super().__init__(player, cooldown=10.0, projectile_number=1)
		self.damage = 55
		self.spritesheet_path = "assets/images/phase2_spritesheet.png"
		self.timer = 0

	def attack(self, all_sprites, projectile_group, sorted_enemies):
		target_pos = self.player.pos


		scythe_anim = ZephyxEdgeSlash(
			player=self.player,
			spritesheet_path=self.spritesheet_path,
			frame_duration=0.12
		)
		scythe_anim.damage = self.damage

		all_sprites.add(scythe_anim)
		projectile_group.add(scythe_anim)