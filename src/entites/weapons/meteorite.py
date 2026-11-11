import pygame
import random
from .base_weapon import BaseWeapon
from src.entites.projectiles import BlastVisual

class Meteorite(BaseWeapon):
    # calls down an explosive strike on a random enemy
    def __init__(self, player):
        super().__init__(player, cooldown_frames=120)  # Slower attack
        self.aoe_radius = 75
        self.damage = 50

    def attack(self, all_sprites, projectile_group, enemy_group):
        if not enemy_group:
            return
        
        # target a random enemy rather than the closest
        target = random.choice(enemy_group.sprites())
        impact_pos = pygame.math.Vector2(target.rect.center)

        # instantly damage all enemies within the blast radius
        for enemy in enemy_group:
            if impact_pos.distance_to(enemy.rect.center) <= self.aoe_radius:
                enemy.take_damage(self.damage)
        
        # spawn the dedicated visual indicator rather than defining it inline
        blast_visual = BlastVisual(pos=impact_pos, radius=self.aoe_radius)
        
        all_sprites.add(blast_visual)
