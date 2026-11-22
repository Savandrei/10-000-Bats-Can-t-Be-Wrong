import pygame
from .base_enemy import BaseEnemy

class SonicRing(pygame.sprite.Sprite):
	def __init__(self, pos, direction, target_player, speed=260, damage=12, lifetime=2.5):
		# starts at the Shrieker and inherits its direction
		super().__init__()
		self.size = 22
		# create a hollow circle for now
		self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		pygame.draw.circle(
			self.image,
			(110, 220, 255),
			(self.size // 2, self.size // 2),
			self.size // 2,
			width=3,
		)
		self.rect = self.image.get_rect(center=pos)

		self.pos = pygame.math.Vector2(pos)
		self.direction = direction.normalize() if direction.length_squared() > 0 else pygame.math.Vector2(1, 0)
		self.target = target_player
		self.speed = speed
		self.damage = damage
		self.lifetime = lifetime

	def update(self, dt, *args, **kwargs):
		self.lifetime -= dt
		# remove expired rings before updating
		if self.lifetime <= 0:
			self.kill()
			return

		self.pos += self.direction * self.speed * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))

		# if it hits the player, deal damage on impact and remove it
		if self.rect.colliderect(self.target.rect):
			if not getattr(self.target, "is_invincible", False):
				if hasattr(self.target, "take_damage"):
					self.target.take_damage(self.damage)
				elif hasattr(self.target, "health"):
					self.target.health -= self.damage
			self.kill()


class Shrieker(BaseEnemy):
	def __init__(self, pos, target_player, all_sprites=None, pickup_group=None):
		super().__init__(
			pos=pos,
			target_player=target_player,
			speed=145,
			health=75,
			damage=10,
			size=(28, 28),
			exp_value=18,
			all_sprites=all_sprites,
			pickup_group=pickup_group,
		)

		frames = self.load_sprite_sheet(
			"assets/images/shrieker.png", 28, 28, columns=4, rows=4
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

		# preferred distance at which it stops to shoot
		self.preferred_range = 260
		self.fire_cooldown = 2.6
		self.fire_timer = 1.5

	def update(self, dt, *args, **kwargs):
		target_pos = pygame.math.Vector2(self.target.rect.center)
		to_target = target_pos - self.pos
		distance = to_target.length()

		if distance > 0:
			direction = to_target.normalize()
			# approach, retreat or circle the player
			if distance > self.preferred_range + 25:
				self.pos += direction * self.speed * dt
			elif distance < self.preferred_range - 25:
				self.pos -= direction * (self.speed * 0.75) * dt
			else:
				strafe = pygame.math.Vector2(-direction.y, direction.x)
				self.pos += strafe * (self.speed * 0.5) * dt

			self.rect.center = (round(self.pos.x), round(self.pos.y))

		# fires only while close enough
		self.fire_timer -= dt
		if self.fire_timer <= 0 and distance <= 480:
			self.fire_timer = self.fire_cooldown
			if self.all_sprites is not None:
				ring = SonicRing(
					pos=self.rect.center,
					direction=to_target,
					target_player=self.target,
				)
				self.all_sprites.add(ring)

		# determine which way it should face
		if to_target.length_squared() > 0:
			if abs(to_target.x) > abs(to_target.y):
				if to_target.x > 0:
					self.facing = "right"
				else:
					self.facing = "left"
			else:
				if to_target.y > 0:
					self.facing = "down"
				else:
					self.facing = "up"

		self.frame_timer += dt
		while self.frame_timer >= 0.12:
			self.frame_timer -= 0.12
			self.frame_index = (self.frame_index + 1) % 4

		self.image = self.animations[self.facing][self.frame_index]
		self.rect = self.image.get_rect(center=self.rect.center)