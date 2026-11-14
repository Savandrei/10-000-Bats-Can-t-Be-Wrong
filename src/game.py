# src/game.py
# done with ai since we dont know
# what to include to make the game run
# probably will change and adapt later

# yea, I changed it literally 15 mins later

import pygame
import math

import src.settings as settings
from src.entites.player import Player
from src.managers.spawner import Spawner
from src.managers.collision import CollisionManager
from src.ui.hud import HUD
from src.ui.menus import pause_menu, start_menu


class Game:
	def __init__(self):
		# display Setup
		self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
		pygame.display.set_caption(settings.TITLE)
		self.clock = pygame.time.Clock()
		self.running = True
		self.paused = False

		# shared Sprite Groups
		self.all_sprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.projectiles = pygame.sprite.Group()
		self.pickups = pygame.sprite.Group()

		# instantiate Entities & Systems
		self.player = Player(pos=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
		self.all_sprites.add(self.player)

		# initialize the HUD
		self.hud = HUD(self.player, self.enemies)

		self.spawner = Spawner(self.all_sprites, self.enemies, self.pickups, self.player)

		self.collision_manager = CollisionManager(
			self.player, self.all_sprites, self.enemies,
			self.projectiles, self.pickups,
		)

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.paused = True
					choice = pause_menu(self.screen)
					self.screen = pygame.display.get_surface()
					if choice == "resume":
						self.paused = False
					if choice == "exit":
						self.running = False
					if choice == "main_menu":
						choice2 = start_menu(self.screen)
						if choice2 == "start":
							self.reset_game()
							self.paused = False
						elif choice2 == "exit":
							self.running = False



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
		self.screen.fill(settings.COLOR_BG)

		# draw all active sprites
		self.all_sprites.draw(self.screen)
		self.hud.draw(self.screen)

		self.player.draw_charge_bar(self.screen)

		# flip display buffers
		pygame.display.update()

	def run(self):
		while self.running:
			# calculate delta time in seconds (e.g., 0.016s at 60 FPS)
			dt = self.clock.tick(settings.FPS) / 1000.0

			self.handle_events()
			if not self.paused:
				self.update(dt)
			self.render()

	def reset_game(self):
		self.all_sprites.empty()
		self.enemies.empty()
		self.projectiles.empty()
		self.pickups.empty()

		self.player = Player(pos=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
		self.all_sprites.add(self.player)

		self.hud = HUD(self.player, self.enemies)
		self.spawner = Spawner(self.all_sprites, self.enemies, self.player)
		self.collision_manager = CollisionManager(
			self.player, self.all_sprites, self.enemies,
			self.projectiles, self.pickups,
		)
