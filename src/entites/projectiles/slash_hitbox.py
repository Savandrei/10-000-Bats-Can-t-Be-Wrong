import pygame
from .base_projectile import BaseProjectile

class SlashHitbox(BaseProjectile):
	def __init__(self, pos, direction):
		super().__init__(
			pos=pos,
			direction=direction,
			speed=0,       
			damage=25,
			pierce=999,    
			lifetime=10,   
			color=(200, 200, 200),
			size=(40, 40)
		)