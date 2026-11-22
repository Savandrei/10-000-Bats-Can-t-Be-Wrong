import pygame
from .base_enemy import BaseEnemy

class Dreadwing(BaseEnemy):
	def __init__(self, pos, target_player, all_sprites=None, pickup_group=None):
		super().__init__(
			pos=pos,
			target_player=target_player,
			speed=115,
			health=165,
			damage=22,
			size=(38, 38),
			exp_value=22,
			all_sprites=all_sprites,
			pickup_group=pickup_group,
		)

		frames = self.load_sprite_sheet(
			"assets/images/dreadwing.png", 38, 38, columns=4, rows=4
		)
		self.animations = {
			"down": frames[0:4],
			"up": frames[4:8],
			"left": frames[8:12],
			"right": frames[12:16],
		}

		# frame animation default state
		self.facing = "down"
		self.frame_index = 0
		self.frame_timer = 0.0
		self.image = self.animations[self.facing][self.frame_index]
		self.rect = self.image.get_rect(center=self.rect.center)

		# dreadwing alternates between stalking, preparing a swoop, and swooping
		self.state = "stalk"
		self.state_timer = 2.2
		self.swoop_dir = pygame.math.Vector2(0, 0)
		self.swoop_speed = 390
		self.swoop_range = 280

	def update(self, dt, *args, **kwargs):
		target_pos = pygame.math.Vector2(self.target.rect.center)
		to_target = target_pos - self.pos
		distance = to_target.length()

		if self.state == "stalk":
			# chase until the initial swoop timer expires and the player is close
			self.state_timer -= dt
			if distance > 0:
				self.pos += to_target.normalize() * self.speed * dt

			if self.state_timer <= 0 and distance <= self.swoop_range:
				self.state = "windup"
				self.state_timer = 0.45
				# save the attack direction
				self.swoop_dir = (
					to_target.normalize()
					if distance > 0
					else pygame.math.Vector2(1, 0)
				)

		elif self.state == "windup":
			# pause for a bit before starting the swoop
			self.state_timer -= dt
			if self.state_timer <= 0:
				self.state = "swoop"
				self.state_timer = 0.55

		elif self.state == "swoop":
			self.state_timer -= dt
			# move quickly in the saved direction
			self.pos += self.swoop_dir * self.swoop_speed * dt
			if self.state_timer <= 0:
				self.state = "stalk"
				self.state_timer = 2.5

		direction = pygame.math.Vector2(self.target.rect.center) - self.pos
		# determine which way it should face
		if direction.length_squared() > 0:
			if abs(direction.x) > abs(direction.y):
				if direction.x > 0:
					self.facing = "right"
				else:
					self.facing = "left"
			else:
				if direction.y > 0:
					self.facing = "down"
				else:
					self.facing = "up"

		self.frame_timer += dt
		while self.frame_timer >= 0.12:
			self.frame_timer -= 0.12
			self.frame_index = (self.frame_index + 1) % 4

		self.image = self.animations[self.facing][self.frame_index]
		self.rect = self.image.get_rect(
			center=(round(self.pos.x), round(self.pos.y))
		)