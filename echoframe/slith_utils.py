"""
Enhanced utility functions for the Slith Pet game with pixel art aesthetics
"""
import pygame
import math
import random
from datetime import datetime, timedelta
import logging # Import logging

# --- Setup Basic Logging ---
# (Assuming logging is configured elsewhere or add basicConfig here if needed)
logger = logging.getLogger(__name__)

# --- Constants Fallback (Keep for standalone use/testing if needed) ---
try:
    from slith_constants import COLORS, STAGES, UI, PIXEL_SCALE, GRID, DIGITAL_RAIN, PARTICLES, CRT_EFFECT, VITALS
    logger.info("Successfully imported constants from slith_constants.")
except ImportError:
    logger.warning("slith_constants.py not found. Using placeholder values in slith_utils.")
    PIXEL_SCALE = 2
    COLORS = {'bg_dark': (10, 8, 16), 'accent': (255, 105, 180), 'neon': (255, 221, 0), 'text': (220, 220, 255)}
    UI = {'progress_border': 2, 'border_thickness': 2, 'panel_padding': 8}
    VITALS = {'decay_rates': {'patience': 4}} # Example fallback
    # Add other fallback constants if functions below depend on them directly

# --- Utility Functions ---

def format_time_delta(seconds):
    """Formats a duration in seconds into a human-readable string (h/m/s)."""
    if seconds < 0:
        return "0s" # Handle negative durations gracefully
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

# --- MODIFIED draw_text function ---
def draw_text(surface, text, font, color, x, y, centered=True, shadow=True, shadow_color=None, shadow_offset=2, right_aligned=False): # Added right_aligned parameter
    """
    Draw pixel art style text on a surface with optional centering, right-alignment, and shadow

    Args:
        surface (pygame.Surface): Surface to draw on
        text (str): Text to draw
        font (pygame.font.Font): Font to use
        color (tuple): RGB color tuple
        x (int): X coordinate (meaning depends on alignment)
        y (int): Y coordinate (meaning depends on alignment, usually vertical center or top)
        centered (bool): If True, center text horizontally at x. Overrides right_aligned.
        shadow (bool): Whether to draw text shadow
        shadow_color (tuple): RGB color for shadow, defaults to darkened text color
        shadow_offset (int): Pixel offset for shadow
        right_aligned (bool): If True and centered is False, align text's right edge to x.
    """
    # If no shadow color provided, create a darker version of the text color
    if shadow_color is None:
        r, g, b = color
        shadow_color = (max(r - 100, 0), max(g - 100, 0), max(b - 100, 0))

    # Render text surfaces
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if shadow:
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect()

    # Position the rectangle based on alignment flags
    if centered:
        text_rect.center = (x, y)
        if shadow:
            shadow_rect.center = (x + shadow_offset, y + shadow_offset)
    elif right_aligned:
        # Align top-right corner to (x, y)
        # Note: Pygame's rect positioning can be tricky. Adjust y as needed.
        # This aligns the vertical *center* of the right edge to (x, y)
        text_rect.centery = y
        text_rect.right = x
        if shadow:
            shadow_rect.centery = y + shadow_offset
            shadow_rect.right = x + shadow_offset
    else: # Default to top-left alignment
        text_rect.topleft = (x, y)
        if shadow:
            shadow_rect.topleft = (x + shadow_offset, y + shadow_offset)

    # Draw shadow first if enabled
    if shadow:
        surface.blit(shadow_surface, shadow_rect)

    # Then draw the main text
    surface.blit(text_surface, text_rect)

    return text_rect
# --- END MODIFIED draw_text function ---


def draw_pixelated_rect(surface, rect, color, border_width=0, border_color=None, corner_radius=0):
    """
    Draw a pixelated rectangle with pixel-perfect borders and optional rounded corners

    Args:
        surface (pygame.Surface): Surface to draw on
        rect (pygame.Rect): Rectangle dimensions
        color (tuple): RGB color tuple
        border_width (int): Border width in pixels (0 for filled rect)
        border_color (tuple): RGB border color, defaults to color
        corner_radius (int): Corner radius in pixels (0 for square corners)
    """
    x, y, width, height = rect

    # Default border color to same as fill color
    if border_color is None:
        border_color = color

    # Scale to pixel grid
    pixel = PIXEL_SCALE
    x = (x // pixel) * pixel
    y = (y // pixel) * pixel
    width = ((width + pixel - 1) // pixel) * pixel  # Round up to nearest pixel
    height = ((height + pixel - 1) // pixel) * pixel  # Round up to nearest pixel

    # Scale border and radius
    border_width = ((border_width + pixel - 1) // pixel) * pixel  # Round up
    corner_radius = ((corner_radius + pixel - 1) // pixel) * pixel  # Round up

    if border_width > 0:
        # Draw border first
        for px in range(x, x + width, pixel):
            for py in range(y, y + height, pixel):
                # Check if this pixel is on the border
                is_border = (
                    px < x + border_width or  # Left border
                    px >= x + width - border_width or  # Right border
                    py < y + border_width or  # Top border
                    py >= y + height - border_width  # Bottom border
                )

                # Skip corners if rounded
                if corner_radius > 0:
                    # Check if in corner regions
                    in_top_left = px < x + corner_radius and py < y + corner_radius
                    in_top_right = px >= x + width - corner_radius and py < y + corner_radius
                    in_bottom_left = px < x + corner_radius and py >= y + height - corner_radius
                    in_bottom_right = px >= x + width - corner_radius and py >= y + height - corner_radius

                    if in_top_left or in_top_right or in_bottom_left or in_bottom_right:
                        # Calculate distance from corner
                        cx, cy = 0, 0
                        if in_top_left:
                            cx, cy = x + corner_radius, y + corner_radius
                        elif in_top_right:
                            cx, cy = x + width - corner_radius, y + corner_radius
                        elif in_bottom_left:
                            cx, cy = x + corner_radius, y + height - corner_radius
                        else:  # bottom_right
                            cx, cy = x + width - corner_radius, y + height - corner_radius

                        # Distance from corner center
                        dist = math.sqrt((px - cx + pixel/2)**2 + (py - cy + pixel/2)**2)

                        # Check if outside inner radius but inside outer radius
                        inner_radius = corner_radius - border_width
                        if dist > inner_radius and dist <= corner_radius:
                            pygame.draw.rect(surface, border_color, (px, py, pixel, pixel))
                        continue

                if is_border:
                    pygame.draw.rect(surface, border_color, (px, py, pixel, pixel))

        # Then draw inner filled rect if needed
        if border_width < width // 2 and border_width < height // 2:
            inner_rect = pygame.Rect(
                x + border_width,
                y + border_width,
                width - 2 * border_width,
                height - 2 * border_width
            )
            draw_pixelated_rect(surface, inner_rect, color, 0, None, max(0, corner_radius - border_width))
    else:
        # Just draw filled rect
        for px in range(x, x + width, pixel):
            for py in range(y, y + height, pixel):
                # Skip corners if rounded
                if corner_radius > 0:
                    # Check if in corner regions
                    in_top_left = px < x + corner_radius and py < y + corner_radius
                    in_top_right = px >= x + width - corner_radius and py < y + corner_radius
                    in_bottom_left = px < x + corner_radius and py >= y + height - corner_radius
                    in_bottom_right = px >= x + width - corner_radius and py >= y + height - corner_radius

                    if in_top_left or in_top_right or in_bottom_left or in_bottom_right:
                        # Calculate distance from corner
                        cx, cy = 0, 0
                        if in_top_left:
                            cx, cy = x + corner_radius, y + corner_radius
                        elif in_top_right:
                            cx, cy = x + width - corner_radius, y + corner_radius
                        elif in_bottom_left:
                            cx, cy = x + corner_radius, y + height - corner_radius
                        else:  # bottom_right
                            cx, cy = x + width - corner_radius, y + height - corner_radius

                        # Distance from corner center
                        dist = math.sqrt((px - cx + pixel/2)**2 + (py - cy + pixel/2)**2)

                        # Skip if outside radius
                        if dist > corner_radius:
                            continue

                pygame.draw.rect(surface, color, (px, py, pixel, pixel))

def draw_progress_bar(surface, x, y, width, height, percentage, color, border_color=None, background_color=None, use_pixel_font=False, pixel_font=None): # Added pixel font args
    """
    Draw a pixelated progress bar

    Args:
        surface (pygame.Surface): Surface to draw on
        x (int): X coordinate of top-left corner
        y (int): Y coordinate of top-left corner
        width (int): Width of the progress bar
        height (int): Height of the progress bar
        percentage (float): Percentage filled (0-100)
        color (tuple): RGB color tuple for the fill
        border_color (tuple): RGB color for border, defaults to darker color
        background_color (tuple): RGB color for background, defaults to COLORS['bg_dark']
        use_pixel_font (bool): Whether to use the provided pixel font for text
        pixel_font (pygame.font.Font): The pixel font object to use
    """
    pixel = PIXEL_SCALE

    # Quantize coordinates to pixel grid
    x = (x // pixel) * pixel
    y = (y // pixel) * pixel
    width = ((width + pixel - 1) // pixel) * pixel  # Round up to nearest pixel
    height = ((height + pixel - 1) // pixel) * pixel  # Round up to nearest pixel

    # Default colors
    if background_color is None:
        background_color = COLORS.get('bg_dark', (10, 8, 16)) # Use .get with fallback
    if border_color is None:
        r, g, b = color
        border_color = (max(r - 70, 0), max(g - 70, 0), max(b - 70, 0))

    # Create background (darker shade)
    background_rect = pygame.Rect(x, y, width, height)
    progress_border_width = UI.get('progress_border', 2) # Use .get with fallback
    draw_pixelated_rect(surface, background_rect, background_color, progress_border_width, border_color, height // 3)

    # Calculate fill width
    fill_width = int((percentage / 100) * (width - 2 * progress_border_width))

    # Draw fill if width > 0
    if fill_width > 0:
        fill_rect = pygame.Rect(
            x + progress_border_width,
            y + progress_border_width,
            fill_width,
            height - 2 * progress_border_width
        )
        draw_pixelated_rect(surface, fill_rect, color, 0, None, (height - 2 * progress_border_width) // 3)

    # Draw percentage text
    percentage_text = f"{int(percentage)}%"
    # Choose font based on flag
    font_to_use = pixel_font if use_pixel_font and pixel_font else pygame.font.SysFont('Arial', height - 6)

    # Calculate text color (light or dark depending on fill color)
    r, g, b = color
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

    # Draw text using the selected font
    draw_text(surface, percentage_text, font_to_use, text_color, x + width//2, y + height//2,
             centered=True, shadow=False, shadow_color=(0, 0, 0), shadow_offset=pixel)


def draw_cyberpunk_button(surface, rect, text, font, color, border_color=None, hover=False, active=False):
    """
    Draw a pixelated cyberpunk-styled button

    Args:
        surface (pygame.Surface): Surface to draw on
        rect (pygame.Rect): Button rectangle
        text (str): Button text
        font (pygame.font.Font): Font to use
        color (tuple): RGB color tuple
        border_color (tuple): RGB border color, defaults to darker color
        hover (bool): Whether button is being hovered
        active (bool): Whether button is active/pressed
    """
    x, y, width, height = rect

    # Default border color
    if border_color is None:
        r, g, b = color
        border_color = (min(r + 50, 255), min(g + 50, 255), min(b + 50, 255))

    # Style changes for hover and active states
    if active:
        # Swap colors and add inset effect
        bg_color = border_color
        edge_color = color
        x += PIXEL_SCALE
        y += PIXEL_SCALE
        width -= 2 * PIXEL_SCALE
        height -= 2 * PIXEL_SCALE
    elif hover:
        # Brighter colors for hover
        r, g, b = color
        bg_color = (min(r + 20, 255), min(g + 20, 255), min(b + 20, 255))
        r, g, b = border_color
        edge_color = (min(r + 30, 255), min(g + 30, 255), min(b + 30, 255))
    else:
        bg_color = color
        edge_color = border_color

    # Draw button background
    button_rect = pygame.Rect(x, y, width, height)
    border_thickness = UI.get('border_thickness', 2) # Use .get with fallback
    border_width = border_thickness * (2 if hover else 1)
    draw_pixelated_rect(surface, button_rect, bg_color, border_width, edge_color, height // 4)

    # Draw text with shadow for cyber effect
    text_color = COLORS.get('text', (220, 220, 255)) # Use .get with fallback
    shadow_offset = PIXEL_SCALE * 2
    text_y_offset = PIXEL_SCALE if active else 0  # Text shifts down when active

    draw_text(surface, text, font, text_color,
             x + width // 2, y + height // 2 + text_y_offset,
             centered=True, shadow=True, shadow_offset=shadow_offset)

    # Add cyber corner accents
    corner_size = min(10, height // 4)
    corners = [
        (x, y),  # Top left
        (x + width - corner_size, y),  # Top right
        (x, y + height - corner_size),  # Bottom left
        (x + width - corner_size, y + height - corner_size)  # Bottom right
    ]

    for cx, cy in corners:
        # Draw L-shaped corner accent
        accent_color = COLORS.get('accent', (255, 105, 180)) if hover else edge_color # Use .get with fallback
        for offset in range(0, corner_size, PIXEL_SCALE):
            # Horizontal line
            pygame.draw.rect(surface, accent_color,
                           (cx + offset, cy, PIXEL_SCALE, PIXEL_SCALE))
            # Vertical line
            pygame.draw.rect(surface, accent_color,
                           (cx, cy + offset, PIXEL_SCALE, PIXEL_SCALE))

def draw_cyberpunk_panel(surface, rect, title=None, font=None, border_color=None, bg_color=None, alpha=255):
    """
    Draw a pixelated cyberpunk-styled panel/window

    Args:
        surface (pygame.Surface): Surface to draw on
        rect (pygame.Rect): Panel rectangle
        title (str): Optional panel title
        font (pygame.font.Font): Font for title
        border_color (tuple): RGB border color, defaults to COLORS['accent']
        bg_color (tuple): RGB background color, defaults to COLORS['bg_dark']
        alpha (int): Alpha transparency (0-255)
    """
    x, y, width, height = rect

    # Default colors
    if border_color is None:
        border_color = COLORS.get('accent', (255, 105, 180)) # Use .get with fallback
    if bg_color is None:
        bg_color = COLORS.get('bg_dark', (10, 8, 16)) # Use .get with fallback

    # Create semi-transparent panel if alpha < 255
    if alpha < 255:
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_color = list(bg_color) + [alpha]  # Add alpha
        border_color = list(border_color) + [alpha]  # Add alpha
    else:
        panel_surface = pygame.Surface((width, height))

    # Draw panel background
    panel_rect = pygame.Rect(0, 0, width, height)
    border_thickness = UI.get('border_thickness', 2) # Use .get with fallback
    draw_pixelated_rect(panel_surface, panel_rect, bg_color, border_thickness, border_color, height // 20)

    # Add title bar if provided
    if title and font:
        panel_padding = UI.get('panel_padding', 8) # Use .get with fallback
        title_height = font.get_height() + panel_padding * 2
        title_rect = pygame.Rect(0, 0, width, title_height)

        # Title bar background
        draw_pixelated_rect(panel_surface, title_rect, border_color, 0, None, height // 20)

        # Title text
        title_color = COLORS.get('text', (220, 220, 255)) # Use .get with fallback
        draw_text(panel_surface, title, font, title_color, width // 2, title_height // 2, centered=True)

        # Divider line
        for x_pos in range(0, width, PIXEL_SCALE):
            pygame.draw.rect(panel_surface, bg_color,
                           (x_pos, title_height, PIXEL_SCALE, PIXEL_SCALE))

    # Draw tech corner accents
    corner_size = min(15, height // 8)
    corners = [
        (0, 0),  # Top left
        (width - corner_size, 0),  # Top right
        (0, height - corner_size),  # Bottom left
        (width - corner_size, height - corner_size)  # Bottom right
    ]

    for cx, cy in corners:
        # Draw diagonal corner accent
        accent_color = COLORS.get('neon', (255, 221, 0)) # Use .get with fallback
        for i in range(0, corner_size, PIXEL_SCALE):
            # Create stepping pattern
            pygame.draw.rect(panel_surface, accent_color,
                           (cx + i, cy, PIXEL_SCALE, PIXEL_SCALE))
            pygame.draw.rect(panel_surface, accent_color,
                           (cx, cy + i, PIXEL_SCALE, PIXEL_SCALE))

    # Blit panel to main surface
    surface.blit(panel_surface, (x, y))

def update_pet_vitals(pet_data):
    """
    Update Slith's vitals based on time elapsed since last check

    Args:
        pet_data (dict): Slith pet data dictionary

    Returns:
        dict: Updated pet data
    """
    # If there's no last_check, set it to now
    if 'last_check' not in pet_data:
        pet_data['last_check'] = datetime.now().isoformat()
        return pet_data

    # Parse last_check timestamp
    try:
        last_check = datetime.fromisoformat(pet_data['last_check'])
    except (ValueError, TypeError):
        # If timestamp is invalid, reset to now
        logger.warning(f"Invalid last_check timestamp '{pet_data.get('last_check')}' for user. Resetting.")
        pet_data['last_check'] = datetime.now().isoformat()
        return pet_data

    # Calculate hours elapsed
    now = datetime.now()
    hours_elapsed = (now - last_check).total_seconds() / 3600

    # Don't update if less than 5 minutes has passed (or adjust threshold)
    min_update_interval_hours = 5 / 60
    if hours_elapsed < min_update_interval_hours:
        return pet_data

    # Get decay rates
    decay_rates = VITALS.get('decay_rates', {}) # Use .get with fallback

    # Ensure 'vitals' key exists
    if 'vitals' not in pet_data:
         pet_data['vitals'] = {'food': 100, 'water': 100, 'entertainment': 100, 'love': 100, 'patience': 100}

    # Update vitals
    for vital, rate in decay_rates.items():
        if vital in pet_data['vitals']:
            # Calculate decay amount
            decay = min(rate * hours_elapsed, pet_data['vitals'][vital])
            # Update vital value
            pet_data['vitals'][vital] = max(0, pet_data['vitals'][vital] - decay)
            # Log the change for debugging
            # logger.debug(f"Vital '{vital}' decayed by {decay:.2f} over {hours_elapsed:.2f} hours. New value: {pet_data['vitals'][vital]:.2f}")

    # Update last check time
    pet_data['last_check'] = now.isoformat()

    return pet_data

def determine_slith_stage(completed_quests, snake_intro_seen, total_beginner=None):
    """
    Determine Slith's growth stage based on quest progress

    Args:
        completed_quests (list): List of completed quest IDs
        snake_intro_seen (bool): Whether the snake intro has been seen
        total_beginner (int, optional): Number of beginner quests. If not
            provided, attempts to import from ``slith_constants``. Defaults
            to ``20`` if unavailable.

    Returns:
        int: Slith stage (0-10)
    """

    if total_beginner is None:
        try:
            from slith_constants import TOTAL_BEGINNER as tb
            total_beginner = tb
        except Exception:
            total_beginner = 20

    snake_quests_completed = sum(1 for qid in completed_quests if qid >= total_beginner)

    # Stage progression based on snake quests
    if snake_quests_completed >= 10:  # Snake Echo 10
        return 10  # Neural implant Slith
    elif snake_quests_completed >= 9:  # Snake Echo 9
        return 9   # Holographic display
    elif snake_quests_completed >= 8:  # Snake Echo 8
        return 8   # Gaming PC
    elif snake_quests_completed >= 7:  # Snake Echo 7
        return 7   # Average PC
    elif snake_quests_completed >= 6:  # Snake Echo 6
        return 6   # CRT monitor
    elif snake_quests_completed >= 5:  # Snake Echo 5
        return 5   # Adult Slith
    elif snake_quests_completed >= 4:  # Snake Echo 4
        return 4   # Teen Slith
    elif snake_quests_completed >= 3:  # Snake Echo 3
        return 3   # Kid Slith
    elif snake_quests_completed >= 1:  # Snake Echo 1 & 2 lead to Baby Slith
        return 2   # Baby Slith (no eggshell)
    elif snake_intro_seen:
        return 1   # Hatching with partial eggshell
    else:
        return 0   # Egg

# --- Background Drawing Functions (Keep if used, ensure constants are available) ---

def draw_cyberpunk_background(surface):
    """
    Draw a cyberpunk-styled background with perspective grid and effects

    Args:
        surface (pygame.Surface): Surface to draw on
    """
    # Fill with base background color
    surface.fill(COLORS.get('bg', (20, 12, 28))) # Use .get with fallback

    # Draw perspective grid if enabled
    if GRID.get('show_grid', False): # Use .get with fallback
        draw_perspective_grid(surface)

    # Draw digital rain (Matrix effect) if enabled
    if DIGITAL_RAIN.get('enabled', False): # Use .get with fallback
        draw_digital_rain(surface)

    # Draw particle effects if enabled
    if PARTICLES.get('enabled', False): # Use .get with fallback
        draw_particles(surface)

    # Apply CRT effect if enabled
    if CRT_EFFECT.get('enabled', False): # Use .get with fallback
        apply_crt_effect(surface)

def draw_perspective_grid(surface):
    """
    Draw a perspective grid like in classic cyberpunk/outrun visuals

    Args:
        surface (pygame.Surface): Surface to draw on
    """
    try:
        width, height = surface.get_size()
        horizon_y = GRID.get('horizon_y', height * 0.6)
        cell_size = GRID.get('cell_size', 40)
        perspective = GRID.get('perspective_factor', 0.8)
        vanishing_x = width // 2
        max_lines = GRID.get('max_lines', 20)
        line_thickness = GRID.get('line_thickness', 1)
        line_fade_start = GRID.get('line_fade_start', 0.6)
        grid_color = GRID.get('color', (40, 40, 60))

        # Draw horizontal grid lines
        for i in range(max_lines):
            y = horizon_y + i * cell_size
            if y >= height: continue
            distance_factor = i / max_lines
            thickness = max(1, int(line_thickness * (1 - distance_factor * 0.5)))
            alpha = 255
            if distance_factor > line_fade_start:
                alpha_factor = max(0, (1 - distance_factor) / (1 - line_fade_start)) # Ensure non-negative
                alpha = int(255 * alpha_factor)
            line_color_alpha = list(grid_color) + [alpha]
            for x in range(0, width, PIXEL_SCALE):
                for t in range(thickness):
                    pixel_surface = pygame.Surface((PIXEL_SCALE, PIXEL_SCALE), pygame.SRCALPHA)
                    pixel_surface.fill(line_color_alpha)
                    surface.blit(pixel_surface, (x, y + t))

        # Draw vertical grid lines
        grid_width_calc = max_lines * cell_size
        for i in range(-max_lines // 2, max_lines // 2 + 1):
            perspective_x = vanishing_x + i * cell_size
            distance_factor = abs(i) / (max_lines // 2) if max_lines > 0 else 0
            spread_factor = 1 + distance_factor * perspective * 5
            start_x = perspective_x; start_y = horizon_y
            end_x = vanishing_x + i * cell_size * spread_factor; end_y = height
            alpha = 255
            if distance_factor > line_fade_start:
                 alpha_factor = max(0, (1 - distance_factor) / (1 - line_fade_start)) # Ensure non-negative
                 alpha = int(255 * alpha_factor)
            line_color_alpha = list(grid_color) + [alpha]

            # Simplified line drawing for utils (Bresenham might be overkill here)
            pygame.draw.aaline(surface, line_color_alpha[:3], (start_x, start_y), (end_x, end_y)) # Use aaline for basic anti-aliasing

    except Exception as e:
        logger.error(f"Error drawing perspective grid: {e}", exc_info=True)


def draw_digital_rain(surface):
    """
    Draw Matrix-style digital rain effect

    Args:
        surface (pygame.Surface): Surface to draw on
    """
    try:
        width, height = surface.get_size()
        char_size = DIGITAL_RAIN.get('char_size', 14)
        columns = DIGITAL_RAIN.get('columns', width // 20)
        spawn_rate = DIGITAL_RAIN.get('spawn_rate', 0.02)
        length_range = DIGITAL_RAIN.get('length_range', (5, 15))
        speed_range = DIGITAL_RAIN.get('speed_range', (1, 4))
        opacity_range = DIGITAL_RAIN.get('opacity_range', (40, 180))
        fade_factor = DIGITAL_RAIN.get('fade_factor', 0.9)
        rain_color = DIGITAL_RAIN.get('color', (0, 255, 0)) # Hacker text color

        if not hasattr(draw_digital_rain, "streams"):
            draw_digital_rain.streams = []
            draw_digital_rain.chars = [chr(i) for i in range(33, 127)] # Printable ASCII
            draw_digital_rain.font = pygame.font.SysFont('monospace', char_size)

        if random.random() < spawn_rate:
            column = random.randint(0, columns - 1)
            x = column * (char_size + 5)
            y = random.randint(-100, int(height * 0.3))
            length = random.randint(*length_range)
            speed = random.uniform(*speed_range)
            opacity = random.randint(*opacity_range)
            chars = [random.choice(draw_digital_rain.chars) for _ in range(length)]
            draw_digital_rain.streams.append({'x': x, 'y': y, 'chars': chars, 'speed': speed, 'opacity': opacity})

        remaining_streams = []
        for stream in draw_digital_rain.streams:
            stream['y'] += stream['speed']
            if stream['y'] - len(stream['chars']) * char_size < height:
                for i, char in enumerate(stream['chars']):
                    char_y = stream['y'] - i * char_size
                    if char_y < 0 or char_y > height: continue
                    char_opacity = int(stream['opacity'] * (fade_factor ** i))
                    if char_opacity < 20: continue
                    char_color_alpha = list(rain_color) + [char_opacity]
                    try:
                        char_surface = draw_digital_rain.font.render(char, True, char_color_alpha[:3])
                        # Apply alpha using a separate surface blend if needed, or directly if supported
                        # pygame.Surface allows setting alpha per pixel, but fill is easier
                        alpha_surface = pygame.Surface(char_surface.get_size(), pygame.SRCALPHA)
                        alpha_surface.fill((255, 255, 255, char_opacity))
                        char_surface.blit(alpha_surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                        surface.blit(char_surface, (stream['x'], char_y))
                    except Exception as render_err:
                        # Log font rendering errors, might happen if font is missing
                        logger.debug(f"Error rendering digital rain character: {render_err}")
                        pass # Skip character if render fails
                remaining_streams.append(stream)
        draw_digital_rain.streams = remaining_streams
    except Exception as e:
        logger.error(f"Error drawing digital rain: {e}", exc_info=True)

def draw_particles(surface):
    """
    Draw floating cyberpunk particle effects

    Args:
        surface (pygame.Surface): Surface to draw on
    """
    try:
        width, height = surface.get_size()
        count = PARTICLES.get('count', 40)
        size_range = PARTICLES.get('size_range', (1, 3))
        speed_range_cfg = PARTICLES.get('speed_range', (0.5, 2.0))
        p_colors = PARTICLES.get('colors', [(255,221,0), (255,105,180), (0,200,80)])
        opacity_range = PARTICLES.get('opacity_range', (50, 150))
        dir_change_chance = PARTICLES.get('direction_change_chance', 0.01)


        if not hasattr(draw_particles, "particles"):
            draw_particles.particles = []
            for _ in range(count):
                particle = {
                    'x': random.uniform(0, width), 'y': random.uniform(0, height),
                    'size': random.randint(*size_range),
                    'speed_x': random.uniform(-speed_range_cfg[1], speed_range_cfg[1]),
                    'speed_y': random.uniform(-speed_range_cfg[1], speed_range_cfg[1]),
                    'color': random.choice(p_colors),
                    'opacity': random.randint(*opacity_range)
                }
                draw_particles.particles.append(particle)

        for particle in draw_particles.particles:
            particle['x'] += particle['speed_x']; particle['y'] += particle['speed_y']
            if particle['x'] < 0: particle['x'] = width
            elif particle['x'] > width: particle['x'] = 0
            if particle['y'] < 0: particle['y'] = height
            elif particle['y'] > height: particle['y'] = 0
            if random.random() < dir_change_chance:
                particle['speed_x'] = random.uniform(-speed_range_cfg[1], speed_range_cfg[1])
                particle['speed_y'] = random.uniform(-speed_range_cfg[1], speed_range_cfg[1])

            particle_color_alpha = list(particle['color']) + [particle['opacity']]
            particle_size_px = particle['size'] * PIXEL_SCALE
            particle_surface = pygame.Surface((particle_size_px, particle_size_px), pygame.SRCALPHA)
            particle_surface.fill(particle_color_alpha)
            surface.blit(particle_surface, (int(particle['x']), int(particle['y'])))
    except Exception as e:
        logger.error(f"Error drawing particles: {e}", exc_info=True)


def apply_crt_effect(surface):
    """
    Apply CRT screen effect (scanlines, noise, etc.)

    Args:
        surface (pygame.Surface): Surface to modify with CRT effect
    """
    try:
        width, height = surface.get_size()
        flicker_chance = CRT_EFFECT.get('flicker_chance', 0.001)
        flicker_duration = CRT_EFFECT.get('flicker_duration', 2)
        scanline_opacity = CRT_EFFECT.get('scanline_opacity', 0.1)
        scanline_spacing = CRT_EFFECT.get('scanline_spacing', 4)
        noise_opacity = CRT_EFFECT.get('noise_opacity', 0.03)
        edge_shadow = CRT_EFFECT.get('edge_shadow', 0.3)

        if random.random() < flicker_chance:
            if not hasattr(apply_crt_effect, "flicker_timer"): apply_crt_effect.flicker_timer = 0
            apply_crt_effect.flicker_timer = flicker_duration

        if hasattr(apply_crt_effect, "flicker_timer") and apply_crt_effect.flicker_timer > 0:
            flicker = pygame.Surface((width, height), pygame.SRCALPHA)
            flicker_alpha = random.randint(10, 40)
            flicker.fill((255, 255, 255, flicker_alpha))
            surface.blit(flicker, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            apply_crt_effect.flicker_timer -= 1

        spacing_px = scanline_spacing * PIXEL_SCALE
        scanline_alpha_val = int(255 * scanline_opacity)
        scanline_color = (0, 0, 0, scanline_alpha_val)
        for y in range(0, height, spacing_px):
            scanline = pygame.Surface((width, PIXEL_SCALE), pygame.SRCALPHA)
            scanline.fill(scanline_color)
            surface.blit(scanline, (0, y))

        if noise_opacity > 0:
            noise_count = int(width * height * 0.01 * noise_opacity)
            noise_alpha_val = int(100 * noise_opacity)
            for _ in range(noise_count):
                noise_x = random.randint(0, width - PIXEL_SCALE)
                noise_y = random.randint(0, height - PIXEL_SCALE)
                noise_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), noise_alpha_val)
                noise_pixel = pygame.Surface((PIXEL_SCALE, PIXEL_SCALE), pygame.SRCALPHA)
                noise_pixel.fill(noise_color)
                surface.blit(noise_pixel, (noise_x, noise_y), special_flags=pygame.BLEND_RGBA_ADD)

        if edge_shadow > 0:
            vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            center_x, center_y = width // 2, height // 2
            max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
            if max_dist == 0: max_dist = 1 # Avoid division by zero
            for x in range(0, width, PIXEL_SCALE * 2):
                for y in range(0, height, PIXEL_SCALE * 2):
                    dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    dist_factor = dist / max_dist
                    darkness = int(255 * edge_shadow * dist_factor ** 2)
                    if darkness > 0:
                        shadow_pixel = pygame.Surface((PIXEL_SCALE * 2, PIXEL_SCALE * 2), pygame.SRCALPHA)
                        shadow_pixel.fill((0, 0, 0, min(255, darkness))) # Clamp alpha
                        vignette_surface.blit(shadow_pixel, (x, y))
            surface.blit(vignette_surface, (0, 0))
    except Exception as e:
        logger.error(f"Error applying CRT effect: {e}", exc_info=True)

# --- End of slith_utils.py ---
