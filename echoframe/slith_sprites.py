# slith_sprites_combined_reworked.py
# Combined SlithSprite and CareItem classes
# Reworked SlithSprite: S-Shape, Stage Variations
# FIXED: Positioning and Draw Order for Stage 6+ accessories (CRT, RGB, Implants)
# FIXED: LoveItem icon shape to look more like a heart.
# FIXED: Vertical centering for WaterItem and LoveItem icons.
# FIXED: Horizontal centering for FoodItem, WaterItem, and LoveItem icons.
# ADDED: Accessory drawing logic and integration.
# FIXED: Added missing update_accessories method.

import pygame
import math
import random
import inspect # Added for checking function signatures
import time # Added for potential accessory animations

# --- Constants Fallback ---
try:
    # Ensure PIXEL_SCALE is imported or defined
    from slith_constants import COLORS, STAGES, ANIMATION_STATES, PIXEL_SCALE, STORE_ITEMS # Added STORE_ITEMS for accessory info if needed later
except ImportError:
    print("Warning: slith_constants.py not found. Using placeholder values.")
    COLORS = {
        'neon': (255, 221, 0), 'accent': (255, 105, 180), 'warning': (255, 165, 0),
        'danger': (255, 50, 50), 'egg_shell': (210, 180, 140), 'bg_dark': (10, 8, 16),
        'bg': (20, 12, 28), 'text_dark': (120, 120, 160), 'food': (255, 100, 100),
        'water': (80, 160, 255), 'entertainment': (170, 100, 255), 'love': (255, 100, 255),
        'text': (220, 220, 255) # Added fallback text color
    }
    STAGES = { i: {'name': f'Stage {i}'} for i in range(11) }
    ANIMATION_STATES = ['idle', 'happy', 'sad', 'back_turned']
    PIXEL_SCALE = 2 # Added fallback pixel scale
    STORE_ITEMS = {} # Fallback store items

# --- Pixel Art Helper Functions ---

def draw_pixel_rect(surface, color, rect, pixel_size):
    """Draws a rectangle aligned to the pixel grid."""
    x, y, w, h = rect
    # Ensure non-negative dimensions before calculations
    x, y, w, h = max(0, x), max(0, y), max(0, w), max(0, h)
    # Align start coordinates to the grid
    x_start = (int(x) // pixel_size) * pixel_size
    y_start = (int(y) // pixel_size) * pixel_size
    # Calculate end coordinates, ensuring at least one pixel block width/height
    x_end = x_start + max(pixel_size, ((int(w) + pixel_size - 1) // pixel_size) * pixel_size)
    y_end = y_start + max(pixel_size, ((int(h) + pixel_size - 1) // pixel_size) * pixel_size)
    # Check for alpha channel
    has_alpha = isinstance(color, (list, tuple)) and len(color) == 4
    # Convert to int for range iteration
    x_start_int, x_end_int = int(x_start), int(x_end)
    y_start_int, y_end_int = int(y_start), int(y_end)
    pixel_size_int = int(pixel_size)

    # Iterate and draw pixel blocks
    for px_coord in range(x_start_int, x_end_int, pixel_size_int):
        for py_coord in range(y_start_int, y_end_int, pixel_size_int):
            if has_alpha: # Handle transparency correctly
                pixel_surface = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
                pixel_surface.fill(color)
                surface.blit(pixel_surface, (px_coord, py_coord))
            else: # Draw opaque rectangle
                pygame.draw.rect(surface, color, (px_coord, py_coord, pixel_size, pixel_size))


def draw_pixel_circle(surface, color, center, radius, pixel_size):
    """Draws a filled circle aligned to the pixel grid."""
    cx, cy = center
    radius_sq = radius * radius
    # Calculate bounding box aligned to grid
    x_start = int(cx - radius) // pixel_size * pixel_size
    y_start = int(cy - radius) // pixel_size * pixel_size
    x_end = int(cx + radius + pixel_size) // pixel_size * pixel_size
    y_end = int(cy + radius + pixel_size) // pixel_size * pixel_size
    pixel_size_int = int(pixel_size)

    # Iterate through grid cells in bounding box
    for x_coord in range(x_start, x_end, pixel_size_int):
        for y_coord in range(y_start, y_end, pixel_size_int):
            # Calculate center of the current pixel block
            px_center_x = x_coord + pixel_size / 2
            px_center_y = y_coord + pixel_size / 2
            # Check if pixel center is within the circle radius
            if (px_center_x - cx) ** 2 + (px_center_y - cy) ** 2 <= radius_sq:
                # Draw the pixel block if it's inside the circle
                draw_pixel_rect(surface, color, (x_coord, y_coord, pixel_size, pixel_size), pixel_size)

def draw_pixel_oval(surface, color, rect, pixel_size):
    """Draws a filled oval aligned to the pixel grid."""
    x_rect, y_rect, w, h = rect
    if w <= 0 or h <= 0: return # Cannot draw oval with zero or negative dimensions
    # Calculate radii and center
    rx, ry = w / 2, h / 2
    cx, cy = x_rect + rx, y_rect + ry
    # Calculate bounding box aligned to grid
    x_start = int(x_rect) // pixel_size * pixel_size
    y_start = int(y_rect) // pixel_size * pixel_size
    x_end = int(x_rect + w + pixel_size) // pixel_size * pixel_size
    y_end = int(y_rect + h + pixel_size) // pixel_size * pixel_size
    pixel_size_int = int(pixel_size)

    # Iterate through grid cells in bounding box
    for x_coord in range(x_start, x_end, pixel_size_int):
        for y_coord in range(y_start, y_end, pixel_size_int):
            # Calculate center of the current pixel block
            px_center_x = x_coord + pixel_size / 2
            px_center_y = y_coord + pixel_size / 2
            # Check if pixel center is within the oval equation
            try:
                if ((px_center_x - cx) / rx) ** 2 + ((px_center_y - cy) / ry) ** 2 <= 1:
                    # Draw the pixel block if it's inside the oval
                    draw_pixel_rect(surface, color, (x_coord, y_coord, pixel_size, pixel_size), pixel_size)
            except ZeroDivisionError:
                # Avoid division by zero if radius is zero (shouldn't happen with check above)
                continue

def draw_pixel_line(surface, color, start_pos, end_pos, pixel_size):
    """Draws a line using pixel blocks (simple Bresenham-like implementation)."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    # Align start and end points to the pixel grid
    x_coord, y_coord = (int(x1) // pixel_size * pixel_size), (int(y1) // pixel_size * pixel_size)
    x2_aligned, y2_aligned = (int(x2) // pixel_size * pixel_size), (int(y2) // pixel_size * pixel_size)

    # Calculate differences and step directions
    dx = abs(x2_aligned - x_coord)
    dy = abs(y2_aligned - y_coord)
    sx = pixel_size if x_coord < x2_aligned else -pixel_size
    sy = pixel_size if y_coord < y2_aligned else -pixel_size
    err = dx - dy # Error term

    safety_count = 0
    # Estimate max pixels needed to prevent infinite loops in edge cases
    max_pixels = (dx + dy) // pixel_size + 2

    # Loop until the end point is reached or safety limit exceeded
    while safety_count < max_pixels * 2:
        # Draw the current pixel block
        draw_pixel_rect(surface, color, (x_coord, y_coord, pixel_size, pixel_size), pixel_size)
        # Check if the end point is reached
        if x_coord == x2_aligned and y_coord == y2_aligned: break

        e2 = 2 * err # Calculate error term * 2
        # Adjust error and move horizontally if needed
        if e2 >= -dy:
            if x_coord == x2_aligned: break # Avoid overshooting horizontally
            err -= dy
            x_coord += sx
        # Adjust error and move vertically if needed
        if e2 <= dx:
             if y_coord == y2_aligned: break # Avoid overshooting vertically
             err += dx
             y_coord += sy
        safety_count += 1

    # Log a warning if the safety limit was reached (indicates a potential issue)
    if safety_count >= max_pixels * 2:
        print(f"Warning: draw_pixel_line exceeded safety limit from {start_pos} to {end_pos}")


# ---------------------------------------------------
# SlithSprite Class
# ---------------------------------------------------
class SlithSprite:
    """Slith character sprite - Reworked shape and stage variations."""
    def __init__(self, stage):
        self.stage = stage
        self.state = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0
        self.x = 300 # Default X position
        self.y = 350 # Default Y position
        self.pixel_size = PIXEL_SCALE # Use constant

        # Animation state variables
        self.idle_state = 'normal' # 'normal' or 'blink'
        self.idle_timer = 0
        self.special_timer = 0 # For other potential idle actions
        self.blink_duration = 8 # Frames for blink
        self.bounce_offset = 0 # Vertical bounce for idle/happy
        self.bounce_direction = 1
        self.rotation = 0 # For potential future effects
        self.scale = 1.0 # For potential future effects
        self.wave_offset = 0 # Horizontal body wave offset
        self.wave_speed = 0.1 # Speed of the body wave

        # Store calculated head position during drawing for accessories
        self.last_head_pos = (self.x, self.y - 50) # Initial estimate
        self.last_head_size = 50 # Initial estimate
        self.last_neck_pos = (self.x, self.y - 20) # Initial estimate

        # Store equipped accessories
        self.accessories = {} # Initialize accessories dictionary

        # Set initial rect (will be updated in draw)
        self.rect = pygame.Rect(self.x - 25, self.y - 25, 50, 50) # Placeholder size


    # --- ADDED: Method to update accessories ---
    def update_accessories(self, equipped_items):
        """Update the equipped accessories for Slith."""
        self.accessories = equipped_items if isinstance(equipped_items, dict) else {}
        # No need to reload sprites as drawing is dynamic


    # --- Accessory Drawing Methods (Integrated) ---

    def draw_hat(self, surface, head_pos, head_size, item_id):
        """Draws a hat accessory on Slith's head."""
        x, y = head_pos # Center of the head
        pixel_size = self.pixel_size

        if item_id == 'top_hat':
            hat_color = (10, 10, 10) # Very dark grey/black
            brim_height = pixel_size * 1
            crown_height = pixel_size * 4
            crown_width = head_size * 0.6
            brim_width = head_size * 0.9

            # Position relative to head center (adjust Y to sit ON TOP)
            hat_base_y = y - head_size * 0.5 # Top of head oval
            brim_y = hat_base_y - brim_height
            crown_y = brim_y - crown_height
            brim_x = x - brim_width / 2
            crown_x = x - crown_width / 2

            # Draw brim first
            draw_pixel_rect(surface, hat_color, (brim_x, brim_y, brim_width, brim_height), pixel_size)
            # Draw crown on top of brim
            draw_pixel_rect(surface, hat_color, (crown_x, crown_y, crown_width, crown_height), pixel_size)

        elif item_id == 'crown':
            crown_color = (255, 215, 0) # Gold
            jewel_color = (255, 0, 0) # Red
            base_height = pixel_size * 1.5
            point_height = pixel_size * 2
            base_width = head_size * 0.7
            num_points = 3

            # Position relative to head center (adjust Y to sit ON TOP)
            base_y = y - head_size * 0.45 - base_height # Position base slightly above head top
            base_x = x - base_width / 2
            points_base_y = base_y - point_height # Points start above the base

            # Draw base band
            draw_pixel_rect(surface, crown_color, (base_x, base_y, base_width, base_height), pixel_size)

            # Draw points
            point_width = base_width / num_points
            for i in range(num_points):
                point_center_x = base_x + i * point_width + (point_width / 2) # Center X of the point base
                # Draw triangle shape for point
                top_x = point_center_x
                top_y = points_base_y
                bottom_left_x = point_center_x - pixel_size * 1.5
                bottom_right_x = point_center_x + pixel_size * 1.5
                bottom_y = base_y # Points connect to the top of the base band

                # Use lines for pixel control
                draw_pixel_line(surface, crown_color, (top_x, top_y), (bottom_left_x, bottom_y), pixel_size)
                draw_pixel_line(surface, crown_color, (top_x, top_y), (bottom_right_x, bottom_y), pixel_size)
                draw_pixel_line(surface, crown_color, (bottom_left_x, bottom_y), (bottom_right_x, bottom_y), pixel_size) # Base of triangle

                # Add jewel (optional) at the top center of the middle point
                if i == 1: # Center point
                     jewel_x = top_x - pixel_size / 2
                     jewel_y = top_y # Place jewel at the very top point
                     draw_pixel_rect(surface, jewel_color, (jewel_x, jewel_y, pixel_size, pixel_size), pixel_size)


        elif item_id == 'farmer_hat':
            hat_color = (210, 180, 140) # Tan/Straw
            band_color = (188, 143, 143) # Rosy Brown for band
            crown_height = pixel_size * 3
            crown_width = head_size * 0.5
            brim_width = head_size * 1.1 # Wide brim
            brim_height = pixel_size * 1.5

            # Position relative to head center (adjust Y to sit ON TOP)
            hat_base_y = y - head_size * 0.5 # Top of head oval
            brim_y = hat_base_y - brim_height
            crown_y = brim_y - crown_height
            brim_x = x - brim_width / 2
            crown_x = x - crown_width / 2

            # Draw brim (draw first so crown overlaps)
            draw_pixel_rect(surface, hat_color, (brim_x, brim_y, brim_width, brim_height), pixel_size)
            # Draw crown (simple rectangle)
            draw_pixel_rect(surface, hat_color, (crown_x, crown_y, crown_width, crown_height), pixel_size)
            # Add a darker band around the base of the crown
            band_y = brim_y - pixel_size # Position the band just above the brim
            draw_pixel_rect(surface, band_color, (crown_x, band_y, crown_width, pixel_size), pixel_size)

        elif item_id == 'bandana': # Handle bandana as a head item too (tied around head)
             bandana_color = (0, 0, 0) # Black for head bandana
             pattern_color = (0, 255, 0) # Green binary pattern
             width = head_size * 0.9
             height = head_size * 0.25

             # Position on forehead
             bandana_x = x - width / 2
             bandana_y = y - head_size * 0.4 # Adjust Y position for forehead

             # Draw main band
             draw_pixel_rect(surface, bandana_color, (bandana_x, bandana_y, width, height), pixel_size)
             # Draw binary pattern (simple alternating 0/1)
             num_bits = int(width / (pixel_size * 2))
             for i in range(num_bits):
                 bit_char = "1" if i % 2 == 0 else "0"
                 bit_x = bandana_x + i * pixel_size * 2 + pixel_size
                 bit_y = bandana_y + height / 2
                 # Render bit character (requires font) - or draw simple pattern
                 # For simplicity, draw alternating blocks
                 if i % 2 == 0:
                      draw_pixel_rect(surface, pattern_color, (bit_x, bandana_y + pixel_size, pixel_size, pixel_size), pixel_size)


    def draw_glasses(self, surface, head_pos, head_size, item_id):
        """Draws glasses accessory (neon glasses on forehead)."""
        x, y = head_pos # Center of the head
        pixel_size = self.pixel_size

        if item_id == 'neon_glasses':
            # Draw ON FOREHEAD, above the regular sunglasses Slith wears
            glasses_color = (0, 255, 255) # Cyan Neon
            frame_color = (50, 50, 50) # Dark frame
            width = head_size * 0.8
            height = head_size * 0.2
            frame_thickness = pixel_size

            # Position higher up on the head, above the default sunglasses
            glasses_y = y - head_size * 0.4 # Adjust Y position to be clearly on the forehead
            glasses_x = x - width / 2

            # Draw frame first
            draw_pixel_rect(surface, frame_color, (glasses_x, glasses_y, width, height), pixel_size)
            # Draw lenses inside frame
            lens_x = glasses_x + frame_thickness
            lens_y = glasses_y + frame_thickness
            lens_width = width - 2 * frame_thickness
            lens_height = height - 2 * frame_thickness
            # Ensure lens dimensions are positive before drawing
            if lens_width > 0 and lens_height > 0:
                 draw_pixel_rect(surface, glasses_color, (lens_x, lens_y, lens_width, lens_height), pixel_size)


    def draw_neck_accessory(self, surface, neck_pos, head_size, item_id):
         """Draws an accessory around Slith's neck area."""
         x, y = neck_pos # Position where neck meets body (approx)
         pixel_size = self.pixel_size

         if item_id == 'bow_tie':
             bowtie_color = (200, 0, 0) # Red
             width = head_size * 0.6 # Slightly smaller
             height = head_size * 0.3
             # Position slightly below head center, adjust based on snake shape
             bowtie_x = x - width / 2
             bowtie_y = y + head_size * 0.05 # Adjust Y pos closer to neck point

             # Draw main bow parts (triangles or simplified rects)
             # Left wing
             draw_pixel_rect(surface, bowtie_color, (bowtie_x, bowtie_y, width / 2 - pixel_size, height), pixel_size)
             # Right wing
             draw_pixel_rect(surface, bowtie_color, (x + pixel_size, bowtie_y, width / 2 - pixel_size, height), pixel_size)
             # Center knot
             knot_width = pixel_size * 2
             knot_height = height * 1.2
             draw_pixel_rect(surface, bowtie_color, (x - knot_width / 2, bowtie_y - (knot_height - height)/2 , knot_width, knot_height), pixel_size)

         elif item_id == 'scarf':
             scarf_color = (0, 150, 255) # Blue
             pattern_color = (0, 255, 255) # Cyan pattern
             width = head_size * 0.8 # Width around neck
             height = head_size * 0.25 # Thickness
             tail_length = head_size * 0.5
             tail_width = width * 0.3

             # Position around neck point
             scarf_x = x - width / 2
             scarf_y = y + head_size * 0.05 # Adjust Y

             # Draw main band
             draw_pixel_rect(surface, scarf_color, (scarf_x, scarf_y, width, height), pixel_size)
             # Draw simple circuit pattern
             for i in range(int(width / (pixel_size * 4))):
                  pat_x = scarf_x + i * pixel_size * 4 + pixel_size
                  draw_pixel_rect(surface, pattern_color, (pat_x, scarf_y + pixel_size, pixel_size * 2, pixel_size), pixel_size)

             # Draw hanging tail
             tail_x = x - tail_width / 2 # Center the tail horizontally
             tail_y = scarf_y + height
             draw_pixel_rect(surface, scarf_color, (tail_x, tail_y, tail_width, tail_length), pixel_size)


    def draw_back_accessory(self, surface, body_center_pos, head_size, item_id):
         """Draws an accessory on Slith's back (placeholder)."""
         # Example: Cape (can be adapted)
         x, y = body_center_pos # Use body center passed from S-shape draw
         pixel_size = self.pixel_size

         if item_id == 'cape':
             cape_width = int(head_size * 1.2) # Adjust size relative to head/body
             cape_length = int(head_size * 2.0)
             cape_x = x - cape_width // 2
             cape_y = y - head_size // 3 # Position behind upper body/neck area

             cape_color = (50, 0, 100) # Dark purple
             edge_color = (150, 0, 200) # Lighter purple edge

             # Draw main cape rectangle
             draw_pixel_rect(surface, cape_color, (cape_x, cape_y, cape_width, cape_length), pixel_size)
             # Draw bottom edge detail
             for i in range(int(cape_width / (pixel_size * 2))):
                 edge_x = cape_x + i * pixel_size * 2
                 draw_pixel_rect(surface, edge_color, (edge_x, cape_y + cape_length - pixel_size, pixel_size*2, pixel_size), pixel_size)


    # --- Stage-Specific Drawing ---
    def draw_egg_sprite(self, surface, color, size, pixel_size, frame_index):
        """Draws the pixelated egg sprite (base version for load_sprites)"""
        # Calculate egg dimensions relative to surface size
        egg_rect = pygame.Rect(size * 0.1, size * 0.05, size * 0.8, size * 0.9)
        # Draw the main egg oval shape
        draw_pixel_oval(surface, color, egg_rect, pixel_size)
        # Add some random "data circuit" blinks on the surface (only for base drawing)
        for _ in range(3):
            px_coord = random.randint(int(size*0.3), int(size*0.7))
            py_coord = random.randint(int(size*0.3), int(size*0.7))
            blink_color = random.choice([COLORS.get('accent'), COLORS.get('neon'), (200,200,255)])
            draw_pixel_rect(surface, blink_color, (px_coord, py_coord, pixel_size, pixel_size), pixel_size)

    def draw_hatching_sprite(self, surface, color, size, pixel_size, frame_index, state):
        """Draws the pixelated hatching sprite (base version for load_sprites)"""
        shell_color = COLORS.get('egg_shell', (200, 200, 200)) # Color for the egg shell part
        # Calculate shell position and size (bottom part of the surface)
        shell_height = size * 0.4
        shell_y = size - shell_height
        shell_rect = pygame.Rect(size * 0.1, shell_y, size * 0.8, shell_height)
        # Draw the bottom shell part
        draw_pixel_oval(surface, shell_color, shell_rect, pixel_size)
        # Add jagged crack effect to the top edge of the shell
        for x_coord in range(int(size * 0.1), int(size * 0.9), pixel_size * 2):
             jag_height = random.choice([0, pixel_size, pixel_size*2]) # Random height for crack segment
             if jag_height > 0:
                 draw_pixel_rect(surface, shell_color, (x_coord, shell_y - jag_height, pixel_size, jag_height), pixel_size)
        # Draw the emerging snake body (top part)
        body_height = size * 0.6
        body_width = size * 0.6
        body_x = (size - body_width) / 2
        body_y = size * 0.05
        body_rect = pygame.Rect(body_x, body_y, body_width, body_height)
        draw_pixel_oval(surface, color, body_rect, pixel_size) # Use the main snake color
        # Draw the face on the emerging body if not turned back
        if state != 'back_turned':
            # Calculate approximate head center for face drawing
            head_center_x = body_x + body_width / 2
            head_center_y = body_y + body_height / 2 - size * 0.1 # Adjust Y pos upwards slightly
            self.draw_slith_face(surface, size, pixel_size, frame_index, state, is_hatching=True, face_center=(int(head_center_x), int(head_center_y)))

    # --- S-Shape Snake Drawing Method ---
    def draw_s_shape_snake(self, surface, color, size, pixel_size, frame_index, state, wave_offset=0, accessories=None):
        """Draws an S-shaped snake body for stages 2+ with dynamic wave animation offset and accessories"""
        if accessories is None: accessories = {} # Default to empty dict

        center_x = size // 2
        center_y = size // 2
        body_thickness = size * 0.15 + (self.stage - 2) * pixel_size
        body_thickness = max(pixel_size * 3, body_thickness)
        curve_height = size * 0.3
        curve_width = size * 0.25
        # Define key points for the S-curve spline
        p1 = (center_x + curve_width, center_y - curve_height) # Approx Head position
        p2 = (center_x, center_y)                             # Midpoint 1
        p3 = (center_x - curve_width, center_y + curve_height) # Midpoint 2
        p4 = (center_x, center_y + curve_height * 1.8)        # Approx Tail position
        num_steps = 15
        shade_color = tuple(max(0, c-40) for c in color[:3])

        # --- Draw Back Accessories FIRST ---
        back_item = accessories.get('back')
        if back_item:
            # Position relative to body center or head (adjust as needed)
            back_pos = (center_x, center_y + pixel_size * 4) # Example position
            self.draw_back_accessory(surface, back_pos, body_thickness * 1.4, back_item) # Pass approx head size


        # --- Draw Tech Details (Behind Snake Body) ---
        tech_base_y = center_y + pixel_size * 6
        if self.stage >= 6: self.draw_computer_sprite(surface, size, pixel_size, frame_index, tech_base_y)
        if self.stage >= 8: self.draw_rgb_lights(surface, size, pixel_size, frame_index, tech_base_y)

        # --- Draw Snake Body Segments ---
        head_x, head_y = p1[0], p1[1] # Initialize head position guess
        neck_x, neck_y = p1[0], p1[1] # Initialize neck position guess (start near head)
        segment_positions = [] # Store segment centers for neck calculation

        for i in range(num_steps):
            t = i / (num_steps - 1)
            x_coord, y_coord = 0, 0

            # Interpolate position along the S-curve
            if t <= 0.33: # Segment 1: p1 to p2
                t_local = t / 0.33; x_coord = p1[0] + (p2[0] - p1[0]) * t_local; y_coord = p1[1] + (p2[1] - p1[1]) * t_local
            elif t <= 0.66: # Segment 2: p2 to p3
                t_local = (t - 0.33) / 0.33; x_coord = p2[0] + (p3[0] - p2[0]) * t_local; y_coord = p2[1] + (p3[1] - p2[1]) * t_local
            else: # Segment 3: p3 to p4
                t_local = (t - 0.66) / 0.34; x_coord = p3[0] + (p4[0] - p3[0]) * t_local; y_coord = p3[1] + (p4[1] - p3[1]) * t_local

            segment_wave_offset = body_thickness * 0.3 * math.sin((y_coord / size) * 4 * math.pi + wave_offset)
            x_coord += segment_wave_offset
            segment_positions.append((x_coord, y_coord)) # Store center

            # Taper body thickness
            thickness_factor = 1.0 - 0.6 * abs(t - 0.5) / 0.5
            current_thickness = body_thickness * thickness_factor
            current_radius = max(pixel_size, current_thickness / 2)

            # Draw body segment
            draw_pixel_circle(surface, color, (int(x_coord), int(y_coord)), int(current_radius), pixel_size)
            shade_offset_x = pixel_size if t < 0.66 else -pixel_size
            draw_pixel_circle(surface, shade_color, (int(x_coord + shade_offset_x), int(y_coord+pixel_size)), int(current_radius * 0.6), pixel_size)

            # Update head position based on the first segment's calculation
            if i == 0: head_x, head_y = x_coord, y_coord
            # Estimate neck position (e.g., after first few segments)
            if i == 2: neck_x, neck_y = x_coord, y_coord


        # --- Draw Stage-Specific Patterns ---
        pattern_color = COLORS.get('accent', (255, 105, 180))
        # (Pattern drawing logic remains the same, using segment_positions if needed)
        if self.stage == 3: # Kid - Simple Dots
            for t_idx in [3, 8, 12]: # Use indices from segment_positions
                 if t_idx < len(segment_positions):
                      x_coord, y_coord = segment_positions[t_idx]
                      draw_pixel_rect(surface, pattern_color, (x_coord - pixel_size, y_coord - pixel_size, pixel_size*2, pixel_size*2), pixel_size)
        elif self.stage == 4: # Teen - Chevrons '>' pointing down
             for t_idx in [4, 9]:
                 if t_idx < len(segment_positions):
                     x_coord, y_coord = segment_positions[t_idx]
                     draw_pixel_rect(surface, pattern_color, (x_coord - pixel_size*2, y_coord, pixel_size*2, pixel_size), pixel_size) # Left arm
                     draw_pixel_rect(surface, pattern_color, (x_coord + pixel_size, y_coord, pixel_size*2, pixel_size), pixel_size) # Right arm
                     draw_pixel_rect(surface, pattern_color, (x_coord, y_coord + pixel_size, pixel_size, pixel_size), pixel_size) # Point
        elif self.stage == 5: # Adult - Diamonds
             for t_idx in [6, 11]:
                 if t_idx < len(segment_positions):
                     x_coord, y_coord = segment_positions[t_idx]
                     draw_pixel_rect(surface, pattern_color, (x_coord, y_coord - pixel_size, pixel_size, pixel_size), pixel_size) # Top
                     draw_pixel_rect(surface, pattern_color, (x_coord - pixel_size, y_coord, pixel_size, pixel_size), pixel_size) # Left
                     draw_pixel_rect(surface, pattern_color, (x_coord + pixel_size, y_coord, pixel_size, pixel_size), pixel_size) # Right
                     draw_pixel_rect(surface, pattern_color, (x_coord, y_coord + pixel_size, pixel_size, pixel_size), pixel_size) # Bottom


        # --- Draw Head ---
        head_size = body_thickness * 1.4
        head_rect = pygame.Rect(head_x - head_size/2, head_y - head_size/2, head_size, head_size)
        draw_pixel_oval(surface, color, head_rect, pixel_size)
        # Store calculated head position and size for accessories
        self.last_head_pos = (int(head_x), int(head_y))
        self.last_head_size = head_size
        self.last_neck_pos = (int(neck_x), int(neck_y)) # Store calculated neck position

        # --- Draw Face ---
        if state != 'back_turned':
             head_tilt_angle = segment_wave_offset * 0.1 # Use wave offset from head segment
             self.draw_slith_face(surface, size, pixel_size, frame_index, state, is_hatching=False, face_center=self.last_head_pos, tilt_angle=head_tilt_angle)
        else:
             draw_pixel_rect(surface, shade_color, (head_x - pixel_size, head_y, pixel_size*2, pixel_size*2), pixel_size)


        # --- Draw Accessories (Overlay Layers) ---
        neck_item = accessories.get('neck')
        if neck_item:
            self.draw_neck_accessory(surface, self.last_neck_pos, self.last_head_size, neck_item)

        head_item = accessories.get('head')
        if head_item:
            self.draw_hat(surface, self.last_head_pos, self.last_head_size, head_item)

        glasses_item = accessories.get('glasses') # Separate slot for forehead glasses
        if glasses_item:
            self.draw_glasses(surface, self.last_head_pos, self.last_head_size, glasses_item)


        # --- Draw Neural Implants (Last, On Top of Head/Hat) ---
        if self.stage >= 10:
             self.draw_neural_implants(surface, size, pixel_size, int(p1[1])) # Draw relative to top curve point


    # --- Face Drawing with Tilt and Improved Sunglasses ---
    def draw_slith_face(self, surface, size, pixel_size, frame_index, state, is_hatching=False, face_center=None, tilt_angle=0):
        """Draws face elements (eyes, mouth, sunglasses) with optional tilt."""
        # Determine center point for face elements
        if face_center:
            center_x, base_y = face_center
        else: # Default position if not specified
            center_x = size // 2
            base_y = size * (0.35 if is_hatching else 0.4) # Slightly higher if hatching

        # Eye parameters
        eye_offset = size * 0.10 # Horizontal distance from center
        eye_size = pixel_size * 2 # Size of the eye block
        eye_y_int = int(base_y) # Integer Y position for eyes

        # Calculate rotation matrix components for tilt
        tilt_rad = math.radians(tilt_angle)
        cos_t = math.cos(tilt_rad)
        sin_t = math.sin(tilt_rad)

        # Helper function to apply tilt rotation to a point relative to the face center
        def tilt_point(x_coord, y_coord):
            x_rel = x_coord - center_x
            y_rel = y_coord - eye_y_int # Use eye_y_int as reference
            new_x = x_rel * cos_t - y_rel * sin_t + center_x
            new_y = x_rel * sin_t + y_rel * cos_t + eye_y_int
            return int(new_x), int(new_y)

        # Check if blinking (based on idle state timer)
        is_blinking = hasattr(self, 'idle_state') and self.idle_state == 'blink' and state == 'idle'

        # Draw Mouth (only if not hatching)
        if not is_hatching:
            mouth_offset_y = eye_size + pixel_size * 2 # Vertical offset from eyes
            mouth_x_base = center_x - pixel_size # Base X for mouth center
            mouth_y_base = eye_y_int + mouth_offset_y # Base Y for mouth
            # Calculate tilted positions for mouth parts
            m1 = tilt_point(mouth_x_base - pixel_size, mouth_y_base + (pixel_size if state != 'happy' else 0)) # Left point
            m2 = tilt_point(mouth_x_base, mouth_y_base + (0 if state != 'sad' else pixel_size)) # Center point
            m3 = tilt_point(mouth_x_base + pixel_size, mouth_y_base + (pixel_size if state != 'happy' else 0)) # Right point

            # Draw mouth based on state (happy, sad, or neutral - implied no drawing)
            mouth_color = COLORS.get('bg_dark', (0,0,0)) # Mouth color
            if state == 'happy': # Upward curve
                draw_pixel_rect(surface, mouth_color, (m1[0], m1[1], pixel_size, pixel_size), pixel_size)
                draw_pixel_rect(surface, mouth_color, (m2[0], m2[1] + pixel_size, pixel_size, pixel_size), pixel_size) # Center lower
                draw_pixel_rect(surface, mouth_color, (m3[0], m3[1], pixel_size, pixel_size), pixel_size)
            elif state == 'sad': # Downward curve
                draw_pixel_rect(surface, mouth_color, (m1[0], m1[1] + pixel_size, pixel_size, pixel_size), pixel_size) # Left lower
                draw_pixel_rect(surface, mouth_color, (m2[0], m2[1], pixel_size, pixel_size), pixel_size)
                draw_pixel_rect(surface, mouth_color, (m3[0], m3[1] + pixel_size, pixel_size, pixel_size), pixel_size) # Right lower

        # Sunglasses Rework (Pink Frame, Black Lenses) - Drawn on top
        lens_height = eye_size + pixel_size # Height of lenses
        lens_width = eye_size * 2.5 # Width of lenses
        bridge_width = pixel_size * 2 # Width of the bridge between lenses
        frame_color = COLORS.get('accent') # Pink frame
        lens_color = COLORS.get('bg_dark', (0,0,0)) # Black lenses
        # Calculate base center positions for lenses
        left_lens_center_x = center_x - eye_offset
        right_lens_center_x = center_x + eye_offset
        lens_y = eye_y_int # Y position aligned with eyes

        # Calculate tilted top-left corners for lenses
        ll_tl = tilt_point(left_lens_center_x - lens_width/2, lens_y - lens_height/2)
        rl_tl = tilt_point(right_lens_center_x - lens_width/2, lens_y - lens_height/2)
        # Ensure integer dimensions aligned to pixel grid
        l_width_int = max(pixel_size, (int(lens_width) // pixel_size) * pixel_size)
        l_height_int = max(pixel_size, (int(lens_height) // pixel_size) * pixel_size)
        frame_thickness = pixel_size

        # Draw Frames first (slightly larger than lenses)
        draw_pixel_rect(surface, frame_color, (ll_tl[0] - frame_thickness, ll_tl[1] - frame_thickness, l_width_int + 2*frame_thickness, l_height_int + 2*frame_thickness), pixel_size)
        draw_pixel_rect(surface, frame_color, (rl_tl[0] - frame_thickness, rl_tl[1] - frame_thickness, l_width_int + 2*frame_thickness, l_height_int + 2*frame_thickness), pixel_size)
        # Draw Lenses (on top of frame background)
        draw_pixel_rect(surface, lens_color, (ll_tl[0], ll_tl[1], l_width_int, l_height_int), pixel_size)
        draw_pixel_rect(surface, lens_color, (rl_tl[0], rl_tl[1], l_width_int, l_height_int), pixel_size)
        # Draw Bridge (on top of lenses/frames)
        bridge_x = center_x - bridge_width / 2 # Center the bridge
        bridge_y = lens_y
        b_tl = tilt_point(bridge_x, bridge_y - pixel_size / 2) # Tilted top-left of bridge
        draw_pixel_rect(surface, frame_color, (b_tl[0], b_tl[1], int(bridge_width), pixel_size), pixel_size)

        # Draw Glint (small white square on left lens) unless blinking
        if not is_blinking:
            glint_rel_x = -lens_width / 2 + pixel_size # Relative position on lens
            glint_rel_y = -lens_height / 2 + pixel_size
            glint_abs_x = left_lens_center_x + glint_rel_x # Absolute position before tilt
            glint_abs_y = lens_y + glint_rel_y
            g_tl = tilt_point(glint_abs_x, glint_abs_y) # Tilted position
            draw_pixel_rect(surface, (255, 255, 255), (g_tl[0], g_tl[1], pixel_size, pixel_size), pixel_size)

        # Tongue Flick Animation (only for idle/happy states on certain frames)
        if frame_index in [1, 3] and state in ['idle', 'happy'] and not is_hatching:
             mouth_base_y_rel = eye_size + pixel_size * 4 # Y position below mouth
             mouth_pos = tilt_point(center_x, eye_y_int + mouth_base_y_rel) # Tilted position
             tongue_y_end = mouth_pos[1] + pixel_size * 3 # End Y position of tongue
             # Draw main tongue line
             draw_pixel_line(surface, COLORS.get('danger'), mouth_pos, (mouth_pos[0], tongue_y_end), pixel_size)
             # Draw fork at the end
             fork_p1 = tilt_point(mouth_pos[0] - pixel_size, tongue_y_end) # Left fork point
             fork_p2 = tilt_point(mouth_pos[0] + pixel_size, tongue_y_end) # Right fork point
             draw_pixel_rect(surface, COLORS.get('danger'), (fork_p1[0], fork_p1[1], pixel_size, pixel_size), pixel_size)
             draw_pixel_rect(surface, COLORS.get('danger'), (fork_p2[0], fork_p2[1], pixel_size, pixel_size), pixel_size)


    # --- Tech Detail Drawing Helpers (Accept Y position) ---
    def draw_computer_sprite(self, surface, size, pixel_size, frame_index, base_y):
        """Draws the computer elements for stages 6+ at specified base_y"""
        # Dimensions relative to sprite size
        computer_height = size // 4
        computer_width = size // 2
        computer_x = (size - computer_width) // 2 # Centered horizontally
        computer_y = int(base_y) # Use provided base Y
        # Draw base rectangle (monitor/case)
        base_rect = pygame.Rect(computer_x, computer_y, computer_width, computer_height)
        draw_pixel_rect(surface, COLORS.get('text_dark'), base_rect, pixel_size)
        # Draw screen area inset within the base
        screen_margin = pixel_size * 2
        screen_x = computer_x + screen_margin
        screen_y = computer_y + screen_margin
        screen_width = computer_width - 2 * screen_margin
        screen_height = computer_height - 2 * screen_margin
        screen_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        # Simple screen color animation (changes slightly with frame_index)
        screen_color = (0, 50 + frame_index * 10, 30 + frame_index * 5)
        # Draw screen only if dimensions are valid
        if screen_rect.width > 0 and screen_rect.height > 0:
            draw_pixel_rect(surface, screen_color, screen_rect, pixel_size)

    def draw_rgb_lights(self, surface, size, pixel_size, frame_index, base_y):
         """Draws RGB lights for stage 8+ at specified base_y"""
         light_y = int(base_y - pixel_size * 2) # Position slightly above the computer base
         light_colors = [COLORS.get('accent'), COLORS.get('neon'), (0, 200, 255)] # Pink, Yellow, Cyan
         spacing = size // 5 # Spacing between lights
         for i, color in enumerate(light_colors):
             light_x = size // 2 - spacing + i * spacing # Calculate horizontal position
             # Simple pulsing brightness effect using sine wave based on time and index
             brightness_mod = 1.0 + 0.2 * math.sin(pygame.time.get_ticks() * 0.003 + i)
             # Apply brightness modification to color
             final_color = tuple(min(255, max(0, int(c * brightness_mod))) for c in color[:3])
             # Slightly change size based on frame index for subtle animation
             light_size = pixel_size * (1 + (frame_index % 2))
             # Draw the light as a circle
             draw_pixel_circle(surface, final_color, (light_x, light_y), light_size, pixel_size)

    def draw_neural_implants(self, surface, size, pixel_size, head_top_y):
        """Draws neural implants for stage 10 near the specified head_top_y"""
        # Central node position on top of the head
        node_center_x = size // 2
        node_center_y = int(head_top_y + size // 10) # Slightly below the very top
        node_radius = pixel_size * 2
        # Draw the central node
        draw_pixel_circle(surface, COLORS.get('accent'), (node_center_x, node_center_y), node_radius, pixel_size)
        # Draw connecting "wires" or lines
        draw_pixel_line(surface, COLORS.get('accent'), (node_center_x, node_center_y), (size * 0.45, head_top_y + size * 0.25), pixel_size)
        draw_pixel_line(surface, COLORS.get('accent'), (node_center_x, node_center_y), (size * 0.55, head_top_y + size * 0.25), pixel_size)


    # --- Other Helpers ---
    def apply_pixel_shift(self, sprite, pixel_size, dx=0, dy=0):
        """Shifts the sprite content by a multiple of pixel_size (unused currently)."""
        shifted_sprite = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        shifted_sprite.blit(sprite, (dx * pixel_size, dy * pixel_size))
        return shifted_sprite

    # --- Core Methods ---
    def update(self, frame):
        """Update the sprite animation state variables."""
        self.animation_frame = frame % 4 # Cycle through 4 animation frames

        # Update wave animation offset
        self.wave_offset += self.wave_speed
        if self.wave_offset > 2 * math.pi: self.wave_offset -= 2 * math.pi # Keep within 0-2pi

        # Update bounce animation offset
        self.bounce_offset += 0.15 * self.bounce_direction # Move up or down
        if abs(self.bounce_offset) >= 3: self.bounce_direction *= -1 # Reverse direction at limits
        self.scale = 1.0; self.rotation = 0 # Reset scale/rotation (unused currently)

        # Update idle state timer (for blinking)
        self.idle_timer += 1
        if self.idle_state == 'normal' and self.idle_timer > 80: # After 80 frames of normal
            if random.random() > 0.7: # 30% chance to blink
                self.idle_state = 'blink'
                self.idle_timer = 0
            else: # Reset timer if not blinking
                self.idle_timer = 0
        elif self.idle_state == 'blink' and self.idle_timer > self.blink_duration: # After blink duration
            self.idle_state = 'normal' # Return to normal
            self.idle_timer = 0


    def draw(self, surface, accessories=None): # Added accessories parameter
        """Draw the sprite to the screen, applying animations dynamically and drawing accessories."""
        if accessories is None: accessories = self.accessories # Use stored accessories if none passed

        # Estimate base size for the temporary surface
        base_size = 50 + (self.stage * 10)
        base_size = max(self.pixel_size * 12, (int(base_size * 1.1) // self.pixel_size) * self.pixel_size)
        temp_surface = pygame.Surface((base_size, base_size), pygame.SRCALPHA)

        color_key = self.state if self.state in COLORS else 'neon' # Use state as key, fallback to neon
        color = COLORS.get(color_key, COLORS.get('neon', (255, 221, 0))) # Get color for current state

        size = temp_surface.get_width()

        # Redraw the sprite appearance based on stage and apply animations
        if self.stage == 0: # Egg Stage
            # (Egg drawing logic remains the same)
            egg_rect = pygame.Rect(size * 0.1, size * 0.05, size * 0.8, size * 0.9)
            pulse_size_mod = 0
            if self.animation_frame == 1: pulse_size_mod = -0.03
            elif self.animation_frame == 3: pulse_size_mod = 0.03
            current_width = egg_rect.width * (1 + pulse_size_mod); current_height = egg_rect.height * (1 + pulse_size_mod)
            offset_x = (size - current_width) / 2; offset_y = (size - current_height) / 2
            pulse_rect = pygame.Rect(offset_x, offset_y, current_width, current_height)
            draw_pixel_oval(temp_surface, color, pulse_rect, self.pixel_size)
            if self.animation_frame % 2 == 0:
                for _ in range(3):
                    px_coord = random.randint(int(size*0.3), int(size*0.7)); py_coord = random.randint(int(size*0.3), int(size*0.7))
                    blink_color = random.choice([COLORS.get('accent'), COLORS.get('neon'), (200,200,255)])
                    draw_pixel_rect(temp_surface, blink_color, (px_coord, py_coord, self.pixel_size, self.pixel_size), self.pixel_size)
        elif self.stage == 1: # Hatching Stage
            # Draw hatching sprite dynamically (includes face animation)
            self.draw_hatching_sprite(temp_surface, color, size, self.pixel_size, self.animation_frame, self.state)
        else: # Snake Stages (2+)
            # Draw S-shape snake dynamically, passing accessories
            self.draw_s_shape_snake(temp_surface, color, size, self.pixel_size, self.animation_frame, self.state, self.wave_offset, accessories)

        # Update the sprite's drawing rectangle based on current position and bounce offset
        self.rect = temp_surface.get_rect(center=(self.x, int(self.y + self.bounce_offset)))
        # Blit the dynamically drawn frame onto the main game surface
        surface.blit(temp_surface, self.rect)


    def set_state(self, state):
        """Set the sprite's animation state (e.g., 'idle', 'happy', 'sad')."""
        if state in ANIMATION_STATES:
            if self.state != state: # Only change if state is different
                self.state = state
                self.animation_frame = 0 # Reset animation frame on state change
                self.idle_state = 'normal' # Reset idle behavior (like blinking)
                self.idle_timer = 0
                # Ensure rect exists even if sprites aren't pre-loaded
                if not hasattr(self, 'rect'):
                    self.rect = pygame.Rect(self.x-25, self.y-25, 50, 50) # Default rect size
        else:
            print(f"Warning: Attempted to set invalid state '{state}'")


    def set_back_turned(self, back_turned):
        """Turn Slith's back to the player if a vital is at zero."""
        if back_turned:
            # If needs to turn back and isn't already, set state
            if self.state != 'back_turned':
                self.set_state('back_turned')
        elif self.state == 'back_turned':
            # If doesn't need to be turned back but currently is, set back to idle
            self.set_state('idle')


# ---------------------------------------------------
# CareItem Classes (Tamagotchi style)
# (No changes needed in CareItem or its subclasses)
# ---------------------------------------------------
class CareItem:
    """Base class for clickable care items (food, water, etc.)."""
    def __init__(self, x, y, color, icon_char):
        self.x = x # Center X position
        self.y = y # Center Y position
        self.color = color # Base color (used for border, icon)
        self.icon_char = icon_char # Original text icon (unused now)
        self.size = 40 # Size of the item button
        self.pixel_size = PIXEL_SCALE # Use constant
        # Calculate initial drawing rectangle centered on x, y
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.hovered = False # Is the mouse hovering over this item?
        self.pulse = 0 # Animation variable for hover effect
        self.animation_frame = 0 # Current frame for icon animation
        self.animation_timer = 0 # Timer for icon animation
        # Generate the animated icon frames on initialization
        self.animation_frames = self.generate_frames()

    def generate_frames(self):
        """Generates multiple surface frames for the item's icon animation."""
        frames = []
        # Create 4 frames for a simple animation loop
        for frame_index in range(4):
            # Create a surface for this frame
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            # Draw the specific icon for this frame using the subclass method
            self.draw_pixel_art_icon(surface, frame_index)
            frames.append(surface)
        return frames

    def draw_pixel_art_icon(self, surface, frame_index):
        """Placeholder method for drawing the icon. Subclasses must override this."""
        # Default: Draw a simple colored square
        icon_size = self.size // 2
        icon_rect = pygame.Rect((self.size - icon_size)//2, (self.size - icon_size)//2, icon_size, icon_size)
        draw_pixel_rect(surface, self.color, icon_rect, self.pixel_size)

    def update(self):
        """Updates animation timers for the item."""
        # Update pulse animation for hover effect
        self.pulse = (self.pulse + 0.15) % (2 * math.pi) # Cycle pulse value
        # Update icon animation timer
        self.animation_timer += 1
        if self.animation_timer >= 12: # Change icon frame every 12 game ticks
            self.animation_timer = 0
            if self.animation_frames: # Ensure frames exist
                # Cycle through the generated animation frames
                self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)

    def draw(self, surface):
        """Draws the care item button and its animated icon."""
        display_size = self.size # Base size
        border_color = self.color # Default border color
        bg_color = COLORS.get('bg_dark', (10, 8, 16)) # Background color for the button

        # Apply hover effect (pulsing size and different border color)
        if self.hovered:
            border_color = COLORS.get('accent', (255, 105, 180)) # Use accent color for hover border
            size_mod = int(3 * math.sin(self.pulse)) # Calculate size change based on pulse
            display_size += size_mod # Apply pulsing size change

        border_thickness = self.pixel_size # Border thickness

        # Calculate the outer rectangle for the button based on display_size
        outer_rect = pygame.Rect(self.x - display_size // 2, self.y - display_size // 2, display_size, display_size)
        # Draw the border rectangle
        draw_pixel_rect(surface, border_color, outer_rect, self.pixel_size)
        # Calculate the inner rectangle for the background
        inner_rect = pygame.Rect(outer_rect.x + border_thickness, outer_rect.y + border_thickness, outer_rect.width - 2 * border_thickness, outer_rect.height - 2 * border_thickness)
        # Draw the inner background rectangle if it has valid dimensions
        if inner_rect.width > 0 and inner_rect.height > 0:
            draw_pixel_rect(surface, bg_color, inner_rect, self.pixel_size)

        # Draw the animated icon
        if self.animation_frames:
            # Get the current frame surface
            current_frame_index = 0
            if len(self.animation_frames) > 0:
                current_frame_index = self.animation_frame % len(self.animation_frames)
            else: return # Do nothing if no frames
            icon_surface = self.animation_frames[current_frame_index]
            # Calculate the position to center the icon within the button
            icon_rect = icon_surface.get_rect(center=(self.x, self.y))
            # Blit the icon onto the main surface
            surface.blit(icon_surface, icon_rect)

        # Update the item's clickable rectangle (used for collision detection)
        self.rect = outer_rect

# --- Specific Care Item Classes ---
class FoodItem(CareItem):
    """Food care item (Burger icon)."""
    def __init__(self, x, y):
        super().__init__(x, y, COLORS.get('food', (255, 100, 100)), "🍔") # Initialize base class

    def draw_pixel_art_icon(self, surface, frame_index):
        """Draws a pixel art burger icon."""
        w, h = surface.get_size()
        px = self.pixel_size
        center_x, center_y = w // 2, h // 2
        # Define colors for burger parts
        bun_c = (210, 140, 90) # Bun color
        patty_c = (100, 60, 40) # Patty color
        cheese_c = COLORS.get('neon', (255, 221, 0)) # Cheese color (yellow)
        lettuce_c = (100, 200, 100) # Lettuce color

        # --- Centering Adjustment ---
        # Define relative coordinates for all parts first to calculate bounds
        burger_parts = [
            # Top bun main
            {'rect': (-px * 4, -px * 4, px * 8, px * 3), 'color': bun_c},
            # Top bun curve
            {'rect': (-px * 3, -px * 5, px * 6, px), 'color': bun_c},
            # Cheese slice
            {'rect': (-px * 4, -px * 2, px * 8, px * 2), 'color': cheese_c},
            # Patty
            {'rect': (-px * 5, 0, px * 10, px * 2), 'color': patty_c},
            # Lettuce
            {'rect': (-px * 4, px * 2, px * 8, px), 'color': lettuce_c},
            # Bottom bun
            {'rect': (-px * 4, px * 3, px * 8, px * 2), 'color': bun_c},
        ]
        # Add cheese drips for animation frames
        drip = px if frame_index in [1, 3] else 0
        if drip:
             burger_parts.append({'rect': (-px * 2, px * 0, px * 2, drip), 'color': cheese_c}) # Drip 1 (Adjusted Y)
             burger_parts.append({'rect': (px * 1, px * 0, px * 2, drip), 'color': cheese_c}) # Drip 2 (Adjusted Y)

        # Calculate bounds
        min_x = min(p['rect'][0] for p in burger_parts)
        max_x = max(p['rect'][0] + p['rect'][2] for p in burger_parts)
        min_y = min(p['rect'][1] for p in burger_parts)
        max_y = max(p['rect'][1] + p['rect'][3] for p in burger_parts)

        pixel_width = max_x - min_x
        pixel_height = max_y - min_y
        horizontal_offset = (w - pixel_width) // 2
        vertical_offset = (h - pixel_height) // 2
        # Correct shift calculation: offset needed to move top-left corner to (horizontal_offset, vertical_offset)
        correct_shift_x = horizontal_offset - min_x
        correct_shift_y = vertical_offset - min_y


        # Draw layers using pixel rects with shift applied
        for part in burger_parts:
            x_rel, y_rel, w_rel, h_rel = part['rect']
            # Apply correct shift to the relative coordinates
            draw_x = x_rel + correct_shift_x
            draw_y = y_rel + correct_shift_y
            draw_pixel_rect(surface, part['color'], (draw_x, draw_y, w_rel, h_rel), px)


class WaterItem(CareItem):
    """Water care item (Droplet icon)."""
    def __init__(self, x, y):
        super().__init__(x, y, COLORS.get('water', (80, 160, 255)), "💧") # Initialize base class

    def draw_pixel_art_icon(self, surface, frame_index):
        """Draws a pixel art water droplet icon."""
        w, h = surface.get_size()
        px = self.pixel_size
        center_x, center_y = w // 2, h // 2
        droplet_color = self.color[:3] # Get base color without alpha
        # Define pixel coordinates relative to the center for the droplet shape
        pixels = [
            (0, -4 * px), (-px, -3 * px), (0, -3 * px), (px, -3 * px),
            (-2 * px, -2 * px), (-px, -2 * px), (0, -2 * px), (px, -2 * px), (2 * px, -2 * px),
            (-3 * px, -px), (-2 * px, -px), (-px, -px), (0, -px), (px, -px), (2 * px, -px), (3 * px, -px),
            (-3 * px, 0), (-2 * px, 0), (-px, 0), (0, 0), (px, 0), (2 * px, 0), (3 * px, 0),
            (-3 * px, px), (-2 * px, px), (-px, px), (0, px), (px, px), (2 * px, px), (3 * px, px),
            (-2 * px, 2 * px), (-px, 2 * px), (0, 2 * px), (px, 2 * px), (2 * px, 2 * px),
            (-px, 3 * px), (0, 3 * px), (px, 3 * px),
            (0, 4 * px)
        ]
        # Add extra pixels at the bottom for dripping animation
        if frame_index in [1, 3]:
            pixels.extend([(-px, 4 * px), (px, 4 * px), (0, 5 * px)])

        # --- Centering Adjustment (Both Axes) ---
        min_x = min(dx for dx, dy in pixels)
        max_x = max(dx for dx, dy in pixels)
        min_y = min(dy for dx, dy in pixels)
        max_y = max(dy for dx, dy in pixels)

        pixel_width = max_x - min_x + px
        pixel_height = max_y - min_y + px
        horizontal_offset = (w - pixel_width) // 2
        vertical_offset = (h - pixel_height) // 2
        # Correct shift calculation
        correct_shift_x = horizontal_offset - min_x
        correct_shift_y = vertical_offset - min_y


        # Draw all pixels defined in the list, applying the shifts
        for dx, dy in pixels:
            draw_x = dx + correct_shift_x
            draw_y = dy + correct_shift_y
            draw_pixel_rect(surface, droplet_color, (draw_x, draw_y, px, px), px)

        # Add a simple highlight (adjust highlight position with the shifts)
        highlight_color = (200, 220, 255)
        # Highlight pixel 1 (relative: -px, -2*px)
        hl1_draw_x = -px + correct_shift_x
        hl1_draw_y = -2*px + correct_shift_y
        draw_pixel_rect(surface, highlight_color, (hl1_draw_x, hl1_draw_y, px, px), px)
        # Highlight pixel 2 (relative: 0, -px)
        hl2_draw_x = 0 + correct_shift_x
        hl2_draw_y = -px + correct_shift_y
        draw_pixel_rect(surface, highlight_color, (hl2_draw_x, hl2_draw_y, px, px), px)


class EntertainmentItem(CareItem):
    """Entertainment care item (Gamepad icon)."""
    def __init__(self, x, y):
        super().__init__(x, y, COLORS.get('entertainment', (170, 100, 255)), "🎮") # Initialize base class

    def draw_pixel_art_icon(self, surface, frame_index):
        """Draws a pixel art gamepad icon."""
        w, h = surface.get_size()
        px = self.pixel_size
        center_x, center_y = w // 2, h // 2
        base_color = self.color[:3] # Gamepad body color
        dark_color = (50, 50, 50) # D-pad color
        accent_color = COLORS.get('accent', (255, 105, 180)) # Button color

        # Define parts relative to (0,0) for centering calculation
        gamepad_parts = [
            # Body
            {'rect': (-px * 6, -px * 3, px * 12, px * 6), 'color': base_color},
            # Grips
            {'rect': (-px * 7, -px * 2, px, px * 4), 'color': base_color}, # Left grip
            {'rect': (px * 6, -px * 2, px, px * 4), 'color': base_color}, # Right grip
            # D-pad
            {'rect': (-px * 4, -px * 1, px, px * 3), 'color': dark_color}, # Vertical
            {'rect': (-px * 5, 0, px * 3, px), 'color': dark_color}, # Horizontal
        ]
        # Buttons (relative positions)
        btn_rel_x = px * 2
        btn_rel_y = -px * 2
        pressed_offset = px if frame_index in [1, 3] else 0
        gamepad_parts.append({'rect': (btn_rel_x, btn_rel_y + pressed_offset, px * 2, px * 2), 'color': COLORS.get('neon')}) # Button 1
        gamepad_parts.append({'rect': (btn_rel_x + px * 2, btn_rel_y + px + pressed_offset, px * 2, px * 2), 'color': accent_color}) # Button 2

        # Calculate bounds
        min_x = min(p['rect'][0] for p in gamepad_parts)
        max_x = max(p['rect'][0] + p['rect'][2] for p in gamepad_parts)
        min_y = min(p['rect'][1] for p in gamepad_parts)
        max_y = max(p['rect'][1] + p['rect'][3] for p in gamepad_parts)

        pixel_width = max_x - min_x
        pixel_height = max_y - min_y
        horizontal_offset = (w - pixel_width) // 2
        vertical_offset = (h - pixel_height) // 2
        # Correct shift calculation
        correct_shift_x = horizontal_offset - min_x
        correct_shift_y = vertical_offset - min_y

        # Draw all parts with shift applied
        for part in gamepad_parts:
            x_rel, y_rel, w_rel, h_rel = part['rect']
            draw_x = x_rel + correct_shift_x
            draw_y = y_rel + correct_shift_y
            draw_pixel_rect(surface, part['color'], (draw_x, draw_y, w_rel, h_rel), px)


class LoveItem(CareItem):
    """Love care item (Heart icon)."""
    def __init__(self, x, y):
        super().__init__(x, y, COLORS.get('love', (255, 100, 255)), "❤️") # Initialize base class

    def draw_pixel_art_icon(self, surface, frame_index):
        """Draws a pixel art heart icon."""
        w, h = surface.get_size()
        px = self.pixel_size
        center_x, center_y = w // 2, h // 2
        heart_color = self.color[:3] # Base heart color
        glow_color = COLORS.get('accent', (255, 105, 180)) # Color for the glow effect

        # Heart Shape Pixel Coordinates (relative to 0,0)
        pixels = [
            (-2*px, -3*px), (-1*px, -3*px), (1*px, -3*px), (2*px, -3*px),
            (-3*px, -2*px), (-2*px, -2*px), (-1*px, -2*px), (0, -2*px), (1*px, -2*px), (2*px, -2*px), (3*px, -2*px),
            (-3*px, -1*px), (-2*px, -1*px), (-1*px, -1*px), (0, -1*px), (1*px, -1*px), (2*px, -1*px), (3*px, -1*px),
            (-2*px, 0), (-1*px, 0), (0, 0), (1*px, 0), (2*px, 0),
            (-1*px, 1*px), (0, 1*px), (1*px, 1*px),
            (0, 2*px)
        ]
        # Outline Coordinates for Glow (relative to 0,0)
        outline_pixels = [
            (-2*px, -4*px), (-1*px, -4*px), (1*px, -4*px), (2*px, -4*px),
            (-3*px, -3*px), (3*px, -3*px),
            (-4*px, -2*px), (4*px, -2*px),
            (-4*px, -1*px), (4*px, -1*px),
            (-3*px, 0), (3*px, 0),
            (-2*px, 1*px), (2*px, 1*px),
            (-1*px, 2*px), (1*px, 2*px),
            (0, 3*px)
        ]

        # Apply scaling animation (pulsing effect)
        scale = 1.0
        if frame_index == 1: scale = 1.1 # Slightly larger
        elif frame_index == 3: scale = 0.9 # Slightly smaller

        # --- Centering Adjustment (Both Axes) ---
        all_coords = pixels + outline_pixels # Consider all pixels for bounding box
        min_x = min(dx for dx, dy in all_coords)
        max_x = max(dx for dx, dy in all_coords)
        min_y = min(dy for dx, dy in all_coords)
        max_y = max(dy for dx, dy in all_coords)

        pixel_width = max_x - min_x + px
        pixel_height = max_y - min_y + px
        horizontal_offset = (w - pixel_width) // 2
        vertical_offset = (h - pixel_height) // 2
        # Correct shift calculation
        correct_shift_x = horizontal_offset - min_x
        correct_shift_y = vertical_offset - min_y

        # Draw the main heart shape using the scaled coordinates and applying shifts
        for dx, dy in pixels:
            scaled_dx = int(dx * scale)
            scaled_dy = int(dy * scale)
            # Align scaled coordinates to the pixel grid and apply shifts
            draw_x = (scaled_dx // px * px) + correct_shift_x # Apply shift_x
            draw_y = (scaled_dy // px * px) + correct_shift_y # Apply shift_y
            draw_pixel_rect(surface, heart_color, (draw_x, draw_y, px, px), px)

        # Draw glow effect on certain frames
        if frame_index in [0, 2]:
             # Create a set of main heart pixel coordinates for quick lookup
             heart_pixel_set = set()
             for dx, dy in pixels:
                 scaled_dx = int(dx * scale); scaled_dy = int(dy * scale)
                 draw_x = (scaled_dx // px * px) + correct_shift_x
                 draw_y = (scaled_dy // px * px) + correct_shift_y
                 heart_pixel_set.add((draw_x, draw_y))

             # Draw outline pixels if they are NOT part of the main heart
             for dx, dy in outline_pixels:
                 scaled_dx = int(dx * scale); scaled_dy = int(dy * scale)
                 draw_x = (scaled_dx // px * px) + correct_shift_x # Apply shift_x
                 draw_y = (scaled_dy // px * px) + correct_shift_y # Apply shift_y
                 if (draw_x, draw_y) not in heart_pixel_set:
                      draw_pixel_rect(surface, glow_color, (draw_x, draw_y, px, px), px)
