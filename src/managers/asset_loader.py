import pygame

class AssetLoader:
	_spritesheet_cache = {}

	@classmethod
	def get_directional_frames(cls, path, cols=4, rows=4, target_size=None):
		# loads a spritesheet and slices it into individual animation frames
		cache_key = (path, cols, rows, target_size)
		if cache_key in cls._spritesheet_cache:
			return cls._spritesheet_cache[cache_key]

		sheet = pygame.image.load(path).convert_alpha()
		sheet_w, sheet_h = sheet.get_size()
		frame_w = sheet_w // cols
		frame_h = sheet_h // rows

		directions = ["S", "N", "W", "E"]
		frames = {}

		for row_idx, direction in enumerate(directions):
			frames[direction] = []
			for col_idx in range(cols):
				# create the area that contains the frame
				rect = pygame.Rect(col_idx * frame_w, row_idx * frame_h, frame_w, frame_h)
				frame = sheet.subsurface(rect)
				if target_size is not None:
					frame = pygame.transform.scale(frame, target_size)
				frames[direction].append(frame)

		cls._spritesheet_cache[cache_key] = frames
		return frames