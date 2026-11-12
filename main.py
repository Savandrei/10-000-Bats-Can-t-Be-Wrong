import sys
import pygame
from src import settings
from src.game import Game
from src.ui.menus import start_menu

""" basically run all the python files"""
def main():
	pygame.init()
	pygame.mixer.init()

	screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
	pygame.display.set_caption(settings.TITLE)

	choice = start_menu(screen)

	if choice == "start":
		Game().run()

	pygame.quit()


if __name__ == "__main__":
	main()
