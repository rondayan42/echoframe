# snake_starters.py
# Contains the starter code templates for each Snake Arc quest.
# UPDATED: Modified to work with headless Pygame environment

# Structure: List index corresponds to snake quest index (0-9)
# Each element is a dictionary mapping filename to starter code string.

# Define starter code for all quests
SNAKE_STARTER_CODE = [
    # Quest 0 (Snake Echo 1: Define the Grid)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
# These constants will be automatically available in other files.

# --- Grid Dimensions ---
# CELL_SIZE = 20   # Example: Size of each grid square in pixels
# GRID_WIDTH = 30  # Example: Number of cells horizontally
# GRID_HEIGHT = 20 # Example: Number of cells vertically

# --- Screen Dimensions (Calculated) ---
# Calculate the total screen size based on the grid
# SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
# SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
# TODO: When you define constants in constants.py, uncomment the next line
# from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# --- Screen Setup ---
# Define the window size using constants from constants.py
# TODO: Uncomment these lines after defining constants and importing them
# window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
# screen = pygame.display.set_mode(window_size)
# pygame.display.set_caption('Snake Echo')
# clock = pygame.time.Clock() # Needed for controlling game speed

# Write your code above
"""
    },

    # Quest 1 (Snake Echo 2: Game Loop)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30  # Corrected from 30 to match typical square grid for snake
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# --- Game Loop ---
# Implement a basic game loop that:
# 1. Processes events
# 2. Handles the quit event
# 3. Updates the display
# 4. Maintains FPS frames per second
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw everything
    screen.fill(BLACK) # Example: Fill screen with black

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
"""
    },

    # Quest 2 (Snake Echo 3: Snake Class)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake
# from food import Food # Food class not used in this quest's snake.py yet

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Create a snake instance
snake = Snake() # Assuming Snake() is defined in snake_class.py

# --- Game Loop ---
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw everything
    screen.fill(BLACK)
    # snake.draw(screen) # TODO: Call snake's draw method here

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        # Initialize the snake at the center of the screen
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        # Set initial direction to 'RIGHT'
        self.direction = 'RIGHT'
        # Create a positions list to store segments (already done above)

    def draw(self, screen):
        # Draw the snake (will implement later)
        # Example:
        # for pos in self.positions:
        #     pygame.draw.rect(screen, GREEN,
        #                      (pos[0] * CELL_SIZE, pos[1] * CELL_SIZE,
        #                       CELL_SIZE, CELL_SIZE))
        pass

    def update(self):
        # Update the snake's position (will implement later)
        pass
""",
        "food.py": """# food.py: Contains the Food class definition
import pygame
import random
from constants import RED, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

class Food:
    def __init__(self):
        # Initialize with a random position
        self.reset()

    def draw(self, screen):
        # Draw a red rectangle for the food
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset(self):
        # Move to a new random position
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))
"""
    },

    # Quest 3 (Snake Echo 4: Colors & Drawing)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake
# from food import Food # Food class not used in this quest's snake.py yet

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Create a snake instance
snake = Snake()

# --- Game Loop ---
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw everything
    screen.fill(BLACK)
    snake.draw(screen)

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'

    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self):
        # Calculate new head position based on direction
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
        self.positions.pop() # Remove tail segment

    def change_direction(self, new_direction):
        # Prevent reversing direction
        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction

    def check_wall_collision(self):
        # Return True if the snake's head is outside grid boundaries
        x, y = self.positions[0]
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def check_self_collision(self):
        # Return True if the snake's head position is also in its body segments
        return self.positions[0] in self.positions[1:]

    def grow(self):
        # Make the snake longer (don't remove tail when growing)
        # We duplicate the last position - it will move on next update
        self.positions.append(self.positions[-1])
""",
        "food.py": """# food.py: Contains the Food class definition
import pygame
import random
from constants import RED, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

class Food:
    def __init__(self):
        # Initialize with a random position
        self.reset()

    def draw(self, screen):
        # Draw a red rectangle for the food
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset(self):
        # Move to a new random position
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))
"""
    },

    # Quest 4 (Snake Echo 5: Movement)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Create a snake instance
snake = Snake()

# --- Game Loop ---
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update snake position
    snake.update()

    # Draw everything
    screen.fill(BLACK)
    snake.draw(screen)

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        # Initialize the snake at the center of the screen
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'

    def draw(self, screen):
        # Draw a green rectangle for each snake segment
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self):
        # Calculate new head position based on direction
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
        self.positions.pop() # Remove tail segment
"""
    },

    # Quest 5 (Snake Echo 6: Keyboard Controls)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake

# --- Preview System Integration ---
def get_user_direction(current_direction):
    \"\"\"
    This function is used by the preview system to control your snake.
    It will be replaced by the backend during preview.
    You should call it once per frame, passing the current direction.
    In normal play, it just returns the current direction.

    Why?
    - The preview system uses this function to inject keyboard input
      and extract game state.
    - If you remove or rename this function, the live preview will not work!
    \"\"\"
    # For local play, you'd handle pygame.key.get_pressed() here
    # or process KEYDOWN events to change direction.
    # For now, it's a placeholder for the preview system.
    for event in pygame.event.get(pygame.KEYDOWN): # Check for key presses specifically
        if event.key == pygame.K_UP:
            return 'UP'
        elif event.key == pygame.K_DOWN:
            return 'DOWN'
        elif event.key == pygame.K_LEFT:
            return 'LEFT'
        elif event.key == pygame.K_RIGHT:
            return 'RIGHT'
    return current_direction  # Default: keep moving in the same direction

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Create a snake instance
snake = Snake()

# --- Game Loop ---
running = True
while running:
    # Process quit events separately
    for event in pygame.event.get(pygame.QUIT):
        if event.type == pygame.QUIT:
            running = False
            
    # --- Preview System: Get direction from preview or user input ---
    # Note: get_user_direction now also processes KEYDOWN events for basic local play
    new_direction = get_user_direction(snake.direction)
    snake.change_direction(new_direction)

    # Update snake position
    snake.update()

    # Draw everything
    screen.fill(BLACK)
    snake.draw(screen)

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'

    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self):
        # Calculate new head position based on direction
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
        # Implement direction change with validation:
        # The snake can't reverse direction (e.g., can't go LEFT when moving RIGHT)
        if new_direction == 'UP' and self.direction != 'DOWN':
            self.direction = new_direction
        elif new_direction == 'DOWN' and self.direction != 'UP':
            self.direction = new_direction
        elif new_direction == 'LEFT' and self.direction != 'RIGHT':
            self.direction = new_direction
        elif new_direction == 'RIGHT' and self.direction != 'LEFT':
            self.direction = new_direction
"""
    },

    # Quest 6 (Snake Echo 7: Food)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake
from food import Food

# --- Preview System Integration ---
def get_user_direction(current_direction):
    \"\"\"
    This function is used by the preview system to control your snake.
    It will be replaced by the backend during preview.
    You should call it once per frame, passing the current direction.
    In normal play, it just returns the current direction.

    Why?
    - The preview system uses this function to inject keyboard input
      and extract game state.
    - If you remove or rename this function, the live preview will not work!
    \"\"\"
    # Basic local input handling
    for event in pygame.event.get(pygame.KEYDOWN):
        if event.key == pygame.K_UP:
            return 'UP'
        elif event.key == pygame.K_DOWN:
            return 'DOWN'
        elif event.key == pygame.K_LEFT:
            return 'LEFT'
        elif event.key == pygame.K_RIGHT:
            return 'RIGHT'
    return current_direction

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Create game objects
snake = Snake()
food = Food()

# --- Game Loop ---
running = True
while running:
    # Process quit events
    for event in pygame.event.get(pygame.QUIT):
        if event.type == pygame.QUIT:
            running = False

    # --- Preview System: Get direction from preview or user input ---
    new_direction = get_user_direction(snake.direction)
    snake.change_direction(new_direction)

    # Update snake position
    snake.update()

    # TODO: Check for food collision and snake growth

    # Draw everything
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'

    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

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
        # self.positions.pop() # Don't pop tail until growth is handled

    def change_direction(self, new_direction):
        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction

    def grow(self):
        # This method will be called when the snake eats food.
        # For now, it just duplicates the tail, effectively growing.
        # The update method will then move the new head, and the old tail won't be popped.
        self.positions.append(self.positions[-1])
""",
        "food.py": """# food.py: Contains the Food class definition
import pygame
import random
from constants import RED, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

class Food:
    def __init__(self):
        self.reset()

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset(self):
        # Move to a new random position
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))
"""
    },

    # Quest 7 (Snake Echo 8: Collision Detection)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake
from food import Food

# --- Preview System Integration ---
def get_user_direction(current_direction):
    \"\"\"Handles input for snake direction.\"\"\"
    for event in pygame.event.get(pygame.KEYDOWN): # Process only KEYDOWN for this function
        if event.key == pygame.K_UP:
            return 'UP'
        elif event.key == pygame.K_DOWN:
            return 'DOWN'
        elif event.key == pygame.K_LEFT:
            return 'LEFT'
        elif event.key == pygame.K_RIGHT:
            return 'RIGHT'
    return current_direction

# --- Initialization ---
pygame.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Create game objects
snake = Snake()
food = Food()
game_over = False # Game state

# --- Game Loop ---
running = True
while running:
    # Temporary variable for new direction from input
    input_direction = snake.direction 

    for event in pygame.event.get(): # Process all events
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not game_over: # Handle input if not game over
            # Get direction based on this specific key event
            # This ensures that get_user_direction processes the current event
            # and doesn't re-pull from the event queue.
            # We pass snake.direction as current_direction if no key is pressed by get_user_direction
            
            # To correctly use get_user_direction, it should ideally not pull events itself
            # or the main loop should pass the event to it.
            # For simplicity here, we'll call it and it will internally check current KEYDOWN events.
            # This might lead to some events being missed if not handled carefully.
            # A better approach is to process events once and pass relevant info.
            
            # Let's refine the input handling for clarity for this quest:
            if event.key == pygame.K_UP:
                input_direction = 'UP'
            elif event.key == pygame.K_DOWN:
                input_direction = 'DOWN'
            elif event.key == pygame.K_LEFT:
                input_direction = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                input_direction = 'RIGHT'
    
    if not game_over:
        snake.change_direction(input_direction) # Change direction based on processed input
        snake.update(food.position) # Pass food position for eating logic

        # Check for collisions
        if snake.check_wall_collision() or snake.check_self_collision():
            game_over = True # Set game over state

        # Check if snake eats food
        if snake.positions[0] == food.position:
            snake.grow()
            food.reset()
            # score += 1 # TODO: Implement score

    # Draw everything
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)
    # TODO: Display score
    # TODO: Display game over message if game_over is True

    # Update display
    pygame.display.flip()

    # Maintain game speed
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'
        self.grow_pending = False # Flag to indicate snake should grow on next update

    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self, food_pos): # food_pos is not used here yet, but good for future
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

        if self.grow_pending:
            self.grow_pending = False # Reset flag
        else:
            self.positions.pop() # Remove tail if not growing

    def change_direction(self, new_direction):
        if (new_direction == 'UP' and self.direction != 'DOWN') or \
           (new_direction == 'DOWN' and self.direction != 'UP') or \
           (new_direction == 'LEFT' and self.direction != 'RIGHT') or \
           (new_direction == 'RIGHT' and self.direction != 'LEFT'):
            self.direction = new_direction

    def grow(self):
        # This method will be called when the snake eats food.
        # For now, it just duplicates the tail, effectively growing.
        # The update method will then move the new head, and the old tail won't be popped.
        self.positions.append(self.positions[-1])
""",
        "food.py": """# food.py: Contains the Food class definition
import pygame
import random
from constants import RED, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

class Food:
    def __init__(self):
        self.reset()

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset(self):
        # Move to a new random position
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))
"""
    },

    # Quest 8 (Snake Echo 9: Score Display)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game Settings ---
FPS = 10 # Define Frames Per Second
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from snake_class import Snake
from food import Food

# --- Preview System Integration ---
def get_user_direction(current_direction):
    \"\"\"
    This function is used by the preview system to control your snake.
    It will be replaced by the backend during preview.
    You should call it once per frame, passing the current direction.
    In normal play, it just returns the current direction.

    Why?
    - The preview system uses this function to inject keyboard input
      and extract game state.
    - If you remove or rename this function, the live preview will not work!
    \"\"\"
    # Basic local input handling
    for event in pygame.event.get(pygame.KEYDOWN):
        if event.key == pygame.K_UP:
            return 'UP'
        elif event.key == pygame.K_DOWN:
            return 'DOWN'
        elif event.key == pygame.K_LEFT:
            return 'LEFT'
        elif event.key == pygame.K_RIGHT:
            return 'RIGHT'
    return current_direction

# --- Initialization ---
pygame.init()
pygame.font.init() # Initialize font module

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo')
clock = pygame.time.Clock()

# Load font and initialize score
try:
    game_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    # It's good practice to define the game_over_font here if it's different
    # For now, we'll use a scaled version of game_font or define another one.
    # game_over_display_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE * 2) # Example
except pygame.error as e:
    print(f"Warning: Could not load system font. Using default. Error: {e}")
    game_font = pygame.font.Font(None, FONT_SIZE) # Fallback to default Pygame font
    # game_over_display_font = pygame.font.Font(None, FONT_SIZE * 2) # Fallback

score = 0
game_over = False

# Create game objects
snake = Snake()
food = Food()

def reset_game():
    global snake, food, score, game_over
    snake = Snake()
    food.reset() # Food needs to be reset
    score = 0
    game_over = False

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                new_dir = get_user_direction(snake.direction)
                snake.change_direction(new_dir)
            else:
                if event.key == pygame.K_SPACE:
                    reset_game()

    if not game_over:
        snake.update() 

        if snake.check_wall_collision() or snake.check_self_collision():
            game_over = True

        if snake.positions[0] == food.position:
            snake.grow()
            food.reset() # Ensure food resets correctly
            score += 1

    # Draw everything
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)

    # Render score text
    score_surface = game_font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, SCORE_POS)

    if game_over:
        # Game over display
        # Using a potentially larger font for "GAME OVER"
        # If game_over_display_font was defined above, use it here.
        # Otherwise, create it or scale dynamically.
        try:
            # Attempt to create a larger font for game over, or use existing if defined
            game_over_text_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE * 2)
        except pygame.error:
            game_over_text_font = pygame.font.Font(None, FONT_SIZE * 2)

        over_text_surface = game_over_text_font.render('GAME OVER', True, RED) # RED is now imported
        restart_text_surface = game_font.render('Press SPACE to restart', True, WHITE)
        
        over_text_rect = over_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - FONT_SIZE))
        restart_text_rect = restart_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + FONT_SIZE))
        
        screen.blit(over_text_surface, over_text_rect)
        screen.blit(restart_text_surface, restart_text_rect)
        # The 'pass' here was a placeholder, actual drawing is above.

    pygame.display.flip()
    clock.tick(FPS)

    get_user_direction()

pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
import pygame
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, GREEN

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'
        self.grow_pending = False # True if snake should grow on next update

    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self): # Removed food_pos, as eating is handled in main loop
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
        x, y = self.positions[0]
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def check_self_collision(self):
        return self.positions[0] in self.positions[1:]

    def grow(self):
        self.grow_pending = True
""",
        "food.py": """# food.py: Contains the Food class definition
import pygame
import random
from constants import RED, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

class Food:
    def __init__(self):
        self.reset()

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset(self):
        # Move to a new random position
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))
"""
    },

    # Quest 9 (Snake Echo 10: Game Over & Restart)
    {
        "constants.py": """# constants.py: Define game settings and colors here.
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0) # Color for Game Over text

# --- Game Settings ---
FPS = 10

# --- Font Settings ---
FONT_NAME = None # Use default system font
FONT_SIZE = 24 # Reduced from 30 to match original constant
SCORE_POS = (10, 10) # Position for the score display
""",
        "snake.py": """# snake.py: Main game logic file.
import pygame
import sys
import random # random is imported but not used in this specific starter
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS, WHITE, RED,
                       FONT_NAME, FONT_SIZE, SCORE_POS)
from snake_class import Snake
from food import Food

# --- Preview System Integration (Placeholder) ---
# For this quest, direct input handling is clearer.
# The preview system's get_user_direction is not the primary focus here.
def get_new_direction_from_input(current_direction, key_event):
    \"\"\"Determines new direction based on key event, preventing reversal.\"\"\"
    if key_event.key == pygame.K_UP and current_direction != 'DOWN':
        return 'UP'
    elif key_event.key == pygame.K_DOWN and current_direction != 'UP':
        return 'DOWN'
    elif key_event.key == pygame.K_LEFT and current_direction != 'RIGHT':
        return 'LEFT'
    elif key_event.key == pygame.K_RIGHT and current_direction != 'LEFT':
        return 'RIGHT'
    return current_direction

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo - Final Quest')
clock = pygame.time.Clock()

# Load fonts
try:
    score_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    game_over_font = pygame.font.SysFont(FONT_NAME, GAME_OVER_FONT_SIZE)
    restart_font = pygame.font.SysFont(FONT_NAME, RESTART_FONT_SIZE)
except pygame.error as e:
    print(f"Warning: Could not load system font. Using default. Error: {e}")
    score_font = pygame.font.Font(None, FONT_SIZE)
    game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
    restart_font = pygame.font.Font(None, RESTART_FONT_SIZE)


# Game state variables
score = 0
game_over = False
snake = Snake() # Initial snake
food = Food()   # Initial food

def reset_game_state():
    \"\"\"Resets the game to its initial state.\"\"\"
    global snake, food, score, game_over
    snake = Snake()
    food.reset_position(snake.positions) # Pass snake positions to avoid overlap
    score = 0
    game_over = False

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_SPACE:
                    reset_game_state()
            else:
                new_dir = get_new_direction_from_input(snake.direction, event)
                snake.change_direction(new_dir)

    if not game_over:
        snake.update()

        if snake.check_wall_collision() or snake.check_self_collision():
            game_over = True

        if snake.positions[0] == food.position:
            snake.grow()
            food.reset_position(snake.positions) # Reset food ensuring no overlap
            score += 1

    # --- Drawing ---
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)

    # Display score
    score_surface = score_font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, SCORE_POS)

    if game_over:
        # Display "GAME OVER"
        over_text_surface = game_over_font.render('GAME OVER', True, RED)
        over_text_rect = over_text_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - GAME_OVER_FONT_SIZE // 2)
        )
        screen.blit(over_text_surface, over_text_rect)

        # Display final score (optional, can be larger)
        final_score_surface = score_font.render(f'Final Score: {score}', True, WHITE)
        final_score_rect = final_score_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_FONT_SIZE)
        )
        screen.blit(final_score_surface, final_score_rect)
        
        # Display "Press SPACE to restart"
        restart_surface = restart_font.render('Press SPACE to restart', True, WHITE)
        restart_rect = restart_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_FONT_SIZE * 2.5)
        )
        screen.blit(restart_surface, restart_rect)

    pygame.display.flip()
    clock.tick(FPS)

    get_user_direction()

# Clean up
pygame.quit()
sys.exit()
""",
        "snake_class.py": """# snake_class.py: Contains the Snake class definition
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
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def check_self_collision(self):
        return self.positions[0] in self.positions[1:]

    def grow(self):
        self.grow_pending = True
""",
        "food.py": """# food.py: Contains the Food class definition
import pygame
import random
from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, RED

class Food:
    def __init__(self):
        self.reset() # Initial reset

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED,
                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset_position(self, snake_positions):
        \"\"\"Moves food to a new random position not occupied by the snake.\"\"\"
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions:
                break
"""
    }
]

# Add a function to explicitly get Echo 10 starter files
def get_echo10_starter_files():
    """Return the fully implemented Echo 10 starter files.

    Returns:
        dict: Dictionary mapping filenames to file contents
    """
    return SNAKE_STARTER_CODE[9]
