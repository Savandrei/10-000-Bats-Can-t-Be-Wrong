import pygame
from .base_weapon import BaseWeapon
from src.settings import COLOR_CYAN, PLAYER_HEIGHT
from src.entites.projectiles import JudgementCutArea


class SoulSerpent(BaseWeapon):
	def __init__(self, player):
		super().__init__(player)
		self.player = player

		self.damage = 25
		self.radius = 110

		self.cooldown = 5 * 1000 #in ms
		self.last_attack_time = 0
		self.state = 'idle'
		self.projectile_number = 2
		self.color = COLOR_CYAN
		self.counter = 0

		self.attack_anim_ms = 250
		self.center_delay_ms = 1000
		self.initial_window_ms = 5000
		self.window_ms = self.initial_window_ms
		self.anim_end_time = 0
		self.check_start_time = 0
		self.check_end_time = 0
		self.e_was_pressed = False

		# audio
		self.attack_sound = pygame.mixer.Sound("assets/sounds/ss_attack.wav")
		self.rep_attack2_sound = pygame.mixer.Sound("assets/sounds/repeated2.wav")
		self.rep_attack3_sound = pygame.mixer.Sound("assets/sounds/repeated_end260.mp3")
		self.attack_sound.set_volume(0.5)
		self.rep_attack_value = 0.05
		self.rep_attack2_sound.set_volume(self.rep_attack_value)
		self.rep_attack3_sound.set_volume(1.0)

		self.attack_sprite, self.stand_sprite, self.glow_sprite = self._load_sprites()

	@property
	def is_busy(self):
		"""True while Soul Serpent locks player movement and overrides player sprite."""
		return self.state != 'idle'

	def get_charge_ratio(self, current_time):
		elapsed = current_time - self.last_attack_time
		return min(1.0, elapsed / self.cooldown)

	def _load_sprites(self):
		attack_raw = pygame.image.load("assets/images/SoulSerpent_attack.png").convert_alpha()
		attack_sprite = pygame.transform.scale(attack_raw, (PLAYER_HEIGHT, PLAYER_HEIGHT))

		sheet_raw = pygame.image.load("assets/images/SoulSerpent_skillCheck.png").convert_alpha()
		if sheet_raw.get_width() > sheet_raw.get_height() * 1.2:
			half_w = sheet_raw.get_width() // 2
			h = sheet_raw.get_height()

			stand_raw = pygame.Surface((half_w, h), pygame.SRCALPHA)
			stand_raw.blit(sheet_raw, (0, 0), (0, 0, half_w, h))

			glow_raw = pygame.Surface((half_w, h), pygame.SRCALPHA)
			glow_raw.blit(sheet_raw, (0, 0), (half_w, 0, half_w, h))
		else:
			stand_raw = None
			glow_raw = sheet_raw

		glow_ratio = PLAYER_HEIGHT / glow_raw.get_height()
		glow_sprite = pygame.transform.scale(
			glow_raw, (round(glow_raw.get_width() * glow_ratio), PLAYER_HEIGHT)
		)

		if stand_raw is not None:
			stand_ratio = PLAYER_HEIGHT / stand_raw.get_height()
			stand_sprite = pygame.transform.scale(
				stand_raw, (round(stand_raw.get_width() * stand_ratio), PLAYER_HEIGHT)
			)
		else:
			stand_sprite = None

		return attack_sprite, stand_sprite, glow_sprite

	def trigger_attack(self, current_time, all_sprites, projectile_group, sorted_enemies, is_chained=False):
		self.counter += 1

		self.attack_sound.play()
		self.rep_attack2_sound.play()
		self.rep_attack_value = min(1.0, self.rep_attack_value * 2)
		self.rep_attack2_sound.set_volume(self.rep_attack_value)
		if self.counter > 9:
			self.rep_attack3_sound.play()

		self.attack(all_sprites, projectile_group, sorted_enemies, self.color)

		if is_chained:
			self.window_ms *= 0.7
			if self.counter <= 4:
				self.color = (0, max(0, self.color[1] - 60), max(0, self.color[2] - 75))
			elif self.counter <= 8:
				self.color = (0, 0, 0)
			else:
				self.color = (255, 255, 255)
		else:
			self.window_ms = self.initial_window_ms

		center_time = current_time + self.center_delay_ms
		half_window = self.window_ms / 2.0

		self.projectile_number += 1
		self.state = 'attack_anim'
		self.anim_end_time = current_time + self.attack_anim_ms
		self.check_start_time = center_time - half_window
		self.check_end_time = center_time + half_window
		self.player.set_override_sprite(self.attack_sprite)

	def reset_combo(self, current_time):
		self.state = 'idle'
		self.window_ms = self.initial_window_ms
		self.last_attack_time = current_time
		self.color = COLOR_CYAN
		self.projectile_number = 2
		self.rep_attack_value = 0.05
		self.counter = 0
		self.player.clear_override_sprite()

	def update(self, dt, all_sprites, projectile_group, sorted_enemies):
		current_time = pygame.time.get_ticks()
		keys = pygame.key.get_pressed()

		e_pressed = keys[pygame.K_e]
		e_just_pressed = e_pressed and not self.e_was_pressed
		self.e_was_pressed = e_pressed

		if self.state == 'idle':
			if e_just_pressed and current_time - self.last_attack_time >= self.cooldown:
				self.trigger_attack(current_time, all_sprites, projectile_group, sorted_enemies, is_chained=False)

		elif self.state == 'attack_anim':
			if current_time >= self.anim_end_time:
				self.state = 'waiting_for_check'
				if self.stand_sprite:
					self.player.set_override_sprite(self.stand_sprite)
				else:
					self.player.clear_override_sprite()
			elif e_just_pressed:
				self.reset_combo(current_time)

		elif self.state == 'waiting_for_check':
			if e_just_pressed:
				self.reset_combo(current_time)
			elif current_time >= self.check_start_time:
				self.state = 'skill_check'
				self.player.set_override_sprite(self.glow_sprite)

		elif self.state == 'skill_check':
			if current_time <= self.check_end_time:
				if e_just_pressed:
					self.trigger_attack(current_time, all_sprites, projectile_group, sorted_enemies, is_chained=True)
			else:
				self.reset_combo(current_time)

	def attack(self, all_sprites, projectile_group, sorted_enemies, color = (0, 180, 255)):
		if not sorted_enemies:
			return

		# Create AoE spheres on sorted enemies
		for _ in range(self.projectile_number):
			if not sorted_enemies:
				return

			closest_enemy = sorted_enemies.pop(0)
			
			# Instantiate AoE directly centered on the target enemy
			aoe_cut = JudgementCutArea(
				pos=closest_enemy.rect.center,
				radius=self.radius,
				duration=0.75,
				damage=self.damage,
				color=color
			)

			all_sprites.add(aoe_cut)
			projectile_group.add(aoe_cut)