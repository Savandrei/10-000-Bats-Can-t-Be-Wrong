import pygame
from src.settings import PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, DASH_SPEED, PLAYER_MAX_HP, COLOR_BLACK, COLOR_CRIMSON
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

		#scythe related variables
		self.isZephixEdge_unlocked = False
		self.ZephyxEdge = ZephyxEdge(self)
		self.ZephyxEdge_cooldown = 5 #in sec
		self.ZephyxEdge_cooldown *= 1000 #transform in ms
		self.ZephyxEdge_lastAttack_time = 0

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

		if self.is_dashing:
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