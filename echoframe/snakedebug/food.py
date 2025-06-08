# food.py: Contains the Food class definition
import pygame
import random
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, RED

class Food:
    def __init__(self):
        self.reset_position([])

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset_position(self, snake_positions):
        """Moves food to a new random position not occupied by the snake."""
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions:
                break 