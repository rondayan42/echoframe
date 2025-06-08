# constants.py: Define game settings and colors here.
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
GAME_OVER_FONT_SIZE = 48 # Larger font for "GAME OVER"
RESTART_FONT_SIZE = 22 