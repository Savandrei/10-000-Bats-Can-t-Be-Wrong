import sys
import pygame
from src.game import Game
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
from src.ui.menus import start_menu

""" basically run all the python files"""
def main():
	pygame.init()
	pygame.mixer.init()

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption(TITLE)

	choice = start_menu(screen)

	if choice == "start":
		Game().run()

	pygame.quit()


if __name__ == "__main__":
	main()
