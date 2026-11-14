import pygame

from src.settings import PLAYER_MAX_HP

class HUD:
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

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