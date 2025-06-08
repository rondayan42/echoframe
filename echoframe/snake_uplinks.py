# Study Uplinks for the Snake Arc
# Peer-to-peer Python tutorial for aspiring game developers

snake_study_docs = {
    0: '''📖 Study Uplink: Snake Echo 1 – Building Your Game Grid

Alright, Snaker. Time to lay the foundation. Every game needs a world, and ours is a grid. We define its rules in `constants.py`.

Think of `constants.py` as the blueprint. Variables defined here are like global settings for our simulation.

### The Grid Blueprint (`constants.py`)
```python
# Size of each grid square (in pixels)
CELL_SIZE = 20

# Grid dimensions (in number of cells)
GRID_WIDTH = 30
GRID_HEIGHT = 30

# Calculate total screen size (in pixels)
# These are derived from the grid settings above
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH   # e.g., 20 * 30 = 600
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT # e.g., 20 * 30 = 600
```

### Using the Blueprint (`snake.py`)
Now, in your main `snake.py` file, you need to tell Pygame how big the game window should be.

```python
# snake.py
# Import necessary libraries first
import pygame
import sys

# Define the window size using the constants
# NOTE: SCREEN_WIDTH and SCREEN_HEIGHT are automatically available
# because constants.py is executed first by the quest runner.
# No 'from constants import ...' needed here!
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

# (Pygame initialization and screen creation will happen in the next quest)
```

### Key Concepts:
- **Constants:** Using uppercase names (like `CELL_SIZE`) for values that don't change makes code readable and easy to modify.
- **Shared Environment:** The quest runner executes `constants.py` first, then `snake.py` (and later, other files) in the *same environment*. This means variables defined in `constants.py` are directly usable in `snake.py` without needing `import`.
- **Coordinates:** We have grid coordinates (like cell 0,0 to 29,29) and pixel coordinates (0,0 to 599,599). `CELL_SIZE` is the key to converting between them.

🎮 Pro Move: Keep configuration separate (`constants.py`) from logic (`snake.py`). It's cleaner.
''',

    1: '''📖 Study Uplink: Snake Echo 2 – The Game Loop Primer

Every game runs on a heartbeat – the **game loop**. It's a `while` loop that keeps running, handling input, updating the game state, and drawing everything to the screen, over and over.

### Setting up Pygame (`snake.py`)
```python
# snake.py (continuing from previous quest)
import pygame
import sys

# Constants like SCREEN_WIDTH, SCREEN_HEIGHT, FPS are available from constants.py

# --- Initialization ---
pygame.init() # Start Pygame's engines

# --- Screen Setup ---
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size) # Create the game window
pygame.display.set_caption('Snake Echo')     # Set window title
clock = pygame.time.Clock()                  # Create a clock to control speed

# --- Game State ---
running = True # Flag to keep the loop going

# --- Main Game Loop ---
while running:
    # --- 1. Event Handling ---
    # Check for player input or window closing
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Did the user click the close button?
            running = False # Set flag to exit the loop

    # --- 2. Game Logic ---
    # (We'll add snake movement updates here later)

    # --- 3. Drawing ---
    # Clear the screen for the new frame
    # BLACK should be defined in constants.py, e.g., BLACK = (0, 0, 0)
    screen.fill(BLACK) # Fill with black (or another background color)

    # (We'll draw the snake and food here later)

    # --- 4. Update Display ---
    # Show everything that was drawn in this frame
    pygame.display.flip()

    # --- 5. Frame Rate Control ---
    # Wait long enough to maintain the target FPS
    # FPS should be defined in constants.py, e.g., FPS = 10
    clock.tick(FPS)

# --- Quit Pygame ---
# Clean up Pygame resources when the loop ends
pygame.quit()
sys.exit() # Exit the script
```

### Loop Breakdown:
1.  **Handle Events:** Check for user actions (keys, mouse, closing window).
2.  **Update State:** Move objects, check collisions, update scores.
3.  **Draw:** Render everything onto the screen surface (like a canvas).
4.  **Flip Display:** Make the newly drawn frame visible.
5.  **Tick Clock:** Pause briefly to control the speed (Frames Per Second).

### Key Concepts:
- **`pygame.init()`:** Essential first step to use Pygame modules.
- **`pygame.display.set_mode()`:** Creates the actual game window surface.
- **`pygame.event.get()`:** Gets a list of all events that happened since the last check.
- **`pygame.QUIT`:** The event triggered by clicking the window's close button.
- **`screen.fill()`:** Clears the screen by filling it with a color.
- **`pygame.display.flip()`:** Makes drawings visible. Without it, you see a blank screen.
- **`clock.tick(FPS)`:** Crucial for consistent game speed across different computers.

🕹️ Remember: This loop is the engine. Everything happens inside it, frame by frame.
''',

    2: '''📖 Study Uplink: Snake Echo 3 – Crafting the Snake Entity

Games need actors. Let's define our main character: the Snake. We use a **class** to blueprint our snake object. Classes bundle data (attributes) and behavior (methods) together.

### The Snake Blueprint (`snake_class.py`)
```python
# snake_class.py
# Constants like GRID_WIDTH, GRID_HEIGHT are available from constants.py

import pygame # Might need later for drawing

class Snake:
    # The __init__ method is the constructor. It runs when you create a Snake object.
    def __init__(self):
        # --- Attributes (Data) ---
        # Calculate starting position (center of the grid)
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2

        # The snake's body is a list of (x, y) grid coordinate tuples.
        # It starts as a single segment at the center.
        self.positions = [(start_x, start_y)]

        # The direction the snake is currently moving.
        self.direction = 'RIGHT' # Can be 'UP', 'DOWN', 'LEFT', 'RIGHT'

        # A flag to track if the snake ate food and needs to grow.
        self.grow_pending = False

    # --- Methods (Behavior) ---
    # This method will draw the snake on the screen (implemented later).
    def draw(self, surface):
        # 'surface' is the game window where we'll draw.
        pass # 'pass' is a placeholder for empty methods

    # This method will handle moving the snake (implemented later).
    def update(self):
        pass

    # This method will change the snake's direction (implemented later).
    def change_direction(self, new_direction):
        pass

    # This method will make the snake longer (implemented later).
    def grow(self):
        pass

    # Collision detection methods (implemented later).
    def check_wall_collision(self):
        return False # Placeholder

    def check_self_collision(self):
        return False # Placeholder

```

### Using the Blueprint (`snake.py`)
Now, back in `snake.py`, we create an *instance* of our Snake class.

```python
# snake.py (inside the setup, before the main loop)

# --- Game Objects ---
# Create an actual Snake object using the Snake class blueprint.
# The Snake class is automatically available from snake_class.py.
snake = Snake()

# --- Main Game Loop ---
while running:
    # ... (event handling) ...

    # --- Game Logic ---
    # (Call snake.update() here later)

    # --- Drawing ---
    screen.fill(BLACK)
    # (Call snake.draw(screen) here later)

    # ... (display flip, clock tick) ...
```

### Key Concepts:
- **Class:** A blueprint for creating objects (like `Snake`).
- **Object/Instance:** A specific thing created from a class (like the `snake` variable).
- **`__init__(self)`:** The constructor method, sets up the object's initial state. `self` refers to the instance being created.
- **Attributes:** Variables belonging to an object (e.g., `snake.positions`, `snake.direction`). Accessed using dot notation.
- **Methods:** Functions belonging to a class that define its behavior (e.g., `snake.draw()`, `snake.update()`). Also accessed using dot notation.

🐍 Pro Tip: Classes help organize complex code by grouping related data and actions.
''',

    3: '''📖 Study Uplink: Snake Echo 4 – Making the Snake Visible

An invisible snake isn't much fun. Let's implement the `draw` method in our `Snake` class.

### Defining Colors (`constants.py`)
First, ensure you have colors defined. Add these to `constants.py` if you haven't already:
```python
# constants.py
# ... (other constants) ...

# --- Colors (RGB Tuples) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)    # Snake color
RED = (255, 0, 0)      # Food color
```

### Drawing the Snake (`snake_class.py`)
Now, fill in the `draw` method in `snake_class.py`.

```python
# snake_class.py
# Constants like CELL_SIZE, GREEN are available from constants.py
import pygame

class Snake:
    def __init__(self):
        # ... (init code from previous step) ...
        pass

    def draw(self, surface):
        # Loop through each (x, y) segment position in the snake's body
        for segment_x, segment_y in self.positions:
            # Create a pygame.Rect object for the segment's screen position and size
            # Multiply grid coordinates by CELL_SIZE to get pixel coordinates
            segment_rect = pygame.Rect(
                segment_x * CELL_SIZE,  # Pixel X position (top-left corner)
                segment_y * CELL_SIZE,  # Pixel Y position (top-left corner)
                CELL_SIZE,              # Pixel width
                CELL_SIZE               # Pixel height
            )
            # Draw the rectangle on the provided surface (the game window)
            # using the GREEN color.
            pygame.draw.rect(surface, GREEN, segment_rect)

    # ... (other methods: update, change_direction, etc.) ...
```

### Calling Draw (`snake.py`)
Finally, call the snake's `draw` method inside the main game loop in `snake.py`, after clearing the screen.

```python
# snake.py
# ... (setup code) ...

snake = Snake()

while running:
    # ... (event handling) ...

    # --- Game Logic ---
    # (snake.update() will go here later)

    # --- Drawing ---
    screen.fill(BLACK) # Clear screen first
    snake.draw(screen) # Call the draw method, passing the screen surface
    # (food.draw(screen) will go here later)

    # ... (display flip, clock tick) ...
```

### Key Concepts:
- **`pygame.Rect(left, top, width, height)`:** Represents a rectangular area on the screen, defined by its top-left corner's pixel coordinates and its dimensions.
- **`pygame.draw.rect(surface, color, rect)`:** Draws a filled rectangle onto a surface.
- **Coordinate Conversion:** Essential step! Multiply grid coordinates (`segment_x`, `segment_y`) by `CELL_SIZE` to get the correct pixel positions for drawing.
- **Iteration:** Looping through `self.positions` ensures every segment of the snake is drawn.

🎨 Remember: Drawing in Pygame happens on a `surface`. You draw shapes/images onto it, then `flip()` the display to show the result.
''',

    4: '''📖 Study Uplink: Snake Echo 5 – Bringing the Snake to Life

A snake that doesn't move is just a line. Let's implement the `update` method to make it slither.

### Movement Logic (`snake_class.py`)
The core idea is simple: calculate where the head *should* be next, add that new position to the front of the `positions` list, and (usually) remove the last segment from the list.

```python
# snake_class.py
# Constants like GRID_WIDTH, GRID_HEIGHT are available

class Snake:
    def __init__(self):
        # ... (init code) ...
        self.grow_pending = False # Important for growth later

    def draw(self, surface):
        # ... (draw code) ...
        pass

    def update(self):
        # 1. Get the current head's grid coordinates
        current_head_x, current_head_y = self.positions[0]

        # 2. Determine the next head's coordinates based on self.direction
        if self.direction == 'UP':
            next_head_x = current_head_x
            next_head_y = current_head_y - 1
        elif self.direction == 'DOWN':
            next_head_x = current_head_x
            next_head_y = current_head_y + 1
        elif self.direction == 'LEFT':
            next_head_x = current_head_x - 1
            next_head_y = current_head_y
        elif self.direction == 'RIGHT':
            next_head_x = current_head_x + 1
            next_head_y = current_head_y
        else: # Should not happen, but handle defensively
            next_head_x, next_head_y = current_head_x, current_head_y

        new_head_pos = (next_head_x, next_head_y)

        # 3. Insert the new head at the beginning of the positions list
        self.positions.insert(0, new_head_pos)

        # 4. Handle growth or remove the tail
        if self.grow_pending:
            # If grow_pending is True (set by the grow method later),
            # we simply reset the flag and DO NOT remove the tail.
            # This makes the snake one segment longer.
            self.grow_pending = False
        else:
            # If not growing, remove the last segment to maintain length.
            self.positions.pop()

    def grow(self):
        # This method just sets a flag. The actual growth happens in update().
        self.grow_pending = True

    # ... (other methods: change_direction, collisions) ...
```

### Calling Update (`snake.py`)
Call `snake.update()` inside the main game loop in `snake.py`, within the game logic section.

```python
# snake.py
# ... (setup code) ...

snake = Snake()

while running:
    # ... (event handling) ...

    # --- Game Logic ---
    if not game_over: # Only update if the game isn't over
        snake.update() # Call the update method once per frame
        # (Collision checks will go here later)

    # --- Drawing ---
    screen.fill(BLACK)
    snake.draw(screen)
    # (food.draw(screen) will go here later)

    # ... (display flip, clock tick) ...
```

### Key Concepts:
- **List Manipulation:**
    - `list.insert(index, item)`: Adds `item` at the specified `index`. `insert(0, ...)` adds to the beginning.
    - `list.pop()`: Removes and returns the *last* item from the list.
- **State Management (`grow_pending`):** Using a flag (`grow_pending`) allows the `grow` method to signal the `update` method to modify its behavior (skip popping the tail) in the next frame. This decouples the *intent* to grow from the *action* of growing.
- **Game Loop Integration:** The `update` method encapsulates the snake's movement logic, making the main loop cleaner.

🚀 Pro Tip: Think of `update` as advancing the simulation one step forward in time for that object.
''',

    5: '''📖 Study Uplink: Snake Echo 6 – Controlling Your Snake

Let's give the player the reins. We need to handle keyboard input in `snake.py` and tell the snake object to change direction using a new method in `snake_class.py`.

### Changing Direction (`snake_class.py`)
Add the `change_direction` method to your `Snake` class. It needs to prevent the snake from immediately reversing.

```python
# snake_class.py

class Snake:
    def __init__(self):
        # ... (init code) ...
        pass

    # ... (draw, update, grow methods) ...

    def change_direction(self, new_direction):
        # Check if the new direction is valid and not the direct opposite
        # of the current direction. Prevents the snake from instantly
        # colliding with its own neck segment.
        if new_direction == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif new_direction == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        elif new_direction == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif new_direction == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

    # ... (collision methods) ...
```

### Handling Input (`snake.py`)
Modify the event handling part of your main loop in `snake.py`.

```python
# snake.py
# ... (setup code) ...

snake = Snake()
game_over = False # Assume game_over flag exists

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for key presses *only if the game is not over*
        elif event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_UP:
                snake.change_direction('UP') # Call the snake's method
            elif event.key == pygame.K_DOWN:
                snake.change_direction('DOWN')
            elif event.key == pygame.K_LEFT:
                snake.change_direction('LEFT')
            elif event.key == pygame.K_RIGHT:
                snake.change_direction('RIGHT')
        # Add restart logic later (e.g., check for SPACE when game_over is True)

    # ... (Game Logic: snake.update(), etc.) ...
    # ... (Drawing: screen.fill(), snake.draw(), etc.) ...
    # ... (display flip, clock tick) ...
```

### Key Concepts:
- **Event Loop (`pygame.event.get()`):** The central place to check for all user inputs (keyboard, mouse, etc.) and system events (like closing the window).
- **`event.type`:** Identifies the kind of event (e.g., `pygame.KEYDOWN` for a key press, `pygame.KEYUP` for release).
- **`event.key`:** For keyboard events, this identifies *which* key was pressed (e.g., `pygame.K_UP`, `pygame.K_LEFT`, `pygame.K_SPACE`).
- **Input Validation:** The logic inside `change_direction` prevents invalid moves (like reversing direction instantly). This makes the game playable.
- **Object Interaction:** The main loop detects input and *tells* the `snake` object what to do by calling its `change_direction` method.

🕹️ Pro Tip: Keep input handling in the main loop and let objects manage their own state changes based on that input.
''',

    6: '''📖 Study Uplink: Snake Echo 7 – Spawning Food

A snake's gotta eat! Let's create a `Food` class to represent the tasty pixels our snake will chase.

### The Food Blueprint (`food.py`)
Create a new file `food.py`.

```python
# food.py
# Constants like GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, RED are available
import pygame
import random # We need this for random positioning

class Food:
    def __init__(self):
        # Initialize position when the object is created.
        # We call reset() immediately to place it randomly.
        self.position = (0, 0) # Default placeholder
        self.reset() # Place it correctly from the start

    def draw(self, surface):
        # Draw the food as a simple rectangle
        x, y = self.position
        food_rect = pygame.Rect(
            x * CELL_SIZE,
            y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(surface, RED, food_rect) # Use RED color

    def reset(self, avoid_positions=None):
        # Move the food to a new random location on the grid.
        # Optionally takes a list of positions to avoid (the snake's body).
        if avoid_positions is None:
            avoid_positions = [] # Default to empty list if nothing to avoid

        # Keep trying random positions until we find an empty one
        while True:
            new_x = random.randint(0, GRID_WIDTH - 1)
            new_y = random.randint(0, GRID_HEIGHT - 1)
            new_pos = (new_x, new_y)

            # Check if the new position overlaps with any forbidden spots
            if new_pos not in avoid_positions:
                self.position = new_pos # Found a valid spot!
                break # Exit the while loop
```

### Using the Food (`snake.py`)
Instantiate and draw the food in `snake.py`.

```python
# snake.py
# ... (imports and setup) ...

# --- Game Objects ---
snake = Snake()
food = Food() # Create a Food object

# ... (game state, font setup) ...

while running:
    # ... (event handling) ...

    # --- Game Logic ---
    if not game_over:
        snake.update()
        # (Collision checks go here later)

    # --- Drawing ---
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen) # Draw the food object
    # (Score drawing goes here later)

    # ... (display flip, clock tick) ...
```

### Key Concepts:
- **`random.randint(a, b)`:** Generates a random integer between `a` and `b` (inclusive).
- **Avoiding Overlap:** The `reset` method takes an optional `avoid_positions` list. It keeps generating random coordinates until it finds one *not* in that list, ensuring food doesn't spawn inside the snake.
- **Instantiation:** Creating `food = Food()` runs the `__init__` method, which immediately calls `reset()` to place the first piece of food.

🍎 Pro Tip: Randomness adds replayability. Making randomness *smart* (like avoiding the snake) makes the game feel less frustrating.
''',

    7: '''📖 Study Uplink: Snake Echo 8 – Survival Mechanics

Time for consequences! Let's add collision detection. The snake needs to react to hitting walls, itself, and food.

### Collision Methods (`snake_class.py`)
Implement the collision check methods in the `Snake` class.

```python
# snake_class.py
# Constants GRID_WIDTH, GRID_HEIGHT are available

class Snake:
    # ... (init, draw, update, change_direction, grow) ...

    def check_wall_collision(self):
        # Get the head's coordinates
        head_x, head_y = self.positions[0]
        # Check if head is outside the grid boundaries
        hit_left_wall = head_x < 0
        hit_right_wall = head_x >= GRID_WIDTH
        hit_top_wall = head_y < 0
        hit_bottom_wall = head_y >= GRID_HEIGHT
        # Return True if any wall was hit
        return hit_left_wall or hit_right_wall or hit_top_wall or hit_bottom_wall

    def check_self_collision(self):
        # Get the head's coordinates
        head = self.positions[0]
        # Check if the head's position exists anywhere in the rest of the body
        # self.positions[1:] creates a slice containing all segments *except* the head
        return head in self.positions[1:]
```

### Integrating Checks (`snake.py`)
Update the main loop in `snake.py` to use these checks and handle food eating.

```python
# snake.py
# ... (setup, game objects: snake, food) ...

game_over = False
score = 0

while running:
    # ... (event handling) ...

    # --- Game Logic ---
    if not game_over:
        snake.update() # Move snake first

        # --- Collision Checks ---
        # 1. Check wall collision
        if snake.check_wall_collision():
            game_over = True
            print("Collision: Wall") # Optional debug print

        # 2. Check self collision (only if wall collision didn't happen)
        elif snake.check_self_collision():
            game_over = True
            print("Collision: Self") # Optional debug print

        # 3. Check food collision (only if no other collision happened)
        elif snake.positions[0] == food.position:
            print("Collision: Food") # Optional debug print
            score += 1
            snake.grow() # Tell the snake to grow on the next update
            # Reset food, avoiding the snake's current body
            food.reset(snake.positions)

    # --- Drawing ---
    # ... (fill screen, draw snake, food, score) ...

    # ... (display flip, clock tick) ...
```

### Key Concepts:
- **Collision Logic:** Breaking down checks (wall, self, food) makes the code easier to manage.
- **Order Matters:** Check for game-ending collisions *before* checking for food. If the snake hits a wall and the food simultaneously, the game should end.
- **`list[1:]` (Slicing):** Creates a new list containing elements from index 1 to the end. Useful for checking the head against the rest of the body.
- **State Change:** Collisions change the `game_over` flag, which affects subsequent logic in the loop. Eating food triggers `snake.grow()` and `food.reset()`.

🛑 Pro Tip: Clear, sequential checks prevent conflicting game states. Handle game-ending conditions first.
''',

    8: '''📖 Study Uplink: Snake Echo 9 – Scoring and Feedback

Players need to see their progress. Let's display the score.

### Score Constants (`constants.py`)
Ensure these are defined in `constants.py`:
```python
# constants.py
# ... (other constants) ...
WHITE = (255, 255, 255) # Color for the score text
SCORE_POS = (10, 10)   # Pixel coordinates for top-left corner of score text
FONT_SIZE = 24         # Size of the score font
```

### Font Setup (`snake.py`)
Initialize the font system and load a font in `snake.py` during setup.

```python
# snake.py
# ... (imports) ...

# --- Initialization ---
pygame.init()
pygame.font.init() # << Initialize the font module

# ... (screen setup, clock) ...

# --- Font Setup ---
# Load a system font. 'None' uses the default system font.
score_font = pygame.font.SysFont(None, FONT_SIZE)

# ... (game objects, game state) ...
```

### Drawing the Score (`snake.py`)
Inside the main loop's drawing section, render the score text and blit (draw) it onto the screen.

```python
# snake.py
# ... (setup) ...

score = 0 # Make sure score is initialized

while running:
    # ... (event handling, game logic including score += 1 on food collision) ...

    # --- Drawing ---
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)

    # --- Draw Score ---
    # 1. Render the text: Create a surface with the score text.
    #    f'Score: {score}' creates the string dynamically.
    #    True enables anti-aliasing (smoother text).
    #    WHITE is the text color.
    score_surface = score_font.render(f'Score: {score}', True, WHITE)

    # 2. Blit the text surface onto the main screen surface
    #    at the position defined by SCORE_POS.
    screen.blit(score_surface, SCORE_POS)

    # ... (game over drawing later) ...

    # --- Update Display ---
    pygame.display.flip()

    # ... (clock tick) ...
```

### Key Concepts:
- **`pygame.font.init()`:** Must be called before using any font functions.
- **`pygame.font.SysFont(name, size)`:** Loads a font available on the system. Using `None` for the name gets a default font.
- **`font.render(text, antialias, color, background=None)`:** Creates a new `Surface` object with the specified text rendered onto it.
    - `text`: The string to render.
    - `antialias`: Boolean for smooth edges (usually `True`).
    - `color`: The text color (RGB tuple).
    - `background`: Optional background color for the text surface.
- **`surface.blit(source_surface, destination_position)`:** Draws one surface onto another. Here, we draw the `score_surface` onto the main `screen` at `SCORE_POS`.

📊 Pro Tip: Keep UI elements like scores updated and clearly visible. It's essential player feedback.
''',

    9: '''📖 Study Uplink: Snake Echo 10 – Game Over and Restart

Every game needs an end... and often, a way to start again. Let's implement the Game Over screen and restart logic.

### Game Over Display (`snake.py`)
We need a way to show the "Game Over" message when the `game_over` flag is True. Let's create a helper function for this in `snake.py`.

```python
# snake.py
# ... (imports, constants, setup) ...

# --- Font Setup ---
score_font = pygame.font.SysFont(None, FONT_SIZE)
# Add fonts for Game Over text
game_over_font = pygame.font.SysFont(None, 48) # Larger font
restart_font = pygame.font.SysFont(None, 32)  # Smaller font for instructions

# ... (game objects, game state: running, game_over, score) ...

# --- Helper Functions ---
def show_game_over_screen(surface, current_score):
    # Render the text lines
    game_over_surf = game_over_font.render('GAME OVER', True, RED) # Use RED
    score_surf = restart_font.render(f'Final Score: {current_score}', True, WHITE)
    restart_surf = restart_font.render('Press SPACE to Restart', True, WHITE)

    # Calculate positions to center the text
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    game_over_rect = game_over_surf.get_rect(center=(center_x, center_y - 40))
    score_rect = score_surf.get_rect(center=(center_x, center_y))
    restart_rect = restart_surf.get_rect(center=(center_x, center_y + 40))

    # Blit the text onto the surface passed to the function
    surface.blit(game_over_surf, game_over_rect)
    surface.blit(score_surf, score_rect)
    surface.blit(restart_surf, restart_rect)

def reset_game():
    # Use 'global' to modify variables defined outside this function
    global snake, food, score, game_over
    print("Resetting game...") # Debug print
    snake = Snake() # Create a new snake
    food.reset(snake.positions) # Reset food, avoiding new snake
    score = 0
    game_over = False

# ... (Main Game Loop) ...
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Check for SPACE press *only if* game is over
            if game_over and event.key == pygame.K_SPACE:
                reset_game() # Call the reset function
            # Handle direction changes *only if* game is NOT over
            elif not game_over:
                # ... (direction change code from Echo 6) ...
                pass

    # --- Game Logic (only if not game over) ---
    if not game_over:
        # ... (snake.update(), collision checks) ...
        pass

    # --- Drawing ---
    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)
    # Draw Score (always show score)
    score_surface = score_font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, SCORE_POS)

    # --- Draw Game Over Screen (if applicable) ---
    if game_over:
        show_game_over_screen(screen, score) # Call the helper function

    # --- Update Display ---
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# ... (Quit Pygame) ...
```

### Key Concepts:
- **Game State (`game_over` flag):** Controls whether game logic runs or the game over screen shows.
- **Conditional Logic:** Input handling and game updates are now conditional based on the `game_over` state.
- **`surface.get_rect(center=(x, y))`:** A useful way to get a `Rect` object for a surface and position it based on its center point. Makes centering text easy.
- **`global` Keyword:** Needed inside `reset_game` to modify variables (`snake`, `food`, `score`, `game_over`) that were defined in the main script scope, not inside the function itself.
- **Restart:** Creates *new* instances of `Snake` and resets `Food`, `score`, and `game_over` to their initial states.

🔄 Pro Tip: Separating drawing logic (like `show_game_over_screen`) into functions keeps the main loop cleaner and more readable. Congratulations, Snaker! You've built a complete game cycle.
'''
}
