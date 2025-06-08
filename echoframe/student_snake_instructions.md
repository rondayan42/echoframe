# How to Create Your Snake Game Files

EchoFrame allows you to create your own Python files for the Snake game. You have the freedom to name your files however you want while still making them work with the platform.

## What Files You Need

For a complete Snake game, you'll typically need the following files (you can name them however you want):

1. **A constants file**: Define your grid size, colors, and other settings
2. **A Snake class file**: Define your snake behavior and properties
3. **A Food class file**: Define how food appears and behaves
4. **A main game file**: Contains your game loop and pulls everything together

## File Detection

The EchoFrame platform will automatically detect your files based on their content:

- **Constants file**: Detected if it contains `GRID_WIDTH`, `GRID_HEIGHT`, and `CELL_SIZE`
- **Snake class file**: Detected if it contains `class Snake` or similar class with positions/segments
- **Food class file**: Detected if it contains `class Food` or food position logic
- **Main game file**: Detected if it contains `pygame.init()` or `pygame.display` and a while loop

## Required Functions and Objects

For your game to work correctly, make sure your code includes:

1. In your main file:
   - Initialize PyGame with `pygame.init()`
   - Create a display with `pygame.display.set_mode()`
   - Implement a game loop
   - Call `pygame.display.flip()` to update the display

2. In your Snake class:
   - Store snake positions in a list of (x,y) coordinates
   - Include methods for drawing and updating the snake

3. In your constants file:
   - Define `GRID_WIDTH`, `GRID_HEIGHT`, and `CELL_SIZE`
   - Define colors like `BLACK`, `GREEN`, `RED`, etc.

## User Input

To get user input from the browser controls, use this special function:

```python
def get_user_direction():
    return 'RIGHT'  # Default direction when nothing is pressed
```

This function will automatically work and will return the current direction being input by the user.

## Examples

### Example constants file (my_constants.py):
```python
# My game constants
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game settings
FPS = 10
```

### Example Snake class file (cool_snake.py):
```python
import pygame

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'
        
    def draw(self, screen):
        for pos in self.positions:
            pygame.draw.rect(screen, GREEN, 
                (pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
    def update(self):
        head_x, head_y = self.positions[0]
        
        if self.direction == 'UP':
            new_head = (head_x, head_y - 1)
        elif self.direction == 'DOWN':
            new_head = (head_x, head_y + 1)
        elif self.direction == 'LEFT':
            new_head = (head_x - 1, head_y)
        else:  # RIGHT
            new_head = (head_x + 1, head_y)
            
        self.positions.insert(0, new_head)
        self.positions.pop()
        
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction
```

### Example main game file (awesome_game.py):
```python
import pygame
import sys
from cool_snake import Snake

# Initialize pygame
pygame.init()

# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('My Awesome Snake Game')
clock = pygame.time.Clock()

# Create game objects
snake = Snake()

# Game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.change_direction('UP')
            elif event.key == pygame.K_DOWN:
                snake.change_direction('DOWN')
            elif event.key == pygame.K_LEFT:
                snake.change_direction('LEFT')
            elif event.key == pygame.K_RIGHT:
                snake.change_direction('RIGHT')
    
    # Get direction from browser controls
    browser_direction = get_user_direction()
    if browser_direction:
        snake.change_direction(browser_direction)
    
    # Update
    snake.update()
    
    # Draw
    screen.fill(BLACK)
    snake.draw(screen)
    
    # Update display
    pygame.display.flip()
    
    # Control game speed
    clock.tick(FPS)

# Cleanup
pygame.quit()
sys.exit()
```

## Troubleshooting

If your game doesn't appear to work:

1. Check that your main file has a working game loop
2. Make sure your constants are properly defined
3. Verify your Snake class properly tracks positions
4. Ensure you're calling `pygame.display.flip()` to update the display

Remember, the platform will help run your code even if it's not complete yet - that's part of the learning process! 