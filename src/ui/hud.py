import pygame

from src.settings import PLAYER_MAX_HP, UI_FONT_PATH

class HUD:
	def __init__(self, player, enemies):
		self.player = player
		self.enemies = enemies
		self.font = pygame.font.Font(UI_FONT_PATH, 24)
		self.small_font = pygame.font.Font(UI_FONT_PATH, 18)

	# create hp bar
	def _draw_bar(self, surface, rect, health, max_health):
		if max_health > 0:
			remaining_health = max(0, min(health / max_health, 1))
		else:
			remaining_health = 0

		pygame.draw.rect(surface, (40, 40, 40), rect)
		fill_rect = rect.copy()
		fill_rect.width = round(rect.width * remaining_health)
		pygame.draw.rect(surface, (255, 0, 0), fill_rect)

	def draw(self, surface):
		# player hp is in top-left corner
		hp_text = self.font.render(f"HP: {self.player.health} / {PLAYER_MAX_HP}", True, (255, 255, 255), )
		surface.blit(hp_text, (16, 16))
		self._draw_bar(surface, pygame.Rect(16, 44, 180, 16), self.player.health, PLAYER_MAX_HP, )

		# exp underneath hp
		level_text = self.font.render(f"Level: {self.player.level}", True, (255, 255, 255))
		surface.blit(level_text, (16, 66))

		# enemy hp underneath them
		for enemy in self.enemies:
			bar_width = max(36, enemy.rect.width)
			bar_rect = pygame.Rect(0, 0, bar_width, 6)
			bar_rect.midtop = (enemy.rect.centerx, enemy.rect.bottom + 3)
			self._draw_bar(surface, bar_rect, enemy.health, enemy.max_health)

	def draw_charge_bar(self, surface):
		state = self.player.get_charge_bar_state()
		if state is None:
			return

		charge_ratio = state["ratio"]

		bar_width = 16
		bar_height = 100
		margin_right = 20
		margin_bottom = 20

		surface_width, surface_height = surface.get_size()
		bar_x = surface_width - margin_right - bar_width
		bar_y = surface_height - margin_bottom - bar_height

		bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
		pygame.draw.rect(surface, (20, 20, 20), bg_rect)
		pygame.draw.rect(surface, (180, 180, 180), bg_rect, 1)

		fill_height = int((bar_height - 2) * charge_ratio)
		if fill_height > 0:
			fill_y = (bar_y + bar_height - 1) - fill_height
			fill_rect = pygame.Rect(bar_x + 1, fill_y, bar_width - 2, fill_height)

			if state["type"] == "zephyx":
				color = (230, 11, 230) if charge_ratio >= 1.0 else (133, 24, 133)
			else:
				color = (0, 255, 255) if charge_ratio >= 1.0 else (0, 140, 255)

			pygame.draw.rect(surface, color, fill_rect)