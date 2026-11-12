import pygame
import src.settings as settings

# took a little bit of inspiration from an example start menu found on the internet

WHITE = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
HOVER_COLOR = (170, 170, 170)
BACKGROUND_COLOR = (1, 2, 3)

def start_menu(screen):
	font = pygame.font.SysFont("Corbel", 40)
	clock = pygame.time.Clock()

	button_width = 200
	button_height = 60
	button_x = (settings.SCREEN_WIDTH - button_width) // 2

	# create the hitboxes for the buttons
	start_button = pygame.Rect(button_x, 260, button_width, button_height)
	settings_button = pygame.Rect(button_x, 340, button_width, button_height)
	exit_button = pygame.Rect(button_x, 420, button_width, button_height)

	buttons = [
		(start_button, "Start"),
		(settings_button, "Settings"),
		(exit_button, "Exit")
		]

	while True:
		for event in pygame.event.get():
			# if you want to exit the old fashioned way
			if event.type == pygame.QUIT:
				return "exit"

			# check if any of the buttons got pressed
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if start_button.collidepoint(event.pos):
					return "start"
				if settings_button.collidepoint(event.pos):
					choice = settings_menu(screen)
					if choice == "exit":
						return "exit"
					screen = pygame.display.get_surface()
				if exit_button.collidepoint(event.pos):
					return "exit"

		mouse_pos = pygame.mouse.get_pos()
		screen.fill(BACKGROUND_COLOR)

		for button, label in buttons:
			# check if any of the buttons are hovered over
			if button.collidepoint(mouse_pos):
				color = HOVER_COLOR 
			else: color = BUTTON_COLOR
			pygame.draw.rect(screen, color, button)

			text = font.render(label, True, WHITE)
			text_rect = text.get_rect(center=button.center)
			screen.blit(text, text_rect)

		pygame.display.flip()
		clock.tick(settings.FPS)

def pause_menu(screen):
	font = pygame.font.SysFont("Corbel", 40)
	clock = pygame.time.Clock()
	
	button_width = 200
	button_height = 60
	button_x = (settings.SCREEN_WIDTH - button_width) // 2

	resume_button = pygame.Rect(button_x, 260, button_width, button_height)
	settings_button = pygame.Rect(button_x, 340, button_width, button_height)
	main_menu_button = pygame.Rect(button_x, 420, button_width, button_height)

	buttons = [
		(resume_button, "Resume"),
		(settings_button, "Settings"),
		(main_menu_button, "Main Menu")
		]

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return "exit"
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				return "resume"

			# check if any of the buttons got pressed
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if resume_button.collidepoint(event.pos):
					return "resume"
				if settings_button.collidepoint(event.pos):
					res = settings_menu(screen)
					if res == "exit":
						return "exit"
					screen = pygame.display.get_surface()
				if main_menu_button.collidepoint(event.pos):
					return "main_menu"

		mouse_pos = pygame.mouse.get_pos()
		screen.fill(BACKGROUND_COLOR)

		for button, label in buttons:
			# check if any of the buttons are hovered over
			if button.collidepoint(mouse_pos):
				color = HOVER_COLOR 
			else: color = BUTTON_COLOR
			pygame.draw.rect(screen, color, button)

			text = font.render(label, True, WHITE)
			text_rect = text.get_rect(center=button.center)
			screen.blit(text, text_rect)

		pygame.display.flip()
		clock.tick(settings.FPS)

def settings_menu(screen):
	font = pygame.font.SysFont("Corbel", 30)
	clock = pygame.time.Clock()

	resolutions = [(800, 600), (1280, 720), (1920, 1080)]
	fps_options = [30, 60, 120, 144]

	res_open = False
	fps_open = False

	button_width = 240
	button_height = 50
	option_height = 45
	button_x = (settings.SCREEN_WIDTH - button_width) // 2

	res_button = pygame.Rect(button_x, 160, button_width, button_height)
	fps_button = pygame.Rect(button_x, 260, button_width, button_height)
	back_button = pygame.Rect(button_x, 460, button_width, button_height)
	while True:
		current_res = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

		# create the hitboxes for the dropdown options
		other_res = [r for r in resolutions if r != current_res]
		res_rects = [(pygame.Rect(button_x, res_button.bottom + i * option_height, button_width, option_height), r)
					for i, r in enumerate(other_res)]

		other_fps = [f for f in fps_options if f != settings.FPS]
		fps_rects = [(pygame.Rect(button_x, fps_button.bottom + i * option_height, button_width, option_height), f)
					for i, f in enumerate(other_fps)]

		mouse_pos = pygame.mouse.get_pos()
		for event in pygame.event.get():
			# this is still possible
			if event.type == pygame.QUIT:
				return "exit"
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				return "back"

			# check if any of the buttons got pressed
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				clicked_dropdown = False

				if res_open:
					for rect, r in res_rects:
						if rect.collidepoint(event.pos):
							# change the resolution and update the display
							settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = r
							screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
							res_open = False
							clicked_dropdown = True
							break

				if fps_open and not clicked_dropdown:
					for rect, f in fps_rects:
						if rect.collidepoint(event.pos):
							# change the FPS setting
							settings.FPS = f
							fps_open = False
							clicked_dropdown = True
							break

				if not clicked_dropdown:
					# check if any of the main buttons got pressed
					if res_button.collidepoint(event.pos):
						res_open = not res_open
						fps_open = False
					# if the resolution dropdown is open, close the fps dropdown
					elif fps_button.collidepoint(event.pos):
						fps_open = not fps_open
						res_open = False
					elif back_button.collidepoint(event.pos):
						return "back"
					else:
						res_open = False
						fps_open = False

		screen.fill(BACKGROUND_COLOR)

		# draw the labels for the dropdowns
		res_label = font.render("Resolution:", True, WHITE)
		screen.blit(res_label, (button_x - 160, res_button.centery - res_label.get_height() // 2))

		fps_label = font.render("Max FPS:", True, WHITE)
		screen.blit(fps_label, (button_x - 160, fps_button.centery - fps_label.get_height() // 2))

		# placeholder symbols, will replace with something else later
		if res_open:
			res_arrow = "^"
		else:
			res_arrow = "<"

		if fps_open:
			fps_arrow = "^"
		else:
			fps_arrow = "<"

		main_buttons = [
			(res_button, f"{settings.SCREEN_WIDTH}x{settings.SCREEN_HEIGHT}  {res_arrow}"),
			(fps_button, f"{settings.FPS}  {fps_arrow}"),
			(back_button, "Back")
		]

		for button, text_str in main_buttons:
			color = HOVER_COLOR if button.collidepoint(mouse_pos) else BUTTON_COLOR
			pygame.draw.rect(screen, color, button)
			pygame.draw.rect(screen, WHITE, button, 1)

			txt = font.render(text_str, True, WHITE)
			screen.blit(txt, txt.get_rect(center=button.center))

		# draw the dropdown options if they are open
		if res_open:
			for rect, r in res_rects:
				color = HOVER_COLOR if rect.collidepoint(mouse_pos) else (65, 65, 65)
				pygame.draw.rect(screen, color, rect)
				pygame.draw.rect(screen, WHITE, rect, 1)

				txt = font.render(f"{r[0]}x{r[1]}", True, WHITE)
				screen.blit(txt, txt.get_rect(center=rect.center))

		if fps_open:
			for rect, f in fps_rects:
				color = HOVER_COLOR if rect.collidepoint(mouse_pos) else (65, 65, 65)
				pygame.draw.rect(screen, color, rect)
				pygame.draw.rect(screen, WHITE, rect, 1)

				txt = font.render(str(f), True, WHITE)
				screen.blit(txt, txt.get_rect(center=rect.center))

		pygame.display.flip()
		clock.tick(settings.FPS)