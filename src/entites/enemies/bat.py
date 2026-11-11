from .base_enemy import BaseEnemy

class Bat(BaseEnemy):
	def __init__(self, pos, target_player):
		super().__init__(
			pos=pos,
			target_player=target_player,
			speed=200,
			health=40,
			damage=10,
			color=(180, 180, 180),
			size=(27, 27)
		)