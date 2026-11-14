from .base_enemy import BaseEnemy

class Zombie(BaseEnemy):
	def __init__(self, pos, target_player, all_sprites = None, pickup_group = None):
		super().__init__(
			pos = pos,
			target_player = target_player,
			speed = 120,
			health = 80,
			damage = 20,
			color = (50, 180, 75),
			size = (32, 32),
			exp_value = 20,
			all_sprites = all_sprites,
			pickup_group = pickup_group,
		)