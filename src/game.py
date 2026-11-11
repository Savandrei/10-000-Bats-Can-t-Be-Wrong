# src/game.py
# done with ai since we dont know
# what to include to make the game run
# probably will change and adapt later

# yea, I changed it literally 15 mins later

import pygame
import math

from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, TITLE
from src.entites.player import Player
from src.managers.spawner import Spawner
from src.managers.collision import CollisionManager
from src.ui.hud import HUD


class Game:
	def __init__(self):
		# display Setup
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption(TITLE)
		self.clock = pygame.time.Clock()
		self.running = True
		self.paused = False

		# shared Sprite Groups
		self.all_sprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.projectiles = pygame.sprite.Group()
		# self.pickups = pygame.sprite.Group()

		# instantiate Entities & Systems
		self.player = Player(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
		self.all_sprites.add(self.player)

		# initialize the HUD
		self.hud = HUD(self.player, self.enemies)

		self.spawner = Spawner(self.all_sprites, self.enemies, self.player)

		self.pickups = pygame.sprite.Group()
		self.collision_manager = CollisionManager(
			self.player, self.enemies, self.projectiles, self.pickups,
		)

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.paused = True
				elif self.paused:
					self.paused = False

	def update(self, dt):

		self.sorted_enemies = sorted(self.enemies, key=lambda e: math.hypot(e.pos.x - self.player.pos.x, e.pos.y - self.player.pos.y))

		self.player.update(dt=dt, all_sprites=self.all_sprites, projectile_group=self.projectiles, sorted_enemies=self.sorted_enemies)

		self.all_sprites.update(dt, all_sprites=self.all_sprites, projectile_group=self.projectiles, sorted_enemies=self.sorted_enemies)
		self.spawner.update(dt)
		self.collision_manager.update()
		# end the game if player ded
		if self.player.health <= 0:
			self.running = False

	def render(self):
		# clear screen with background color
		self.screen.fill(COLOR_BG)

		# draw all active sprites
		self.all_sprites.draw(self.screen)
		self.hud.draw(self.screen)

		# draw UI overlay on top
		# self.hud.draw(self.screen)

		# flip display buffers
		pygame.display.update()

	def run(self):
		while self.running:
			# calculate delta time in seconds (e.g., 0.016s at 60 FPS)
			dt = self.clock.tick(FPS) / 1000.0

			self.handle_events()
			if not self.paused:
				self.update(dt)
			self.render()