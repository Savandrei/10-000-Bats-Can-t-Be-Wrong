import pygame
from .base_weapon import BaseWeapon
from src.entites.projectiles import SlashHitbox

class Slash(BaseWeapon):
    # short-range sweeping attack toward the closest enemy
    def __init__(self, player):
        super().__init__(player, cooldown_frames=50) 

    def attack(self, all_sprites, projectile_group, enemy_group):
        if not enemy_group:
            return

        closest_enemy = min(
            enemy_group.sprites(),
            key=lambda e: pygame.math.Vector2(self.player.rect.center).distance_to(e.rect.center)
        )
        
        # calculate direction and spawn position slightly in front of the player
        direction = pygame.math.Vector2(closest_enemy.rect.center) - self.player.rect.center
        if direction.length_squared() > 0:
            direction = direction.normalize()
        
        spawn_pos = self.player.rect.center + (direction * 25)

        # spawn the dedicated hitbox rather than defining stats directly in the weapon
        slash_proj = SlashHitbox(pos=spawn_pos, direction=direction)
        
        all_sprites.add(slash_proj)
        projectile_group.add(slash_proj)