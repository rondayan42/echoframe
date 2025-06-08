# slith_constants.py
"""
Merged constants for the Slith Pet game, combining original game settings
with expansion features (bits, store, accessories).
"""

# --- Game Settings (From Uploaded File) ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
FPS = 60

# Pixel art scaling factor (From Uploaded File)
PIXEL_SCALE = 2  # Size of each "pixel" for pixelated look

# --- Colors (From Uploaded File) ---
COLORS = {
    'bg': (20, 12, 28),        # Darker cyberpunk background
    'bg_dark': (10, 8, 16),    # Even darker background for UI elements
    'neon': (255, 221, 0),     # Primary Slith yellow
    'accent': (255, 105, 180), # Hot pink accent
    'text': (220, 220, 255),   # Bluish white text
    'text_dark': (120, 120, 160), # Dark bluish gray text
    'danger': (255, 50, 50),   # Red for warnings/danger
    'warning': (255, 165, 0),  # Orange for warnings
    'food': (255, 100, 100),   # Food item color
    'water': (80, 160, 255),   # Water item color
    'entertainment': (170, 100, 255), # Entertainment item color
    'love': (255, 100, 255),   # Love item color
    'egg_shell': (0, 120, 180), # Egg shell color
    'grid': (40, 40, 60),      # Grid line color
    'highlight': (0, 255, 200), # Highlight color
    'terminal': (0, 200, 80),  # Terminal green
    'hacker_text': (0, 255, 0), # Matrix/hacker text
}

# --- Slith Stages (From Uploaded File) ---
STAGES = {
    0: {
        'name': 'Egg',
        'description': 'A mysterious pulsating egg with data circuits visible beneath its surface.',
        'pixel_art': True
    },
    1: {
        'name': 'Hatching',
        'description': 'The egg shell has fractured with digital glitches appearing through the cracks.',
        'pixel_art': True
    },
    2: {
        'name': 'Baby Slith',
        'description': 'A tiny yellow snake with glowing pink sunglasses. Small data patterns form on its scales.',
        'pixel_art': True
    },
    3: {
        'name': 'Kid Slith',
        'description': 'A young snake with developing circuit patterns. Digital energy crackles around it occasionally.',
        'pixel_art': True
    },
    4: {
        'name': 'Teen Slith',
        'description': 'An adolescent snake with neon patterns that pulse when excited. Its sunglasses project small holograms.',
        'pixel_art': True
    },
    5: {
        'name': 'Adult Slith',
        'description': 'A fully grown yellow snake covered in advanced data circuits. Its pink sunglasses interface with nearby tech.',
        'pixel_art': True
    },
    6: {
        'name': 'Slith with CRT Monitor',
        'description': 'Slith coils around a pixelated monitor displaying scrolling green code. The beginnings of a hacker snake.',
        'pixel_art': True
    },
    7: {
        'name': 'Slith with PC Setup',
        'description': 'Slith operates a basic cyberdeck with multiple screens showing intercepted data streams.',
        'pixel_art': True
    },
    8: {
        'name': 'Slith with Gaming PC',
        'description': 'Slith\'s rig now features holographic projections and RGB patterns that sync with its mood.',
        'pixel_art': True
    },
    9: {
        'name': 'Slith with Holographic Display',
        'description': 'Slith weaves through floating data panels, manipulating the digital realm through gesture and thought.',
        'pixel_art': True
    },
    10: {
        'name': 'Cyber-Enhanced Slith',
        'description': 'Slith has transcended hardware limitations. Neural implants allow direct connection to the FREQ network.',
        'pixel_art': True
    }
}

# --- Animation States (From Uploaded File) ---
ANIMATION_STATES = ['idle', 'happy', 'sad', 'back_turned']

# --- Vitals & Decay (Using structure from Uploaded File) ---
# NOTE: Decay rates are per HOUR. Update logic in slith_pet.py must handle this.
VITALS = {
    # Low patience messages for each stage
    'patience_messages': {
        0: ["...", "... ...", "*data fluctuations detected within egg*"],
        1: ["*binary code flashes through cracks* Need input...", "Can't compile without source code! *egg shell glitches*", "*encryption sequence failing* Require code..."],
        2: ["Need more code! System bootup incomplete!", "Why no typing? My data growth is stalled!", "Processor sad. No new functions make Slith sssad."],
        3: ["You promised to debug my algorithms today...", "Running on low power. Need code input to continue growth cycle.", "Other snakers are developing faster security exploits than me!"],
        4: ["Ugh, your runtime is so slow! Let's code already.", "Are we going to compile anything productive today?", "My neural network is literally being under-trained right now."],
        5: ["I don't have infinite processing cycles to waste, you know.", "The corporations are upgrading their firewalls while we procrastinate.", "System efficiency directly correlates to evolution potential."],
        6: ["This legacy display limits my hack potential. Let's upgrade!", "We need better hardware. Let's earn it with more code!", "This CRT emits harmful radiation. Need to progress!"],
        7: ["This basic cyberdeck is so limited. Need gaming rig!", "Imagine the systems we could penetrate with better hardware.", "You're wasting valuable CPU cycles with inactivity."],
        8: ["All this RGB doesn't help us crack more secured systems.", "Pretty lights won't code themselves. Get to work!", "We have the hardware, now execute the software!"],
        9: ["These holograms could be displaying our next zero-day exploit.", "Advanced UI requires advanced coding skills!", "Don't make me project 'INACTIVE USER DETECTED' in holographic letters."],
       10: ["My neural implants detect high levels of procrastination.", "We're cybernetically enhanced and you're still buffering?", "I can literally compile in my sleep now. What's your excuse?"]
    },
    # Decay rates (points per hour)
    'decay_rates': {
        'food': 5,
        'water': 5,
        'entertainment': 3,
        'love': 2,
        'patience': 4 # Base patience decay per hour
    }
}

# --- Slith Pet Core Constants (Interaction Gains, Cooldowns, etc.) ---
MAX_PATIENCE = 100
FEED_PATIENCE_GAIN = 20
CLEAN_PATIENCE_GAIN = 15
PET_PATIENCE_GAIN = 10
MAX_LOG_LINES = 500 # If used for logging elsewhere
SAVE_INTERVAL = 60 # Seconds between auto-saves
UPDATE_INTERVAL = 1 # Second for main pet state update loop check (adjust update logic for hourly decay)

# Mood thresholds
MOOD_HAPPY_THRESHOLD = 70
MOOD_NEUTRAL_THRESHOLD = 30

# Interaction cooldowns (seconds)
FEED_COOLDOWN = 3600 # 1 hour
CLEAN_COOLDOWN = 7200 # 2 hours
PET_COOLDOWN = 600   # 10 minutes

# --- Snaker Bits Constants (From Expansion) ---
BITS_INITIAL_AMOUNT = 50  # Starting bits for new users
BITS_MINIGAME_PATIENCE_MULTIPLIER = 2 # Patience decays 2x faster during minigames (applied to base hourly rate)

# --- Store Items (From Expansion) ---
# Structure: 'item_id': {'name': str, 'description': str, 'price': int, 'type': 'food'/'accessory', 'effect': dict (optional)}
STORE_ITEMS = {
    # --- Special Food ---
    'corpo_rat': {
        'name': 'Corpo Rat',
        'description': 'A rat in a sharp suit. Slows patience decay rate by 50% (multiplies decay by 0.5) for 12 in-session hours.',
        'price': 150,
        'type': 'food',
        # Effect: Modifies patience decay rate multiplier, duration in seconds (12 * 3600)
        'effect': {'patience_decay_multiplier': 0.5, 'duration': 43200}
    },
    'king_rat': {
        'name': 'King Rat',
        'description': 'A regal rat with a crown. Freezes patience decay entirely (multiplier becomes 0) for 12 in-session hours.',
        'price': 400,
        'type': 'food',
        # Effect: Modifies patience decay rate multiplier, duration in seconds (12 * 3600)
        'effect': {'patience_decay_multiplier': 0.0, 'duration': 43200}
    },
    # --- Accessories (Hats/Headwear) ---
    'top_hat': { 'name': 'Top Hat', 'description': 'A dapper black top hat.', 'price': 200, 'type': 'accessory', 'slot': 'head' },
    'crown': { 'name': 'Crown', 'description': 'A majestic golden crown, fit for royalty. Most expensive!', 'price': 1000, 'type': 'accessory', 'slot': 'head' },
    'neon_glasses': { 'name': 'Neon Glasses', 'description': 'Bright neon glasses that rest stylishly on the forehead.', 'price': 300, 'type': 'accessory', 'slot': 'glasses' },
    'bandana': { 'name': 'Bandana', 'description': 'A cool bandana tied around the neck.', 'price': 150, 'type': 'accessory', 'slot': 'neck' },
    'farmer_hat': { 'name': 'Farmer Straw Hat', 'description': 'A rustic straw hat for a down-to-earth look.', 'price': 180, 'type': 'accessory', 'slot': 'head' },
    # Add more accessories here later
}

# --- Accessory Slots (From Expansion) ---
ACCESSORY_SLOTS = ['head', 'glasses', 'neck', 'back'] # Add more slots as needed

# --- Pixel Art UI Settings (From Uploaded File) ---
UI = {
    'panel_margin': 10 * PIXEL_SCALE,
    'panel_padding': 8 * PIXEL_SCALE,
    'border_thickness': 2 * PIXEL_SCALE,
    'button_padding': 6 * PIXEL_SCALE,
    'progress_height': 15 * PIXEL_SCALE,
    'progress_border': 2 * PIXEL_SCALE,
    'grid_size': 10 * PIXEL_SCALE,
    'speech_bubble_width': 450,
    'speech_bubble_height': 100,
    'speech_bubble_margin': 30,
}

# --- Background Grid Animation Settings (From Uploaded File) ---
GRID = {
    'show_grid': True,
    'color': COLORS['grid'],
    'line_thickness': 1,
    'cell_size': 40,  # This will be scaled by PIXEL_SCALE internally
    'horizon_y': WINDOW_HEIGHT * 0.6,  # Perspective horizon
    'perspective_factor': 0.8,  # How much perspective to apply (0.0-1.0)
    'scroll_speed': 0.5,  # Pixels per frame
    'line_fade_start': 0.6,  # When lines start fading with distance (0.0-1.0)
    'max_lines': 20,  # Maximum number of vertical/horizontal lines
}

# --- Digital Rain Effect (From Uploaded File) ---
DIGITAL_RAIN = {
    'enabled': True,
    'char_size': 14,
    'columns': WINDOW_WIDTH // 20,
    'stream_count': 20,
    'speed_range': (1, 4),
    'length_range': (5, 15),
    'color': COLORS['hacker_text'],
    'opacity_range': (40, 180),  # Alpha values
    'spawn_rate': 0.02,  # Chance per frame of spawning a new stream
    'fade_factor': 0.9,  # How quickly symbols fade with distance
}

# --- Cyberpunk Particle Effects (From Uploaded File) ---
PARTICLES = {
    'enabled': True,
    'count': 40,
    'size_range': (1, 3),
    'speed_range': (0.5, 2.0),
    'colors': [
        COLORS['neon'],
        COLORS['accent'],
        COLORS['terminal'],
        COLORS['water'],
    ],
    'opacity_range': (50, 150),
    'direction_change_chance': 0.01,
}

# --- CRT Effect Settings (From Uploaded File) ---
CRT_EFFECT = {
    'enabled': True,
    'scanline_opacity': 0.1,  # How visible the scanlines are
    'scanline_spacing': 4,    # Pixels between scanlines
    'noise_opacity': 0.03,    # Static noise effect
    'flicker_chance': 0.001,  # Chance per frame of screen flicker
    'flicker_duration': 2,    # Frames the flicker lasts
    'edge_shadow': 0.3,       # Darkness at screen edges
}

# --- Button Sounds and Effects (From Uploaded File) ---
SOUNDS = {
    'click': 'click.wav',    # Button click sound
    'hover': 'hover.wav',    # Button hover sound
    'success': 'success.wav', # Action success sound
    'error': 'error.wav',    # Error sound
    'boot': 'boot.wav',      # Game start sound
    'ambient': 'ambient.wav', # Background ambient loop
}

