import pygame
from .base_weapon import BaseWeapon
from src.entites.projectiles.zephyx_edge_slash import ZephyxEdgeSlash

class ZephyxEdge(BaseWeapon):

	def __init__(self, player):
		super().__init__(player, cooldown=10.0, projectile_number=1)
		self.damage = 9999
		self.timer = 0

		# Load, slice, and pre-flip frames once on weapon initialization
		spritesheet_path = "assets/images/phase2_spritesheet.png"
		sheet = pygame.image.load(spritesheet_path).convert_alpha()
		sheet_w, sheet_h = sheet.get_size()
		frame_w, frame_h = sheet_w // 4, sheet_h // 2

		self.frames = []
		for row in range(2):
			for col in range(4):
				rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
				frame_surf = sheet.subsurface(rect)
				self.frames.append(frame_surf)

		self.frames[2] = pygame.transform.flip(self.frames[2], True, False)

		# Load sound once to avoid disk I/O during combat
		self.attack_sound = pygame.mixer.Sound("assets/sounds/scythe_attack.mp3")
		self.attack_sound.set_volume(0.7)

	def attack(self, all_sprites, projectile_group, sorted_enemies):
		scythe_anim = ZephyxEdgeSlash(
			player=self.player,
			frames=self.frames,
			damage=self.damage,
			attack_sound=self.attack_sound,
			frame_duration=0.12
		)
		all_sprites.add(scythe_anim)