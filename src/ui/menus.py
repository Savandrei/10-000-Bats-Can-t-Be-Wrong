import pygame

from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

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
	button_x = (SCREEN_WIDTH - button_width) // 2

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
				if exit_button.collidepoint(event.pos):
					return "exit"
				# settings does nothing for now

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
		clock.tick(FPS)