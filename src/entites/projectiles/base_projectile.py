import pygame

class BaseProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, damage, pierce, lifetime, color, size):
        super().__init__()
        
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(pos)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.pierce = pierce
        self.lifetime = lifetime  # lifetime duration in seconds

    def update(self, dt, *args, **kwargs):
        # move projectile using delta time
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # decrease lifetime timer by dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()