from .base_enemy import BaseEnemy

class Slime(BaseEnemy):
	def __init__(self, pos, target_player, all_sprites = None, pickup_group = None):
		super().__init__(
			pos = pos,
			target_player = target_player,
			speed = 180,
			health = 40,
			damage = 10,
			color = (255, 100, 100),
			size = (20, 20),
			exp_value = 10,
			all_sprites = all_sprites,
			pickup_group = pickup_group,
		)