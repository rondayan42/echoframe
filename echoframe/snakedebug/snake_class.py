# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'
        self.grow_pending = False # True if snake should grow on next update

    def draw(self, screen):
        for pos_x, pos_y in self.positions:
            rect = pygame.Rect(pos_x * CELL_SIZE, pos_y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, rect)

    def update(self):
        current_head_x, current_head_y = self.positions[0]
        if self.direction == 'UP':
            new_head = (current_head_x, current_head_y - 1)
        elif self.direction == 'DOWN':
            new_head = (current_head_x, current_head_y + 1)
        elif self.direction == 'LEFT':
            new_head = (current_head_x - 1, current_head_y)
        else:  # RIGHT
            new_head = (current_head_x + 1, current_head_y)

        self.positions.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False # Reset flag after growing
        else:
            self.positions.pop() # Remove tail segment if not growing

    def change_direction(self, new_direction):
        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction

    def check_wall_collision(self):
        head_x, head_y = self.positions[0]
        return head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT

    def check_self_collision(self):
        return self.positions[0] in self.positions[1:]

    def grow(self):
        self.grow_pending = True 