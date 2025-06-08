# slith_minigames.py
"""
Cyberpunk minigames for the Slith Pet - Complete rewrite with improved visuals and stability
Features:
- Robust error handling and logging
- Improved pixel art sprites with dynamic generation
- Consistent game mechanics
- Enhanced visual effects
"""

import pygame
import random
import math
import time
import os
import logging
from typing import Tuple, List, Dict, Any, Optional, Union, Callable



# --- Setup Logging ---
log_file_path = os.path.join(os.path.dirname(__file__), 'slith_minigames.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# --- Import Constants or Use Fallbacks ---
try:
    from slith_constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLORS, PIXEL_SCALE
    logger.info("Successfully imported base constants")
    try:
        from slith_utils import draw_text as util_draw_text
        from slith_utils import generate_beep
        logger.info("Successfully imported utility functions")
    except ImportError:
        logger.warning("Utilities not found. Using fallback drawing functions.")
        # Fallback function definitions will follow
except ImportError:
    logger.warning("Constants not found. Using fallback values.")
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS = 800, 800, 60
    COLORS = {
        'bg': (20, 12, 28),        # Darker cyberpunk background
        'bg_dark': (10, 8, 16),    # Even darker background for UI elements
        'neon': (255, 221, 0),     # Primary yellow
        'accent': (255, 105, 180), # Hot pink accent
        'text': (220, 220, 255),   # Bluish white text
        'text_dark': (120, 120, 160), # Dark bluish gray text
        'danger': (255, 50, 50),   # Red for warnings/danger
        'warning': (255, 165, 0),  # Orange for warnings
        'cyan': (0, 255, 255),     # Cyan for highlights
        'terminal': (0, 200, 80),  # Terminal green
        'grid': (40, 40, 60),      # Grid line color
        'highlight': (0, 255, 200), # Highlight color
        'hacker_text': (0, 255, 0), # Matrix/hacker text
    }
    PIXEL_SCALE = 2

# --- Script Directory ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Script directory: {SCRIPT_DIR}")

# --- Fallback Utility Functions ---
def util_draw_text(surface, text, font, color, x, y, centered=True, **kwargs):
    """Draw text with centering option and color validation"""
    try:
        # --- Color Validation and Fallback ---
        default_color = (255, 255, 255) # White fallback
        error_color = (255, 0, 0) # Red for obvious errors if font exists
        valid_color = default_color # Start with default

        if isinstance(color, (tuple, list)) and len(color) >= 3:
            # Check if components are integers within range
            if all(isinstance(c, int) and 0 <= c <= 255 for c in color[:3]):
                valid_color = color # Keep original alpha if present
            else:
                logger.warning(f"Invalid color component type/range in util_draw_text: {color}. Using error color.")
                if font: # Only use error color if font is valid
                     valid_color = error_color
                else:
                     valid_color = default_color # Fallback to white if font is bad too
        elif color is not None:
            logger.warning(f"Invalid color format in util_draw_text: {color} (Type: {type(color)}). Using error/default color.")
            if font:
                valid_color = error_color
            else:
                valid_color = default_color
        else: # color is None
             logger.warning(f"Received None color in util_draw_text. Using default.")
             valid_color = default_color
        # --- END Color Validation ---

        # Ensure font is valid before rendering
        if not font or not hasattr(font, 'render'):
             logger.error(f"Invalid font object passed to util_draw_text.")
             placeholder_rect = pygame.Rect(x, y, 10, 10)
             pygame.draw.rect(surface, error_color, placeholder_rect, 1) # Draw red outline
             return placeholder_rect

        # Use only RGB for rendering, alpha handled separately if needed
        render_color = valid_color[:3]
        surf = font.render(text, True, render_color)
        rect = surf.get_rect()

        # Apply alpha if the original valid color had it
        if len(valid_color) > 3:
             surf.set_alpha(valid_color[3])

        if centered:
            rect.center = (x, y)
        elif kwargs.get('right_aligned'):
            rect.centery = y
            rect.right = x
        else:
            rect.topleft = (x, y)

        surface.blit(surf, rect)
        return rect
    except Exception as e:
        logger.error(f"Text drawing error: {e}", exc_info=True) # Log traceback
        try:
            pygame.draw.circle(surface, (255,0,0), (int(x), int(y)), 5)
        except: pass
        return pygame.Rect(x, y, 10, 10)


def generate_beep(frequency=440, duration_ms=100, volume=0.1):
    """Generate a simple beep sound"""
    try:
        import numpy
        from pygame import sndarray, mixer
        
        if not mixer.get_init():
            mixer.init()
            
        sample_rate = 44100
        num_samples = int(sample_rate * duration_ms / 1000.0)
        buf = numpy.zeros((num_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            sine_val = math.sin(2.0 * math.pi * frequency * t)
            sample_val = int(max_sample * volume * sine_val)
            buf[i][0] = sample_val
            buf[i][1] = sample_val
            
        sound = sndarray.make_sound(buf)
        return sound
    except Exception as e:
        logger.warning(f"Sound generation failed: {e}")
        
        class DummySound:
            def play(self): pass
        return DummySound()

# --- Drawing Utilities ---
def draw_pixel_rect(surface, color, rect, pixel_size):
    """Draw a pixelated rectangle with color check"""
    try:
        # --- Color Validation and Fallback ---
        default_color = (255, 0, 0) # Red fallback for visibility
        valid_color = default_color

        if isinstance(color, (tuple, list)) and len(color) >= 3:
             if all(isinstance(c, int) and 0 <= c <= 255 for c in color[:3]):
                 valid_color = color
             else:
                 logger.warning(f"Invalid color component in draw_pixel_rect: {color}. Using RED.")
        elif color is not None:
             logger.warning(f"Invalid color format in draw_pixel_rect: {color}. Using RED.")
        else: # color is None
             logger.warning(f"draw_pixel_rect received None color. Using RED.")
        # --- END Color Validation ---

        x, y, w, h = rect
        has_alpha = len(valid_color) > 3

        if w <= 0 or h <= 0: return

        x_aligned = (x // pixel_size) * pixel_size
        y_aligned = (y // pixel_size) * pixel_size
        w_aligned = max(pixel_size, ((w + pixel_size - 1) // pixel_size) * pixel_size)
        h_aligned = max(pixel_size, ((h + pixel_size - 1) // pixel_size) * pixel_size)

        if has_alpha:
            temp_surf = pygame.Surface((w_aligned, h_aligned), pygame.SRCALPHA)
            temp_surf.fill(valid_color)
            surface.blit(temp_surf, (x_aligned, y_aligned))
        else:
            pygame.draw.rect(surface, valid_color[:3], (x_aligned, y_aligned, w_aligned, h_aligned))

    except Exception as e:
        logger.error(f"Error drawing rectangle: {e}", exc_info=True)
def draw_pixel_circle(surface, color, center, radius, pixel_size):
    """Draw a pixelated circle with robust color handling"""
    try:
        # --- Color Validation and Fallback ---
        default_color = (255, 0, 0) # Red fallback
        valid_color = default_color

        if isinstance(color, (tuple, list)) and len(color) >= 3:
             if all(isinstance(c, int) and 0 <= c <= 255 for c in color[:3]):
                 valid_color = color
             else:
                 logger.warning(f"Invalid color component in draw_pixel_circle: {color}. Using RED.")
        elif color is not None:
             logger.warning(f"Invalid color format in draw_pixel_circle: {color}. Using RED.")
        else: # color is None
             logger.warning(f"draw_pixel_circle received None color. Using RED.")
        # --- END Color Validation ---

        has_alpha = len(valid_color) > 3
        cx, cy = center
        radius_sqr = radius * radius

        left = ((cx - radius) // pixel_size) * pixel_size
        top = ((cy - radius) // pixel_size) * pixel_size
        right = ((cx + radius + pixel_size) // pixel_size) * pixel_size
        bottom = ((cy + radius + pixel_size) // pixel_size) * pixel_size

        for x in range(left, right, pixel_size):
            for y in range(top, bottom, pixel_size):
                dx = (x + pixel_size/2) - cx
                dy = (y + pixel_size/2) - cy
                if dx*dx + dy*dy <= radius_sqr:
                    if has_alpha:
                        temp_surf = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
                        temp_surf.fill(valid_color)
                        surface.blit(temp_surf, (x, y))
                    else:
                        pygame.draw.rect(surface, valid_color[:3], (x, y, pixel_size, pixel_size))
    except Exception as e:
        logger.error(f"Error drawing circle: {e}", exc_info=True)

def draw_pixel_line(surface, color, start, end, pixel_size):
    """Draw a pixelated line with color check"""
    try:
        # --- Color Validation and Fallback ---
        default_color = (255, 0, 0) # Red fallback
        valid_color = default_color

        if isinstance(color, (tuple, list)) and len(color) >= 3:
             if all(isinstance(c, int) and 0 <= c <= 255 for c in color[:3]):
                 valid_color = color
             else:
                 logger.warning(f"Invalid color component in draw_pixel_line: {color}. Using RED.")
        elif color is not None:
             logger.warning(f"Invalid color format in draw_pixel_line: {color}. Using RED.")
        else: # color is None
             logger.warning(f"draw_pixel_line received None color. Using RED.")
        # --- END Color Validation ---

        x1, y1 = start
        x2, y2 = end

        x1_a = (x1 // pixel_size) * pixel_size
        y1_a = (y1 // pixel_size) * pixel_size
        x2_a = (x2 // pixel_size) * pixel_size
        y2_a = (y2 // pixel_size) * pixel_size

        dx = abs(x2_a - x1_a)
        dy = abs(y2_a - y1_a)
        sx = pixel_size if x1_a < x2_a else -pixel_size
        sy = pixel_size if y1_a < y2_a else -pixel_size
        err = dx - dy
        x, y = x1_a, y1_a
        max_steps = (dx + dy) // pixel_size + 2 # Safety break

        for _ in range(max_steps):
            draw_pixel_rect(surface, valid_color, (x, y, pixel_size, pixel_size), pixel_size)
            if x == x2_a and y == y2_a: break
            e2 = 2 * err
            if e2 >= -dy:
                if x == x2_a: break
                err -= dy
                x += sx
            if e2 <= dx:
                if y == y2_a: break
                err += dx
                y += sy
    except Exception as e:
        logger.error(f"Error drawing line: {e}", exc_info=True)

def create_pixel_sprite(design, scale=1, color_map=None):
    """
    Create a pixel sprite from a design matrix
    
    Args:
        design: List of strings representing pixel rows (e.g., ["000", "010", "000"])
        scale: Scaling factor (int)
        color_map: Dictionary mapping characters to RGB color tuples
        
    Returns:
        pygame.Surface: The rendered sprite
    """
    try:
        # Default color map if not provided
        if color_map is None:
            color_map = {
                '1': COLORS.get('neon', (255, 221, 0)),
                '2': COLORS.get('accent', (255, 105, 180)),
                '3': COLORS.get('cyan', (0, 255, 255)),
                '4': COLORS.get('danger', (255, 50, 50)),
                '5': COLORS.get('terminal', (0, 200, 80)),
                '0': (0, 0, 0, 0)  # Transparent
            }
        
        # Calculate dimensions
        height = len(design)
        width = max(len(row) for row in design) if height > 0 else 0
        
        if width == 0 or height == 0:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        
        # Create surface
        surf = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
        
        # Draw pixels
        for y, row in enumerate(design):
            for x, char in enumerate(row):
                if char in color_map and char != '0':
                    # Get color and ensure it's valid (RGB or RGBA)
                    color = color_map[char]
                    if color is None:
                        # Default to red if color is None (for visibility of issues)
                        color = (255, 0, 0)
                    # Ensure color has 3 or 4 components
                    if not hasattr(color, '__len__') or len(color) < 3:
                        color = (255, 0, 0)  # Default to red
                    elif len(color) == 3:
                        # RGB color (without alpha)
                        pygame.draw.rect(
                            surf, 
                            color, 
                            (x * scale, y * scale, scale, scale)
                        )
                    else:
                        # RGBA color (with alpha)
                        temp_surf = pygame.Surface((scale, scale), pygame.SRCALPHA)
                        temp_surf.fill(color)
                        surf.blit(temp_surf, (x * scale, y * scale))
        
        # Optional: Add a glow effect
        try:
            glow_surf = pygame.Surface((width * scale + 4, height * scale + 4), pygame.SRCALPHA)
            glow_surf.blit(surf, (2, 2))
            
            # Simple blur effect
            for _ in range(1):
                temp = pygame.transform.smoothscale(glow_surf, (glow_surf.get_width() * 2, glow_surf.get_height() * 2))
                glow_surf = pygame.transform.smoothscale(temp, (glow_surf.get_width(), glow_surf.get_height()))
            
            glow_surf.set_alpha(100)
            
            final_surf = pygame.Surface((width * scale + 4, height * scale + 4), pygame.SRCALPHA)
            final_surf.blit(glow_surf, (0, 0))
            final_surf.blit(surf, (2, 2))
            
            return final_surf
        except Exception as e:
            logger.warning(f"Glow effect failed, falling back to basic sprite: {e}")
            return surf
    except Exception as e:
        logger.error(f"Error creating sprite: {e}")
        # Return a minimal fallback sprite
        fallback = pygame.Surface((scale, scale), pygame.SRCALPHA)
        fallback.fill((255, 0, 0, 128))  # Semi-transparent red
        return fallback

def create_sprite_sheet(designs, scale=1, color_map=None):
    """Create a sprite sheet from multiple designs"""
    sprites = []
    for design in designs:
        sprites.append(create_pixel_sprite(design, scale, color_map))
    return sprites

def lerp_color(color1, color2, t):
    """Linear interpolation between two colors with robust error handling"""
    try:
        # Ensure colors are valid
        if color1 is None:
            color1 = (255, 0, 0)
        if color2 is None:
            color2 = (255, 0, 0)
            
        # Ensure t is in range [0, 1]
        t = max(0.0, min(1.0, t))
        
        # Check for valid color length (at least RGB)
        if not hasattr(color1, '__len__') or len(color1) < 3:
            color1 = (255, 0, 0)
        if not hasattr(color2, '__len__') or len(color2) < 3:
            color2 = (255, 0, 0)
            
        # Interpolate RGB values
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        
        # Handle alpha if both colors have it
        if len(color1) > 3 and len(color2) > 3:
            a = int(color1[3] + (color2[3] - color1[3]) * t)
            return (r, g, b, a)
        return (r, g, b)
    except Exception as e:
        logger.error(f"Error in lerp_color: {e}")
        return (255, 0, 0)  # Return red as default error color
# --- Sprite Design Definitions ---
SPRITE_DESIGNS = {
    'player': [
        "00000111110000000",
        "00011122211100000",
        "00112223222110000",
        "01122332233211000",
        "01233222233321000",
        "12332222223332100",
        "12322222222332100",
        "12322222222332100",
        "12332222223332100",
        "01233333333321000",
        "01122333322110000",
        "00112222221100000",
        "00011111111000000",
    ],
    'enemy': [
        "00000444440000000",
        "00044422244400000",
        "00422233322240000",
        "04223322332224000",
        "04232222222324000",
        "42322222222232400",
        "42322222222232400",
        "42322222222232400",
        "42322222222232400",
        "04232222222324000",
        "04223322332224000",
        "00422233322240000",
        "00044422244400000",
    ],
    'barrier': [
        "00011111111100000",
        "00122222222210000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "01233333333321000",
        "00122222222210000",
        "00011111111100000",
    ],
    'collectible': [
        "00000033000000",
        "00003333300000",
        "00033313330000",
        "00331113113000",
        "03311111133300",
        "03111111111300",
        "03111111111300",
        "03111111111300",
        "03311111133300",
        "00331113113000",
        "00033313330000",
        "00003333300000",
        "00000033000000",
    ],
    'heart': [
        "00022000220000",
        "02222022222000",
        "22222222222200",
        "22222222222200",
        "02222222222200",
        "00222222222000",
        "00022222220000",
        "00002222200000",
        "00000222000000",
        "00000020000000",
    ],
    'node': [
        "0000111111000000",
        "0011222222110000",
        "0122233332221000",
        "1223333333322100",
        "1233333333332100",
        "1233333333332100",
        "1233333333332100",
        "1233333333332100",
        "1233333333332100",
        "1233333333332100",
        "1223333333322100",
        "0122233332221000",
        "0011222222110000",
        "0000111111000000",
    ],
}

# --- Base Minigame Class ---
class BaseMinigame:
    """Base class for all minigames"""
    
    def __init__(self, screen, clock):
        """Initialize the minigame"""
        logger.debug(f"Initializing {self.__class__.__name__}")
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()
        self.running = False
        self.game_over = False
        self.score = 0
        self.bits_earned = 0
        self.time_elapsed = 0
        
        # Load fonts
        self.load_fonts()
        
        # Sound effects
        self.success_sound = generate_beep(880, 50, 0.1)
        self.fail_sound = generate_beep(220, 150, 0.1)  
        self.quit_sound = generate_beep(440, 80, 0.1)
        
        # Animation variables
        self.animation_frame = 0
        self.animation_timer = 0
        self.particles = []
        
        # Instructions and title (to be overridden)
        self.title = self.__class__.__name__
        self.instructions = ["Game instructions missing", "Press SPACE to start"]
    
    def load_fonts(self):
        """Load game fonts"""
        try:
            font_path = os.path.join(SCRIPT_DIR, 'PressStart2P-Regular.ttf')
            self.game_font_small = pygame.font.Font(font_path, 8 * PIXEL_SCALE)
            self.game_font_medium = pygame.font.Font(font_path, 10 * PIXEL_SCALE)
            self.game_font_large = pygame.font.Font(font_path, 16 * PIXEL_SCALE)
        except (IOError, pygame.error) as e:
            logger.warning(f"Font not found: {e}, using system fonts")
            # Fallback to system fonts
            self.game_font_small = pygame.font.SysFont('Arial', 10 * PIXEL_SCALE)
            self.game_font_medium = pygame.font.SysFont('Arial', 14 * PIXEL_SCALE)
            self.game_font_large = pygame.font.SysFont('Arial', 20 * PIXEL_SCALE)
    
    def handle_input(self, events):
        """Handle player input"""
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Quit event received")
                self.running = False
                if self.quit_sound:
                    self.quit_sound.play()
                return False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                logger.info("Escape key pressed")
                self.running = False
                if self.quit_sound:
                    self.quit_sound.play()
                return False
                
        return True
    
    def show_instructions(self, title, instructions):
        logger.debug(f"Showing instructions for {title}")
        running = True
        instruction_start_time = time.time()
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    logger.info("Instructions dismissed via quit/ESC")
                    self.running = False
                    return False
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    logger.info("Instructions dismissed via SPACE")
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    logger.info("Instructions dismissed via click")
                    running = False
            
            # Minimum display time for instructions (0.5 seconds)
            if time.time() - instruction_start_time < 0.5:
                self.clock.tick(FPS)
                continue
                
            try:
                # Draw instructions
                self.screen.fill(COLORS.get('bg_dark', (10, 8, 16)))
                
                # Semi-transparent overlay
                try:
                    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    self.screen.blit(overlay, (0, 0))
                except Exception as e:
                    logger.error(f"Error creating overlay: {e}")
                    # Fallback to solid background
                    self.screen.fill(COLORS.get('bg_dark', (10, 8, 16)))
                
                # Instruction box
                box_width = int(self.width * 0.7)
                box_height = int(self.height * 0.7)
                box_x = (self.width - box_width) // 2
                box_y = (self.height - box_height) // 2
                
                # Draw box background
                pygame.draw.rect(
                    self.screen,
                    COLORS.get('bg_dark', (10, 8, 16)), 
                    (box_x, box_y, box_width, box_height)
                )
                
                # Draw border as separate lines
                border_color = COLORS.get('cyan', (0, 255, 255))
                if border_color is None:
                    border_color = (0, 255, 255)  # Default cyan if None
                    
                # Top border
                pygame.draw.rect(self.screen, border_color, 
                            (box_x, box_y, box_width, PIXEL_SCALE))
                # Bottom border
                pygame.draw.rect(self.screen, border_color, 
                            (box_x, box_y + box_height - PIXEL_SCALE, box_width, PIXEL_SCALE))
                # Left border
                pygame.draw.rect(self.screen, border_color, 
                            (box_x, box_y, PIXEL_SCALE, box_height))
                # Right border
                pygame.draw.rect(self.screen, border_color, 
                            (box_x + box_width - PIXEL_SCALE, box_y, PIXEL_SCALE, box_height))
                
                # Draw title
                title_color = COLORS.get('neon', (255, 221, 0))
                if title_color is None:
                    title_color = (255, 221, 0)  # Default yellow if None
                    
                util_draw_text(self.screen, title, self.game_font_large, 
                            title_color, 
                            self.width // 2, box_y + 40, True)
                
                # Draw instructions
                line_spacing = 25 * PIXEL_SCALE
                start_y = box_y + 100
                
                text_color = COLORS.get('text', (220, 220, 255))
                if text_color is None:
                    text_color = (220, 220, 255)  # Default text color if None
                    
                for i, line in enumerate(instructions):
                    util_draw_text(self.screen, line, self.game_font_small, 
                                text_color, 
                                self.width // 2, start_y + i * line_spacing, True)
                
                # Continue prompt 
                prompt_text = "[ Press SPACE or CLICK to continue ]"
                prompt_color = COLORS.get('accent', (255, 105, 180))
                if prompt_color is None:
                    prompt_color = (255, 105, 180)  # Default pink if None
                    
                util_draw_text(self.screen, prompt_text, self.game_font_small, 
                            prompt_color, self.width // 2, box_y + box_height - 40, True)
                    
            except Exception as e:
                logger.error(f"Error in show_instructions: {e}")
                # Draw a simple error message if the fancy version fails
                self.screen.fill((0, 0, 0))
                if hasattr(self, 'game_font_medium') and self.game_font_medium:
                    util_draw_text(self.screen, "Press SPACE to continue", 
                                self.game_font_medium, (255, 255, 255),
                                self.width // 2, self.height // 2, True)
                
            pygame.display.flip()
            self.clock.tick(FPS)
    
        return True
    
    def update(self, dt):
        """Update game state"""
        self.time_elapsed += dt
        self.animation_timer += dt
        
        # Update animation frame every 0.1 seconds
        if self.animation_timer >= 0.1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        # Update particles
        self.update_particles(dt)
    
    def draw(self):
        """Draw the game"""
        self.screen.fill(COLORS.get('bg_dark'))
        
        # Draw background effects
        self.draw_cyber_background(self.time_elapsed)
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw particles
        self.draw_particles()
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Score
        util_draw_text(self.screen, f"SCORE: {self.score}", 
                     self.game_font_medium, COLORS.get('neon'),
                     10, 10, False)
        
        # Time
        minutes = int(self.time_elapsed // 60)
        seconds = int(self.time_elapsed % 60)
        util_draw_text(self.screen, f"TIME: {minutes:02d}:{seconds:02d}", 
                     self.game_font_medium, COLORS.get('neon'),
                     self.width - 10, 10, False, right_aligned=True)
    
    def draw_cyber_background(self, time_elapsed):
        """Draw cyberpunk-style background effects"""
        # Draw grid
        self.draw_grid(time_elapsed)
        
        # Digital rain effect (optional)
        # self.draw_digital_rain(time_elapsed)
    
    def draw_grid(self, time_elapsed):
        """Draw perspective grid background"""
        horizon_y = self.height * 0.6
        grid_color = COLORS.get('grid')
        cell_size = 40 * PIXEL_SCALE
        
        # Scrolling effect
        scroll_offset = time_elapsed * 20 % cell_size
        
        # Horizontal lines
        for i in range(int(self.height / cell_size) + 2):
            y = horizon_y + i * cell_size - scroll_offset
            if y >= self.height:
                continue
                
            alpha = max(0, int(255 * (1 - y / self.height)))
            pygame.draw.line(self.screen, (*grid_color[:3], alpha), 
                           (0, int(y)), (self.width, int(y)),
                           max(1, PIXEL_SCALE // 2))
        
        # Vertical lines
        vanishing_x = self.width // 2
        for i in range(-15, 16):
            if i == 0:
                continue
                
            start_x = vanishing_x + i * cell_size
            end_x = vanishing_x + i * cell_size * 3  # Perspective effect
            
            alpha = max(0, int(255 * (1 - abs(i) / 15)))
            pygame.draw.line(self.screen, (*grid_color[:3], alpha),
                           (start_x, horizon_y), (end_x, self.height),
                           max(1, PIXEL_SCALE // 2))
    
    def create_particle(self, x, y, color, size=2, duration=1.0, speed_x=0, speed_y=0):
        """Create a particle effect"""
        return {
            'x': x,
            'y': y,
            'color': color,
            'size': size * PIXEL_SCALE,
            'duration': duration,
            'timer': 0,
            'speed_x': speed_x,
            'speed_y': speed_y,
            'alpha': 255
        }
    
    def update_particles(self, dt):
        """Update particle positions and lifetimes"""
        # Filter out expired particles
        remaining_particles = []
        
        for p in self.particles:
            p['timer'] += dt
            
            if p['timer'] < p['duration']:
                # Update position
                p['x'] += p['speed_x'] * dt
                p['y'] += p['speed_y'] * dt
                
                # Fade out particles near the end of their life
                fade_start = p['duration'] * 0.7
                if p['timer'] > fade_start:
                    fade_pct = (p['timer'] - fade_start) / (p['duration'] - fade_start)
                    p['alpha'] = int(255 * (1 - fade_pct))
                
                remaining_particles.append(p)
        
        self.particles = remaining_particles
    
    def draw_particles(self):
        for p in self.particles:
            try:
                if p.get('alpha', 0) <= 0:
                    continue
                
                # Make sure color is valid
                color = p.get('color')
                if color is None:
                    color = (255, 0, 0)  # Default to red for visibility
                    
                # Draw particle with glow effect
                glow_size = int(p.get('size', 2) * 2)
                glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                # Create alpha color values safely
                alpha = p.get('alpha', 255)
                color_rgb = color[:3] if hasattr(color, '__len__') and len(color) >= 3 else (255, 0, 0)
                color_with_alpha = (*color_rgb, alpha)
                glow_color = (*color_rgb, alpha // 3)
                
                # Inner particle
                pygame.draw.circle(glow_surf, color_with_alpha, 
                                (glow_size // 2, glow_size // 2), 
                                p.get('size', 2) // 2)
                
                # Outer glow
                pygame.draw.circle(glow_surf, glow_color,
                                (glow_size // 2, glow_size // 2),
                                p.get('size', 2))
                
                # Blit to screen
                self.screen.blit(glow_surf, 
                            (int(p.get('x', 0) - glow_size // 2), 
                                int(p.get('y', 0) - glow_size // 2)))
            except Exception as e:
                logger.error(f"Error drawing particle: {e}")
                continue
    def calculate_bits(self):
        """Calculate bits earned based on score and time"""
        try:
            # Base formula: score / 10
            base_bits = max(0, int(self.score / 10))
            
            # Time bonus if under 60 seconds
            time_bonus = 0
            if 0 < self.time_elapsed < 60:
                time_bonus = int((60 - self.time_elapsed) / 6)
            
            self.bits_earned = base_bits + time_bonus
            logger.debug(f"Score={self.score}, Time={self.time_elapsed:.2f}, Bits={self.bits_earned}")
        except Exception as e:
            logger.error(f"Error calculating bits: {e}")
            self.bits_earned = 0
    
    def draw_game_over(self, show_continue=True):
        """Draw game over screen"""
        try:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            util_draw_text(self.screen, "GAME OVER", self.game_font_large,
                         COLORS.get('danger'), 
                         self.width // 2, self.height // 2 - 60, True)
            
            # Score
            util_draw_text(self.screen, f"SCORE: {self.score}", 
                         self.game_font_medium, COLORS.get('neon'),
                         self.width // 2, self.height // 2, True)
            
            # Bits earned
            util_draw_text(self.screen, f"SNAKER_BITS EARNED: {self.bits_earned}",
                         self.game_font_medium, COLORS.get('accent'),
                         self.width // 2, self.height // 2 + 30, True)
            
            # Continue prompt
            if show_continue:
                prompt_alpha = int(128 + 127 * math.sin(time.time() * 3))
                prompt_color = (*COLORS.get('text')[:3], prompt_alpha)
                
                prompt_surf = self.game_font_small.render("Press ESC to continue", True, prompt_color[:3])
                prompt_surf.set_alpha(prompt_alpha)
                prompt_rect = prompt_surf.get_rect(center=(self.width // 2, self.height // 2 + 80))
                self.screen.blit(prompt_surf, prompt_rect)
                
        except Exception as e:
            logger.error(f"Error drawing game over: {e}")
    
    def run(self):
        """Main game loop"""
        logger.info(f"Starting {self.__class__.__name__}")
        self.running = True
        self.bits_earned = 0
        self.time_elapsed = 0
        self.game_over = False
        last_time = time.time()

        # Show instructions
        if not self.show_instructions(self.title, self.instructions):
            return self.score, self.bits_earned

        # --- Fade in ---
        try:
            # Create fade surface
            fade_surface = pygame.Surface((self.width, self.height))
            # --- ADDED: Define fade color with fallback ---
            fade_color = COLORS.get('bg_dark', (0, 0, 0)) # Use bg_dark or black fallback
            if not isinstance(fade_color, (tuple, list)) or len(fade_color) < 3:
                 logger.warning(f"Invalid fade_color {fade_color} in fade-in. Using black.")
                 fade_color = (0, 0, 0)
            # --- END ADDED ---
            fade_surface.fill(fade_color[:3]) # Use only RGB for fill

            # Fade from black
            for alpha in range(255, 0, -15):
                self.draw() # Draw the current game state underneath
                fade_surface.set_alpha(alpha)
                self.screen.blit(fade_surface, (0, 0))
                pygame.display.flip()
                self.clock.tick(FPS)
        except Exception as e:
            logger.error(f"Error during fade-in: {e}", exc_info=True)
        # --- End Fade in ---

        # Main game loop
        try:
            while self.running:
                # Calculate delta time
                current_time = time.time()
                dt = min(current_time - last_time, 0.1)  # Cap dt
                last_time = current_time

                # Process events
                events = pygame.event.get()
                if not self.handle_input(events):
                    break # Exit loop if handle_input returns False (e.g., ESC pressed)

                # Update game state
                self.update(dt)

                # Draw everything
                self.draw()

                # Update display
                pygame.display.flip()

                # Cap frame rate
                self.clock.tick(FPS)

        except Exception as e:
            logger.critical(f"Error in game loop: {e}", exc_info=True)
            # Display error message on screen
            try:
                 error_bg_color = COLORS.get('danger', (255, 0, 0))
                 error_text_color = COLORS.get('text', (255, 255, 255))
                 self.screen.fill(error_bg_color)
                 util_draw_text(self.screen, "Game Error!", self.game_font_large,
                               error_text_color, self.width // 2, self.height // 2 - 40, True)
                 # Try to display specific error type/message if possible
                 error_lines = [f"Error: {type(e).__name__}", str(e)]
                 for i, line in enumerate(error_lines):
                      util_draw_text(self.screen, line, self.game_font_small,
                                    error_text_color, self.width // 2, self.height // 2 + i*20, True)

                 util_draw_text(self.screen, "Press ESC to exit", self.game_font_medium,
                               error_text_color, self.width // 2, self.height // 2 + 60, True)
                 pygame.display.flip()

                 # Wait for ESC key press to exit after error
                 waiting_for_esc = True
                 while waiting_for_esc:
                     for event in pygame.event.get():
                         if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                             waiting_for_esc = False
                     self.clock.tick(10) # Keep Pygame responsive
            except Exception as draw_err:
                 logger.error(f"Error drawing error screen: {draw_err}") # Log error during error display
            finally:
                 self.running = False # Ensure loop terminates after error

        finally:
            # Calculate bits earned regardless of how the loop ended (error or normal exit)
            self.calculate_bits()

            # --- Fade out ---
            # Only fade if the game wasn't terminated abruptly by an error screen needing ESC
            if not self.game_over and self.running == False: # Check if exited normally (e.g., via ESC in handle_input)
                 try:
                     # Create fade surface
                     fade_surface = pygame.Surface((self.width, self.height))
                     # --- ADDED: Define fade color with fallback ---
                     fade_color = COLORS.get('bg_dark', (0, 0, 0)) # Use bg_dark or black fallback
                     if not isinstance(fade_color, (tuple, list)) or len(fade_color) < 3:
                          logger.warning(f"Invalid fade_color {fade_color} in fade-out. Using black.")
                          fade_color = (0, 0, 0)
                     # --- END ADDED ---
                     fade_surface.fill(fade_color[:3]) # Use only RGB for fill

                     # Fade to black
                     for alpha in range(0, 255, 15):
                         # It's often better to draw the *last valid game frame* underneath the fade
                         # If self.draw() might error here, consider drawing a static image or just the fade
                         try:
                              self.draw() # Draw the final game state
                         except Exception as draw_err_fade:
                              logger.error(f"Error drawing final frame during fade-out: {draw_err_fade}")
                              self.screen.fill(fade_color[:3]) # Fallback: just fill screen if draw fails

                         fade_surface.set_alpha(alpha)
                         self.screen.blit(fade_surface, (0, 0))
                         pygame.display.flip()
                         self.clock.tick(FPS)
                 except Exception as e:
                     logger.error(f"Error during fade-out: {e}", exc_info=True)
            # --- End Fade out ---

            logger.info(f"{self.__class__.__name__} finished. Score: {self.score}, Bits: {self.bits_earned}")
            return self.score, self.bits_earned
# --- NodeDefender Game ---
class NodeDefenderGame(BaseMinigame):
    """
    Node Defender Game
    Protect your data node from cyber invaders by placing barriers
    """
    
    def __init__(self, screen, clock):
        super().__init__(screen, clock)

        # Set title and instructions
        self.title = "NODE DEFENDER"
        self.instructions = [
            "Protect your data node from cyber-drones!",
            "",
            "- Click to place barriers (cost: 10 points)",
            "- Barriers: Standard, Reflective, Explosive",
            "- Press 1-3 to change barrier type",
            "- Press G to toggle grid display",
            "- Game over if node health reaches 0",
            "",
            "Press SPACE or click to start"
        ]

        # Game specific variables
        self.node_health = 100
        self.node_pos = (self.width // 2, self.height - 100 * PIXEL_SCALE)
        self.barriers = []
        self.enemies = []
        self.max_barriers = 7
        self.barrier_cost = 10
        self.wave = 0
        self.wave_timer = 0
        self.spawn_timer = 0
        self.barrier_cooldown = 0
        self.mouse_pos = (0, 0)
        self.grid_visible = True
        self.barrier_preview = None

        # --- ADDED: Start score at 10 ---
        self.score = 10 # Start with enough points for one barrier
        # --- END ADDED ---


        # Barrier types
        self.barrier_types = ['standard', 'reflective', 'explosive']
        self.current_barrier_type = 'standard'

        # Enemy types
        self.enemy_types = ['standard', 'fast', 'tank']

        # Sounds
        self.barrier_sound = generate_beep(880, 80, 0.15)
        self.enemy_hit_sound = generate_beep(220, 100, 0.1)
        self.node_hit_sound = generate_beep(110, 200, 0.2)
        self.wave_sound = generate_beep(660, 300, 0.1)

        # Load sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load game sprites"""
        # Create color map for sprites
        color_map = {
            '0': (0, 0, 0, 0),       # Transparent
            '1': COLORS.get('neon'),  # Primary color
            '2': COLORS.get('accent'),# Secondary color
            '3': COLORS.get('cyan'),  # Highlight
            '4': COLORS.get('danger'),# Danger/Enemy
            '5': COLORS.get('terminal'),# Green tech
            '6': COLORS.get('warning') # Warning/Explosive
        }
        
        # Load node sprite
        node_design = [
            "00001111100000",
            "00111222111000",
            "01122333221100",
            "01233333332100",
            "12333535333210",
            "12335555533210",
            "12335555533210",
            "12333535333210",
            "01233333332100",
            "01122333221100",
            "00111222111000",
            "00001111100000"
        ]
        self.node_sprite = create_pixel_sprite(node_design, PIXEL_SCALE, color_map)
        
        # Load barrier sprites
        self.barrier_sprites = {
            'standard': create_pixel_sprite(SPRITE_DESIGNS.get('barrier'), PIXEL_SCALE, color_map),
            'reflective': None,
            'explosive': None
        }
        
        # Create reflective barrier (blue/cyan)
        reflective_map = color_map.copy()
        reflective_map['1'] = COLORS.get('cyan')
        reflective_map['3'] = COLORS.get('text')
        self.barrier_sprites['reflective'] = create_pixel_sprite(SPRITE_DESIGNS.get('barrier'), PIXEL_SCALE, reflective_map)
        
        # Create explosive barrier (orange/red)
        explosive_map = color_map.copy()
        explosive_map['1'] = COLORS.get('warning')
        explosive_map['3'] = COLORS.get('danger')
        self.barrier_sprites['explosive'] = create_pixel_sprite(SPRITE_DESIGNS.get('barrier'), PIXEL_SCALE, explosive_map)
        
        # Load enemy sprites
        self.enemy_sprites = {
            'standard': create_pixel_sprite(SPRITE_DESIGNS.get('enemy'), PIXEL_SCALE, color_map),
            'fast': None,
            'tank': None
        }
        
        # Create fast enemy (smaller, cyan)
        fast_map = color_map.copy()
        fast_map['4'] = COLORS.get('cyan')
        self.enemy_sprites['fast'] = create_pixel_sprite(SPRITE_DESIGNS.get('enemy'), int(PIXEL_SCALE * 0.8), fast_map)
        
        # Create tank enemy (larger, orange)
        tank_map = color_map.copy()
        tank_map['4'] = COLORS.get('warning')
        self.enemy_sprites['tank'] = create_pixel_sprite(SPRITE_DESIGNS.get('enemy'), int(PIXEL_SCALE * 1.2), tank_map)
    
    def handle_input(self, events):
        """Handle player input"""
        if not super().handle_input(events):
            return False
        
        # Track mouse position
        self.mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    # Toggle grid
                    self.grid_visible = not self.grid_visible
                    logger.debug(f"Grid visibility: {self.grid_visible}")
                elif event.key == pygame.K_1:
                    # Switch to standard barrier
                    self.current_barrier_type = 'standard'
                    logger.debug("Barrier type: Standard")
                elif event.key == pygame.K_2:
                    # Switch to reflective barrier
                    self.current_barrier_type = 'reflective'
                    logger.debug("Barrier type: Reflective")
                elif event.key == pygame.K_3:
                    # Switch to explosive barrier
                    self.current_barrier_type = 'explosive'
                    logger.debug("Barrier type: Explosive")
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Try to place barrier if not in cooldown and game not over
                if not self.game_over and self.barrier_cooldown <= 0:
                    logger.debug("Attempting to place barrier")
                    self.place_barrier(event.pos)
        
        return True
    
    def place_barrier(self, pos):
        """Place a barrier at the specified position"""
        # Check if maximum barriers reached or not enough score
        if len(self.barriers) >= self.max_barriers or self.score < self.barrier_cost:
            logger.warning("Cannot place barrier: max reached or insufficient score")
            if self.fail_sound:
                self.fail_sound.play()
            return False
        
        # Check distance from node (prevent blocking node)
        barrier_radius = 20 * PIXEL_SCALE
        node_dist = math.hypot(pos[0] - self.node_pos[0], pos[1] - self.node_pos[1])
        if node_dist < 50 * PIXEL_SCALE + barrier_radius:
            logger.warning("Cannot place: too close to node")
            if self.fail_sound:
                self.fail_sound.play()
            return False
        
        # Check distance from other barriers (prevent overlapping)
        for barrier in self.barriers:
            dist = math.hypot(pos[0] - barrier['x'], pos[1] - barrier['y'])
            if dist < barrier['radius'] + barrier_radius:
                logger.warning("Cannot place: too close to another barrier")
                if self.fail_sound:
                    self.fail_sound.play()
                return False
        
        # Create new barrier
        new_barrier = {
            'x': pos[0],
            'y': pos[1],
            'radius': barrier_radius,
            'health': 100,
            'type': self.current_barrier_type,
            'reflect_cooldown': 0
        }
        
        # Add barrier and subtract cost
        self.barriers.append(new_barrier)
        self.score -= self.barrier_cost
        self.barrier_cooldown = 0.5
        
        logger.info(f"Placed {self.current_barrier_type} barrier. Score: {self.score}")
        
        # Play sound effect
        if self.barrier_sound:
            self.barrier_sound.play()
        
        # Add placement particles
        for _ in range(15):
            angle = random.random() * math.pi * 2
            speed = random.uniform(30, 80) * PIXEL_SCALE
            self.particles.append(self.create_particle(
                pos[0], pos[1], 
                COLORS.get('cyan'), 
                random.uniform(1, 3),
                random.uniform(0.3, 0.8), 
                math.cos(angle) * speed, 
                math.sin(angle) * speed
            ))
        
        return True
    
    def spawn_enemy(self):
        """Spawn a new enemy"""
        # Choose enemy type (weighted)
        enemy_type = random.choices(
            self.enemy_types, 
            weights=[0.6, 0.3, 0.1]
        )[0]
        
        # Random starting position (top of screen)
        start_x = random.randint(50 * PIXEL_SCALE, self.width - 50 * PIXEL_SCALE)
        start_y = -20 * PIXEL_SCALE
        
        # Adjust speed and health based on type and wave
        base_speed = 50 + self.wave * 5
        type_speed_factors = {'fast': 1.5, 'tank': 0.7, 'standard': 1.0}
        speed = base_speed * PIXEL_SCALE * type_speed_factors[enemy_type]
        
        base_health = 10 + self.wave * 2
        type_health_factors = {'tank': 2.0, 'fast': 0.5, 'standard': 1.0}
        health = base_health * type_health_factors[enemy_type]
        
        # Adjust radius based on type
        base_radius = 10 * PIXEL_SCALE
        type_radius_factors = {'tank': 1.5, 'fast': 0.7, 'standard': 1.0}
        radius = base_radius * type_radius_factors[enemy_type]
        
        # Create enemy
        new_enemy = {
            'x': start_x,
            'y': start_y,
            'radius': radius,
            'speed': speed,
            'health': health,
            'max_health': health,
            'type': enemy_type
        }
        
        self.enemies.append(new_enemy)
        logger.debug(f"Spawned {enemy_type} enemy: Health={health}, Speed={speed}")
    
    def update(self, dt):
        """Update game state"""
        super().update(dt)
        
        # Skip updates if game over
        if self.game_over:
            return
        
        # Update barrier placement cooldown
        if self.barrier_cooldown > 0:
            self.barrier_cooldown -= dt
        
        # Update wave timer
        self.wave_timer += dt
        if self.wave_timer > 8:  # New wave every 8 seconds
            self.wave += 1
            self.wave_timer = 0
            logger.info(f"Wave {self.wave + 1} started")
            if self.wave_sound:
                self.wave_sound.play()
        
        # Spawn enemies
        self.spawn_timer += dt
        spawn_interval = max(0.3, 1.5 / (1 + self.wave * 0.3))  # Faster spawns in later waves
        if self.spawn_timer > spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # Lists to track entities for removal
        enemies_to_remove = []
        barriers_to_remove = []
        
        # Update enemies
        for i, enemy in enumerate(self.enemies):
            # Move toward node
            dx = self.node_pos[0] - enemy['x']
            dy = self.node_pos[1] - enemy['y']
            length = math.hypot(dx, dy)
            
            if length > 1:
                nx, ny = dx / length, dy / length
                enemy['x'] += nx * enemy['speed'] * dt
                enemy['y'] += ny * enemy['speed'] * dt
            
            # Check collision with node
            node_dist = math.hypot(enemy['x'] - self.node_pos[0], enemy['y'] - self.node_pos[1])
            if node_dist < 50 * PIXEL_SCALE + enemy['radius']:
                # Damage node
                self.node_health -= 10
                logger.info(f"Node hit! Health: {self.node_health}")
                enemies_to_remove.append(i)
                
                if self.node_hit_sound:
                    self.node_hit_sound.play()
                
                # Add explosion particles
                for _ in range(10):
                    angle = random.random() * math.pi * 2
                    speed = random.uniform(50, 100) * PIXEL_SCALE
                    self.particles.append(self.create_particle(
                        enemy['x'], enemy['y'], 
                        COLORS.get('danger'), 
                        random.uniform(2, 4),
                        random.uniform(0.5, 1.0), 
                        math.cos(angle) * speed, 
                        math.sin(angle) * speed
                    ))
                
                # Check if game over
                if self.node_health <= 0:
                    self.node_health = 0
                    self.game_over = True
                    logger.info("GAME OVER: Node destroyed")
                    if self.fail_sound:
                        self.fail_sound.play()
                
                continue
            
            # Check collision with barriers
            for j, barrier in enumerate(self.barriers):
                if j in barriers_to_remove:
                    continue
                
                barrier_dist = math.hypot(enemy['x'] - barrier['x'], enemy['y'] - barrier['y'])
                if barrier_dist < enemy['radius'] + barrier['radius']:
                    # Handle collision based on barrier type
                    if barrier['type'] == 'reflective' and barrier['reflect_cooldown'] <= 0:
                        # Reflect enemy
                        enemy['speed'] = -enemy['speed']
                        barrier['reflect_cooldown'] = 1.0
                        logger.debug(f"Enemy {i} reflected by barrier {j}")
                        if self.enemy_hit_sound:
                            self.enemy_hit_sound.play()
                    
                    elif barrier['type'] == 'explosive':
                        # Explosive damage
                        enemy['health'] -= 50
                        barrier['health'] -= 20
                        
                        # Area damage
                        for k, other_enemy in enumerate(self.enemies):
                            if k != i and math.hypot(other_enemy['x'] - barrier['x'], other_enemy['y'] - barrier['y']) < 50 * PIXEL_SCALE:
                                other_enemy['health'] -= 30
                        
                        logger.debug(f"Explosive barrier {j} damaged enemies")
                        
                        # Add explosion particles
                        for _ in range(20):
                            angle = random.random() * math.pi * 2
                            speed = random.uniform(50, 150) * PIXEL_SCALE
                            self.particles.append(self.create_particle(
                                barrier['x'], barrier['y'], 
                                COLORS.get('warning'), 
                                random.uniform(2, 5),
                                random.uniform(0.5, 1.2), 
                                math.cos(angle) * speed, 
                                math.sin(angle) * speed
                            ))
                    
                    else:
                        # Standard damage
                        enemy['health'] -= 20
                        barrier['health'] -= 10
                        if self.enemy_hit_sound:
                            self.enemy_hit_sound.play()
                    
                    # Check if barrier destroyed
                    if barrier['health'] <= 0 and j not in barriers_to_remove:
                        barriers_to_remove.append(j)
                        logger.debug(f"Barrier {j} destroyed")
                    
                    # Check if enemy destroyed
                    if enemy['health'] <= 0:
                        enemies_to_remove.append(i)
                        self.score += 20 + self.wave * 5
                        logger.debug(f"Enemy {i} destroyed. Score: {self.score}")
                        
                        # Add destruction particles
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.uniform(50, 100) * PIXEL_SCALE
                            self.particles.append(self.create_particle(
                                enemy['x'], enemy['y'], 
                                COLORS.get('cyan'), 
                                random.uniform(2, 4),
                                random.uniform(0.5, 1.0), 
                                math.cos(angle) * speed, 
                                math.sin(angle) * speed
                            ))
                    
                    break
        
        # Remove destroyed entities
        for idx in sorted(list(set(enemies_to_remove)), reverse=True):
            if 0 <= idx < len(self.enemies):
                del self.enemies[idx]
        
        for idx in sorted(list(set(barriers_to_remove)), reverse=True):
            if 0 <= idx < len(self.barriers):
                del self.barriers[idx]
        
        # Update barrier cooldowns
        for barrier in self.barriers:
            if barrier['reflect_cooldown'] > 0:
                barrier['reflect_cooldown'] -= dt
        
        # Update barrier preview
        if not self.game_over and self.barrier_cooldown <= 0 and self.score >= self.barrier_cost:
            mouse_x, mouse_y = self.mouse_pos
            valid = True
            
            # Check if too close to node
            node_dist = math.hypot(mouse_x - self.node_pos[0], mouse_y - self.node_pos[1])
            if node_dist < 50 * PIXEL_SCALE * 2:
                valid = False
            
            # Check if too close to other barriers
            for barrier in self.barriers:
                dist = math.hypot(mouse_x - barrier['x'], mouse_y - barrier['y'])
                if dist < barrier['radius'] * 2:
                    valid = False
                    break
            
            self.barrier_preview = {
                'x': mouse_x,
                'y': mouse_y,
                'valid': valid and len(self.barriers) < self.max_barriers,
                'type': self.current_barrier_type
            }
        else:
            self.barrier_preview = None
    
    def draw(self):
        """Draw the game"""
        # Draw background and UI
        super().draw()
        
        # Draw barriers
        for barrier in self.barriers:
            # Get sprite for barrier type
            sprite = self.barrier_sprites[barrier['type']]
            
            # Health-based tint
            health_pct = max(0, barrier['health'] / 100.0)
            tint_color = lerp_color(COLORS.get('danger'), COLORS.get('neon'), health_pct)
            
            # Create tinted sprite
            tinted_sprite = sprite.copy()
            tinted_sprite.fill((*tint_color[:3], 200), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw barrier
            self.screen.blit(
                tinted_sprite,
                (int(barrier['x'] - sprite.get_width() // 2),
                 int(barrier['y'] - sprite.get_height() // 2))
            )
            
            # Draw health bar
            bar_width = 40 * PIXEL_SCALE
            bar_height = 5 * PIXEL_SCALE
            bar_x = barrier['x'] - bar_width / 2
            bar_y = barrier['y'] + barrier['radius'] + 5 * PIXEL_SCALE
            
            # Background
            draw_pixel_rect(
                self.screen,
                COLORS.get('bg_dark'),
                (bar_x, bar_y, bar_width, bar_height),
                PIXEL_SCALE
            )
            
            # Health fill
            if health_pct > 0:
                fill_width = bar_width * health_pct
                draw_pixel_rect(
                    self.screen,
                    tint_color,
                    (bar_x, bar_y, fill_width, bar_height),
                    PIXEL_SCALE
                )
        
        # Draw enemies
        for enemy in self.enemies:
            # Get sprite for enemy type
            sprite = self.enemy_sprites[enemy['type']]
            
            # Health-based tint
            health_pct = max(0, enemy['health'] / enemy['max_health'])
            tint_color = lerp_color(COLORS.get('danger'), COLORS.get('accent'), health_pct)
            
            # Create tinted sprite
            tinted_sprite = sprite.copy()
            tinted_sprite.fill((*tint_color[:3], 200), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw enemy
            self.screen.blit(
                tinted_sprite,
                (int(enemy['x'] - sprite.get_width() // 2),
                 int(enemy['y'] - sprite.get_height() // 2))
            )
        
        # Draw node
        self.screen.blit(
            self.node_sprite,
            (int(self.node_pos[0] - self.node_sprite.get_width() // 2),
             int(self.node_pos[1] - self.node_sprite.get_height() // 2))
        )
        
        # Draw barrier preview
        if self.barrier_preview:
            sprite = self.barrier_sprites[self.barrier_preview['type']]
            alpha = 150 if self.barrier_preview['valid'] else 50
            
            # Create semi-transparent preview
            preview_sprite = sprite.copy()
            preview_sprite.set_alpha(alpha)
            
            self.screen.blit(
                preview_sprite,
                (int(self.barrier_preview['x'] - sprite.get_width() // 2),
                 int(self.barrier_preview['y'] - sprite.get_height() // 2))
            )
        
        # Draw UI overlay
        self.draw_game_ui()
    
    def draw_game_ui(self):
        """Draw game-specific UI elements"""
        # Node health
        node_health_text = f"NODE: {max(0, self.node_health)}%"
        node_health_color = COLORS.get('neon') if self.node_health > 30 else COLORS.get('danger')
        util_draw_text(
            self.screen,
            node_health_text,
            self.game_font_medium,
            node_health_color,
            self.width - 10,
            40,
            False,
            right_aligned=True
        )
        
        # Wave info
        util_draw_text(
            self.screen,
            f"WAVE: {self.wave + 1}",
            self.game_font_medium,
            COLORS.get('accent'),
            self.width // 2,
            10,
            True
        )
        
        # Barrier info
        util_draw_text(
            self.screen,
            f"BARRIERS: {len(self.barriers)}/{self.max_barriers}",
            self.game_font_small,
            COLORS.get('text'),
            10,
            40,
            False
        )
        
        # Cost info
        cost_color = COLORS.get('neon') if self.score >= self.barrier_cost else COLORS.get('text_dark')
        util_draw_text(
            self.screen,
            f"COST: {self.barrier_cost} PTS",
            self.game_font_small,
            cost_color,
            10,
            60,
            False
        )
        
        # Current barrier type
        type_text = f"TYPE: {self.current_barrier_type.upper()} (1/2/3)"
        util_draw_text(
            self.screen,
            type_text,
            self.game_font_small,
            COLORS.get('cyan'),
            10,
            80,
            False
        )


# --- TerminalTyper Game ---
class TerminalTyperGame(BaseMinigame):
    """
    Terminal Typer Game
    Type the falling commands before they reach the bottom
    """
    
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        
        # Set title and instructions
        self.title = "TERMINAL TYPER"
        self.instructions = [
            "Type commands to clear the terminal!",
            "",
            "- Type words exactly as shown",
            "- Press ENTER to submit",
            "- Power-ups: Slow (cyan), Clear (pink)",
            "- Game over after 12 misses",
            "- Build combos for bonus points",
            "",
            "Press SPACE or click to start"
        ]
        
        # Game specific variables
        self.words = []
        self.current_input = ""
        self.combo = 0
        self.max_combo = 0
        self.level = 1
        self.missed_words = 0
        self.correct_words = 0
        self.powerups = []
        self.active_powerups = []
        
        # Word lists by difficulty
        self.word_lists = {
            'easy': [
                "cd", "ls", "rm", "cp", "mv", "cat", "pwd", "git", "ssh", "apt",
                "grep", "echo", "sudo", "nano", "ping", "exit", "mkdir", "touch"
            ],
            'medium': [
                "python", "docker", "filter", "commit", "config", "server", "client",
                "update", "status", "search", "modify", "system", "kernel", "buffer"
            ],
            'hard': [
                "encryption", "algorithm", "directory", "overwrite", "recursion",
                "parameters", "deployment", "repository", "permission", "variables"
            ],
            'commands': [
                "git clone", "ssh login", "chmod +x", "cat file.txt", "rm -rf",
                "sudo apt", "grep -i", "tar -xvf", "python3 -m", "kill -9"
            ]
        }
        
        # Grid animation properties
        self.grid_scroll_y = 0
        
        # Background effects
        self.rain_columns = []
        self.init_rain_effect()
        
        # Timers
        self.spawn_timer = 0
        self.wave_timer = 0
        
        # Sounds
        self.type_sound = generate_beep(440, 20, 0.05)
        self.word_complete_sound = generate_beep(880, 50, 0.1)
        self.word_miss_sound = generate_beep(220, 100, 0.1)
        self.powerup_sound = generate_beep(660, 100, 0.15)
        
        # Load sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load game sprites"""
        # Create color map for sprites
        color_map = {
            '0': (0, 0, 0, 0),       # Transparent
            '1': COLORS.get('terminal'),  # Terminal green
            '2': COLORS.get('accent'),    # Secondary color
            '3': COLORS.get('cyan'),      # Highlight
            '4': COLORS.get('danger'),    # Danger/Enemy
            '5': COLORS.get('neon'),      # Yellow
            '6': COLORS.get('warning')    # Warning/Explosive
        }
        
        # Load powerup sprites
        self.powerup_sprites = {
            'slow': create_pixel_sprite([
                "0000111111000000",
                "0011122211100000",
                "0112233332211000",
                "1123333333321100",
                "1233333333332100",
                "1233333333332100",
                "1233331333332100",
                "1233331333332100",
                "1233331333332100",
                "1233331333332100",
                "1233333333332100",
                "1233333333332100",
                "1123333333321100",
                "0112233332211000",
                "0011122211100000",
                "0000111111000000"
            ], PIXEL_SCALE, color_map),
            
            'clear': create_pixel_sprite([
                "0000222222000000",
                "0022233322200000",
                "0223333333322000",
                "2233333333332200",
                "2333333333333200",
                "2333333333333200",
                "2333332333333200",
                "2333332333333200",
                "2333332333333200",
                "2333332333333200",
                "2333333333333200",
                "2333333333333200",
                "2233333333332200",
                "0223333333322000",
                "0022233322200000",
                "0000222222000000"
            ], PIXEL_SCALE, color_map)
        }
    
    def init_rain_effect(self):
        """Initialize digital rain effect"""
        num_columns = self.width // (14 * PIXEL_SCALE)
        chars = "01235789ABCDEFabcdef#$%&@!?><;:/\\[]{}()*-+=.,"
        
        for i in range(num_columns):
            x = i * 14 * PIXEL_SCALE + random.randint(-5, 5) * PIXEL_SCALE
            self.rain_columns.append({
                'x': x,
                'y': random.randint(-500, -50),
                'speed': random.uniform(50, 200) * PIXEL_SCALE,
                'chars': [random.choice(chars) for _ in range(random.randint(5, 20))],
                'opacity': random.randint(40, 180)
            })
    
    def handle_input(self, events):
        if not super().handle_input(events):
            return False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    continue

                # --- MODIFIED: Only check for ENTER key to submit ---
                if event.key == pygame.K_RETURN and self.current_input:
                # --- END MODIFIED ---
                    # Submit current input
                    self.check_input()
                elif event.key == pygame.K_BACKSPACE and self.current_input:
                    # Delete last character
                    self.current_input = self.current_input[:-1]
                    if self.type_sound:
                        self.type_sound.play()
                # --- ADDED: Explicitly allow SPACE character input ---
                elif event.unicode and (event.unicode.isprintable() or event.key == pygame.K_SPACE):
                    # Add character to input (allow space)
                    self.current_input += event.unicode
                    if self.type_sound:
                        self.type_sound.play()
                # --- END ADDED ---

        return True
    
    def check_input(self):
        """Check if current input matches any falling word"""
        if not self.current_input:
            return
        
        input_text = self.current_input.strip().lower()
        matched = False
        
        for i, word in enumerate(self.words):
            if word['text'].lower() == input_text:
                # Match found! Remove word and add score
                score_gain = len(word['text']) * 5 * (self.combo + 1)
                self.score += score_gain
                self.words.pop(i)
                matched = True
                self.correct_words += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                
                # Create particles at word position
                for _ in range(10):
                    self.particles.append(self.create_particle(
                        word['x'] + word['width'] // 2,
                        word['y'] + word['height'] // 2,
                        COLORS.get('terminal'),
                        random.uniform(1, 2),
                        random.uniform(0.3, 0.8),
                        random.uniform(-50, 50) * PIXEL_SCALE,
                        random.uniform(-80, -20) * PIXEL_SCALE
                    ))
                
                # Play sound
                if self.word_complete_sound:
                    self.word_complete_sound.play()
                
                break
        
        if not matched:
            # Reset combo on mistake
            self.combo = 0
            
            # Red flash effect
            flash = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 30))
            self.screen.blit(flash, (0, 0))
            
            if self.word_miss_sound:
                self.word_miss_sound.play()
        
        # Clear current input
        self.current_input = ""
    
    def spawn_word(self, difficulty=None):
        """Spawn a new falling word"""
        # Determine word difficulty
        if difficulty is None:
            # Random difficulty weighted by level
            weights = {}
            
            # Adjust weights based on level
            if self.level <= 2:
                weights = {'easy': 0.7, 'medium': 0.2, 'hard': 0.05, 'commands': 0.05}
            elif self.level <= 5:
                weights = {'easy': 0.4, 'medium': 0.4, 'hard': 0.1, 'commands': 0.1}
            else:
                weights = {'easy': 0.2, 'medium': 0.3, 'hard': 0.3, 'commands': 0.2}
            
            difficulty_choices = list(weights.keys())
            difficulty_weights = list(weights.values())
            difficulty = random.choices(difficulty_choices, weights=difficulty_weights)[0]
        
        # Get a random word from the selected difficulty list
        if difficulty in self.word_lists and self.word_lists[difficulty]:
            text = random.choice(self.word_lists[difficulty])
        else:
            # Fallback
            text = "404"
        
        # Calculate word dimensions
        try:
            surf = self.game_font_medium.render(text, True, (0, 255, 0))
            text_width, text_height = surf.get_size()
        except Exception as e:
            logger.error(f"Error rendering word: {e}")
            text_width, text_height = 100, 20
        
        # Random horizontal position
        min_x = 10
        max_x = self.width - text_width - 10
        x = random.randint(min_x, max_x)
        
        # Start above screen
        y = -text_height - random.randint(0, 50)
        
        # Calculate speed based on difficulty and level
        difficulty_speed_factor = {
            'easy': 1.0,
            'medium': 1.2,
            'hard': 1.5,
            'commands': 1.3
        }
        
        base_speed = 20 + self.level * 3
        speed = base_speed * difficulty_speed_factor.get(difficulty, 1.0)
        
        # Check for slow powerup effect
        if any(p['type'] == 'slow' for p in self.active_powerups):
            speed *= 0.5
        
        # Create word
        word = {
            'text': text,
            'color': COLORS.get('terminal'),
            'x': x,
            'y': y,
            'width': text_width,
            'height': text_height,
            'speed': speed,
            'difficulty': difficulty
        }
        
        self.words.append(word)
    
    def spawn_powerup(self):
        """Randomly spawn a powerup"""
        if random.random() > 0.2:  # 20% chance
            return
        
        powerup_type = random.choice(['slow', 'clear'])
        sprite = self.powerup_sprites[powerup_type]
        
        # Random position
        x = random.randint(50, self.width - 50)
        y = -sprite.get_height()
        
        # Create powerup
        powerup = {
            'type': powerup_type,
            'x': x,
            'y': y,
            'width': sprite.get_width(),
            'height': sprite.get_height(),
            'speed': 100 * PIXEL_SCALE,
            'rotation': 0
        }
        
        self.powerups.append(powerup)
    
    def activate_powerup(self, powerup_type):
        """Activate a powerup effect"""
        if powerup_type == 'slow':
            # Slow down all words for 5 seconds
            self.active_powerups.append({
                'type': 'slow',
                'duration': 5.0,
                'elapsed': 0.0
            })
            logger.debug("Activated SLOW powerup")
        
        elif powerup_type == 'clear':
            # Clear half of the words on screen
            if self.words:
                to_remove = min(len(self.words) // 2 + 1, len(self.words))
                self.words = self.words[to_remove:]
                logger.debug(f"Activated CLEAR powerup, removed {to_remove} words")
                
                # Create particles
                for _ in range(20):
                    self.particles.append(self.create_particle(
                        self.width // 2,
                        self.height // 2,
                        COLORS.get('accent'),
                        random.uniform(2, 4),
                        random.uniform(0.5, 1.2),
                        random.uniform(-200, 200) * PIXEL_SCALE,
                        random.uniform(-200, 200) * PIXEL_SCALE
                    ))
        
        # Play sound
        if self.powerup_sound:
            self.powerup_sound.play()
    
    def update(self, dt):
        """Update game state"""
        super().update(dt)
        
        # Skip updates if game over
        if self.game_over:
            return
        
        # Update grid animation
        self.grid_scroll_y += 30 * dt
        
        # Update spawn timer
        self.spawn_timer += dt
        spawn_interval = max(0.4, 1.8 - (self.level * 0.2))
        
        if self.spawn_timer > spawn_interval and len(self.words) < 12:
            self.spawn_word()
            self.spawn_timer = 0
            
            # Chance to spawn powerup
            if random.random() < 0.1:  # 10% chance
                self.spawn_powerup()
        
        # Update active powerups
        powerups_to_remove = []
        for i, powerup in enumerate(self.active_powerups):
            powerup['elapsed'] += dt
            if powerup['elapsed'] >= powerup['duration']:
                powerups_to_remove.append(i)
        
        # Remove expired powerups
        for idx in sorted(powerups_to_remove, reverse=True):
            if 0 <= idx < len(self.active_powerups):
                logger.debug(f"Powerup {self.active_powerups[idx]['type']} expired")
                del self.active_powerups[idx]
        
        # Update falling words
        words_to_remove = []
        for i, word in enumerate(self.words):
            # Apply appropriate speed
            word['y'] += word['speed'] * dt
            
            # Check if word reached bottom
            if word['y'] > self.height:
                words_to_remove.append(i)
                self.missed_words += 1
                self.combo = 0
                
                if self.missed_words >= 12:
                    self.game_over = True
                    logger.info("Game over - too many missed words")
        
        # Remove words that fell off screen
        for idx in sorted(words_to_remove, reverse=True):
            if 0 <= idx < len(self.words):
                # Play miss sound
                if self.word_miss_sound:
                    self.word_miss_sound.play()
                del self.words[idx]
        
        # Update falling powerups
        powerups_to_remove = []
        for i, powerup in enumerate(self.powerups):
            powerup['y'] += powerup['speed'] * dt
            powerup['rotation'] += 90 * dt  # Spin animation
            
            # Check if out of screen
            if powerup['y'] > self.height:
                powerups_to_remove.append(i)
                continue
                
            # Check for collision with input box
            input_box_y = self.height - 60 * PIXEL_SCALE
            input_box_height = 30 * PIXEL_SCALE
            
            if (powerup['y'] + powerup['height'] > input_box_y and 
                powerup['y'] < input_box_y + input_box_height):
                # Activate powerup
                self.activate_powerup(powerup['type'])
                powerups_to_remove.append(i)
        
        # Remove collected or off-screen powerups
        for idx in sorted(powerups_to_remove, reverse=True):
            if 0 <= idx < len(self.powerups):
                del self.powerups[idx]
        
        # Update level based on correct words
        if self.correct_words >= self.level * 10:
            self.level += 1
            logger.info(f"Level up! Now at level {self.level}")
    
    def draw_digital_rain(self):
        """Draw Matrix-style digital rain effect"""
        try:
            for column in self.rain_columns:
                # Animation
                column['y'] += column['speed'] * 0.01
                
                # Reset if too far down
                if column['y'] > self.height + 500:
                    column['y'] = random.randint(-500, -50)
                    column['speed'] = random.uniform(50, 200) * PIXEL_SCALE
                
                # Draw characters
                for i, char in enumerate(column['chars']):
                    y_pos = column['y'] + i * 20 * PIXEL_SCALE
                    
                    # Skip if off-screen
                    if y_pos < -20 or y_pos > self.height:
                        continue
                    
                    # Calculate fade
                    fade = 1.0 - (i / len(column['chars']))
                    alpha = int(column['opacity'] * fade)
                    
                    # Leading character is brighter
                    color = COLORS.get('hacker_text') if i == 0 else COLORS.get('terminal')
                    
                    # Draw character
                    char_surf = self.game_font_small.render(char, True, color)
                    char_surf.set_alpha(alpha)
                    self.screen.blit(char_surf, (column['x'], y_pos))
        except Exception as e:
            logger.error(f"Error drawing digital rain: {e}")
    
    def draw(self):
        """Draw the game"""
        try: # Add try-except around the entire draw method
            # Fill background
            self.screen.fill(COLORS.get('bg_dark', (10, 8, 16)))

            # Draw digital rain effect
            self.draw_digital_rain()

            # Draw grid
            self.draw_terminal_grid()

            # Draw UI elements
            self.draw_ui()

            # Draw falling words
            for word in self.words:
                # Different colors based on difficulty
                color = COLORS.get('terminal', (0, 200, 80))  # Default green
                if word['difficulty'] == 'medium':
                    color = COLORS.get('accent', (255, 105, 180))  # Pink
                elif word['difficulty'] == 'hard':
                    color = COLORS.get('warning', (255, 165, 0))  # Orange
                elif word['difficulty'] == 'commands':
                    color = COLORS.get('cyan', (0, 255, 255))  # Cyan

                # --- ADDED: Color validation for words ---
                if not isinstance(color, (tuple, list)) or len(color) < 3:
                    logger.warning(f"Invalid color for word '{word['text']}'. Using fallback green.")
                    color = (0, 200, 80) # Fallback green
                # --- END ADDED ---

                # Apply flicker effect
                flicker = random.uniform(0.9, 1.0) if random.random() < 0.1 else 1.0
                final_color = tuple(int(c * flicker) for c in color[:3]) # Use RGB

                # Draw shadow for depth
                shadow_offset = 2 * PIXEL_SCALE
                util_draw_text(
                    self.screen,
                    word['text'],
                    self.game_font_medium,
                    (20, 20, 20), # Shadow color
                    word['x'] + shadow_offset,
                    word['y'] + shadow_offset,
                    False
                )

                # Draw the word
                util_draw_text(
                    self.screen,
                    word['text'],
                    self.game_font_medium,
                    final_color, # Use validated RGB color
                    word['x'],
                    word['y'],
                    False
                )

            # Draw powerups
            for powerup in self.powerups:
                sprite = self.powerup_sprites.get(powerup['type']) # Use .get for safety
                if sprite: # Only draw if sprite exists
                    # Apply rotation if needed (simplified blit)
                    self.screen.blit(
                        sprite,
                        (int(powerup['x'] - sprite.get_width() // 2),
                         int(powerup['y'] - sprite.get_height() // 2))
                    )

            # Draw input box
            input_y = self.height - 60 * PIXEL_SCALE
            input_box_w = 300 * PIXEL_SCALE
            input_box_h = 30 * PIXEL_SCALE
            input_box_x = (self.width - input_box_w) // 2

            # Draw box background
            draw_pixel_rect(
                self.screen,
                COLORS.get('bg_dark', (10, 8, 16)),
                (input_box_x, input_y, input_box_w, input_box_h),
                PIXEL_SCALE
            )

            # Draw box border
            border_color = COLORS.get('cyan', (0, 255, 255))
            # --- ADDED: Color validation for input box border ---
            if not isinstance(border_color, (tuple, list)) or len(border_color) < 3:
                 logger.warning(f"Invalid border_color {border_color} for input box. Using cyan.")
                 border_color = (0, 255, 255) # Fallback cyan
            # --- END ADDED ---
            for i in range(PIXEL_SCALE):
                # --- FIXED: Use validated border_color ---
                pygame.draw.rect(
                    self.screen,
                    border_color[:3], # Use RGB
                    (input_box_x + i, input_y + i, input_box_w - 2*i, input_box_h - 2*i),
                    1 # Use thickness 1 for outline
                )
                # --- END FIXED ---


            # Draw current input or placeholder
            input_text = self.current_input if self.current_input else "Type here..."
            input_color = COLORS.get('terminal', (0, 200, 80)) if self.current_input else COLORS.get('text_dark', (120, 120, 160))

            util_draw_text(
                self.screen,
                input_text,
                self.game_font_medium,
                input_color, # util_draw_text handles None/invalid color
                input_box_x + 10 * PIXEL_SCALE,
                input_y + input_box_h // 2,
                False
            )

            # Draw active powerups
            for i, powerup in enumerate(self.active_powerups):
                padding = 10 * PIXEL_SCALE
                util_draw_text(
                    self.screen,
                    f"{powerup['type'].upper()}: {int(powerup['duration'] - powerup['elapsed'])}s",
                    self.game_font_small,
                    COLORS.get('cyan'), # util_draw_text handles None/invalid color
                    padding,
                    (60 + i * 20) * PIXEL_SCALE,
                    False
                )

            # Draw particles
            self.draw_particles()

            # Draw game over screen if needed
            if self.game_over:
                self.draw_game_over()
        except Exception as e:
             logger.error(f"Error in TerminalTyperGame.draw: {e}", exc_info=True)
             # Draw minimal error indicator
             try:
                 pygame.draw.rect(self.screen, (255,0,0), (10,10,50,20))
                 util_draw_text(self.screen, "DRAW ERR", self.game_font_small, (255,255,255), 35, 20, True)
             except: pass # Ignore errors during error drawing
    
    def draw_terminal_grid(self):
        """Draw grid background for terminal effect"""
        # Draw vertical grid lines
        for x in range(0, self.width, 40 * PIXEL_SCALE):
            alpha = 30  # Subtle lines
            pygame.draw.line(
                self.screen,
                (*COLORS.get('grid')[:3], alpha),
                (x, 0),
                (x, self.height),
                PIXEL_SCALE
            )
        
        # Draw horizontal grid lines
        for y in range(0, self.height, 40 * PIXEL_SCALE):
            alpha = 30
            pygame.draw.line(
                self.screen,
                (*COLORS.get('grid')[:3], alpha),
                (0, y),
                (self.width, y),
                PIXEL_SCALE
            )
        
        # Draw scrolling effect
        offset_y = int(self.grid_scroll_y) % (40 * PIXEL_SCALE)
        for y in range(-offset_y, self.height, 40 * PIXEL_SCALE):
            alpha = 20  # Even more subtle
            pygame.draw.line(
                self.screen,
                (*COLORS.get('terminal')[:3], alpha),
                (0, y),
                (self.width, y),
                1
            )
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Score
        util_draw_text(
            self.screen,
            f"SCORE: {self.score}",
            self.game_font_medium,
            COLORS.get('neon'),
            10,
            10,
            False
        )
        
        # Level
        util_draw_text(
            self.screen,
            f"LEVEL: {self.level}",
            self.game_font_medium,
            COLORS.get('accent'),
            self.width // 2,
            10,
            True
        )
        
        # Combo
        combo_color = COLORS.get('neon')
        if self.combo >= 10:
            combo_color = COLORS.get('warning')
        elif self.combo >= 5:
            combo_color = COLORS.get('cyan')
        
        util_draw_text(
            self.screen,
            f"COMBO: x{self.combo}",
            self.game_font_medium,
            combo_color,
            self.width - 10,
            10,
            False,
            right_aligned=True
        )
        
        # Missed counter
        missed_color = COLORS.get('neon')
        if self.missed_words >= 10:
            missed_color = COLORS.get('danger')
        elif self.missed_words >= 6:
            missed_color = COLORS.get('warning')
        
        util_draw_text(
            self.screen,
            f"MISSED: {self.missed_words}/12",
            self.game_font_small,
            missed_color,
            10,
            40 * PIXEL_SCALE,
            False
        )


# --- NeonJetpack Game ---
class NeonJetpackGame(BaseMinigame):
    """
    Neon Jetpack Game
    Fly through the neon skyline collecting data packets and avoiding obstacles
    """
    
    # slith_minigames.py

# Inside class NeonJetpackGame:
    # slith_minigames.py

# Inside class NeonJetpackGame:
    def __init__(self, screen, clock):
        super().__init__(screen, clock)

        # Set title and instructions
        self.title = "NEON JETPACK"
        self.instructions = [
            "Fly through the neon skyline!",
            "",
            "- Press SPACE or UP to boost jetpack",
            "- Collect data bits for points",
            "- Avoid obstacles and buildings",
            "- Game over if you crash",
            "",
            "Press SPACE or click to start"
        ]

        # Game specific variables
        self.player_x = self.width // 4
        self.player_y = self.height // 2
        self.player_velocity = 0
        # --- FURTHER ADJUSTED PHYSICS VALUES ---
        self.gravity = 175 * PIXEL_SCALE  # Reduced further from 350
        self.boost_power = -475 * PIXEL_SCALE # Slightly more boost from -450
        # --- END ADJUSTED VALUES ---
        self.boosting = False
        self.obstacles = []
        self.collectibles = []
        self.player_size = 20 * PIXEL_SCALE # Base size, actual collision uses sprite
        self.bg_offset = 0
        self.bg_speed = 100 * PIXEL_SCALE

        # Sounds
        self.boost_sound = generate_beep(440, 100, 0.1)
        self.collect_sound = generate_beep(880, 50, 0.1)
        self.crash_sound = generate_beep(110, 300, 0.2)

        # Load sprites
        self.load_sprites()

        # Ensure player_sprite is loaded before accessing its size
        if hasattr(self, 'player_sprite') and self.player_sprite:
             # Use sprite height for vertical boundary checks, width might differ
             self.player_size = self.player_sprite.get_height()
             logger.debug(f"Player size set from sprite: {self.player_size}")
        else:
             logger.warning("Player sprite not loaded in __init__, using default player_size.")
             self.player_size = 20 * PIXEL_SCALE # Keep default if sprite fails

    # ... (rest of the NeonJetpackGame methods) ...


    
    def load_sprites(self):
        """Load game sprites"""
        # Create color map for sprites
        color_map = {
            '0': (0, 0, 0, 0),       # Transparent
            '1': COLORS.get('neon'),  # Primary color (yellow)
            '2': COLORS.get('accent'),# Secondary color (pink)
            '3': COLORS.get('cyan'),  # Highlight (cyan)
            '4': COLORS.get('danger'),# Danger color (red)
            '5': COLORS.get('warning') # Warning color (orange)
        }
        
        # Load player sprite
        self.player_sprite = create_pixel_sprite(SPRITE_DESIGNS.get('player'), PIXEL_SCALE, color_map)
        
        # Load collectible sprite
        self.collectible_sprite = create_pixel_sprite(SPRITE_DESIGNS.get('collectible'), PIXEL_SCALE, color_map)
    
    def handle_input(self, events):
        """Handle player input"""
        if not super().handle_input(events):
            return False
        
        # Reset boosting flag
        self.boosting = False
        
        # Check for boost key held down
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.boosting = True
        
        # Check for new key presses
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not self.game_over:
                    # Play boost sound once on initial press
                    if self.boost_sound:
                        self.boost_sound.play()
        
        return True
    
    def spawn_obstacle(self):
        """Spawn a new obstacle"""
        # Random height for the obstacle
        obstacle_height = random.randint(50, 200) * PIXEL_SCALE
        obstacle_width = random.randint(30, 80) * PIXEL_SCALE
        
        # Position at top or bottom of screen
        is_top = random.choice([True, False])
        obstacle_y = 0 if is_top else self.height - obstacle_height
        
        # Increasing speed based on score
        obstacle_speed = (100 + self.score // 50) * PIXEL_SCALE
        
        # Create obstacle
        new_obstacle = {
            'x': self.width,
            'y': obstacle_y,
            'width': obstacle_width,
            'height': obstacle_height,
            'speed': obstacle_speed,
            'color': COLORS.get('danger')
        }
        
        self.obstacles.append(new_obstacle)
    
    def spawn_collectible(self):
        """Spawn a new collectible"""
        # Size and position
        size = 15 * PIXEL_SCALE
        x = self.width + size
        y = random.randint(size, self.height - size)
        
        # Increasing speed based on score
        speed = (100 + self.score // 100) * PIXEL_SCALE
        
        # Create collectible
        new_collectible = {
            'x': x,
            'y': y,
            'size': size,
            'speed': speed,
            'rotation': 0,
            'value': 10
        }
        
        self.collectibles.append(new_collectible)
    
    def update(self, dt):
        """Update game state"""
        super().update(dt)
        
        # Skip updates if game over
        if self.game_over:
            return
        
        # Apply physics to player
        if self.boosting:
            # Apply boost force
            self.player_velocity += self.boost_power * dt
            
            # Add boost particles
            for _ in range(3):
                px = self.player_x - 10 * PIXEL_SCALE
                py = self.player_y + random.uniform(-5, 5) * PIXEL_SCALE
                self.particles.append(self.create_particle(
                    px, py,
                    COLORS.get('neon'),
                    random.uniform(1, 3),
                    random.uniform(0.3, 0.8),
                    -random.uniform(30, 80) * PIXEL_SCALE,
                    random.uniform(-20, 20) * PIXEL_SCALE
                ))
        
        # Apply gravity
        self.player_velocity += self.gravity * dt
        
        # Update player position
        self.player_y += self.player_velocity * dt
        
        # Check boundaries
        if self.player_y < self.player_size:
            self.player_y = self.player_size
            self.player_velocity = 0
        elif self.player_y > self.height - self.player_size:
            self.player_y = self.height - self.player_size
            self.game_over = True
            logger.info("Game over: Player hit bottom")
            
            if self.crash_sound:
                self.crash_sound.play()
            
            # Add crash particles
            for _ in range(20):
                angle = random.random() * math.pi * 2
                speed = random.uniform(50, 150) * PIXEL_SCALE
                self.particles.append(self.create_particle(
                    self.player_x, self.player_y,
                    COLORS.get('danger'),
                    random.uniform(2, 5),
                    random.uniform(0.5, 1.2),
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ))
        
        # Update scrolling background
        self.bg_offset += self.bg_speed * dt
        if self.bg_offset > 40 * PIXEL_SCALE:
            self.bg_offset += self.bg_speed * dt
        
        # Spawn obstacles and collectibles
        spawn_timer = getattr(self, "spawn_timer", 0)
        spawn_timer += dt
        
        if spawn_timer > 1.5:
            spawn_timer = 0
            self.spawn_obstacle()
            self.spawn_collectible()
        
        self.spawn_timer = spawn_timer
        
        # Update obstacles
        obstacles_to_remove = []
        for i, obstacle in enumerate(self.obstacles):
            # Move obstacle
            obstacle['x'] -= obstacle['speed'] * dt
            
            # Remove if off-screen
            if obstacle['x'] + obstacle['width'] < 0:
                obstacles_to_remove.append(i)
                continue
            # Check for collision with player
            if not self.game_over:
                player_rect = pygame.Rect(
                    self.player_x - self.player_size // 2,
                    self.player_y - self.player_size // 2,
                    self.player_size,
                    self.player_size
                )
                
                obstacle_rect = pygame.Rect(
                    obstacle['x'],
                    obstacle['y'],
                    obstacle['width'],
                    obstacle['height']
                )
                
                if player_rect.colliderect(obstacle_rect):
                    self.game_over = True
                    logger.info("Game over: Player hit obstacle")
                    
                    if self.crash_sound:
                        self.crash_sound.play()
                    
                    # Add crash particles
                    for _ in range(20):
                        angle = random.random() * math.pi * 2
                        speed = random.uniform(50, 150) * PIXEL_SCALE
                        self.particles.append(self.create_particle(
                            self.player_x, self.player_y,
                            COLORS.get('danger'),
                            random.uniform(2, 5),
                            random.uniform(0.5, 1.2),
                            math.cos(angle) * speed,
                            math.sin(angle) * speed
                        ))
        
        # Remove obstacles that are off-screen
        for idx in sorted(obstacles_to_remove, reverse=True):
            if 0 <= idx < len(self.obstacles):
                del self.obstacles[idx]
        
        # Update collectibles
        collectibles_to_remove = []
        for i, collectible in enumerate(self.collectibles):
            # Move collectible
            collectible['x'] -= collectible['speed'] * dt
            
            # Update rotation animation
            collectible['rotation'] += 180 * dt
            
            # Remove if off-screen
            if collectible['x'] + collectible['size'] < 0:
                collectibles_to_remove.append(i)
                continue
            
            # Check for collision with player
            if not self.game_over:
                player_rect = pygame.Rect(
                    self.player_x - self.player_size // 2,
                    self.player_y - self.player_size // 2,
                    self.player_size,
                    self.player_size
                )
                
                collectible_rect = pygame.Rect(
                    collectible['x'] - collectible['size'] // 2,
                    collectible['y'] - collectible['size'] // 2,
                    collectible['size'],
                    collectible['size']
                )
                
                if player_rect.colliderect(collectible_rect):
                    collectibles_to_remove.append(i)
                    self.score += collectible['value']
                    
                    if self.collect_sound:
                        self.collect_sound.play()
                    
                    # Add collection particles
                    for _ in range(10):
                        angle = random.random() * math.pi * 2
                        speed = random.uniform(30, 80) * PIXEL_SCALE
                        self.particles.append(self.create_particle(
                            collectible['x'], collectible['y'],
                            COLORS.get('cyan'),
                            random.uniform(1, 3),
                            random.uniform(0.3, 0.8),
                            math.cos(angle) * speed,
                            math.sin(angle) * speed
                        ))
        
        # Remove collected or off-screen collectibles
        for idx in sorted(collectibles_to_remove, reverse=True):
            if 0 <= idx < len(self.collectibles):
                del self.collectibles[idx]
    
    def draw(self):
        """Draw the game"""
        # Draw base background
        self.screen.fill(COLORS.get('bg_dark'))
        
        # Draw cyberpunk background
        self.draw_cyberpunk_background(self.time_elapsed)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(
                self.screen,
                obstacle['color'],
                (int(obstacle['x']), int(obstacle['y']), int(obstacle['width']), int(obstacle['height']))
            )
            
            # Add neon outline
            pygame.draw.rect(
                self.screen,
                COLORS.get('neon'),
                (int(obstacle['x']), int(obstacle['y']), int(obstacle['width']), int(obstacle['height'])),
                max(1, PIXEL_SCALE)
            )
        
        # Draw collectibles
        for collectible in self.collectibles:
            # Since rotation is expensive, we'll use sprite animation instead
            frame = int(collectible['rotation'] / 90) % 4
            x_offset = 0 if frame % 2 == 0 else collectible['size'] * 0.1
            y_offset = 0 if frame < 2 else collectible['size'] * 0.1
            
            self.screen.blit(
                self.collectible_sprite,
                (int(collectible['x'] - self.collectible_sprite.get_width() // 2 + x_offset),
                 int(collectible['y'] - self.collectible_sprite.get_height() // 2 + y_offset))
            )
        
        # Draw player
        self.screen.blit(
            self.player_sprite,
            (int(self.player_x - self.player_sprite.get_width() // 2),
             int(self.player_y - self.player_sprite.get_height() // 2))
        )
        
        # Draw jetpack flame if boosting
        if self.boosting and not self.game_over:
            flame_height = random.randint(15, 25) * PIXEL_SCALE
            flame_width = 10 * PIXEL_SCALE
            flame_x = self.player_x - self.player_size // 2 - flame_width // 2
            flame_y = self.player_y + self.player_size // 2
            
            # Randomize flame color
            flame_color = random.choice([COLORS.get('danger'), COLORS.get('warning')])
            
            # Draw flame
            flame_points = [
                (flame_x, flame_y),
                (flame_x + flame_width, flame_y),
                (flame_x + flame_width // 2, flame_y + flame_height)
            ]
            pygame.draw.polygon(self.screen, flame_color, flame_points)
            
            # Inner flame (brighter)
            inner_flame_height = flame_height * 0.7
            inner_flame_width = flame_width * 0.7
            inner_flame_x = flame_x + (flame_width - inner_flame_width) // 2
            inner_flame_points = [
                (inner_flame_x, flame_y),
                (inner_flame_x + inner_flame_width, flame_y),
                (flame_x + flame_width // 2, flame_y + inner_flame_height)
            ]
            pygame.draw.polygon(self.screen, COLORS.get('neon'), inner_flame_points)
        
        # Draw particles
        self.draw_particles()
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
    
# slith_minigames.py

# Inside class NeonJetpackGame:
    def draw_cyberpunk_background(self, time_elapsed):
        """Draw cyberpunk city background with correct right-to-left scrolling."""
        try:
            grid_size = 40 * PIXEL_SCALE
            grid_color = COLORS.get('grid', (40, 40, 60))
            if not isinstance(grid_color, (tuple, list)) or len(grid_color) < 3: 
                grid_color = (40, 40, 60)

            
            for x in range(int(self.bg_offset) % grid_size, self.width + grid_size, grid_size):
                pygame.draw.line(
                    self.screen, 
                    grid_color, 
                    (x, 0), 
                    (x, self.height), 
                    PIXEL_SCALE
                )
            
            # Horizontal lines (static)
            for y in range(0, self.height, grid_size):
                pygame.draw.line(
                    self.screen,
                    grid_color,
                    (0, y),
                    (self.width, y),
                    PIXEL_SCALE
                )
            
            # --- Draw Buildings (Right-to-Left Scroll) ---
            building_spacing = grid_size * 5
            
            # Calculate first building position that would be on screen
            first_building = int(self.bg_offset / building_spacing)
            
            # Draw enough buildings to fill the screen
            for i in range(first_building - 1, first_building + self.width // building_spacing + 2):
                # Calculate screen x-position for this building
                screen_x = i * building_spacing - int(self.bg_offset)
                
                # Skip if completely off-screen
                if screen_x + building_spacing < 0 or screen_x > self.width:
                    continue
                    
                # Use deterministic seed based on building's world position
                building_seed = hash(i)
                random.seed(building_seed)
                
                # Generate building properties
                building_height = random.randint(100, 400) * PIXEL_SCALE
                building_width = random.randint(40, 100) * PIXEL_SCALE
                building_x = screen_x + (building_spacing - building_width) // 2
                building_color = (
                    random.randint(10, 30),
                    random.randint(5, 25),
                    random.randint(20, 40)
                )
                
                # Draw the building
                draw_pixel_rect(
                    self.screen,
                    building_color,
                    (building_x, self.height - building_height, building_width, building_height),
                    PIXEL_SCALE
                )
                
                # Draw windows
                window_size = 4 * PIXEL_SCALE
                window_margin = 6 * PIXEL_SCALE
                window_spacing = 10 * PIXEL_SCALE
                
                window_colors = [
                    COLORS.get('neon', (255, 221, 0)),
                    COLORS.get('accent', (255, 105, 180)),
                    COLORS.get('cyan', (0, 255, 255)),
                    COLORS.get('terminal', (0, 200, 80))
                ]
                
                for wx in range(int(building_x + window_margin), int(building_x + building_width - window_margin), int(window_spacing)):
                    for wy in range(int(self.height - building_height + window_margin), int(self.height - window_margin), int(window_spacing)):
                        # Unique seed for each window
                        window_seed = hash((i, wx-building_x, wy-(self.height-building_height)))
                        random.seed(window_seed)
                        
                        # 70% chance window is lit
                        if random.random() < 0.7:
                            window_color = random.choice(window_colors)
                            draw_pixel_rect(
                                self.screen,
                                window_color,
                                (wx, wy, window_size, window_size),
                                PIXEL_SCALE
                            )
            
            # Reset random seed
            random.seed(None)
            
        except Exception as e:
            logger.error(f"Error drawing cyberpunk background: {e}", exc_info=True)
            self.screen.fill(COLORS.get('bg_dark', (10, 8, 16)))




# --- SignalTracer Game ---
class SignalTracerGame(BaseMinigame):
    """
    Signal Tracer Game
    Navigate the grid to trace signal patterns in the correct order
    """
    
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        
        # Set title and instructions
        self.title = "SIGNAL TRACER"
        self.instructions = [
            "Navigate the grid to trace signal patterns!",
            "",
            "- Use arrow keys to move your cursor",
            "- Trace over signal paths in the correct order",
            "- Follow the numbered sequence (1, 2, 3...)",
            "- Numbers disappear at higher levels!",
            "- Watch out for decoys and interference",
            "- Complete patterns before time runs out",
            "",
            "Press SPACE or click to start"
        ]
        
        # Game specific variables
        self.grid_size = 10  # Larger grid, more challenge
        self.cell_size = min(self.width, self.height) // (self.grid_size + 4)
        self.grid_offset_x = (self.width - self.grid_size * self.cell_size) // 2
        self.grid_offset_y = (self.height - self.grid_size * self.cell_size) // 2
        
        # Initialize grid and paths
        self.grid = None
        self.target_path = None
        self.player_path = None
        self.player_pos = None
        self.decoy_cells = []  # For decoy signals
        self.interference = [] # For static interference
        
        # Game state
        self.level = 1
        self.timer = 60
        self.game_active = False
        self.show_numbers = True  # Numbers hide at higher levels
        self.hint_timer = 0  # For periodic hints
        self.hint_interval = 5  # Show hint every 5 seconds
        self.hint_duration = 0.5  # Show hint for 0.5 seconds
        self.hint_active = False
        
        # Sounds
        self.win_sound = generate_beep(880, 300, 0.15)
        self.move_sound = generate_beep(440, 50, 0.05)
        self.error_sound = generate_beep(220, 100, 0.1)
        self.decoy_sound = generate_beep(330, 100, 0.1)
        
        # Generate first level
        self.generate_level()
        
    def generate_level(self):
        """Generate a new level with signal path and challenges"""
        # Create empty grid
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Reset paths and challenges
        self.player_path = []
        self.target_path = []
        self.decoy_cells = []
        self.interference = []
        
        # Set player to random position
        self.player_pos = [
            random.randint(1, self.grid_size - 2),
            random.randint(1, self.grid_size - 2)
        ]
        
        # Start target path from player position
        start_pos = tuple(self.player_pos)
        self.target_path.append(start_pos)
        
        # Generate path with increasing difficulty
        path_length = 3 + self.level * 2  # More steps at higher levels
        current = start_pos
        
        # Generate path steps
        for step in range(1, path_length):
            # Find valid moves (adjacent cells not in path)
            valid_moves = []
            x, y = current
            
            # Check all four directions
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, Right, Down, Left
                nx, ny = x + dx, y + dy
                
                # Check bounds and not already in path
                if (0 <= nx < self.grid_size and 
                    0 <= ny < self.grid_size and 
                    (nx, ny) not in self.target_path):
                    valid_moves.append((nx, ny))
            
            # If no valid moves, break early
            if not valid_moves:
                break
                
            # Choose random valid move with preference for longer paths
            weights = [1.0] * len(valid_moves)
            for i, (nx, ny) in enumerate(valid_moves):
                # Prefer cells that are further from other path cells
                min_dist = float('inf')
                for px, py in self.target_path:
                    dist = abs(px - nx) + abs(py - ny)
                    min_dist = min(min_dist, dist)
                # Higher weight for cells further away
                weights[i] = min_dist * 0.5 + 1.0
            
            # Weighted random choice if available
            if hasattr(random, 'choices'):  # Python 3.6+
                next_pos = random.choices(valid_moves, weights=weights, k=1)[0]
            else:
                # Fallback for older Python
                next_pos = random.choice(valid_moves)
            
            self.target_path.append(next_pos)
            current = next_pos
        
        # Mark grid cells with path numbers
        for i, (x, y) in enumerate(self.target_path):
            self.grid[y][x] = i + 1  # 1-based indexing
        
        # Add decoy paths (increasing with level)
        num_decoys = min(10, self.level + 2)
        for _ in range(num_decoys):
            # Find empty cell for decoy
            while True:
                dx = random.randint(0, self.grid_size - 1)
                dy = random.randint(0, self.grid_size - 1)
                if self.grid[dy][dx] == 0:
                    # Assign a random number that's in the path
                    decoy_value = random.randint(1, len(self.target_path))
                    self.grid[dy][dx] = -decoy_value  # Negative indicates decoy
                    self.decoy_cells.append((dx, dy))
                    break
        
        # Add interference (static) in later levels
        if self.level >= 3:
            num_interference = self.level - 2
            for _ in range(num_interference):
                # Find empty cell for interference
                while True:
                    ix = random.randint(0, self.grid_size - 1)
                    iy = random.randint(0, self.grid_size - 1)
                    if self.grid[iy][ix] == 0:
                        self.grid[iy][ix] = -99  # Special value for interference
                        self.interference.append((ix, iy))
                        break
        
        # Decide whether to show numbers based on level
        self.show_numbers = self.level <= 3  # Only show in first 3 levels
        
        # Reset player path and include starting position
        self.player_path = [start_pos]
        
        # Set timer based on level (less time at higher levels)
        self.timer = max(15, 60 - self.level * 3)
        self.game_active = True
        self.hint_timer = 0
        self.hint_active = False
        
    def handle_input(self, events):
        """Handle player input"""
        if not super().handle_input(events):
            return False
        
        if self.game_over:
            return True
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.game_active:
                    continue
                    
                # Store original position
                old_pos = self.player_pos.copy()
                moved = False
                
                # Handle arrow key movements
                if event.key == pygame.K_UP and self.player_pos[1] > 0:
                    self.player_pos[1] -= 1
                    moved = True
                elif event.key == pygame.K_DOWN and self.player_pos[1] < self.grid_size - 1:
                    self.player_pos[1] += 1
                    moved = True
                elif event.key == pygame.K_LEFT and self.player_pos[0] > 0:
                    self.player_pos[0] -= 1
                    moved = True
                elif event.key == pygame.K_RIGHT and self.player_pos[0] < self.grid_size - 1:
                    self.player_pos[0] += 1
                    moved = True
                
                if moved:
                    # Get new position
                    new_pos = tuple(self.player_pos)
                    cell_value = self.grid[self.player_pos[1]][self.player_pos[0]]
                    
                    # Check for interference cell
                    if cell_value == -99:
                        # Interference: random teleport and lose time
                        self.timer -= 3  # Lose 3 seconds
                        
                        # Teleport to random position (not on path or interference)
                        valid_teleports = []
                        for r in range(self.grid_size):
                            for c in range(self.grid_size):
                                if self.grid[r][c] == 0:
                                    valid_teleports.append((c, r))
                        
                        if valid_teleports:
                            new_pos = random.choice(valid_teleports)
                            self.player_pos = list(new_pos)
                        else:
                            # Fallback to old position
                            self.player_pos = old_pos
                            new_pos = tuple(old_pos)
                        
                        # Create interference particles
                        cx = self.grid_offset_x + self.player_pos[0] * self.cell_size + self.cell_size // 2
                        cy = self.grid_offset_y + self.player_pos[1] * self.cell_size + self.cell_size // 2
                        
                        for _ in range(10):
                            angle = random.random() * math.pi * 2
                            speed = random.uniform(30, 100) * PIXEL_SCALE
                            color = COLORS.get('danger', (255, 50, 50))
                            self.particles.append(self.create_particle(
                                cx, cy, color, random.uniform(2, 4),
                                random.uniform(0.5, 1.0),
                                math.cos(angle) * speed, math.sin(angle) * speed
                            ))
                        
                        if self.error_sound:
                            self.error_sound.play()
                    
                    # Check if this position is already in our path
                    if new_pos in self.player_path:
                        # If revisiting a position, truncate path up to this point
                        index = self.player_path.index(new_pos)
                        self.player_path = self.player_path[:index+1]
                    else:
                        # Add new position to path
                        self.player_path.append(new_pos)
                        
                        # Check for decoy cell
                        if cell_value < 0 and cell_value != -99:
                            # Stepped on decoy
                            self.timer -= 2  # Lose 2 seconds
                            
                            # Create decoy particles
                            cx = self.grid_offset_x + self.player_pos[0] * self.cell_size + self.cell_size // 2
                            cy = self.grid_offset_y + self.player_pos[1] * self.cell_size + self.cell_size // 2
                            
                            for _ in range(5):
                                angle = random.random() * math.pi * 2
                                speed = random.uniform(20, 60) * PIXEL_SCALE
                                color = COLORS.get('warning', (255, 165, 0))
                                self.particles.append(self.create_particle(
                                    cx, cy, color, random.uniform(1, 3),
                                    random.uniform(0.3, 0.8),
                                    math.cos(angle) * speed, math.sin(angle) * speed
                                ))
                            
                            if self.decoy_sound:
                                self.decoy_sound.play()
                        else:
                            # Not a decoy or interference, check path correctness
                            expected_step = len(self.player_path)
                            expected_pos = self.target_path[expected_step-1] if expected_step-1 < len(self.target_path) else None
                            
                            # Check if this matches the expected path step
                            if new_pos != expected_pos:
                                # Wrong move - revert position and truncate path
                                self.player_pos = old_pos
                                self.player_path.pop()  # Remove last position
                                
                                # Play error sound
                                if self.error_sound:
                                    self.error_sound.play()
                                continue
                            
                            # Correct move
                            if self.move_sound:
                                self.move_sound.play()
                            
                            # Create movement particles
                            cx = self.grid_offset_x + self.player_pos[0] * self.cell_size + self.cell_size // 2
                            cy = self.grid_offset_y + self.player_pos[1] * self.cell_size + self.cell_size // 2
                            
                            for _ in range(3):
                                angle = random.random() * math.pi * 2
                                speed = random.uniform(10, 30) * PIXEL_SCALE
                                color = COLORS.get('cyan', (0, 255, 255))
                                self.particles.append(self.create_particle(
                                    cx, cy, color, random.uniform(1, 2),
                                    random.uniform(0.3, 0.6),
                                    math.cos(angle) * speed, math.sin(angle) * speed
                                ))
                    
                    # Check if level complete
                    if len(self.player_path) == len(self.target_path):
                        # Verify entire path matches
                        correct = all(p1 == p2 for p1, p2 in zip(self.player_path, self.target_path))
                        
                        if correct:
                            # Level complete!
                            self.level += 1
                            self.score += int(self.timer * 10 * (1 + self.level * 0.1))  # More points at higher levels
                            
                            # Play victory sound
                            if self.win_sound:
                                self.win_sound.play()
                            
                            # Create success particles
                            for pos in self.player_path:
                                cx = self.grid_offset_x + pos[0] * self.cell_size + self.cell_size // 2
                                cy = self.grid_offset_y + pos[1] * self.cell_size + self.cell_size // 2
                                
                                for _ in range(5):
                                    angle = random.random() * math.pi * 2
                                    speed = random.uniform(30, 80) * PIXEL_SCALE
                                    color = COLORS.get('neon', (255, 221, 0))
                                    self.particles.append(self.create_particle(
                                        cx, cy, color, random.uniform(1, 3),
                                        random.uniform(0.5, 1.0),
                                        math.cos(angle) * speed, math.sin(angle) * speed
                                    ))
                            
                            # Generate next level
                            self.generate_level()
        
        return True
    
    def update(self, dt):
        """Update game state"""
        super().update(dt)
        
        if self.game_over or not self.game_active:
            return
        
        # Update timer
        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0
            self.game_over = True
            logger.info("Game over: Time expired")
            
        # Update hint timer
        self.hint_timer += dt
        if self.hint_timer >= self.hint_interval:
            self.hint_active = True
            if self.hint_timer >= self.hint_interval + self.hint_duration:
                self.hint_active = False
                self.hint_timer = 0

    def draw_grid_background(self):
        """Draw background effects for grid"""
        # Draw horizontal and vertical scan lines
        scan_time = self.time_elapsed * 2
        
        # Horizontal scan
        h_scan_y = int(self.height * (0.5 + 0.4 * math.sin(scan_time * 0.3)))
        h_scan_height = 10 * PIXEL_SCALE
        h_scan_rect = pygame.Rect(0, h_scan_y - h_scan_height // 2, self.width, h_scan_height)
        h_scan_color = (*COLORS.get('terminal', (0, 200, 80))[:3], 30)  # Semi-transparent
        
        pygame.draw.rect(self.screen, h_scan_color, h_scan_rect)
        
        # Vertical scan
        v_scan_x = int(self.width * (0.5 + 0.4 * math.sin(scan_time * 0.2 + math.pi / 2)))
        v_scan_width = 10 * PIXEL_SCALE
        v_scan_rect = pygame.Rect(v_scan_x - v_scan_width // 2, 0, v_scan_width, self.height)
        v_scan_color = (*COLORS.get('accent', (255, 105, 180))[:3], 30)  # Semi-transparent
        
        pygame.draw.rect(self.screen, v_scan_color, v_scan_rect)
        
        # Draw grid overlay
        grid_spacing = 40 * PIXEL_SCALE
        grid_color = (*COLORS.get('grid', (40, 40, 60))[:3], 20)  # Very transparent
        
        # Draw horizontal grid lines
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), max(1, PIXEL_SCALE // 2))
            
        # Draw vertical grid lines
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), max(1, PIXEL_SCALE // 2))

    def draw(self):
        """Draw the Signal Tracer game"""
        try:
            # Fill background
            self.screen.fill(COLORS.get('bg_dark', (10, 8, 16)))
            
            # Draw grid background
            self.draw_grid_background()
            
            # Draw grid and numbered cells
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    cell_x = self.grid_offset_x + c * self.cell_size
                    cell_y = self.grid_offset_y + r * self.cell_size
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    
                    # Draw cell outline
                    pygame.draw.rect(self.screen, COLORS.get('grid', (40, 40, 60)), cell_rect, PIXEL_SCALE)
                    
                    # Get cell value (step number)
                    cell_value = self.grid[r][c]
                    
                    # Negative values are decoys or interference
                    is_decoy = cell_value < 0 and cell_value != -99
                    is_interference = cell_value == -99
                    is_path = cell_value > 0
                    
                    # Inner rectangle
                    inner_rect = pygame.Rect(
                        cell_x + PIXEL_SCALE, 
                        cell_y + PIXEL_SCALE, 
                        self.cell_size - 2*PIXEL_SCALE, 
                        self.cell_size - 2*PIXEL_SCALE
                    )
                    
                    # Draw path cells
                    if is_path:
                        # Path cell: different colors based on step number
                        factor = min(1.0, cell_value / len(self.target_path))
                        start_color = COLORS.get('terminal', (0, 200, 80))
                        end_color = COLORS.get('cyan', (0, 255, 255))
                        
                        # Linear interpolation between colors
                        cell_color = (
                            int(start_color[0] + (end_color[0] - start_color[0]) * factor),
                            int(start_color[1] + (end_color[1] - start_color[1]) * factor),
                            int(start_color[2] + (end_color[2] - start_color[2]) * factor)
                        )
                        
                        # Draw cell fill
                        pygame.draw.rect(self.screen, cell_color, inner_rect)
                        
                        # Draw step number if enabled or hint is active
                        show_number = self.show_numbers or (self.hint_active and not self.show_numbers)
                        if show_number:
                            util_draw_text(
                                self.screen,
                                str(cell_value),
                                self.game_font_medium,
                                COLORS.get('text', (220, 220, 255)),
                                cell_x + self.cell_size // 2,
                                cell_y + self.cell_size // 2,
                                True
                            )
                    
                    # Draw decoy cells
                    elif is_decoy:
                        # Decoy cell: similar color but different shade
                        abs_value = abs(cell_value)
                        factor = min(1.0, abs_value / len(self.target_path))
                        
                        # Yellow-orange gradient for decoys
                        start_color = COLORS.get('warning', (255, 165, 0))
                        end_color = COLORS.get('neon', (255, 221, 0))
                        
                        # Linear interpolation
                        cell_color = (
                            int(start_color[0] + (end_color[0] - start_color[0]) * factor),
                            int(start_color[1] + (end_color[1] - start_color[1]) * factor),
                            int(start_color[2] + (end_color[2] - start_color[2]) * factor)
                        )
                        
                        # Draw cell fill
                        pygame.draw.rect(self.screen, cell_color, inner_rect)
                        
                        # Show number during hint or at lower levels
                        show_number = self.level <= 2 or (self.hint_active and self.level <= 5)
                        if show_number:
                            util_draw_text(
                                self.screen,
                                str(abs_value),
                                self.game_font_medium,
                                COLORS.get('text', (220, 220, 255)),
                                cell_x + self.cell_size // 2,
                                cell_y + self.cell_size // 2,
                                True
                            )
                    
                    # Draw interference cells
                    elif is_interference:
                        # Static effect
                        static_color = COLORS.get('danger', (255, 50, 50))
                        
                        # Draw static blocks
                        block_size = max(2, PIXEL_SCALE)
                        for sx in range(inner_rect.left, inner_rect.right, block_size*2):
                            for sy in range(inner_rect.top, inner_rect.bottom, block_size*2):
                                # Random static
                                if random.random() < 0.4:
                                    static_rect = pygame.Rect(sx, sy, block_size, block_size)
                                    pygame.draw.rect(self.screen, static_color, static_rect)
            
            # Draw player path
            if len(self.player_path) > 1:
                path_color = COLORS.get('neon', (255, 221, 0))
                
                for i in range(len(self.player_path) - 1):
                    start_x, start_y = self.player_path[i]
                    end_x, end_y = self.player_path[i+1]
                    
                    # Convert to screen coordinates
                    start_px = self.grid_offset_x + start_x * self.cell_size + self.cell_size // 2
                    start_py = self.grid_offset_y + start_y * self.cell_size + self.cell_size // 2
                    end_px = self.grid_offset_x + end_x * self.cell_size + self.cell_size // 2
                    end_py = self.grid_offset_y + end_y * self.cell_size + self.cell_size // 2
                    
                    # Draw line with thickness
                    pygame.draw.line(self.screen, path_color, (start_px, start_py), (end_px, end_py), PIXEL_SCALE * 2)
            
            # Draw player cursor with pulsing effect
            player_x = self.grid_offset_x + self.player_pos[0] * self.cell_size
            player_y = self.grid_offset_y + self.player_pos[1] * self.cell_size
            
            # Calculate pulse effect
            pulse = math.sin(time.time() * 5) * 3
            cursor_size = int(self.cell_size * 0.8 + pulse)
            cursor_offset = (self.cell_size - cursor_size) // 2
            
            cursor_rect = pygame.Rect(
                player_x + cursor_offset,
                player_y + cursor_offset,
                cursor_size,
                cursor_size
            )
            
            cursor_color = COLORS.get('accent', (255, 105, 180))
            pygame.draw.rect(self.screen, cursor_color, cursor_rect, PIXEL_SCALE * 2)
            
            # Draw particles
            self.draw_particles()
            
            # Draw UI
            self.draw_ui()
            
            # Draw hint indicator
            if not self.show_numbers:
                hint_text = "HINT in" if not self.hint_active else "HINT!"
                hint_color = COLORS.get('terminal', (0, 200, 80)) if self.hint_active else COLORS.get('text_dark', (120, 120, 160))
                hint_time = max(0, int(self.hint_interval - self.hint_timer)) if not self.hint_active else int(self.hint_duration - (self.hint_timer - self.hint_interval))
                
                if hint_time > 0 or self.hint_active:
                    hint_str = f"{hint_text}: {hint_time}s"
                    util_draw_text(
                        self.screen,
                        hint_str,
                        self.game_font_small,
                        hint_color,
                        self.width // 2,
                        self.height - 60,
                        True
                    )
            
            # Draw level difficulty indicator
            difficulty_str = f"Difficulty: {'★' * min(5, self.level)}"
            util_draw_text(
                self.screen,
                difficulty_str,
                self.game_font_small,
                COLORS.get('warning', (255, 165, 0)),
                self.width // 2,
                40,
                True
            )
            
            # Draw game over screen if needed
            if self.game_over:
                self.draw_game_over()
                
        except Exception as e:
            logger.error(f"Error drawing Signal Tracer game: {e}", exc_info=True)
            self.screen.fill((0, 0, 0))
            util_draw_text(self.screen, f"DRAW ERROR: {e}", self.game_font_medium, (255, 0, 0), self.width//2, self.height//2, True)
    
    def draw_ui(self):
        """Draw game UI elements"""
        # Score display
        util_draw_text(
            self.screen,
            f"SCORE: {self.score}",
            self.game_font_medium,
            COLORS.get('neon', (255, 221, 0)),
            10,
            10,
            False
        )
        
        # Level display
        util_draw_text(
            self.screen,
            f"LEVEL: {self.level}",
            self.game_font_medium,
            COLORS.get('neon', (255, 221, 0)),
            self.width // 2,
            10,
            True
        )
        
        # Timer display - color changes as time runs out
        timer_pct = self.timer / (30 + self.level * 5)  # Calculate percentage of time left
        
        if timer_pct < 0.3:
            timer_color = COLORS.get('danger', (255, 50, 50))
        elif timer_pct < 0.6:
            timer_color = COLORS.get('warning', (255, 165, 0))
        else:
            timer_color = COLORS.get('neon', (255, 221, 0))
            
        util_draw_text(
            self.screen,
            f"TIME: {int(self.timer)}s",
            self.game_font_medium,
            timer_color,
            self.width - 10,
            10,
            False,
            right_aligned=True
        )
        
        # Controls reminder
        util_draw_text(
            self.screen,
            "Use Arrow Keys to Move",
            self.game_font_small,
            COLORS.get('text', (220, 220, 255)),
            self.width // 2,
            self.height - 30,
            True
        )


# --- Initialize and Run Minigames ---
def get_available_minigames():
    """Return dictionary of available minigames"""
    return {
        'node_defender': NodeDefenderGame,
        'terminal_typer': TerminalTyperGame,
        'neon_jetpack': NeonJetpackGame,
        'signal_tracer': SignalTracerGame
    }

# Entry point function
def run_minigame(screen, clock, game_id):
    """Run a specific minigame by ID"""
    minigames = get_available_minigames()
    
    if game_id in minigames:
        game_class = minigames[game_id]
        game = game_class(screen, clock)
        return game.run()
    else:
        logger.error(f"Unknown minigame ID: {game_id}")
        return 0, 0