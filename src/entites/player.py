import pygame
from src.settings import PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, DASH_SPEED, PLAYER_MAX_HP, COLOR_CYAN
from src.entites.weapons import BaseWeapon, MagicWand, Slash, Meteorite, BulletWand, SoulSerpent, ZephyxEdge
import math

# trial and error
PLAYER_HEIGHT = 90
PLAYER_WIDTH = 60


# pretty much just java code from this point on
class Player(pygame.sprite.Sprite):

	# initialization
	def __init__(self, pos):
		super().__init__()

		self.health = PLAYER_MAX_HP
		self.damage_invulnerable_until = 0
		self.damage_invulnerability_ms = 1000

		self.exp = 0
		self.level = 1
		self.exp_to_next_level = 50

		#scythe related variables
		self.isZephixEdge_unlocked = False
		self.ZephyxEdge = ZephyxEdge(self)
		self.ZephyxEdge_cooldown = 5 #in sec
		self.ZephyxEdge_cooldown *= 1000 #transform in ms
		self.ZephyxEdge_lastAttack_time = 0

		#Soul serpent aoe variables
		self.isSoulSerpent_unlocked = False
		self.SoulSerpent = SoulSerpent(self)
		self.SoulSerpent_cooldown = 5 #in sec
		self.SoulSerpent_cooldown *= 1000 #transform in ms
		self.SoulSerpent_lastAttack_time = 0

		self.ss_state = 'idle'
		self.ss_attack_anim_ms = 250
		self.ss_center_delay_ms = 1000
		self.ss_initial_window_ms = 5000
		self.ss_window_ms = self.ss_initial_window_ms
		self.ss_anim_end_time = 0
		self.ss_check_start_time = 0
		self.ss_check_end_time = 0
		self.e_was_pressed = False
		self.ss_color = COLOR_CYAN
		self.SoulSerpent.projectile_number = 2

		self.ss_attack_sound = pygame.mixer.Sound("assets/sounds/ss_attack.wav")
		self.ss_repAttack_sound = pygame.mixer.Sound("assets/sounds/repeated.wav")
		self.ss_attack_sound.set_volume(0.5)
		self.ss_repAttack_value = 0
		self.ss_repAttack_sound.set_volume(self.ss_repAttack_value)

		#dash related variables
		self.is_dashing = False
		self.last_dash_time = 0
		self.is_invincible = False
		self.dash_dx = 0
		self.dash_dy = 0
		self.dash_duration = 60
		self.dash_cooldown = 1000

		frames = self.load_sprite_sheet("assets/images/player_sprite_sheet.png", PLAYER_WIDTH, PLAYER_HEIGHT, 4, 2)

		self.sprites = {
			'up': frames[0],
			'up_right': frames[1],
			'right': frames[2],
			'down_right': frames[3],
			'down': frames[4],
			'down_left': frames[5],
			'left': frames[6],
			'up_left': frames[7],
		}

		self.ss_attack_sprite, self.ss_stand_sprite, self.ss_glow_sprite = self.load_soul_serpent_sprites()

		self.facing = 'down'
		self.image = self.sprites[self.facing]

		#########################################

		self.rect = self.image.get_rect(center=pos)
		self.rect = self.image.get_rect(center=pos)

		#########################################
		#  ^
		#  |  yay first merge conflict
		#  |

		self.pos = pygame.math.Vector2(pos)
		self.speed = PLAYER_SPEED

		self.weapons = []
		# self.add_weapon(MagicWand(self))
		self.add_weapon(BulletWand(self))
		# self.add_weapon(SoulSerpent(self))
		# self.add_weapon(SoulSerpent(self, color = COLOR_BLACK))
		# self.add_weapon(SoulSerpent(self, color = COLOR_CRIMSON))
		self.add_weapon(ZephyxEdge(self))



##############################################################
	def add_weapon(self, weapon: BaseWeapon):
		if isinstance(weapon, ZephyxEdge):
			self.isZephixEdge_unlocked = True
		elif isinstance(weapon, SoulSerpent):
			self.isSoulSerpent_unlocked = True
		else:
			self.weapons.append(weapon)

##############################################################
	def load_sprite_sheet(self, path, frame_width, frame_height, columns, rows):
		# convert_alpha() is for png to be a png and not a box
		sheet = pygame.image.load(path).convert_alpha()

		cell_width = sheet.get_width() // columns
		cell_height = sheet.get_height() // rows

		frames = []

		for row in range(rows):
			for col in range(columns):

				frame = pygame.Surface((cell_width, cell_height), pygame.SRCALPHA)
				frame.blit(sheet, (0, 0), (col * cell_width, row * cell_height, cell_width, cell_height))
				frame = pygame.transform.scale(frame, (frame_width, frame_height))

				frames.append(frame)

		return frames

##############################################################
	def load_soul_serpent_sprites(self):
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

			scale_ratio = PLAYER_HEIGHT / glow_raw.get_height()
			target_width = round(glow_raw.get_width() * scale_ratio)
			glow_sprite = pygame.transform.scale(glow_raw, (target_width, PLAYER_HEIGHT))

			if stand_raw is not None:
				stand_ratio = PLAYER_HEIGHT / stand_raw.get_height()
				stand_width = round(stand_raw.get_width() * stand_ratio)
				stand_sprite = pygame.transform.scale(stand_raw, (stand_width, PLAYER_HEIGHT))
			else:
				stand_sprite = None

			return attack_sprite, stand_sprite, glow_sprite

##############################################################
	def set_soul_serpent_sprite(self, sprite):
		self.image = sprite
		self.rect = self.image.get_rect(center=self.rect.center)

##############################################################
	def trigger_soul_serpent_attack(self, current_time, all_sprites, projectile_group, sorted_enemies, is_chained=False):

		self.ss_attack_sound.play()
		self.ss_repAttack_sound.play()
		self.ss_repAttack_value = min(1, self.ss_repAttack_value + 0.2)
		self.ss_repAttack_sound.set_volume(self.ss_repAttack_value)

		self.SoulSerpent.attack(all_sprites, projectile_group, sorted_enemies, self.ss_color)


		if is_chained:
			self.ss_window_ms *= 0.7
			if (self.ss_color[1] > 0):
				self.ss_color = (0, self.ss_color[1] - 60, self.ss_color[2] -  75)
			else:
				self.ss_color = (0, 0 , 0)
		else:
			self.ss_window_ms = self.ss_initial_window_ms

		center_time = current_time + self.ss_center_delay_ms
		half_window = self.ss_window_ms / 2.0

		self.SoulSerpent.projectile_number += 1
		self.ss_state = 'attack_anim'
		self.ss_anim_end_time = current_time + self.ss_attack_anim_ms
		self.ss_check_start_time = center_time - half_window
		self.ss_check_end_time = center_time + half_window
		self.set_soul_serpent_sprite(self.ss_attack_sprite)

##############################################################
	def reset_soul_serpent_combo(self, current_time):
		self.ss_state = 'idle'
		self.ss_window_ms = self.ss_initial_window_ms
		self.SoulSerpent_lastAttack_time = current_time
		self.set_soul_serpent_sprite(self.sprites[self.facing])
		self.ss_color = COLOR_CYAN
		self.SoulSerpent.projectile_number = 2
		self.ss_repAttack_value = 0

##############################################################
	def update_soul_serpent_state(self, current_time, e_just_pressed, all_sprites, projectile_group, sorted_enemies):
		if not self.isSoulSerpent_unlocked:
			return

		if self.ss_state == 'idle':
			if e_just_pressed and current_time - self.SoulSerpent_lastAttack_time >= self.SoulSerpent_cooldown:
				self.trigger_soul_serpent_attack(current_time, all_sprites, projectile_group, sorted_enemies, is_chained=False)

		elif self.ss_state == 'attack_anim':
			if current_time >= self.ss_anim_end_time:
				self.ss_state = 'waiting_for_check'
				self.set_soul_serpent_sprite(self.ss_stand_sprite or self.sprites[self.facing])
			elif e_just_pressed:
				self.reset_soul_serpent_combo(current_time)

		elif self.ss_state == 'waiting_for_check':
			if e_just_pressed:
				self.reset_soul_serpent_combo(current_time)
			elif current_time >= self.ss_check_start_time:
				self.ss_state = 'skill_check'
				self.set_soul_serpent_sprite(self.ss_glow_sprite)

		elif self.ss_state == 'skill_check':
			if current_time <= self.ss_check_end_time:
				if e_just_pressed:
					self.trigger_soul_serpent_attack(current_time, all_sprites, projectile_group, sorted_enemies, is_chained=True)
			else:
				self.reset_soul_serpent_combo(current_time)

##############################################################
	def update_facing(self, direction):
		# determine which of the 8 directions the player is facing.
		dx = direction.x
		dy = direction.y

		if dx == 0 and dy < 0:
			facing = 'up'
		elif dx == 0 and dy > 0:
			facing = 'down'
		elif dx < 0 and dy == 0:
			facing = 'left'
		elif dx > 0 and dy == 0:
			facing = 'right'
		elif dx < 0 and dy < 0:
			facing = 'up_left'
		elif dx > 0 and dy < 0:
			facing = 'up_right'
		elif dx < 0 and dy > 0:
			facing = 'down_left'
		elif dx > 0 and dy > 0:
			facing = 'down_right'
		else:
			return

		if facing != self.facing:
			self.facing = facing
			if self.ss_state == 'idle':
				self.image = self.sprites[self.facing]

				self.rect = self.image.get_rect(center=self.rect.center)

############################################################
	def get_input(self, dt, all_sprites, projectile_group, sorted_enemies):
		keys = pygame.key.get_pressed()
		direction = pygame.math.Vector2(0, 0)

		current_time = pygame.time.get_ticks()

		if keys[pygame.K_q] and self.isZephixEdge_unlocked:
			if current_time - self.ZephyxEdge_lastAttack_time >= self.ZephyxEdge_cooldown:
				self.ZephyxEdge_lastAttack_time = current_time
				self.ZephyxEdge.attack(all_sprites, projectile_group, sorted_enemies)


		e_pressed = keys[pygame.K_e]
		e_just_pressed = e_pressed and not self.e_was_pressed
		self.e_was_pressed = e_pressed

		self.update_soul_serpent_state(current_time, e_just_pressed, all_sprites, projectile_group, sorted_enemies)

		if self.ss_state != 'idle':
			return direction

		# arrow movement
		if keys[pygame.K_UP]:
			direction.y -= 1
		if keys[pygame.K_DOWN]:
			direction.y += 1
		if keys[pygame.K_LEFT]:
			direction.x -= 1
		if keys[pygame.K_RIGHT]:
			direction.x += 1

		# wasd movement
		if keys[pygame.K_w]:
			direction.y -= 1
		if keys[pygame.K_s]:
			direction.y += 1
		if keys[pygame.K_a]:
			direction.x -= 1
		if keys[pygame.K_d]:
			direction.x += 1

		# fix diagonal movement
		# 1 / sqrt2 ~ 0.707
		if direction.x != 0 and direction.y != 0:
			direction.x *= 0.707
			direction.y *= 0.707

		#sets dash direction
		if direction != (0,0):
			self.dash_dx = direction.x
			self.dash_dy = direction.y

		if keys[pygame.K_LSHIFT] and not self.is_dashing:
			if current_time - self.last_dash_time >= self.dash_cooldown: #time elapsed > cooldown
				self.is_dashing = True
				self.is_invincible = True
				self.last_dash_time = current_time

		return direction

#############################################################
	def no_offscreen_warriors(self):
		self.rect.left = max(0, self.rect.left)
		self.rect.right = min(SCREEN_WIDTH, self.rect.right)
		self.rect.top = max(0, self.rect.top)
		self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)


		# I would debug for hours bcuz I forgot abt this
		# thx ai
		self.pos.x = self.rect.centerx
		self.pos.y = self.rect.centery

##############################################################
	def update(self, dt, all_sprites=None, projectile_group=None, sorted_enemies=None):
		direction = self.get_input(dt, all_sprites, projectile_group, sorted_enemies)
		current_time = pygame.time.get_ticks()

		self.update_facing(direction)

		if self.ss_state != 'idle':
			self.is_dashing = False
			self.is_invincible = False
			self.speed = PLAYER_SPEED
			direction = pygame.math.Vector2(0, 0)
		elif self.is_dashing:
			# if dash ends
			if current_time - self.last_dash_time >= self.dash_duration:
				self.is_dashing = False
				self.is_invincible = False
				self.speed = PLAYER_SPEED
			else:
				# if dash started or still is in effect
				direction.x = self.dash_dx
				direction.y = self.dash_dy
				self.speed = DASH_SPEED


		# first time writing this line managed
		# to achieve the speed of light (forgot dt)
		self.pos += direction * self.speed * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))

		self.no_offscreen_warriors()

		# sorting enemies based on how close
		# they are for efficient weapon targeting


		if all_sprites is not None and projectile_group is not None and sorted_enemies is not None:
			for weapon in self.weapons:
				weapon.update(dt, all_sprites, projectile_group, sorted_enemies)

##############################################################
	def take_damage(self, amount):
		now = pygame.time.get_ticks()

		# dash already makes the player invulnerable so use that
		if self.is_dashing or now < self.damage_invulnerable_until:
			return

		self.health = max(0, self.health - amount)
		self.damage_invulnerable_until = now + self.damage_invulnerability_ms

##############################################################
	def gain_exp(self, amount):
		self.exp += amount
		if self.exp >= self.exp_to_next_level:
			self.level += 1
			self.exp -= self.exp_to_next_level
			self.exp_to_next_level = int(self.exp_to_next_level * 1.25)

##############################################################
	def draw_charge_bar(self, surface):
		if not self.isZephixEdge_unlocked and not self.isSoulSerpent_unlocked:
			return

		current_time = pygame.time.get_ticks()

		if (self.isZephixEdge_unlocked):
			elapsed = current_time - self.ZephyxEdge_lastAttack_time
			charge_ratio = min(1.0, elapsed / self.ZephyxEdge_cooldown)
		else:
			elapsed = current_time - self.SoulSerpent_lastAttack_time
			charge_ratio = min(1.0, elapsed / self.SoulSerpent_cooldown)

		bar_width = 16
		bar_height = 100
		margin_right = 20
		margin_bottom = 20

		bar_x = SCREEN_WIDTH - margin_right - bar_width
		bar_y = SCREEN_HEIGHT - margin_bottom - bar_height

		bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
		pygame.draw.rect(surface, (20, 20, 20), bg_rect)
		pygame.draw.rect(surface, (180, 180, 180), bg_rect, 1)

		fill_height = int((bar_height - 2) * charge_ratio)
		if fill_height > 0:
			fill_y = (bar_y + bar_height - 1) - fill_height
			fill_rect = pygame.Rect(bar_x + 1, fill_y, bar_width - 2, fill_height)

			if self.isZephixEdge_unlocked:
				color = (230, 11, 230) if charge_ratio >= 1.0 else (133, 24, 133)
			else:
				color = (0, 255, 255) if charge_ratio >= 1.0 else (0, 140, 255)
			pygame.draw.rect(surface, color, fill_rect)

