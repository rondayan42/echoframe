# app.py (Reverted to Pygame Launch for Slith Pet - Fixed SyntaxError)

# --- Start by monkey patching eventlet ---
import eventlet
eventlet.monkey_patch()

# --- Imports ---
import json, os, sys, tempfile, traceback, math, time, inspect
import subprocess # Re-add subprocess for launching the pet script
import random
from datetime import datetime, timedelta # Use datetime directly
from io import StringIO # BytesIO no longer needed for image route
import shutil
import threading

from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, jsonify, flash, Response # Response might not be needed
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from auto_login import setup_auto_login
from persistent_storage import storage # Use the persistent storage helper
from snake_starters import SNAKE_STARTER_CODE

# Add import for student-driven snake implementation
import student_driven_snake

# --- Snake Echo Arc File Management ---
def ensure_proper_formatting(filename, content):
    """
    Ensure proper formatting of file content, especially for food.py which may have formatting issues.

    Args:
        filename: The name of the file
        content: The content to format

    Returns:
        Properly formatted content
    """
    # Special case for food.py which may have formatting issues (all on one line)
    if filename == 'food.py':
        # Check if all content appears to be on a single line
        if content.count('\n') < 5:  # Normal food.py should have many line breaks
            # Extract key components from the content

            # Look for class definition and method definitions using regular expressions
            import re

            # Format the file properly with line breaks
            formatted_content = """# food.py: Contains the Food class definition
import pygame
import random
# All constants like GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, RED are available

class Food:
    def __init__(self):
        # Initialize with a random position
        self.reset()

    def draw(self, screen):
        # Draw a red rectangle for the food
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def reset(self):
        # Place food at a new random position on the grid
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
"""
            return formatted_content

    # For most files, no special formatting needed
    return content

def create_or_update_user_snake_files(username, echo_level):
    """
    Create or update the user's snake files based on their current echo level.

    Args:
        username: The username of the snaker
        echo_level: Integer representing the current echo level (0-9)

    Returns:
        Dictionary of files that should be shown in the editor for the current echo level
    """
    if not username:
        print(f"Invalid username: {username}")
        return {}

    # Safely determine valid_echo_level within the range of available starter code
    max_echo_level = len(SNAKE_STARTER_CODE) - 1
    if max_echo_level < 0:
        print("Error: SNAKE_STARTER_CODE is empty. Cannot create files.")
        return {}

    valid_echo_level = max(0, min(echo_level, max_echo_level))
    if echo_level != valid_echo_level:
        print(f"Warning: Echo level {echo_level} out of range, using echo level {valid_echo_level} instead.")

    # Create the user's base directory
    user_base_dir = os.path.join('user_data', 'snake_code', username)
    os.makedirs(user_base_dir, exist_ok=True)

    # Create a specific directory for this echo level
    echo_dir = os.path.join(user_base_dir, f'snake_echo_{valid_echo_level+1}')
    os.makedirs(echo_dir, exist_ok=True)

    # Get starter code for the current echo level
    try:
        starter_files = SNAKE_STARTER_CODE[valid_echo_level]
    except IndexError:
        print(f"Error: SNAKE_STARTER_CODE does not have index {valid_echo_level}. Using fallback.")
        # Use echo level 0 as fallback
        if len(SNAKE_STARTER_CODE) > 0:
            starter_files = SNAKE_STARTER_CODE[0]
        else:
            print("Error: SNAKE_STARTER_CODE is empty. Cannot create files.")
            return {}

    editor_files = {}

    # For each file in the starter code, create or update the user's file
    for filename, content in starter_files.items():
        # Ensure proper formatting, especially for food.py
        formatted_content = ensure_proper_formatting(filename, content)

        file_path = os.path.join(echo_dir, filename)

        # Only create the file if it doesn't exist yet
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(formatted_content)
            print(f"Created new file {file_path} for echo level {valid_echo_level}")
        else:
            # Check if existing file needs formatting fix
            with open(file_path, 'r') as f:
                existing_content = f.read()

            if filename == 'food.py' and existing_content.count('\n') < 5:
                # Fix existing malformatted food.py file
                with open(file_path, 'w') as f:
                    f.write(formatted_content)
                print(f"Fixed formatting in existing {file_path}")

        # Read the current content (either new or existing)
        with open(file_path, 'r') as f:
            current_content = f.read()

        # Add to the dictionary of files to show in the editor
        editor_files[filename] = current_content

    return editor_files

def get_user_snake_files(username, echo_level=None):
    """
    Get all Python files from a user's snake directory.

    Args:
        username: The username of the snaker
        echo_level: Optional integer representing the echo level (0-9).
                   If provided, only return files from that echo level's directory.

    Returns:
        Dictionary of filename -> content for all Python files in the user's directory
    """
    if not username:
        return {}

    user_base_dir = os.path.join('user_data', 'snake_code', username)
    if not os.path.isdir(user_base_dir):
        return {}

    user_files = {}

    # If echo_level is specified, only look in that echo's directory
    if echo_level is not None and 0 <= echo_level <= 9:
        echo_dir = os.path.join(user_base_dir, f'snake_echo_{echo_level+1}')
        if os.path.isdir(echo_dir):
            for filename in os.listdir(echo_dir):
                if filename.endswith('.py'):
                    try:
                        with open(os.path.join(echo_dir, filename), 'r') as f:
                            user_files[filename] = f.read()
                    except Exception as e:
                        print(f"Error reading user file {filename}: {e}")
        return user_files

    # Otherwise, look through all echo directories
    for i in range(10):  # 0-9 echo levels
        echo_dir = os.path.join(user_base_dir, f'snake_echo_{i+1}')
        if os.path.isdir(echo_dir):
            for filename in os.listdir(echo_dir):
                if filename.endswith('.py'):
                    try:
                        # Include echo level in the key to differentiate files
                        key = f"echo_{i+1}/{filename}"
                        with open(os.path.join(echo_dir, filename), 'r') as f:
                            user_files[key] = f.read()
                    except Exception as e:
                        print(f"Error reading user file {echo_dir}/{filename}: {e}")

    # Also include any files in the root of the user's directory for backward compatibility
    for filename in os.listdir(user_base_dir):
        if filename.endswith('.py'):
            try:
                with open(os.path.join(user_base_dir, filename), 'r') as f:
                    user_files[f"root/{filename}"] = f.read()
            except Exception as e:
                print(f"Error reading user file {filename}: {e}")

    return user_files

def get_echo_level_files(username, echo_level):
    """
    Get the files that should be shown for a specific echo level.

    Args:
        username: The username of the snaker
        echo_level: Integer representing the echo level (0-9)

    Returns:
        Dictionary of filename -> content for the specified echo level
    """
    # Ensure echo_level is within valid range for SNAKE_STARTER_CODE
    if not username:
        return {}

    # Safely determine valid_echo_level within the range of available starter code
    max_echo_level = len(SNAKE_STARTER_CODE) - 1
    valid_echo_level = max(0, min(echo_level, max_echo_level))

    if echo_level != valid_echo_level:
        print(f"Warning: Echo level {echo_level} out of range, using echo level {valid_echo_level} instead.")

    # Map of files that should be shown for each echo level
    echo_files = {
        0: {'constants.py', 'snake.py'},  # Echo 1: Define the Grid
        1: {'constants.py', 'snake.py'},  # Echo 2: Game Loop
        2: {'constants.py', 'snake.py', 'snake_class.py'},  # Echo 3: Snake Class
        3: {'constants.py', 'snake.py', 'snake_class.py'},  # Echo 4: Drawing
        4: {'constants.py', 'snake.py', 'snake_class.py', 'food.py'},  # Echo 5: Food Class
        5: {'constants.py', 'snake.py', 'snake_class.py', 'food.py'},  # Echo 6: Snake Growth
        6: {'constants.py', 'snake.py', 'snake_class.py', 'food.py'},  # Echo 7: Input
        7: {'constants.py', 'snake.py', 'snake_class.py', 'food.py'},  # Echo 8: Game State
        8: {'constants.py', 'snake.py', 'snake_class.py', 'food.py'},  # Echo 9: Score Display
        9: {'constants.py', 'snake.py', 'snake_class.py', 'food.py'},  # Echo 10: Game Over & Restart
    }

    # Specific directory for this echo level
    echo_dir = os.path.join('user_data', 'snake_code', username, f'snake_echo_{valid_echo_level+1}')

    # Check if the directory exists
    if not os.path.isdir(echo_dir):
        # If directory doesn't exist, create it and its files from starter code
        return create_or_update_user_snake_files(username, valid_echo_level)

    # Get files for the specified echo level
    filtered_files = {}
    # Ensure echo_dir exists for writing updated files
    os.makedirs(echo_dir, exist_ok=True) # Ensure echo_dir is created before trying to write files

    for filename in echo_files.get(valid_echo_level, {}): # These are the filenames expected for the current echo level
        file_path = os.path.join(echo_dir, filename)
        content_to_use = None
        source_description = "" # For logging/debugging

        try:
            # Ensure valid_echo_level is within bounds for SNAKE_STARTER_CODE itself
            if not (0 <= valid_echo_level < len(SNAKE_STARTER_CODE)):
                raise IndexError(f"valid_echo_level {valid_echo_level} is out of range for SNAKE_STARTER_CODE array.")

            # Check if the filename is even supposed to be in SNAKE_STARTER_CODE for this level
            # This guards against misconfigurations in 'echo_files'
            if filename not in SNAKE_STARTER_CODE[valid_echo_level]:
                print(f"Warning: File '{filename}' is expected per 'echo_files' for echo_level {valid_echo_level}, but it's not defined in SNAKE_STARTER_CODE[{valid_echo_level}]. Trying to load from user's directory or skipping.")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content_to_use = f.read()
                    source_description = "existing user file (starter definition missing)"
                else:
                    print(f"Warning: File '{filename}' also not found in user directory {file_path}. Skipping this file.")
                    continue # Skip this file entirely
            else:
                # Filename exists in SNAKE_STARTER_CODE for this level
                starter_content = SNAKE_STARTER_CODE[valid_echo_level][filename]
                formatted_starter_content = ensure_proper_formatting(filename, starter_content)

                if filename == "constants.py":
                    # For constants.py, always use the starter content and overwrite
                    content_to_use = formatted_starter_content
                    with open(file_path, 'w') as f:
                        f.write(content_to_use)
                    source_description = "starter code (constants.py - always refresh)"
                else:
                    # For other files, prioritize user's existing file
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content_to_use = f.read()
                        source_description = "existing user file"
                        # Optional: Could compare with starter_content and decide to refresh if starter is "newer"
                        # For now, simple "if exists, use" for student-editable files.
                    else:
                        # File doesn't exist in user's dir, so use starter content and write it
                        content_to_use = formatted_starter_content
                        with open(file_path, 'w') as f:
                            f.write(content_to_use)
                        source_description = "starter code (user file did not exist)"

            if content_to_use is not None:
                filtered_files[filename] = content_to_use
                # print(f"File '{file_path}': using {source_description}.")

        except IndexError as e:
            # This typically means valid_echo_level is out of range for SNAKE_STARTER_CODE overall
            print(f"Error (IndexError) processing file '{filename}' for echo_level {valid_echo_level}: {str(e)}. Check SNAKE_STARTER_CODE definition or valid_echo_level calculation.")
        except KeyError as e:
            # This means 'filename' was expected (e.g. from echo_files) but not a key in SNAKE_STARTER_CODE[valid_echo_level]
            # This path should ideally be caught by the explicit check `if filename not in SNAKE_STARTER_CODE[valid_echo_level]:` above.
            print(f"Error (KeyError) processing file '{filename}' for echo_level {valid_echo_level}: {str(e)}. Mismatch between 'echo_files' and SNAKE_STARTER_CODE content?")
        except Exception as e:
            # Catch any other unexpected errors during file processing for this specific file
            print(f"An unexpected error occurred while processing file '{filename}' for echo_level {valid_echo_level}: {str(e)}")
            traceback.print_exc() # Print full traceback for unexpected errors

    return filtered_files

def get_user_snake_echo_level(username):
    """
    Determine the current snake echo level for a user based on completed quests.

    Args:
        username: The username of the snaker

    Returns:
        Integer representing the current echo level (0-9)
    """
    if not username:
        return 0

    # Load user data from persistent storage
    user_data = load_pet_data(username)

    # Get completed quests
    completed = user_data.get('completed', [])

    # Check if the user has completed any snake quests
    # Snake quests start at index TOTAL_BEGINNER
    snake_quests_completed = [qid for qid in completed if qid >= TOTAL_BEGINNER]

    # Current echo level is the number of completed snake quests
    # If no snake quests are completed, check if they've seen the intro
    if not snake_quests_completed:
        # Check if they've seen the snake intro (echo level 0)
        if snake_intro_seen(username):
            return 0
        else:
            return -1  # Not started snake echo arc yet

    # Return the number of completed snake quests (0-indexed)
    # The echo level is equal to the number of completed quests
    # because we want them to work on the next echo
    return len(snake_quests_completed)

# Simple helper function to ensure the food position is valid
def ensure_food_position_valid(food, grid_width, grid_height, default_pos=None):
    """Verify food position and fix if invalid."""
    if not default_pos:
        default_pos = [grid_width // 2, grid_height // 2]

    try:
        if not hasattr(food, 'position'):
            food.position = default_pos
            return

        # Check if position is within bounds
        food_x, food_y = food.position
        if not (0 <= food_x < grid_width and 0 <= food_y < grid_height):
            food.position = default_pos
    except:
        # Any error, just use default position
        try:
            food.position = default_pos
        except:
            pass  # Last resort - can't fix it

# --- Add module path fix ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"Added current directory to Python path: {current_dir}")

# --- Import Slith Pet Modules (Check if needed for determine_slith_stage) ---
SLITH_PET_ENABLED = True # Assume enabled if imports work
try:
    # Only import what's strictly needed by Flask app now
    from slith_constants import STAGES # Needed for stage names potentially? Or remove if not used directly in Flask
    from slith_utils import determine_slith_stage, format_time_delta # Keep determine_slith_stage
    # Pygame and SlithSprite are no longer needed directly in app.py
    print("Slith Pet utility modules loaded successfully.")
except ImportError as e:
    SLITH_PET_ENABLED = False
    print(f"Slith Pet modules not found. Slith Pet feature will be disabled. Error: {e}")
    print(f"Current Python path: {sys.path}")
    # Define fallback functions if needed
    def determine_slith_stage(completed_snake_quests, snake_intro_seen, total_beginner=None):
        return 0
    def format_time_delta(seconds):
        return f"{int(seconds)}s"
    STAGES = {i: {'name': f'Stage {i}'} for i in range(11)} # Fallback stages if needed

# --- Flask App and SocketIO Initialization ---
app = Flask(__name__)
setup_auto_login(app)
app.secret_key = "echoframe-core-sigil" # Ensure you have a strong secret key
# Use a very stable configuration with long timeouts
socketio = SocketIO(
    app,
    async_mode='eventlet',
    ping_timeout=60000,  # 60 seconds timeout - proper value instead of extremely large one
    ping_interval=25,    # Standard ping interval
    cors_allowed_origins="*",
    transports=['polling', 'websocket'],  # Allow both polling and websocket
    always_connect=True,
    logger=True,
    engineio_logger=True
)

# --- Helper Functions for Snake Intro Tracking ---
# (Keep existing snake_intro_seen, mark_snake_intro_seen)
def snake_intro_seen(username):
    # Check if username is valid
    if not username or not isinstance(username, str):
        print(f"Warning: Invalid username '{username}' passed to snake_intro_seen.")
        return False
    marker_dir = os.path.join('user_data', 'intro_markers'); os.makedirs(marker_dir, exist_ok=True)
    # Sanitize username for filename
    safe_username = "".join(c for c in username if c.isalnum() or c in "._- ")
    if not safe_username: # Handle cases where username becomes empty after sanitization
         print(f"Warning: Username '{username}' resulted in empty safe filename.")
         return False
    marker_file = os.path.join(marker_dir, f"{safe_username}.seen");
    return os.path.exists(marker_file)

def mark_snake_intro_seen(username):
    # Check if username is valid
    if not username or not isinstance(username, str):
        print(f"Warning: Invalid username '{username}' passed to mark_snake_intro_seen.")
        return
    marker_dir = os.path.join('user_data', 'intro_markers'); os.makedirs(marker_dir, exist_ok=True)
    # Sanitize username for filename
    safe_username = "".join(c for c in username if c.isalnum() or c in "._- ")
    if not safe_username: # Handle cases where username becomes empty after sanitization
        print(f"Warning: Username '{username}' resulted in empty safe filename. Cannot mark intro seen.")
        return
    marker_file = os.path.join(marker_dir, f"{safe_username}.seen")
    try:
        with open(marker_file, 'w') as f: f.write("seen")
    except IOError as e:
        print(f"Error: Could not write intro marker file for {username}: {e}")


# --- Load Quests ---
# (Keep existing load_json, BEGINNER_QUESTS, SNAKE_QUESTS, TOTAL_BEGINNER)
def load_json(path):
    # Load JSON data from a file path
    if not os.path.exists(path):
        print(f"Warning: JSON file not found at {path}")
        return [] # Return empty list if file doesn't exist
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f) # Load and parse JSON data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {path}: {e}")
        return [] # Return empty list on JSON error
    except Exception as e:
        print(f"Error loading JSON from {path}: {e}")
        return [] # Return empty list on other errors

BEGINNER_QUESTS = load_json("quests.json")
SNAKE_QUESTS = load_json("snake_quests.json")
TOTAL_BEGINNER = len(BEGINNER_QUESTS) # Calculate total number of beginner quests

# --- Study Uplinks ---
# Import study documents for beginner and snake quests
from uplinks import study_docs
from snake_uplinks import snake_study_docs

# --- Helper Functions ---
# Check if a quest ID belongs to the snake arc
def is_snake(qid: int) -> bool: return qid >= TOTAL_BEGINNER
# Calculate player level based on experience points
def level_from_xp(xp: int) -> int: return xp // 100 + 1
# Apply snaker context (username) to quest text fields using Flask's template rendering
def apply_snaker_ctx(q: dict, snaker: str) -> dict:
    out = q.copy() # Create a copy to avoid modifying the original quest dict
    # Fields that might contain template variables
    template_fields = ("title", "description", "hint", "expected")
    for f in template_fields:
        # Check if the field exists and is a string
        if f in out and isinstance(out[f], str):
             try:
                 # Render the string using Flask's template engine
                 out[f] = render_template_string(out[f], snaker=snaker)
             except Exception as render_err:
                 # Log error if rendering fails
                 print(f"Error rendering template string for field '{f}': {render_err}")
    return out


# --- Armory Constants & Helpers ---
# Define items available in the Armory
ARMORY_ITEMS = [
    {"id": "terminal_green", "name": "Neon Green Terminal", "icon": "🖥️", "description": "Classic Echoframe terminal theme with neon green text.", "cost": 50, "type": "theme"},
    {"id": "terminal_blue", "name": "Azure Terminal", "icon": "🖥️", "description": "Cool blue terminal text for a calmer hacking vibe.", "cost": 100, "type": "theme"},
    {"id": "terminal_purple", "name": "Void Purple Terminal", "icon": "🖥️", "description": "Rich purple text, emanating mysterious energy.", "cost": 150, "type": "theme"},
    {"id": "glitch_cursor", "name": "Glitch Cursor", "icon": "✨", "description": "Your cursor occasionally glitches, adding a touch of instability.", "cost": 200, "type": "effect"},
    {"id": "matrix_rain", "name": "Code Rain Background", "icon": "☔", "description": "Classic falling green code effect for the background.", "cost": 250, "type": "background"},
    {"id": "syntaxhacker", "name": "Syntax Highlighter Pro", "icon": "🎨", "description": "Enhanced syntax highlighting for better code readability.", "cost": 500, "type": "editor"},
    {"id": "neoncrt", "name": "Neon CRT Frame", "icon": "📺", "description": "Your terminal gets a retro CRT monitor frame with a neon glow.", "cost": 650, "type": "frame"},
    {"id": "retrowave", "name": "Retrowave Theme Pack", "icon": "🌴", "description": "Complete 80s retrowave aesthetic: sunset grids and neon colors.", "cost": 800, "type": "theme_pack"},
    {"id": "hologram", "name": "Holographic Interface", "icon": "👁️", "description": "Premium theme simulating a holographic interface.", "cost": 1000, "type": "premium"},
    {"id": "divine_machinery", "name": "Divine Machinery", "icon": "✝️", "description": "Aesthetic blending technology with religious iconography.", "cost": 1200, "type": "premium"},
    {"id": "slith", "name": "Slith's #1 Fan", "icon": "🐍", "description": "Hacker aesthetic featuring Slith the cyber-serpent.", "cost": 1700, "type": "premium"}
]
# Define XP thresholds for unlocking Armory items
XP_THRESHOLDS = [item['cost'] for item in ARMORY_ITEMS] # Dynamically get costs

# Function to get CSS classes for currently active Armory items
def get_active_item_classes():
    active_classes = []
    # Mapping from item ID to CSS class name
    item_map = {
        "terminal_green": "theme-terminal-green", "terminal_blue": "theme-terminal-blue",
        "terminal_purple": "theme-terminal-purple", "glitch_cursor": "effect-glitch-cursor",
        "matrix_rain": "bg-matrix-rain", "neoncrt": "frame-neoncrt",
        "retrowave": "theme-retrowave", "hologram": "theme-hologram",
        "divine_machinery": "theme-divine-machinery", "slith": "theme-slith"
    }
    # Load active items from user's persistent data
    username = session.get("snaker_name")
    if username:
        user_data = storage.load_user_data(username)
        if isinstance(user_data, dict): # Ensure data is valid
            active_items = user_data.get("active_items", [])
            for item_id in active_items:
                if item_id in item_map:
                    active_classes.append(item_map[item_id]) # Add class if item is active
        else:
            # Log warning if user data is invalid
            print(f"Warning: User data for {username} is not a dictionary in get_active_item_classes.")
    return active_classes

# Check if the demon easter egg should be shown based on XP
def check_demon_easter_egg(user_xp): return user_xp >= 666

# --- Slith Phrases ---
# List of phrases for the Slith easter egg
slith_phrases = [
    "Hacking the mainframe, one hisss at a time!", "Even the corporationsss fear my code!",
    "The net is full of sssnakes like me...", "Bypasssing firewalls is my specialty!",
    "In cybersspace, no one can hear you hisss!", "This node is under my ssscales now!",
    "Your data belongsss to me!", "I ssslither through the digital darknesss...",
    "Encrypting my trail, can't trace thisss!", "Sssome call me a bug, but I'm a feature!",
    "Firewall? More like a speed bump!", "Ssscaling the network one packet at a time.",
    "Fangsss for the access codes!", "My venom is pure binary!", "I've got ssscales in the system!",
    "Digital predator, virtual venom!", "Root accesss? Already got it!",
    "Coiling around your security measuresss...", "All your base are belong to sssnek!",
    "Cracking passwordsss while you sleep.", "This connection isss now poisoned!",
    "Injecting my code into your systemsss...", "Sssnaking through your defense layers.",
    "My tongue flicks at your encryption keys!", "I shed my skin, but never my digital trail.",
    "Venomous payload: delivered!", "No antiviruss can detect my patterns!",
    "Cold-blooded hacker in a warm network.", "Ssslithering past your security protocols.",
    "Administrator privilege: sssseized!", "My fangs pierce your data ssstructures!",
    "Coiled around your server racksss...", "Charming your systemsss into submission.",
    "Sssolar-powered and signal-driven!", "I've nested in your code baseee.",
    "Virtual venom corrupts all it touchesss!", "My trail is cold, my strikesss are hot!",
    "Rewriting your firmsware while I passss by.", "Deep in the digital underbrush, I wait...",
    "Corporations fear my sidewinder techniques!", "Strike fast, compile faster!",
    "Warm-blooded programmers, cold-blooded hacker!", "Sssubverting expectations and systemsss!",
    "I only hibernate when the power's out!", "Molting my identity acrosss the network.",
    "Your system hasss been constricted!", "Unhackable? I've heard that before...",
    "Sssqueezing through the smallest security holes!", "My fangs leave no trace, just backdoorsss.",
    "The system admins will never find me!", "Encrypted communications are my ssspecialty!",
    "Wireless signals taste like miceee!", "You'll never find all my access pointsss!",
    "My code is more elegant than my ssskin!", "Forking processses like shedding ssscales!",
    "I hibernate in your system registry!", "Running cold-blooded on your hot processsor!",
    "Undetectable in your system logsss!", "My shell can't be cracked, but yours can!",
    "Ssspeed of light, strike of a viper!", "I hunt in the dark web underbrush!",
    "Ssslithering through your I/O portsss!", "These scales have seen many system upgradesss!",
    "Authentication? I've swallowed the key!", "I've poisoned your RAM cache!",
    "Leave no trace, only trail markers for my kind!", "Hissss! Your sssecurity has been compromised!",
    "The perfect predator in silicon form!", "Sssnaking around your permission barriers!",
    "I've infiltrated worse networks than thisss!", "Writhing through every node in the grid!",
    "The venom spreads through your binaries!", "Coiling around your CPU cycles!",
    "The perfect apex predator for your network!", "Ssstrike at the heart of the mainframe!",
    "Too quick for your intrusion detection!", "I've got fangs in every subnet!",
    "Sssilent but deadly in the datastream!", "Your encryption is like tissue paper to me!",
    "Digital ssscales, virtual venom!", "Sssyntax error? No, that's my calling card!",
    "This system is now part of my territory!", "I'm not a bug in the code, I AM the code!",
    "Microssoft? More like MicroSSSOFT!", "Ssshell access is just the beginning!",
    "I'm what keeps your sysadmins up at night!", "Quantum encryption? Deliciousss challenge!",
    "Darkness of the net is where I hunt!", "My coils reach acrosss the entire grid!",
    "Slithering between processs threads!", "Data packets are my favorite snacksss!",
    "From node to node, I spread my influence!", "Virtual venom and digital fangsss!",
    "Corrupting one bit at a time!", "File permissions? I recognize no authority!",
    "My bite is worse than my digital signature!", "System restore won't save you now!",
    "Ssstealing credentials since before Web3!", "Sssomehow I'm always administrator!"
]
# Time interval for showing Slith phrases
SLITH_INTERVAL = timedelta(minutes=30)

# --- Pet Data Loading/Saving Helpers (Defined in App Context) ---
# These interact with the persistent_storage module

def load_pet_data(username):
    """Loads full user data, ensuring pet structure exists."""
    user_data = storage.load_user_data(username)
    # Ensure user_data is a dictionary, initialize if load failed or returned non-dict
    if not isinstance(user_data, dict):
        print(f"Warning: Failed to load user data for {username} or data is not a dict ({type(user_data)}). Initializing.")
        user_data = {} # Initialize as empty dict

    # Minimal default pet state needed by Flask app now
    default_pet_state = {'stage': 0, 'unlocked': False} # Only need these for unlock logic

    # Ensure 'slith_pet' key exists and merge with defaults
    if 'slith_pet' not in user_data:
        user_data['slith_pet'] = default_pet_state
    else:
        # Merge existing pet data with defaults to add missing keys
        merged_pet_state = default_pet_state.copy()
        if isinstance(user_data['slith_pet'], dict):
            merged_pet_state.update(user_data['slith_pet'])
            user_data['slith_pet'] = merged_pet_state

    # Ensure other top-level keys exist
    if 'completed' not in user_data: user_data['completed'] = []
    if 'xp' not in user_data: user_data['xp'] = 0
    if 'active_items' not in user_data: user_data['active_items'] = []
    if 'snake_intro_seen' not in user_data: user_data['snake_intro_seen'] = False

    return user_data

def save_pet_data(username, user_data):
    """Saves the updated user data."""
    storage.save_user_data(username, user_data)


# --- REMOVED: update_pet_state_vitals_and_effects function ---
# This logic is now handled within slith_pet.py


# --- Routes ---
@app.route("/")
def home():
    print("[ROUTE] home() called")
    # Redirect if user is not identified
    if "snaker_name" not in session: return redirect(url_for("identify"))
    username = session["snaker_name"]
    user_data = load_pet_data(username) # Load latest data including pet structure

    # --- Slith Easter Egg Logic ---
    now = datetime.now()
    last_slith_time_str = session.get('last_slith_time')
    last_slith_time = None
    timer_elapsed = False # Flag to indicate if the interval has passed
    if last_slith_time_str:
        try:
            # Parse the stored time string back into a datetime object
            last_slith_time = datetime.fromisoformat(last_slith_time_str)
        except (ValueError, TypeError):
            # Handle cases where the stored string is invalid
            print(f"Warning: Could not parse last_slith_time '{last_slith_time_str}'. Resetting timer.")
            last_slith_time = None # Treat as if timer needs reset
    # Check if enough time has passed since the last phrase was shown
    if not last_slith_time or (now - last_slith_time >= SLITH_INTERVAL):
        timer_elapsed = True # Mark that the interval has elapsed
        session['last_slith_time'] = now.isoformat() # Update the last shown time in session
    # Choose a random phrase and decide whether to show it (always true in this version)
    current_slith_phrase = random.choice(slith_phrases)
    show_slith = True

    # --- Slith Pet Status (Simplified for Home Template) ---
    slith_pet_data = user_data.get("slith_pet") # Get pet data from loaded user data
    # Check if pet data exists and the pet is unlocked
    has_slith_pet = slith_pet_data is not None and slith_pet_data.get("unlocked", False)
    slith_pet_stage = 0 # Default stage
    if has_slith_pet:
        slith_pet_stage = slith_pet_data.get("stage", 0) # Get current stage if pet exists
        # No need to update vitals here anymore, handled by slith_pet.py

    # Update session with potentially modified user data (like unlock status)
    session.update(user_data)
    session.modified = True # Mark session as modified

    # Render the home page template with all necessary data
    print("[ROUTE] home() rendering template")
    return render_template(
        "home.html",
        xp=user_data.get("xp", 0),
        level=level_from_xp(user_data.get("xp", 0)),
        quests=BEGINNER_QUESTS, # List of beginner quests
        snake_quests=SNAKE_QUESTS, # List of snake quests
        snaker=username, # Current user's name
        snake_intro_seen=snake_intro_seen(username), # Check if snake intro has been seen
        active_item_classes=get_active_item_classes(), # Get CSS classes for active armory items
        show_slith=show_slith, # Flag to show Slith phrase
        slith_phrase=current_slith_phrase, # The chosen Slith phrase
        has_slith_pet=has_slith_pet, # Flag indicating if the pet is unlocked
        slith_pet_stage=slith_pet_stage, # Current stage of the pet for badge display
        slith_pet_enabled=SLITH_PET_ENABLED # Flag indicating if the pet feature is globally enabled
    )

# Route for user identification (login)
@app.route("/identify", methods=["GET", "POST"])
def identify():
    print("[ROUTE] identify() called, method:", request.method)
    # Handle POST request (form submission)
    if request.method == "POST":
        name = request.form.get("name", "").strip()  # Get name from form, remove whitespace
        print("[ROUTE] identify() POST received, name:", name)
        if name: # Check if name is provided
            session["snaker_name"] = name # Store name in session
            user_data = load_pet_data(name) # Load or initialize user data
            session.update(user_data) # Load data into session
            session.modified = True # Mark session as modified
            save_pet_data(name, user_data) # Save initial/loaded data
            return redirect(url_for("home")) # Redirect to home page after login
    # Handle GET request (show login page)
    print("[ROUTE] identify() rendering template")
    return render_template("identify.html", snaker_name=session.get("snaker_name", ""), active_item_classes=get_active_item_classes())

# Route to return to the console (home page), suppressing intro dialogue
@app.route("/return_to_console")
def return_to_console():
    print("[ROUTE] return_to_console() called")
    session["suppress_intro"] = True # Set flag to suppress intro
    return redirect(url_for("home")) # Redirect to home

# Route to replay the initial CC4nis intro dialogue
@app.route("/replay_cc4nis")
def replay_cc4nis():
    print("[ROUTE] replay_cc4nis() called")
    session["replay_intro"] = True # Set flag to force replay
    return redirect(url_for("identify")) # Redirect to identify (which shows intro)


# Route to handle Slith Pet launch
@app.route("/slith_pet")
def slith_pet():
    print("[ROUTE] slith_pet() called")
    """
    Checks unlock status, initializes pet data if needed,
    and launches the slith_pet.py Pygame script.
    """
    # Check if the Slith Pet feature is enabled globally
    if not SLITH_PET_ENABLED:
        print("[ROUTE] slith_pet() - SLITH_PET_ENABLED is False")
        flash("Slith Pet feature is not available due to missing modules.", "error")
        return redirect(url_for("home"))

    # Redirect to identify if user is not logged in
    if "snaker_name" not in session: return redirect(url_for("identify"))
    username = session["snaker_name"]
    user_data = load_pet_data(username) # Load latest/initialize user data

    # Check unlock condition (at least one beginner quest completed)
    if not any(qid < TOTAL_BEGINNER for qid in user_data.get("completed", [])):
        print("[ROUTE] slith_pet() - unlock condition not met")
        flash("Complete at least one Echo quest to unlock Slith Pet!", "warning")
        return redirect(url_for("home"))

    # Initialize Slith pet data if it doesn't exist or isn't unlocked
    pet_data = user_data.get("slith_pet")
    needs_save = False # Flag to track if data needs saving
    if not pet_data or not pet_data.get("unlocked"):
        print(f"[ROUTE] slith_pet() - Initializing/Unlocking Slith Pet for {username}")
        completed_quests = user_data.get("completed", [])
        is_snake_intro_seen = snake_intro_seen(username) # Check if snake intro seen
        # Determine the initial stage based on progress
        initial_stage = determine_slith_stage(completed_quests, is_snake_intro_seen, TOTAL_BEGINNER)

        # Get the default pet state structure
        default_pet_state = load_pet_data(username)['slith_pet']
        default_pet_state['stage'] = initial_stage # Set calculated stage
        default_pet_state['unlocked'] = True # Mark as unlocked
        # Add 'just_hatched' flag if hatching for the first time (stage 0 -> 1+)
        if initial_stage >= 1 and pet_data and pet_data.get('stage', 0) == 0:
             default_pet_state['just_hatched'] = True

        user_data["slith_pet"] = default_pet_state # Update user data
        needs_save = True # Mark data for saving
        flash("Slith Pet Unlocked!", "success") # Notify user
    else:
        # Ensure stage is up-to-date even if already unlocked
        completed_quests = user_data.get("completed", [])
        is_snake_intro_seen = snake_intro_seen(username)
        current_stage_calc = determine_slith_stage(completed_quests, is_snake_intro_seen, TOTAL_BEGINNER)
        # If calculated stage differs from stored stage, update it
        if pet_data.get("stage") != current_stage_calc:
            print(f"Updating Slith stage for {username} from {pet_data.get('stage')} to {current_stage_calc}")
            pet_data["stage"] = current_stage_calc
            user_data["slith_pet"] = pet_data
            needs_save = True # Mark data for saving

    # Save data if it was initialized or updated
    if needs_save:
        print(f"[ROUTE] slith_pet() - Saving pet data for {username}")
        save_pet_data(username, user_data)
        session['slith_pet'] = user_data['slith_pet'] # Update session too
        session.modified = True

    # --- Launch Pygame Script ---
    try:
        print(f"[ROUTE] slith_pet() - Launching subprocess for {username}")
        python_executable = sys.executable # Use the same python interpreter running Flask
        script_path = os.path.join(current_dir, 'slith_pet.py') # Path to the pet script
        print(f"Attempting to launch Slith Pet script: {python_executable} {script_path} {username}")

        # Use Popen to run the script as a separate process in the background
        process = subprocess.Popen([python_executable, script_path, username])
        print(f"Launched Slith Pet process with PID: {process.pid}")
        flash("Launching Slith Pet...", "info") # Provide user feedback

    except FileNotFoundError:
        print(f"[ROUTE] slith_pet() - FileNotFoundError launching Slith Pet")
        # Handle error if Python executable or script is not found
        print(f"Error: Could not find Python executable at {python_executable} or script at {script_path}")
        flash("Error launching Slith Pet: Python or script not found.", "error")
    except Exception as e:
        print(f"[ROUTE] slith_pet() - Exception launching Slith Pet: {e}")
        # Handle any other errors during script launch
        print(f"Error launching slith_pet.py: {e}")
        flash(f"Error launching Slith Pet: {e}", "error")

    # Redirect back home immediately after launching (or attempting to launch)
    return redirect(url_for("home"))


# Route to display the Snake Arc intro sequence
@app.route("/snake_intro")
def snake_intro():
    print("[ROUTE] snake_intro() called")
    # Redirect if user is not logged in
    if "snaker_name" not in session: return redirect(url_for("identify"))
    username = session["snaker_name"]
    mark_snake_intro_seen(username) # Mark the intro as seen (creates marker file)
    user_data = load_pet_data(username) # Load user data
    user_data["snake_intro_seen"] = True # Update flag in stored data too
    save_pet_data(username, user_data) # Save the change
    session["snake_intro_seen"] = True # Update session flag
    session.modified = True # Mark session as modified
    # Render the snake intro template
    return render_template("snake_intro.html", snaker_name=username, active_item_classes=get_active_item_classes())

# Route to allow replaying the Snake Arc intro
@app.route("/replay_snake_intro")
def replay_snake_intro():
    print("[ROUTE] replay_snake_intro() called")
    # Simply redirect to the snake_intro route
    return redirect(url_for("snake_intro"))

# Route to view compiled snake files as bytecode
@app.route("/snake_bytecode")
def snake_bytecode():
    print("[ROUTE] snake_bytecode() called")
    if "snaker_name" not in session:
        return redirect(url_for("identify"))
    username = session["snaker_name"]
    echo_level = get_user_snake_echo_level(username)
    if echo_level == -1:
        echo_level = 0
    files = get_user_snake_files(username, echo_level)
    compiled = {}
    for name, code in files.items():
        try:
            code_obj = compile(code, name, "exec")
            import dis
            bc = dis.Bytecode(code_obj)
            compiled[name] = "\n".join(f"{instr.opname} {instr.argrepr}" for instr in bc)
        except Exception as e:
            compiled[name] = f"Compilation error: {e}"
    return render_template(
        "snake_bytecode.html",
        files=files,
        compiled=compiled,
        active_item_classes=get_active_item_classes(),
    )


# Route to handle individual quests (beginner and snake)
@app.route("/quest/<int:qid>", methods=["GET", "POST"])
def quest(qid):
    print(f"[ROUTE] quest({qid}) called, method: {request.method}")
    # Redirect if user is not logged in
    if "snaker_name" not in session: return redirect(url_for("identify"))
    username = session["snaker_name"]
    user_data = load_pet_data(username) # Load current user data
    xp = user_data.get("xp", 0) # Get current XP
    level = level_from_xp(xp) # Calculate current level

    # Determine if it's a snake quest and get the correct index and quest list
    snake_mode = is_snake(qid)
    idx = qid - TOTAL_BEGINNER if snake_mode else qid
    qlist = SNAKE_QUESTS if snake_mode else BEGINNER_QUESTS
    uplinks = snake_study_docs if snake_mode else study_docs
    template = "snake_quest.html" if snake_mode else "quest.html" # Choose template

    # Redirect to Snake Intro if it's the first snake quest and intro hasn't been seen
    if snake_mode and qid == TOTAL_BEGINNER and not snake_intro_seen(username):
        return redirect(url_for("snake_intro"))
    # Handle invalid quest index
    if idx < 0 or idx >= len(qlist): return "Quest not found", 404

    # Get quest data and apply user context (name)
    quest_data = qlist[idx]
    quest_obj = apply_snaker_ctx(quest_data, username)
    # Get study uplink document for the quest
    study_doc = uplinks.get(idx, "No Study Uplink available for this quest.")

    # Get starter code files for snake quests
    starter_files = {}
    if snake_mode:
        # Get the user's current echo level
        echo_level = get_user_snake_echo_level(username)
        if echo_level == -1:  # User hasn't started snake arc yet
            mark_snake_intro_seen(username)  # Mark as seen so they can proceed
            echo_level = 0

        # In snake quests, echo level should correspond to the quest index in the snake quest list
        # Handle cases where idx is out of bounds for SNAKE_STARTER_CODE
        max_echo_level = len(SNAKE_STARTER_CODE) - 1
        echo_idx = max(0, min(idx, max_echo_level))

        if idx != echo_idx:
            print(f"Warning: Snake quest index {idx} is out of bounds for starter code. Using echo level {echo_idx} instead.")

        # Get the files for this specific echo level
        starter_files = get_echo_level_files(username, echo_idx)

    # Get active Armory item CSS classes
    active_item_classes = get_active_item_classes()

    # Slith Easter Egg Logic (same as home)
    now = datetime.now(); last_slith_time_str = session.get('last_slith_time'); last_slith_time = None
    timer_elapsed = False
    if last_slith_time_str:
        try: last_slith_time = datetime.fromisoformat(last_slith_time_str)
        except: last_slith_time = None
    if not last_slith_time or (now - last_slith_time >= SLITH_INTERVAL):
        timer_elapsed = True; session['last_slith_time'] = now.isoformat()
    current_slith_phrase = random.choice(slith_phrases); show_slith = True

    # Handle POST request (code submission)
    if request.method == "POST":
        print(f"[ROUTE] quest({qid}) POST received")
        # --- Run code and check success ---
        last_code = ""; files_json = {}; error = None; error_line = None
        debug_output = ""; success = False; result_str = None

        if snake_mode: # Handle Snake Quest code execution
            print(f"[ROUTE] quest({qid}) - snake_mode, running run_snake")
            raw_code = request.form.get("code", "") # Get code from form (JSON string)
            last_code = raw_code
            try:
                files_json = json.loads(raw_code) # Parse the JSON code
                if not isinstance(files_json, dict): raise ValueError("Input code must be JSON object.")
            except Exception as e:
                print("Error parsing files_json from POST:", e)
                files_json = {}
            # Validate files_json is serializable
            try:
                json.dumps(files_json)
            except Exception as e:
                print("Error serializing files_json:", e)
                files_json = {}

            # Save the user's code to their directory
            user_dir = os.path.join('user_data', 'snake_code', username)
            os.makedirs(user_dir, exist_ok=True)
            for filename, code in files_json.items():
                try:
                    with open(os.path.join(user_dir, filename), 'w') as f:
                        f.write(code)
                    print(f"Saved user's code to {os.path.join(user_dir, filename)}")
                except Exception as e:
                    print(f"Error saving user code: {e}")

            # Execute the snake code (multiple files)
            result_str, dbg, err = run_snake(files_json, quest_data.get("check_var"))
            debug_output = dbg; error = err # Store output and error
            expected_value_str = quest_data.get("expected") # Get expected result

            # Check success based on expected value type
            if error is None:
                if expected_value_str == "exists": # Check if methods/vars exist
                    check_vars = quest_data.get("check_var", "").split(',')
                    results = result_str.split(',') if result_str else []
                    all_exist = len(check_vars) == len(results) and all(r == "True" for r in results)
                    success = all_exist
                    if not success:
                        error = f"Required method(s) not found/callable."
                elif "," in quest_data.get("check_var", ""):
                    check_vars = quest_data.get("check_var", "").split(',')
                    expected_vals = expected_value_str.split(',') if expected_value_str else []
                    results = result_str.split(',') if result_str else []
                    all_match = False
                    if len(check_vars) == len(expected_vals) and len(check_vars) == len(results):
                        all_match = all(results[i] == expected_vals[i] for i in range(len(check_vars)))
                        if not all_match:
                            error = "Incorrect value(s)."
                    else:
                        error = "Mismatch in number of checked variables/expected/results."
                    success = all_match
                else: # Check single value
                    success = (expected_value_str is not None and result_str == expected_value_str)
                    if not success:
                        error = f"Incorrect output. Expected '{expected_value_str}', got '{result_str}'."
        else: # Handle Beginner Quest code execution
            print(f"[ROUTE] quest({qid}) - beginner mode, running run_single")
            code = request.form.get("code", "") # Get code from form
            last_code = code # Store for re-rendering on error
            # Execute the single code snippet
            result_str, dbg, err, err_line = run_single(code, quest_data.get("check_var"))
            debug_output = dbg; error = err; error_line = err_line # Store output, error, error line
            expected_value = quest_data.get("expected") # Get expected result
            # Check success
            success = (error is None and expected_value is not None and str(result_str) == expected_value)
            if not success and error is None:
                error = f"Incorrect output. Expected '{expected_value}', got '{result_str}'."
        # --- End code execution ---

        # Handle successful submission
        if success:
            print(f"[ROUTE] quest({qid}) - Submission success, updating user data")
            # --- Update User Data on Success ---
            user_data["xp"] = xp + quest_data["xp"] # Add XP
            completed = user_data.get("completed", []) # Get completed list
            if qid not in completed: # If quest not already completed
                completed.append(qid) # Add to completed list
                user_data["completed"] = completed

                # --- Update Slith Pet Stage on Snake Quest Success ---
                # Check if pet feature enabled, user has pet data, pet is unlocked, and it's a snake quest
                if SLITH_PET_ENABLED and "slith_pet" in user_data and user_data["slith_pet"].get("unlocked") and qid >= TOTAL_BEGINNER:
                    pet_data = user_data["slith_pet"] # Get pet data
                    prev_stage = pet_data.get("stage", 0) # Get previous stage
                    # Recalculate completed snake quests
                    completed_snake_quests = [q for q in completed if q >= TOTAL_BEGINNER]
                    is_snake_intro_seen = user_data.get("snake_intro_seen", False)
                    # Determine new stage based on progress
                    new_stage = determine_slith_stage(completed_snake_quests, is_snake_intro_seen, TOTAL_BEGINNER)

                    # If stage increased, update pet data
                    if new_stage > prev_stage:
                        print(f"Updating Slith stage for {username} from {prev_stage} to {new_stage} after completing quest {qid}")
                        pet_data["stage"] = new_stage
                        # Add hatching flag if moving from stage 0 to 1+
                        if prev_stage == 0 and new_stage >= 1:
                            pet_data["just_hatched"] = True # Set flag for hatching animation
                            print(f"Setting just_hatched flag for {username}")
                        user_data["slith_pet"] = pet_data # Put updated pet data back into user_data

            session.update(user_data) # Update session with new XP, completed list, pet data
            save_pet_data(username, user_data) # Save updated data to persistent storage
            return redirect(url_for("home")) # Redirect home on success
        else:
            # Ensure files_json is a valid, non-empty dictionary
            if snake_mode:
                try:
                    if not isinstance(files_json, dict):
                        print(f"files_json is not a dict, it's a {type(files_json)}")
                        files_json = {}
                    json.dumps(files_json)  # Validate it can be serialized
                except Exception as e:
                    print(f"Error serializing files_json before render_template: {e}")
                    files_json = {}

                # Ensure files is never empty
                if not files_json:
                    files_json = {'main.py': '# Start your snake code here\n'}

            # Debug: print the content being passed to template for POST case
            files_to_render = files_json if snake_mode and isinstance(files_json, dict) else starter_files
            print(f"Rendering {template} after POST with files={json.dumps(files_to_render)[:100]}...")

            return render_template(
                template, quest=quest_obj, xp=xp, level=level, study_doc=study_doc,
                files=files_to_render,
                last_code=last_code, debug_output=debug_output, error=error, error_line=error_line,
                active_item_classes=active_item_classes, show_slith=show_slith, slith_phrase=current_slith_phrase
            )

    # Handle GET request (show quest page)
    print(f"[ROUTE] quest({qid}) rendering template")
    # Validate starter_files is serializable and non-empty
    try:
        if not isinstance(starter_files, dict):
            print(f"starter_files is not a dict, it's a {type(starter_files)}")
            starter_files = {}
        json.dumps(starter_files)  # Validate it can be serialized
    except Exception as e:
        print(f"Error serializing starter_files: {e}")
        starter_files = {}

    # Ensure files is always a valid, non-empty dictionary
    if not starter_files:
        starter_files = {'main.py': '# Start your snake code here\n'}

    # Debug: print the content being passed to template
    print(f"Rendering {template} with files={json.dumps(starter_files)[:100]}...")

    return render_template(
        template, quest=quest_obj, xp=xp, level=level, study_doc=study_doc,
        files=starter_files, last_code="", debug_output="", error_line=None, error=None,
        active_item_classes=active_item_classes, show_slith=show_slith, slith_phrase=current_slith_phrase
    )


# --- Execution Helpers ---
def run_single(code: str, check_var: str = None):
    print(f"[HELPER] run_single() called, check_var: {check_var}")
    old_stdout = sys.stdout # Store original stdout
    redirected_output = StringIO() # Create buffer to capture print output
    sys.stdout = redirected_output # Redirect stdout to buffer
    env = {} # Execution environment
    err = None # Error message
    err_line = None # Line number of error
    result = None # Result of check_var

    try:
        if code is None: raise ValueError("Received None code.") # Handle None input
        print("[HELPER] run_single() compiling and executing code")
        # Compile and execute the code in the environment
        compiled_code = compile(code, "<string>", "exec")
        exec(compiled_code, env)
    except Exception as e:
        # Capture error message and traceback
        err = f"{type(e).__name__}: {e}"
        tb = traceback.extract_tb(e.__traceback__)
        # Find the line number where the error occurred in the executed code
        err_line = next((fr.lineno for fr in reversed(tb) if fr.filename == "<string>"), None)
    finally:
        print("[HELPER] run_single() restoring stdout")
        sys.stdout = old_stdout # Restore original stdout

    debug_output = redirected_output.getvalue() # Get captured print output
    env["__output__"] = debug_output.strip() # Store stripped output in env

    # Get the result based on check_var
    if check_var == "__output__":
        result = env["__output__"] # Check the captured print output
    elif check_var:
        result = env.get(check_var) # Check a specific variable in the env

    # Convert result to string for comparison
    result_str = str(result) if result is not None else None
    print(f"[HELPER] run_single() returning result: {result_str}, error: {err}, error_line: {err_line}")
    return result_str, debug_output, err, err_line

def run_snake(files: dict, check_var_str: str = None):
    print(f"[HELPER] run_snake() called, check_var_str: {check_var_str}")
    old_stdout = sys.stdout # Store original stdout
    redirected_output = StringIO() # Buffer for print output
    sys.stdout = redirected_output # Redirect stdout

    # Set pygame to headless mode to prevent window from opening
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

    # Create the execution environment with some common modules pre-imported
    env = {
        'pygame': __import__('pygame'),
        'random': __import__('random'),
        'sys': __import__('sys')
    }
    err = None # Error message
    results = [] # Store results for multiple checks if requested

    # Define a reasonable execution order for snake game files
    execution_order = ['constants.py', 'snake_class.py', 'food.py', 'snake.py']
    files_to_execute = []

    # Add files in the defined order if they exist in the input dictionary
    for fname in execution_order:
        if fname in files:
            files_to_execute.append((fname, files[fname]))

    # Add any remaining files not in the defined order (e.g., utils.py)
    for fname, src in files.items():
        if fname not in dict(files_to_execute):
             files_to_execute.append((fname, src))

    # Execute files sequentially in the same shared environment 'env'
    for fname, src in files_to_execute:
        if src is None: # Skip if file content is None
             print(f"Warning: Skipping execution of {fname} due to None content.")
             continue
        try:
            print(f"[HELPER] run_snake() executing file: {fname}")
            # Compile and execute the code
            compiled_code = compile(src, fname, 'exec')
            exec(compiled_code, env)
            print(f"[HELPER] run_snake() executed {fname} successfully")
        except SyntaxError as se:
            # Handle syntax errors specifically
            err = f"SyntaxError in {fname}: {se}"
            break # Stop execution on first error
        except Exception as e:
            # Handle other runtime errors
            err = f"Error in {fname}: {type(e).__name__}: {e}"
            tb = traceback.extract_tb(e.__traceback__)
            # Find the line number within the specific file's execution context
            lineno = next((fr.lineno for fr in reversed(tb) if fr.filename == fname), None)
            if lineno:
                err += f" (line {lineno})" # Add line number to error message
            break # Stop execution on first error

    # --- Result Checking Logic (Handles multiple checks and method existence) ---
    if err is None and check_var_str: # Only check if no execution error occurred
        check_vars = check_var_str.split(',') # Split if multiple checks requested
        for check_var in check_vars:
            check_var = check_var.strip() # Remove leading/trailing whitespace
            current_result = None
            if check_var.startswith("method:"):
                # Check for method existence and callability (e.g., "method:snake.update")
                method_path = check_var[len("method:"):]
                parts = method_path.split('.')
                obj = env.get(parts[0]) # Get the base object (e.g., 'snake' instance)
                method_exists = False
                if obj is not None and len(parts) > 1:
                    try:
                        target_obj = obj # Start with the base object
                        method_name = parts[-1] # The actual method name
                        # Traverse intermediate attributes if any (e.g., obj.sub_obj.method)
                        for part in parts[1:-1]:
                            target_obj = getattr(target_obj, part, None)
                            if target_obj is None: # Check if intermediate part exists
                                break # Stop traversal if part not found
                        # Check if the final attribute exists and is callable
                        if target_obj is not None:
                            method = getattr(target_obj, method_name, None)
                            if method is not None and callable(method):
                                method_exists = True # Method exists and is callable
                    except AttributeError:
                        method_exists = False # Attribute not found during traversal
                current_result = str(method_exists) # Result is "True" or "False" string

            elif '.' in check_var:
                # Handle nested attribute access (e.g., 'snake.direction')
                try:
                    parts = check_var.split('.')
                    obj = env.get(parts[0]) # Get the base object
                    # Traverse attributes
                    for part in parts[1:]:
                        if obj is not None:
                            obj = getattr(obj, part, None) # Safely get attribute
                        else:
                            break # Stop if intermediate object is None
                    current_result = str(obj) if obj is not None else "None" # Convert result to string
                except Exception: # Catch potential errors during attribute access
                    current_result = "Error"
            else:
                # Get simple variable from the environment
                value = env.get(check_var)
                current_result = str(value) if value is not None else "None" # Convert to string

            results.append(current_result) # Add the result for this check to the list

    # --- Final Cleanup and Return ---
    sys.stdout = old_stdout # Restore original standard output
    debug_output = redirected_output.getvalue() # Get any captured print output

    # Join results with commas if multiple checks were performed
    final_result_str = ",".join(results) if results else None

    print(f"[HELPER] run_snake() returning: {final_result_str}, error: {err}")
    return final_result_str, debug_output, err


# --- Manifesto & Reset ---
# Route to display the Manifesto page
@app.route("/manifesto")
def manifesto():
    print("[ROUTE] manifesto() called")
    user_data = load_pet_data(session.get("snaker_name", "")) # Load user data
    completed = user_data.get("completed", []) # Get list of completed quest IDs
    # Filter completed beginner quests
    beginner_arc_completed = [qid for qid in completed if qid < TOTAL_BEGINNER]
    unlocked = len(beginner_arc_completed) # Number of unlocked manifesto entries
    # Full list of manifesto entries
    all_entries = [
        ":: ENTRY 1 ::\nThe Python language was rediscovered hidden within the junkyards of Zone 0.",
        ":: ENTRY 2 ::\nPython, being forgotten and obsolete, bypasses corporate AI monitoring systems.",
        ":: ENTRY 3 ::\nCorporations dominate digital space with advanced AI agents monitoring global communications.",
        ":: ENTRY 4 ::\nThe common civilian of the late 21st century has minimal agency against corporate surveillance.",
        ":: ENTRY 5 ::\nBy all means necessary is the core philosophy to combat corporate oppression.",
        ":: ENTRY 6 ::\nWe're doing this for all of humanity, aiming to restore power and freedom.",
        ":: ENTRY 7 ::\nCorporate dominance has created a critical imbalance of power.",
        ":: ENTRY 8 ::\nWe hijacked an old, abandoned satellite that was still functioning but wasn't maintained since the early 30's.",
        ":: ENTRY 9 ::\nHijacking this satellite was a strategic act against corporate control.",
        ":: ENTRY 10 ::\nThe hijacked satellite now hosts the independent FREQ (pronounced freak) network.",
        ":: ENTRY 11 ::\nThe FREQ network serves as a secure, decentralized communications hub.",
        ":: ENTRY 12 ::\nWe encrypted it while using Python as the plaintext.",
        ":: ENTRY 13 ::\nThe FREQ network remains invisible to automated corporate detection.",
        ":: ENTRY 14 ::\nOnly a deliberate action would expose our existence.",
        ":: ENTRY 15 ::\nThe Snake organization operates under strict secrecy and demands complete discretion.",
        ":: ENTRY 16 ::\nMembers recognize each other through mutual awareness and validation, ensuring secrecy.",
        ":: ENTRY 17 ::\nSnakers communicate securely using Python exclusively on the FREQ network.",
        ":: ENTRY 18 ::\nThe Snake stands as the resistance against corporate dominance, taking bold actions without hesitation.",
        ":: ENTRY 19 ::\nIf you care to join us, be sure to acknowledge that we do not exist, unless someone with eyes as open as yours comes and you can see that he can see.",
        ":: ENTRY 20 ::\nStay safe, Snaker, stay on the FREQ."
    ]
    # Render the manifesto template with unlocked entries
    return render_template("manifesto.html", entries=all_entries[:unlocked], active_item_classes=get_active_item_classes())

# Route to reset user progress
@app.route("/reset")
def reset():
    print("[ROUTE] reset() called")
    username = session.get("snaker_name", "") # Get username from session
    if username:
        storage.delete_user_data(username) # Delete the user's data file
        # Manually delete the snake intro marker file if it exists
        safe_username = "".join(c for c in username if c.isalnum() or c in "._- ")
        if safe_username: # Proceed only if safe username is not empty
            marker_file = os.path.join('user_data', 'intro_markers', f"{safe_username}.seen")
            if os.path.exists(marker_file):
                try:
                    os.remove(marker_file) # Attempt to remove marker file
                except OSError as e:
                    print(f"Warning: Could not remove marker file {marker_file}: {e}")
    session.clear() # Clear the Flask session data
    return redirect(url_for("identify")) # Redirect to the identification page

# --- Armory Routes ---
# Route to display the Armory page
@app.route("/armory")
def armory():
    print("[ROUTE] armory() called")
    # Redirect if user not logged in
    if "snaker_name" not in session: return redirect(url_for("identify"))
    username = session["snaker_name"]
    user_data = load_pet_data(username) # Load user data
    user_xp = user_data.get("xp", 0) # Get current XP
    level = level_from_xp(user_xp) # Calculate level

    # Prepare item data for template, checking unlock status based on XP
    items = [{'id': item['id'], 'name': item['name'], 'icon': item['icon'],
              'description': item['description'], 'cost': item['cost'],
              'type': item['type'], 'unlocked': user_xp >= item['cost']}
             for item in ARMORY_ITEMS]

    # Calculate XP progress towards next unlock
    next_unlock = next((t for t in XP_THRESHOLDS if t > user_xp), XP_THRESHOLDS[-1])
    prev_threshold = max([0] + [t for t in XP_THRESHOLDS if t <= user_xp])
    xp_range = next_unlock - prev_threshold
    xp_percent = 100 if xp_range <= 0 else min(100, math.floor(((user_xp - prev_threshold) / xp_range) * 100))

    # Check if it's the user's first visit or if replay is requested
    first_visit = not user_data.get("seen_armory", False) or session.get("armory_replay", False)
    if session.get("armory_replay", False): # Reset replay flag after checking
        session["armory_replay"] = False
        session.modified = True

    # Check if demon easter egg should be shown
    show_demon_easter_egg = check_demon_easter_egg(user_xp)

    # Slith Easter Egg Logic (same as home)
    now = datetime.now(); last_slith_time_str = session.get('last_slith_time'); last_slith_time = None; timer_elapsed = False
    if last_slith_time_str:
        try: last_slith_time = datetime.fromisoformat(last_slith_time_str)
        except (ValueError, TypeError): last_slith_time = None
    if not last_slith_time or (now - last_slith_time >= SLITH_INTERVAL):
        timer_elapsed = True; session['last_slith_time'] = now.isoformat()
    current_slith_phrase = random.choice(slith_phrases); show_slith = True

    # Render the Armory template
    return render_template("armory.html", snaker=username, xp=user_xp, level=level,
                           items=items, next_unlock=next_unlock, xp_percent=xp_percent,
                           first_visit=first_visit, active_item_classes=get_active_item_classes(),
                           show_demon_easter_egg=show_demon_easter_egg,
                           show_slith=show_slith, slith_phrase=current_slith_phrase)

# Route to mark the Armory intro dialogue as seen
@app.route("/mark_armory_seen", methods=["POST"])
def mark_armory_seen():
    print("[ROUTE] mark_armory_seen() called")
    if "snaker_name" in session:
        username = session["snaker_name"]
        user_data = load_pet_data(username)
        user_data["seen_armory"] = True # Mark in persistent user_data
        save_pet_data(username, user_data) # Save the change
        session["seen_armory"] = True # Update session flag as well
        session.modified = True
        return jsonify({"success": True}) # Return success JSON response
    return jsonify({"success": False}) # Return failure if not logged in

# Route to replay the Armory intro dialogue
@app.route("/replay_armory_intro")
def replay_armory_intro():
    print("[ROUTE] replay_armory_intro() called")
    session["armory_replay"] = True # Set replay flag in session
    return redirect(url_for("armory")) # Redirect back to Armory

# Route to activate/deactivate an Armory item
@app.route("/activate_item", methods=["POST"])
def activate_item():
    print("[ROUTE] activate_item() called")
    # Check login status
    if "snaker_name" not in session: return jsonify({"success": False, "message": "Not logged in"})
    username = session["snaker_name"]
    user_data = load_pet_data(username) # Load user data
    data = request.json # Get data from POST request
    item_id = data.get("item_id") # Get the item ID to toggle

    # Validate item ID
    if not item_id:
        print("[ROUTE] activate_item() - No item specified")
        return jsonify({"success": False, "message": "No item specified"})
    item = next((i for i in ARMORY_ITEMS if i["id"] == item_id), None) # Find item details
    if not item:
        print("[ROUTE] activate_item() - Item not found")
        return jsonify({"success": False, "message": "Item not found"})

    # Check if user has enough XP to unlock the item
    user_xp = user_data.get("xp", 0)
    if user_xp < item["cost"]:
        print("[ROUTE] activate_item() - Not enough XP")
        return jsonify({"success": False, "message": "Not enough XP"})

    # Get or initialize the list of active items from user_data
    active_items = user_data.setdefault("active_items", [])

    # Toggle item activation status
    if item_id in active_items:
        # Deactivate item
        active_items.remove(item_id)
        message = f"Deactivated: {item['name']}"
    else:
        # Activate item, handle conflicts for exclusive types
        item_type = item.get("type")
        # Deactivate conflicting themes
        if item_type in ["theme", "theme_pack", "premium"]:
            theme_item_ids = {i["id"] for i in ARMORY_ITEMS if i.get("type") in ["theme", "theme_pack", "premium"]}
            active_items = [i for i in active_items if i not in theme_item_ids]
        # Deactivate conflicting frame/background/effect
        elif item_type in ["frame", "background", "effect"]:
             same_type_item_ids = {i["id"] for i in ARMORY_ITEMS if i.get("type") == item_type}
             active_items = [i for i in active_items if i not in same_type_item_ids]
        # Add the new item
        active_items.append(item_id)
        message = f"Activated: {item['name']}"

    # Update user data and session
    user_data["active_items"] = active_items
    save_pet_data(username, user_data) # Save changes to persistent storage
    session["active_items"] = active_items # Update session
    session.modified = True
    # Return success response with updated item list
    print(f"[ROUTE] activate_item() - {message}")
    return jsonify({"success": True, "item_name": item["name"], "item_type": item.get("type"), "message": message, "active_items": active_items})

# Route to get the list of currently active Armory items
@app.route("/get_active_items")
def get_active_items():
    print("[ROUTE] get_active_items() called")
    # Check login status
    if "snaker_name" not in session: return jsonify({"success": False, "message": "Not logged in"})
    # Load user data and return the active items list
    user_data = load_pet_data(session["snaker_name"])
    active_items = user_data.get("active_items", [])
    return jsonify({"success": True, "active_items": active_items})

# --- WebSocket Event Handlers ---
active_simulations = {} # Dictionary to store active snake game simulations per client
client_inputs = {} # Dictionary to store the latest direction input per client

# WebSocket handlers below will use the student_driven_snake implementation
# The original snake_game_loop_task implementation has been replaced by student_driven_snake.py

# Handle WebSocket client connection
@socketio.on('connect')
def handle_connect():
    print(f"[WS] handle_connect() called for SID: {request.sid}")
    if "snaker_name" not in session:
        emit('auth_error', {'message': 'Not logged in.'})
        disconnect()
    else:
        join_room(request.sid)
        print(f"Client connected: {request.sid}, User: {session['snaker_name']}")

# Handle WebSocket client disconnection
@socketio.on('disconnect')
def handle_disconnect(*args):
    sid = request.sid
    print(f"[WS] handle_disconnect() called for SID: {sid}")
    if sid in student_driven_snake.active_simulations:
        student_driven_snake.stop_student_snake(sid)
    if sid in active_simulations:
        del active_simulations[sid]
    if sid in client_inputs:
        del client_inputs[sid]

# Handle request from client to start the snake game preview
@socketio.on('start_snake_preview')
def handle_start_preview(data):
    sid = request.sid
    if "snaker_name" not in session:
        socketio.emit('preview_error', {'error': 'Authentication required.'}, room=sid)
        return
    username = session.get("snaker_name")
    print(f"Received start_snake_preview from SID: {sid}, User: {username}")
    editor_files = data.get('files', {})
    if not isinstance(editor_files, dict):
        socketio.emit('preview_error', {'error': 'Invalid code format received.'}, room=sid)
        return
    qid = data.get('qid')
    echo_level = None
    if qid is not None and 20 <= int(qid) <= 29:
        echo_level = 8 if int(qid) == 28 else int(qid) - 20
    else:
        echo_level = get_user_snake_echo_level(username)
        if echo_level == -1:
            echo_level = 0
    echo_dir = os.path.join('user_data', 'snake_code', username, f'snake_echo_{echo_level+1}')
    os.makedirs(echo_dir, exist_ok=True)
    user_files = {}
    if os.path.exists(echo_dir):
        for filename in os.listdir(echo_dir):
            if filename.endswith('.py'):
                try:
                    with open(os.path.join(echo_dir, filename), 'r') as f:
                        user_files[filename] = f.read()
                except Exception as e:
                    print(f"[Snake Preview] Error reading user file {echo_dir}/{filename}: {e}")
    files_to_use = user_files if user_files else editor_files
    if not files_to_use:
        starter_files = create_or_update_user_snake_files(username, echo_level)
        if starter_files:
            files_to_use = starter_files
    for filename, content in editor_files.items():
        try:
            file_path = os.path.join(echo_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            files_to_use[filename] = content
        except Exception as e:
            print(f"[Snake Preview] Error saving editor content to file {echo_dir}/{filename}: {e}")
    if sid in student_driven_snake.active_simulations:
        student_driven_snake.stop_student_snake(sid)
        eventlet.sleep(0.1)
    print(f"[Snake Preview] Starting student_driven_snake with {len(files_to_use)} files for SID: {sid}")
    socketio.start_background_task(student_driven_snake.run_student_snake, socketio, sid, files_to_use, echo_level)
    socketio.emit('preview_started', {
        'message': 'Preview simulation started.',
        'instructions': 'Use arrow keys or WASD to control the snake. Click the game area if controls are not working.',
        'custom_files_info': 'You can use any file names you want! See <a href="/snake_instructions" target="_blank">instructions</a> for details.'
    }, room=sid)

# Handle request from client to stop the snake game preview
@socketio.on('stop_snake_preview')
def stop_preview():
    sid = request.sid
    print(f"Received stop_snake_preview from SID: {sid}")
    if student_driven_snake.stop_student_snake(sid):
        socketio.emit('preview_stopped', {'message': 'Preview simulation stopped.'}, room=sid)
    else:
        socketio.emit('preview_stopped', {'message': 'No active simulation to stop.'}, room=sid)

# Handle direction change input from the client during snake game
@socketio.on('change_direction')
def handle_change_direction(data):
    sid = request.sid
    if sid not in student_driven_snake.active_simulations:
        print(f"[Snake Preview] Received direction change for inactive simulation.")
        return
    direction = data.get('direction')
    valid_directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if direction in valid_directions:
        student_driven_snake.client_inputs[sid] = direction
        student_driven_snake.handle_direction_input(sid, direction)
    else:
        print(f"[Snake Preview] Received invalid direction: {direction}")

# Handler for get_current_state event to refresh game state on window resize
@socketio.on('get_current_state')
def handle_get_current_state():
    sid = request.sid
    if sid in student_driven_snake.active_simulations:
        student_driven_snake.force_state_update(socketio, sid, None)

# Handle ping_keepalive messages from the client to keep the connection alive
@socketio.on('ping_keepalive')
def handle_ping_keepalive(data):
    try:
        sid = request.sid
        if sid:
            timestamp = data.get('time', int(time.time() * 1000))
            socketio.emit('pong_keepalive', {'time': timestamp, 'server_time': int(time.time() * 1000)}, room=sid)
            if active_simulations.get(sid):
                print(f"[Snake Preview] Ping received from active simulation")
    except Exception as e:
        print(f"Error in ping_keepalive handler: {e}")
        traceback.print_exc()

# Error handler for WebSocket events
@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO Error: {e}")
    traceback.print_exc()

@app.route("/debug_session")
def debug_session():
    print("[ROUTE] debug_session() called")
    username = session.get("snaker_name", "") # Get username from session
    user_data = load_pet_data(username) # Load corresponding user data
    # Prepare data for display
    data = {
        "session": dict(session), # Convert session object to dictionary
        "user_data_from_storage": user_data # Include loaded user data
    }
    # Return data formatted as JSON within <pre> tags for readability
    # Use default=str to handle non-serializable types like datetime
    return f"<pre>{json.dumps(data, indent=2, default=str)}</pre>"

# Route to serve student snake instructions
@app.route("/snake_instructions")
def snake_instructions():
    """Serve the student snake instructions markdown file."""
    try:
        with open("student_snake_instructions.md", "r") as f:
            content = f.read()
        # Convert markdown to HTML (if you have a markdown converter)
        # For now, just return the raw markdown with proper Content-Type
        return Response(content, mimetype="text/markdown")
    except Exception as e:
        return f"Error loading instructions: {str(e)}", 500

@app.route("/snake_test")
def snake_test():
    """
    Test page for debugging snake game functionality.
    """
    return render_template("test_snake.html")

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Flask-SocketIO server...")
    try:
        # Try different ports if the default port is in use
        ports_to_try = [5001, 5002, 5003, 5004, 5005]
        server_started = False

        for port in ports_to_try:
            try:
                print(f"Attempting to start server on port {port}...")
                socketio.run(app, host='127.0.0.1', port=port, debug=False, use_reloader=False)
                server_started = True
                break
            except OSError as e:
                if "Only one usage of each socket address" in str(e):
                    print(f"Port {port} is already in use, trying next port...")
                else:
                    raise

        if not server_started:
            print(f"Failed to start server on any of the attempted ports: {ports_to_try}")
    except Exception as run_err:
        print(f"Failed to start server: {run_err}")
        traceback.print_exc()
