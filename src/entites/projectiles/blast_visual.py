import pygame
from .base_projectile import BaseProjectile

class BlastVisual(BaseProjectile):
    # a visual-only explosion indicator that deals no direct projectile damage
    def __init__(self, pos, radius):
        # convert 15 frame lifetime to 0.25 seconds
        super().__init__(
            pos=pos,
            direction=pygame.math.Vector2(1, 0),
            speed=0,
            damage=0, 
            pierce=0,
            lifetime=0.25,
            color=(255, 100, 0), 
            size=(radius * 2, radius * 2)
        )
        
        # render visual circle on surface
        pygame.draw.circle(self.image, (255, 100, 0), (radius, radius), radius)

    def update(self, dt, *args, **kwargs):
        # call base update to handle lifetime timer with dt
        super().update(dt, *args, **kwargs)