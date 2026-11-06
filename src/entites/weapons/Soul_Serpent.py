import pygame
from .base_weapon import BaseWeapon
from src.entites.projectiles import JudgementCutArea

class SoulSerpent(BaseWeapon):
    """Weapon that targets nearest enemies with Judgement Cut / Waterfowl slash spheres."""
    
    def __init__(self, player, color = (0, 180, 255)):
        super().__init__(player, cooldown=2.5, projectile_number=3)
        self.damage = 25  # Damage per sphere duration
        self.radius = 110
        self.color = color

    def attack(self, all_sprites, projectile_group, sorted_enemies):
        if not sorted_enemies:
            return

        # Create AoE spheres on sorted enemies
        for _ in range(self.projectile_number):
            if not sorted_enemies:
                return

            closest_enemy = sorted_enemies.pop(0)
            
            # Instantiate AoE directly centered on the target enemy
            aoe_cut = JudgementCutArea(
                pos=closest_enemy.rect.center,
                radius=self.radius,
                duration=0.75,
                damage=self.damage,
                color=self.color
            )

            all_sprites.add(aoe_cut)
            projectile_group.add(aoe_cut)