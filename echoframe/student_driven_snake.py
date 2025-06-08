"""
student_driven_snake.py - The primary game implementation that students will modify.

This file contains a working snake game that mirrors what students build in the echoes.
The implementation follows the EchoFrame pedagogical approach where students control
the game loop and game logic directly in their code rather than having it managed by the backend.
"""
import pygame
import sys
import random
import os
import time
import traceback
import importlib
import shutil
import tempfile
from io import StringIO
import eventlet
from flask_socketio import emit
from flask import request
import types
import builtins
import inspect
import threading
import importlib.util
import json
import multiprocessing

# Custom exception for file loading
class FileLoadedException(Exception):
    """Exception raised when files are loaded in a special way."""
    pass

# Dictionary to track active simulations by session ID
active_simulations = {}
# Dictionary to store client input by session ID
client_inputs = {}
# Dictionary to store student namespace by session ID
student_namespaces = {}
# Global socketio reference for use in handlers
global_socketio = None

# --- Constants ---
# These constants are the default values that will be used if not defined in student's code
CELL_SIZE = None
GRID_WIDTH = None
GRID_HEIGHT = None
SCREEN_WIDTH = None
SCREEN_HEIGHT = None

# Colors
BLACK = None
WHITE = None
GREEN = None
RED = None
BLUE = None
YELLOW = None
GRAY = None
GREY = None

# Game settings
FPS = None
FONT_SIZE = None
SNAKE_SPEED = None

# Direction constants
UP = None
DOWN = None
LEFT = None
RIGHT = None

# Element colors
SNAKE_COLOR = None
FOOD_COLOR = None
BG_COLOR = None
BACKGROUND_COLOR = None

# Position constants
CENTER = None
SCORE_POS = None
GAME_OVER_POS = None
RESTART_TEXT_POS = None
FINAL_SCORE_POS = None
TOP_LEFT = None
TOP_RIGHT = None
BOTTOM_LEFT = None
BOTTOM_RIGHT = None

# Text constants
GAME_OVER_TEXT = 'GAME OVER'
RESTART_TEXT = 'Press SPACE to restart'
SMALL_FONT_SIZE = 24
MEDIUM_FONT_SIZE = 36
LARGE_FONT_SIZE = 72
TEXT_COLOR = WHITE
GAME_OVER_COLOR = RED
BORDER_COLOR = WHITE

# Key constants - pygame key constants for easier student access
K_UP = 273  # pygame.K_UP
K_DOWN = 274  # pygame.K_DOWN
K_LEFT = 276  # pygame.K_LEFT
K_RIGHT = 275  # pygame.K_RIGHT
K_SPACE = 32  # pygame.K_SPACE
K_RETURN = 13  # pygame.K_RETURN
K_ESCAPE = 27  # pygame.K_ESCAPE

# Function to get the directory for a user's snake files
def get_user_snake_dir(username, echo_level=None, create=True):
    """
    Get the directory for a user's snake files.

    Args:
        username: The username of the snaker
        echo_level: Optional integer representing the echo level (0-9).
                   If provided, return the directory for that echo level.
        create: Boolean, whether to create the directory if it doesn't exist

    Returns:
        Path to the user's snake code directory or echo-specific directory
    """
    base_dir = os.path.join('user_data', 'snake_code')
    user_dir = os.path.join(base_dir, username)

    if create and not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)

    # If echo level is provided, get the echo-specific directory
    if echo_level is not None and 0 <= echo_level < 10:
        echo_dir = os.path.join(user_dir, f'snake_echo_{echo_level+1}')
        if create and not os.path.exists(echo_dir):
            os.makedirs(echo_dir, exist_ok=True)
        return echo_dir

    return user_dir

# Custom module mock for pygame to prevent window opening
class MockPygame:
    """Mock pygame module to prevent window opening in preview mode."""
    class Surface:
        def __init__(self, size):
            self.size = size

        def fill(self, color):
            pass

        def blit(self, source, dest, area=None, special_flags=0):
            pass

    class Rect:
        def __init__(self, left, top, width, height):
            self.left = left
            self.top = top
            self.width = width
            self.height = height
            self.size = (width, height)
            self.topleft = (left, top)

        def colliderect(self, rect):
            return False

        def move(self, x, y):
            return MockPygame.Rect(self.left + x, self.top + y, self.width, self.height)

    class Event:
        def __init__(self, type, **kwargs):
            self.type = type
            for key, value in kwargs.items():
                setattr(self, key, value)

    class MockDraw:
        def rect(self, surface, color, rect, width=0):
            pass

        def circle(self, surface, color, center, radius, width=0):
            pass

        def line(self, surface, color, start_pos, end_pos, width=1):
            pass

    class MockDisplay:
        def set_mode(self, size, flags=0, depth=0, display=0, vsync=0):
            return MockPygame.Surface(size)

        def set_caption(self, caption):
            pass

        def flip(self):
            pass

        def update(self, *args):
            pass

    class MockTime:
        def Clock(self):
            return type('MockClock', (), {
                'tick': lambda fps: time.sleep(1/fps),
                'get_fps': lambda: 30
            })

    class MockFont:
        def __init__(self):
            pass

        def init(self):
            pass

        def SysFont(self, name, size):
            return type('MockFont', (), {
                'render': lambda text, antialias, color: MockPygame.Surface((100, 30))
            })

    class MockEvent:
        def get(self, *args, **kwargs):
            events = []
            return events

    # Constants
    QUIT = 12
    KEYDOWN = 2
    K_UP = 273
    K_DOWN = 274
    K_LEFT = 276
    K_RIGHT = 275
    K_SPACE = 32

    # Create instances of our mock classes
    display = MockDisplay()
    draw = MockDraw()
    time = MockTime()
    font = MockFont()
    event = MockEvent()

    def init(self=None):
        return 6, 0

    def quit(self=None):
        pass

# Function to determine the echo level based on files
def _determine_echo_level(files):
    """Determine which echo level the student is at based on their code."""
    echo_level = 0

    # Check for constants definition (Echo 1)
    for _, code in files.items():
        if 'GRID_WIDTH' in code and 'GRID_HEIGHT' in code and 'CELL_SIZE' in code:
            echo_level = max(echo_level, 1)

    # Check for game loop (Echo 2)
    for _, code in files.items():
        if 'pygame.init()' in code and 'while' in code and 'pygame.display.flip()' in code:
            echo_level = max(echo_level, 2)

    # Check for Snake class (Echo 3)
    for _, code in files.items():
        if 'class Snake' in code:
            echo_level = max(echo_level, 3)

    # Check for draw method (Echo 4)
    for _, code in files.items():
        if 'class Snake' in code and 'def draw' in code and 'pygame.draw.rect' in code:
            echo_level = max(echo_level, 4)

    # Check for Food class (Echo 5)
    for _, code in files.items():
        if 'class Food' in code:
            echo_level = max(echo_level, 5)

    # Check for snake growth (Echo 6)
    for _, code in files.items():
        if ('grow' in code or 'eat' in code) and 'food' in code.lower():
            echo_level = max(echo_level, 6)

    # Check for input handling (Echo 7)
    for _, code in files.items():
        if 'pygame.K_UP' in code or 'pygame.K_DOWN' in code:
            echo_level = max(echo_level, 7)

    # Check for collision detection (Echo 8)
    for _, code in files.items():
        if ('collision' in code or 'collide' in code) and ('wall' in code or 'self' in code):
            echo_level = max(echo_level, 8)

    # Check for game over (Echo 9)
    for _, code in files.items():
        if 'game over' in code.lower() or 'gameover' in code.lower() or 'restart' in code.lower():
            echo_level = max(echo_level, 9)

    return echo_level

# Functions to manage built-in constants
def _setup_builtins_constants(global_dict):
    """Add game constants to builtins so they're available in all modules."""
    for name, value in global_dict.items():
        if name.isupper():
            setattr(builtins, name, value)

def _cleanup_builtins_constants(global_dict):
    """Remove game constants from builtins."""
    for name in global_dict:
        if name.isupper() and hasattr(builtins, name):
            delattr(builtins, name)

# Function to stop the snake game for a session
def stop_student_snake(sid):
    """Stop the snake game for a specific session."""
    if sid in active_simulations:
        print(f"Stopping student snake game for session {sid}")
        active_simulations[sid] = False
        if sid in student_namespaces:
            del student_namespaces[sid]
        if sid in client_inputs:
            del client_inputs[sid]
        return True
    return False

# Function to handle direction input from client
def handle_direction_input(sid, direction):
    """Handle direction input from the client."""
    if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        client_inputs[sid] = direction  # Update client_inputs with the valid direction
        print(f"[{sid}] client_inputs for SID {sid} updated to: {direction}") # Log the update

        if sid not in active_simulations or not active_simulations.get(sid):
            print(f"[{sid}] INFO: Direction input '{direction}' processed by handle_direction_input. Simulation was not marked as 'active' in active_simulations dictionary (or SID not found). client_inputs still updated.")
        else:
            print(f"[{sid}] INFO: Direction input '{direction}' processed by handle_direction_input for an active simulation.")
            # Optional: Keep the debug direct manipulation attempt for logging if useful,
            # but it's understood this doesn't directly affect student_process.
            if sid in student_namespaces and 'snake' in student_namespaces[sid]:
                snake_obj = student_namespaces[sid].get('snake')
                if hasattr(snake_obj, 'direction'):
                    print(f"[{sid}] DEBUG_DIRECT_MANIP: current snake_obj.direction in namespace: {getattr(snake_obj, 'direction', 'N/A')}")
                # else:
                #     print(f"[{sid}] DEBUG_DIRECT_MANIP: snake_obj in namespace has no 'direction' attribute.")
            # else:
            #     print(f"[{sid}] DEBUG_DIRECT_MANIP: No 'snake' obj in student_namespaces for SID {sid}.")

        return True # Return True because a valid direction was received and stored in client_inputs
    else:
        print(f"[{sid}] Invalid direction received in handle_direction_input: {direction}")
        return False # Invalid direction string

# Function to send game state updates
def send_game_state_update(socketio, sid, game_state):
    """Send game state update to the client."""
    try:
        socketio.emit('game_state_update', game_state, room=sid)
    except Exception as e:
        print(f"Error sending game state update: {e}")

# Define a helper function to determine echo level
def determine_echo_level(sid, username, socketio_instance=None):
    """Determine the echo level for a user.

    Args:
        sid: The socket ID
        username: The username if available
        socketio_instance: The socketio instance if available

    Returns:
        int: The echo level (1-10)
    """
    echo_level = None
    socketio_to_use = socketio_instance or global_socketio

    print(f"[{sid}] DEBUG: Determining echo level...")

    # Direct mapping from quest ID to echo level
    quest_to_echo = {
        20: 1,  # Quest 20 = Echo 1
        21: 2,  # Quest 21 = Echo 2
        22: 3,  # Quest 22 = Echo 3
        23: 4,  # Quest 23 = Echo 4
        24: 5,  # Quest 24 = Echo 5
        25: 6,  # Quest 25 = Echo 6
        26: 7,  # Quest 26 = Echo 7
        27: 8,  # Quest 27 = Echo 8
        28: 9,  # Quest 28 = Echo 9
        29: 10  # Quest 29 = Echo 10
    }

    # Method 1: From app function - most reliable if username is available
    if username:
        try:
            from app import get_user_snake_echo_level
            echo_level = get_user_snake_echo_level(username)
            print(f"[{sid}] Retrieved echo level for {username}: {echo_level}")
            if echo_level is not None and echo_level >= 0:
                return echo_level + 1  # Convert 0-based to 1-based
        except Exception as e:
            print(f"[{sid}] Error getting echo level from app: {e}")

    # Method 2: Extract quest ID from request context if available
    try:
        from flask import has_request_context, request
        if has_request_context():
            # Get path from request
            path = request.path
            print(f"[{sid}] URL path from request: {path}")

            # Extract quest number using regex for more reliable parsing
            import re
            quest_match = re.search(r'/quest/(\d+)', path)
            if quest_match:
                quest_id = int(quest_match.group(1))
                print(f"[{sid}] Found quest ID in path: {quest_id}")
                # Special case handling for Quest 28 (Echo 9)
                if quest_id == 28:
                    print(f"[{sid}] Special case: Quest 28 maps to Echo 9")
                    return 9  # Echo 9
                if quest_id in quest_to_echo:
                    return quest_to_echo[quest_id]

            # Check query parameter as fallback
            if hasattr(request, 'args') and 'echo' in request.args:
                try:
                    echo_level = int(request.args.get('echo'))
                    print(f"[{sid}] Found echo level in query param: {echo_level}")
                    if 1 <= echo_level <= 10:
                        return echo_level
                except ValueError:
                    pass

            # Check URL directly for echoframe-related paths
            url_path = request.path
            print(f"[{sid}] Checking URL path directly: {url_path}")

            # Check for quest in URL components
            url_parts = url_path.split('/')
            for i, part in enumerate(url_parts):
                if part == 'quest' and i+1 < len(url_parts):
                    try:
                        quest_id = int(url_parts[i+1])
                        print(f"[{sid}] Found quest ID {quest_id} in URL parts")
                        if quest_id in quest_to_echo:
                            return quest_to_echo[quest_id]
                    except (ValueError, IndexError):
                        pass

            # Check URL query parameters
            if hasattr(request, 'args'):
                print(f"[{sid}] Checking URL query parameters: {request.args}")
                if 'quest' in request.args:
                    try:
                        quest_id = int(request.args.get('quest'))
                        print(f"[{sid}] Found quest ID {quest_id} in query param")
                        if quest_id in quest_to_echo:
                            return quest_to_echo[quest_id]
                    except ValueError:
                        pass

    except Exception as e:
        print(f"[{sid}] Error extracting quest ID from path: {e}")

    # Method 3: Check headers from socketio or session
    try:
        # Try to get quest ID from session
        from flask import session
        if hasattr(session, 'get'):
            current_quest = session.get('current_quest')
            print(f"[{sid}] Found current_quest in session: {current_quest}")
            if current_quest and isinstance(current_quest, int) and current_quest in quest_to_echo:
                return quest_to_echo[current_quest]

        # Check headers from socketio environ
        if socketio_to_use and hasattr(socketio_to_use, 'server'):
            for client_sid, client_session in socketio_to_use.server.environ.items():
                if client_sid == sid:
                    # Print all headers for debugging
                    print(f"[{sid}] All headers in socketio.server.environ: {client_session}")

                    # Check various possible sources of the quest ID
                    for header_name in ['PATH_INFO', 'HTTP_REFERER', 'REQUEST_URI']:
                        header_value = client_session.get(header_name, '')
                        print(f"[{sid}] Header {header_name}: {header_value}")

                        # Try to extract quest ID
                        import re
                        quest_match = re.search(r'/quest/(\d+)', header_value)
                        if quest_match:
                            quest_id = int(quest_match.group(1))
                            print(f"[{sid}] Found quest ID {quest_id} in {header_name}")
                            if quest_id in quest_to_echo:
                                return quest_to_echo[quest_id]

                    # Check if we can extract directly from the URL
                    request_uri = client_session.get('REQUEST_URI', '')
                    if request_uri:
                        url_parts = request_uri.split('/')
                        for i, part in enumerate(url_parts):
                            if part == 'quest' and i+1 < len(url_parts):
                                try:
                                    quest_id = int(url_parts[i+1])
                                    print(f"[{sid}] Found quest ID {quest_id} in REQUEST_URI parts")
                                    if quest_id in quest_to_echo:
                                        return quest_to_echo[quest_id]
                                except (ValueError, IndexError):
                                    pass

                    # Try to get the flask session from the client_session
                    if 'flask.session' in client_session:
                        try:
                            flask_session = client_session['flask.session']
                            if isinstance(flask_session, dict):
                                current_quest = flask_session.get('current_quest')
                                print(f"[{sid}] Found current_quest in flask.session: {current_quest}")
                                if current_quest and isinstance(current_quest, int) and current_quest in quest_to_echo:
                                    return quest_to_echo[current_quest]
                        except Exception as e:
                            print(f"[{sid}] Error accessing flask.session: {e}")
    except Exception as e:
        print(f"[{sid}] Error checking headers or session: {e}")

    # Last resort: Try to extract quest info from url in referer
    try:
        if socketio_to_use and hasattr(socketio_to_use, 'server'):
            for client_sid, client_session in socketio_to_use.server.environ.items():
                if client_sid == sid:
                    referer = client_session.get('HTTP_REFERER', '')
                    if referer:
                        import re
                        for match in re.finditer(r'quest[=/](\d+)', referer):
                            try:
                                quest_id = int(match.group(1))
                                print(f"[{sid}] Found potential quest ID {quest_id} in referer URL")
                                if quest_id in quest_to_echo:
                                    return quest_to_echo[quest_id]
                            except (ValueError, IndexError):
                                pass
    except Exception as e:
        print(f"[{sid}] Error extracting from referer: {e}")

    # Default to Echo 1 as the starting point
    print(f"[{sid}] Defaulting to echo level 1")
    return 1

# Force an immediate game state update
def force_state_update(socketio, sid, student_namespace):
    """Force an immediate state update for the given session."""
    try:
        # Default fallback state
        default_state = {
            "snake": [[15, 10]],
            "food": [20, 10],
            "score": 0,
            "grid_width": 30,
            "grid_height": 20,
            "message_title": "Snake Echo Loading",
            "message_text": "Initializing...",
            "message_details": "Please wait while we load your game code",
            "message_hint": "Watch this space for updates",
            "echo_level": 1
        }

        # If we don't have a namespace for this session, nothing to update
        if sid not in student_namespaces:
            # Just send a default loading state
            print(f"[{sid}] Force state update requested but no namespace exists")
            socketio.emit('game_state_update', default_state, room=sid)
            return

        # Get the student's namespace
        ns = student_namespaces[sid]

        # Try to gather state from the namespace
        # This will vary based on the echo level

        # Get echo level (either from namespace or assuming based on available objects)
        echo_level = 1
        socketio_instance = socketio or global_socketio
        username = None

        # Try to get echo level from Flask session
        if hasattr(socketio_instance, 'server'):
            for client_sid, client_session in socketio_instance.server.environ.items():
                if client_sid == sid and 'flask.session' in client_session:
                    try:
                        flask_session = client_session['flask.session']
                        if isinstance(flask_session, dict) and 'snaker_name' in flask_session:
                            username = flask_session['snaker_name']
                            # Use a try/except to safely determine echo level
                            try:
                                echo_level = determine_echo_level(sid, username, socketio_instance)
                            except Exception as e:
                                print(f"[{sid}] Error determining echo level: {e}")
                            break
                    except:
                        pass

                # Special case check for quest/29 (Echo 10) in path or referer
                path = client_session.get('PATH_INFO', '')
                referer = client_session.get('HTTP_REFERER', '')

                if '/quest/29' in path or '/quest/29' in referer:
                    echo_level = 10
                    print(f"[{sid}] Special case: Found quest/29 in path or referer, forcing Echo 10")

                # Special case check for quest/28 (Echo 9) in path or referer
                if '/quest/28' in path or '/quest/28' in referer:
                    echo_level = 9  # Echo 9 specifically for Quest 28
                    print(f"[{sid}] Special case: Found quest/28 in path or referer, forcing Echo 9")

        # Check if all required constants exist with values
        required_constants = ['CELL_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'BLACK', 'WHITE', 'GREEN', 'RED']
        constants_exist = True
        for const in required_constants:
            if const not in ns or ns[const] is None:
                constants_exist = False
                print(f"[{sid}] Missing constant: {const}")
                break

        print(f"[{sid}] Force state update - Constants exist: {constants_exist}")

        # If constants are missing, provide a message about defining constants
        if not constants_exist:
            state = {
                "snake": [[15, 10]],
                "food": [20, 10],
                "score": 0,
                "grid_width": 30,
                "grid_height": 20,
                "message_title": f"Snake Echo {echo_level}",
                "message_text": "Waiting for setup...",
                "message_details": "Required: Define constants and create snake object",
                "message_hint": "Check the instructions for this echo level",
                "echo_level": echo_level
            }
            socketio.emit('game_state_update', state, room=sid)
            return
    except Exception as e:
        print(f"[{sid}] Error forcing state update: {e}")
        traceback.print_exc()

# Before we create the module system, let's check for common module patterns and provide stubs
def create_stub_modules(temp_dir, files):
    """Create stub modules for common imports students might use."""
    # --- Snake Class Stub ---
    # Check if 'snake_class.py' is referenced but not provided
    needs_snake_class = False
    snake_class_exists = 'snake_class.py' in files

    # Look for imports of snake_class in files
    for content in files.values():
        if 'import snake_class' in content or 'from snake_class import' in content:
            needs_snake_class = True
            break

    # Create snake_class.py stub if needed
    if needs_snake_class and not snake_class_exists:
        print("Creating stub for snake_class.py")
        snake_class_stub = """
# Auto-generated snake_class stub module
import pygame
import random

# Direction constants in case students import them from here
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

class Snake:
    def __init__(self):
        self.positions = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
        self.direction = RIGHT
        self.grow = False

    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self):
        head_x, head_y = self.positions[0]

        if self.direction == UP:
            new_head = [head_x, head_y - 1]
        elif self.direction == DOWN:
            new_head = [head_x, head_y + 1]
        elif self.direction == LEFT:
            new_head = [head_x - 1, head_y]
        else:  # RIGHT
            new_head = [head_x + 1, head_y]

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        self.direction = new_direction

    def check_collision(self):
        head = self.positions[0]
        body = self.positions[1:]
        for segment in body:
            if segment[0] == head[0] and segment[1] == head[1]:
                return True
        return False

    def grow_snake(self):
        self.grow = True

    def check_boundary_collision(self, grid_width, grid_height):
        head_x, head_y = self.positions[0]
        return head_x < 0 or head_x >= grid_width or head_y < 0 or head_y >= grid_height
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "snake_class.py"), "w") as f:
            f.write(snake_class_stub)

        # Add to files so it gets loaded
        files["snake_class.py"] = snake_class_stub

    # --- Food Class Stub ---
    # Check if 'food_class.py' or 'food.py' is referenced but not provided
    needs_food_class = False
    food_class_exists = 'food_class.py' in files or 'food.py' in files

    # Look for imports of food module in files
    for content in files.values():
        if ('import food_class' in content or 'from food_class import' in content or
            'import food' in content or 'from food import' in content):
            needs_food_class = True
            break

    # Create food_class.py stub if needed
    if needs_food_class and not food_class_exists:
        print("Creating stub for food_class.py")
        food_class_stub = """
# Auto-generated food_class stub module
import pygame
import random

class Food:
    def __init__(self):
        self.position = self.get_random_position()

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def get_random_position(self):
        return [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]

    def reset(self, snake_positions=None):
        # Find a position not occupied by the snake
        new_pos = self.get_random_position()
        if snake_positions:
            # Try to find a position not occupied by the snake
            max_attempts = 100
            attempts = 0
            while new_pos in snake_positions and attempts < max_attempts:
                new_pos = self.get_random_position()
                attempts += 1
        self.position = new_pos
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "food_class.py"), "w") as f:
            f.write(food_class_stub)

        # Add to files so it gets loaded
        files["food_class.py"] = food_class_stub

        # For compatibility, create food.py with the full Food class implementation
        with open(os.path.join(temp_dir, "food.py"), "w") as f:
            f.write("""
# food.py: Contains the Food class definition
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

    def reset(self, snake_positions=None):
        # Find a position not occupied by the snake
        new_pos = self.get_random_position()
        if snake_positions:
            # Try to find a position not occupied by the snake
            max_attempts = 100
            attempts = 0
            while new_pos in snake_positions and attempts < max_attempts:
                new_pos = self.get_random_position()
                attempts += 1
        self.position = new_pos
""")
        # Set the content in files dictionary
        files["food.py"] = food_class_stub  # Use the same content we created for food_class.py

    # --- Game Utilities Stub ---
    # Check if game_utils.py is referenced but not provided
    needs_game_utils = False
    game_utils_exists = 'game_utils.py' in files or 'utils.py' in files

    # Look for imports of game_utils module in files
    for content in files.values():
        if ('import game_utils' in content or 'from game_utils import' in content or
            'import utils' in content or 'from utils import' in content):
            needs_game_utils = True
            break

    # Create game_utils.py stub if needed
    if needs_game_utils and not game_utils_exists:
        print("Creating stub for game_utils.py")
        game_utils_stub = """
# Auto-generated game_utils stub module
import pygame

def draw_grid(screen):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_text(screen, text, position, color=WHITE, font_size=FONT_SIZE):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def check_collision(pos1, pos2):
    return pos1[0] == pos2[0] and pos1[1] == pos2[1]

def game_over_screen(screen, score):
    draw_text(screen, "GAME OVER", (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
    draw_text(screen, f"SCORE: {score}", (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 10))
    draw_text(screen, "Press SPACE to Play Again", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "game_utils.py"), "w") as f:
            f.write(game_utils_stub)

        # Add to files so it gets loaded
        files["game_utils.py"] = game_utils_stub

        # Also create utils.py as an alias
        with open(os.path.join(temp_dir, "utils.py"), "w") as f:
            f.write("""
# Auto-generated utils.py stub module - redirects to game_utils
from game_utils import *
""")
        files["utils.py"] = "from game_utils import *"

    # --- Constants Module ---
    needs_constants = False
    constants_exists = 'constants.py' in files

    # Look for imports of constants in files
    for content in files.values():
        if 'import constants' in content or 'from constants import' in content:
            needs_constants = True
            break

    # Create constants.py stub if needed
    if needs_constants and not constants_exists:
        print("Creating stub for constants.py")
        constants_stub = """
# Auto-generated constants.py stub module
# Game dimensions
GRID_WIDTH = 30
GRID_HEIGHT = 30
CELL_SIZE = 15
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Game speed
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Font
FONT_SIZE = 36

# Directions
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "constants.py"), "w") as f:
            f.write(constants_stub)

        # Add to files so it gets loaded
        files["constants.py"] = constants_stub

# Add this function after the create_stub_modules function
def ensure_globals_in_namespace(files, namespace, echo_level=None, sid=None):
    """
    Make sure all necessary global constants are available in the namespace.

    Args:
        files: Dict of filename -> content
        namespace: The namespace (dictionary) to populate
        echo_level: Optional echo level (1-10)
        sid: Optional socket session ID for logging
    """
    print(f"[{sid}] Ensuring globals in namespace")

    # For better debugging, log which constants are already defined
    constants_to_check = ['CELL_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'BLACK', 'WHITE', 'GREEN', 'RED', 'FPS']
    defined_constants = [const for const in constants_to_check if const in namespace]
    missing_constants = [const for const in constants_to_check if const not in namespace]

    print(f"[{sid}] Already defined constants: {defined_constants}")
    print(f"[{sid}] Missing constants: {missing_constants}")

    # If constants file exists, it should define these variables
    has_constants_file = False
    constants_content = ""

    for filename, content in files.items():
        if filename.lower() == 'constants.py':
            has_constants_file = True
            constants_content = content
            # Parse constants file content to extract values
            print(f"[{sid}] Found constants.py file, checking content")

            # For each missing constant, try to extract from the constants file
            for const in missing_constants:
                import re
                match = re.search(f"{const}\\s*=\\s*([^\\n]+)", content)
                if match:
                    try:
                        # Try to evaluate the constant value
                        const_value = eval(match.group(1), {}, {})
                        namespace[const] = const_value
                        print(f"[{sid}] Extracted {const} = {const_value} from constants.py")
                    except Exception as e:
                        print(f"[{sid}] Error evaluating {const}: {e}")
                else:
                    print(f"[{sid}] Constant {const} not found in constants.py")

    # If constants file doesn't exist, log a warning
    if not has_constants_file:
        print(f"[{sid}] Warning: No constants.py file found in student code!")
        print(f"[{sid}] Files found: {list(files.keys())}")

    # Use default values for missing constants based on echo level
    if 'CELL_SIZE' not in namespace:
        namespace['CELL_SIZE'] = 20
        print(f"[{sid}] Using default CELL_SIZE = 20")

    if 'GRID_WIDTH' not in namespace:
        namespace['GRID_WIDTH'] = 30
        print(f"[{sid}] Using default GRID_WIDTH = 30")

    if 'GRID_HEIGHT' not in namespace:
        namespace['GRID_HEIGHT'] = 20
        print(f"[{sid}] Using default GRID_HEIGHT = 20")

    if 'SCREEN_WIDTH' not in namespace:
        namespace['SCREEN_WIDTH'] = namespace['GRID_WIDTH'] * namespace['CELL_SIZE']
        print(f"[{sid}] Calculated SCREEN_WIDTH = {namespace['SCREEN_WIDTH']}")

    if 'SCREEN_HEIGHT' not in namespace:
        namespace['SCREEN_HEIGHT'] = namespace['GRID_HEIGHT'] * namespace['CELL_SIZE']
        print(f"[{sid}] Calculated SCREEN_HEIGHT = {namespace['SCREEN_HEIGHT']}")

    # Colors
    if 'BLACK' not in namespace: namespace['BLACK'] = (0, 0, 0)
    if 'WHITE' not in namespace: namespace['WHITE'] = (255, 255, 255)
    if 'GREEN' not in namespace: namespace['GREEN'] = (0, 255, 0)
    if 'RED' not in namespace: namespace['RED'] = (255, 0, 0)

    # Game settings
    if 'FPS' not in namespace: namespace['FPS'] = 10

    return namespace

# Define a minimalist placeholder when student code is empty or missing
game_code = """
# Error screen for when no student code is available
import pygame
import sys

# Initialize pygame
pygame.init()

# Set default screen size
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 400
screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
pygame.display.set_caption('Snake Echo - Error')
clock = pygame.time.Clock()

# Simple game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Fill the screen with a dark color
    screen.fill((40, 40, 60))

    # Display error message
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Missing Student Code", True, (255, 100, 100))
    title_rect = title.get_rect(center=(DEFAULT_WIDTH//2, 100))
    screen.blit(title, title_rect)

    # Display instructions
    font = pygame.font.SysFont(None, 32)

    msg1 = font.render("This echo requires you to write the snake code.", True, (220, 220, 220))
    msg1_rect = msg1.get_rect(center=(DEFAULT_WIDTH//2, 180))
    screen.blit(msg1, msg1_rect)

    msg2 = font.render("Please check the instructions and write your code", True, (220, 220, 220))
    msg2_rect = msg2.get_rect(center=(DEFAULT_WIDTH//2, 220))
    screen.blit(msg2, msg2_rect)

    msg3 = font.render("in the appropriate files.", True, (220, 220, 220))
    msg3_rect = msg3.get_rect(center=(DEFAULT_WIDTH//2, 260))
    screen.blit(msg3, msg3_rect)

    # Display hint
    hint_font = pygame.font.SysFont(None, 28)
    hint = hint_font.render("Remember: The code you write controls the snake game", True, (150, 255, 150))
    hint_rect = hint.get_rect(center=(DEFAULT_WIDTH//2, 330))
    screen.blit(hint, hint_rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
"""

# --- Top-level student_process for multiprocessing (Windows fix) ---
def student_process(child_conn, temp_dir, student_path):
    import sys, importlib.util, traceback, os
    print('[DEBUG] student_process started')
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.display.set_mode = lambda *args, **kwargs: pygame.Surface((640, 480))
    pygame.display.flip = lambda *args, **kwargs: None
    sys.path.insert(0, temp_dir)
    # Inject custom get_user_direction
    def get_user_direction():
        ns = sys.modules['__main__'].__dict__
        print(f"[DEBUG get_user_direction] Called.")

        # Determine a fallback direction based on snake's current direction if possible
        fallback_direction = 'RIGHT' # Default fallback
        if 'snake' in ns:
            snake_obj = ns['snake']
            if hasattr(snake_obj, 'direction'):
                # This assumes student's snake.direction is a string 'UP', 'DOWN', etc.
                # If it's a tuple (dx, dy) or constant, this part would need adjustment
                # or the student code would rely purely on the received direction.
                if isinstance(snake_obj.direction, str) and snake_obj.direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    fallback_direction = snake_obj.direction

        # Send current game state
        try:
            snake_positions = [[15,10]] # Default
            if 'snake' in ns and hasattr(ns['snake'], 'positions'):
                snake_positions = list(ns['snake'].positions)
            elif 'snake' in ns and isinstance(ns['snake'], list): # Basic list of positions
                snake_positions = ns['snake']

            food_position = [20,10] # Default
            if 'food' in ns and hasattr(ns['food'], 'position'):
                food_position = list(ns['food'].position)
            elif 'food' in ns and isinstance(ns['food'], (list, tuple)): # Basic list/tuple
                food_position = list(ns['food'])

            game_state = {
                'grid_width': ns.get('GRID_WIDTH', 30),
                'grid_height': ns.get('GRID_HEIGHT', 20),
                'snake': snake_positions,
                'food': food_position,
                'score': ns.get('score', 0),
                'game_over': ns.get('game_over', False),
                'message_title': '', 'message_text': '', 'message_hint': ''
            }
            child_conn.send(game_state)
        except Exception as e:
            # Send error if state extraction fails
            child_conn.send({'error': f'Error in get_user_direction while extracting state: {traceback.format_exc()}'})

        # Wait for direction from parent process
        try:
            # Poll for a short time (e.g., up to 50ms, matching frame_delay)
            # This timeout should ideally be less than or equal to frame_delay in run_student_snake
            polled_value = child_conn.poll(0.04)
            print(f"[DEBUG get_user_direction] child_conn.poll(0.04) result: {polled_value}")
            if polled_value:
                new_direction = child_conn.recv()
                print(f"[DEBUG get_user_direction] Received new_direction: {new_direction}")
                if new_direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    print(f"[DEBUG get_user_direction] Returning NEWLY RECEIVED direction: {new_direction}")
                    return new_direction
        except EOFError: # Pipe might have been closed
            pass # Will use fallback
        except Exception: # Other potential errors during recv (e.g., timeout, deserialization)
            pass # Will use fallback

        print(f"[DEBUG get_user_direction] Returning FALLBACK direction: {fallback_direction}")
        return fallback_direction
    import builtins
    builtins.get_user_direction = get_user_direction
    try:
        print('[DEBUG] student_process importing student code:', student_path)
        spec = importlib.util.spec_from_file_location("student_main", student_path)
        student_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(student_mod)
        print('[DEBUG] student_process finished student code')
    except Exception as e:
        child_conn.send({'error': traceback.format_exc()})
        print('[DEBUG] error sent (importing student code):', traceback.format_exc())

def run_student_snake(socketio, sid, files, pre_determined_echo_level=None):
    """
    Run the student's snake code in a subprocess, capturing game state as JSON after each frame.
    Inject a custom get_user_direction() that sends state to the parent process after each frame.
    On error, send error state to the client. All file/echo handling is dynamic and global.
    """
    import sys, importlib.util, traceback, time, multiprocessing, os, tempfile, shutil, json
    try:
        # --- PATCH: Enforce headless Pygame and suppress window creation ---
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        import pygame
        pygame.display.set_mode = lambda *args, **kwargs: pygame.Surface((640, 480))
        pygame.display.flip = lambda *args, **kwargs: None
        # ---------------------------------------------------------------

        # Setup: create a temp directory for the student's files
        temp_dir = tempfile.mkdtemp(prefix=f"snake_{sid}_")
        sys.path.insert(0, temp_dir)
        for filename, content in files.items():
            with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
        main_file = 'snake.py' if 'snake.py' in files else 'main.py'
        student_path = os.path.join(temp_dir, main_file)

        # Use multiprocessing Pipe for communication
        parent_conn, child_conn = multiprocessing.Pipe()

        # Start the student process (now top-level)
        proc = multiprocessing.Process(target=student_process, args=(child_conn, temp_dir, student_path))
        proc.start()
        max_frames = 200
        frame_delay = 0.05
        for _ in range(max_frames):
            if parent_conn.poll(timeout=frame_delay * 2):
                msg = parent_conn.recv()
                if isinstance(msg, dict) and 'error' in msg:
                    socketio.emit('preview_error', {'error': msg['error']}, room=sid)
                    break
                else:
                    socketio.emit('game_state_update', msg, room=sid)

                # Send the current direction from client_inputs to the student_process
                # Default to 'RIGHT' if no input has been registered for the session yet
                current_input = client_inputs.get(sid, 'RIGHT')
                print(f"[DEBUG run_student_snake SID: {sid}] Sending to student_process direction: {current_input}")
                parent_conn.send(current_input)
            if not proc.is_alive():
                break
        proc.terminate()
        proc.join(timeout=0.5)
        shutil.rmtree(temp_dir)
    except Exception as e:
        socketio.emit('preview_error', {'error': f'Internal error: {traceback.format_exc()}'}, room=sid)

# --- Standalone gameplay code below ---
# This code is only used when running the file directly (not when imported)
if __name__ == "__main__" and not os.environ.get('SDL_VIDEODRIVER') == 'dummy':
    # Set SDL_VIDEODRIVER to 'dummy' to prevent window from opening when testing
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

    # --- Initialization ---
    pygame.init()

    # --- Screen Setup ---
    window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Snake Echo')
    clock = pygame.time.Clock()

    # --- Game Variables ---
    score = 0
    game_over = False

    # Function to get user input from the frontend
    # (This is provided by the simulation framework)
    def get_user_direction():
        return 'RIGHT'  # Default direction if no input available

    # --- Game Text Rendering ---
    def render_text(text, size, color, position):
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

    # --- Snake Class ---
    class Snake:
        def __init__(self):
            # Initialize the snake at the center of the screen
            self.positions = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
            self.direction = RIGHT
            self.grow = False

        def draw(self, screen):
            # Draw the snake segments
            for position in self.positions:
                pygame.draw.rect(screen, GREEN,
                                (position[0] * CELL_SIZE, position[1] * CELL_SIZE,
                                 CELL_SIZE, CELL_SIZE))

        def update(self):
            # Create a new head position based on current direction
            head = self.positions[0].copy()

            # Update the head based on direction
            if self.direction == UP:
                head[1] -= 1
            elif self.direction == DOWN:
                head[1] += 1
            elif self.direction == LEFT:
                head[0] -= 1
            elif self.direction == RIGHT:
                head[0] += 1

            # Add the new head
            self.positions.insert(0, head)

            # Remove the tail unless we need to grow
            if not self.grow:
                self.positions.pop()
            else:
                self.grow = False

            # Wrap around behavior for edges
            if head[0] < 0:
                head[0] = GRID_WIDTH - 1
            elif head[0] >= GRID_WIDTH:
                head[0] = 0
            if head[1] < 0:
                head[1] = GRID_HEIGHT - 1
            elif head[1] >= GRID_HEIGHT:
                head[1] = 0

        def check_collision(self):
            # Check if snake collides with itself
            head = self.positions[0]
            body = self.positions[1:]
            for segment in body:
                if segment[0] == head[0] and segment[1] == head[1]:
                    return True
            return False

        def grow_snake(self):
            self.grow = True

    # --- Food Class ---
    class Food:
        def __init__(self):
            # Initialize food at a random position
            self.position = self.get_random_position()

        def draw(self, screen):
            # Draw the food
            pygame.draw.rect(screen, RED,
                            (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE,
                             CELL_SIZE, CELL_SIZE))

        def get_random_position(self):
            # Place food at a random position on the grid
            return [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]

        def reposition(self, snake_positions):
            # Reposition food, ensuring it's not on the snake
            self.position = self.get_random_position()
            while self.position in snake_positions:
                self.position = self.get_random_position()

    # Create snake and food instances
    snake = Snake()
    food = Food()

    # --- Game Loop ---
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == K_SPACE and game_over:
                    # Reset the game
                    snake = Snake()
                    food = Food()
                    score = 0
                    game_over = False

        # Get direction from user input if available
        if not game_over:
            user_dir = get_user_direction()
            if user_dir == UP and snake.direction != DOWN:
                snake.direction = UP
            elif user_dir == DOWN and snake.direction != UP:
                snake.direction = DOWN
            elif user_dir == LEFT and snake.direction != RIGHT:
                snake.direction = LEFT
            elif user_dir == RIGHT and snake.direction != LEFT:
                snake.direction = RIGHT

        # Update game state if not game over
        if not game_over:
            # Update snake position
            snake.update()

            # Check for collision with food
            snake_head = snake.positions[0]
            food_pos = food.position
            if snake_head[0] == food_pos[0] and snake_head[1] == food_pos[1]:
                snake.grow_snake()
                food.reposition(snake.positions)
                score += 1

            # Check for collision with self
            if snake.check_collision():
                game_over = True

        # Draw everything
        screen.fill(BG_COLOR)

        # Draw snake and food
        snake.draw(screen)
        food.draw(screen)

        # Display score
        render_text(f"Score: {score}", SMALL_FONT_SIZE, TEXT_COLOR,
                    (SCORE_POS[0] + 50, SCORE_POS[1] + 10))

        # Display game over message
        if game_over:
            render_text(GAME_OVER_TEXT, LARGE_FONT_SIZE, GAME_OVER_COLOR,
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            render_text(f"Final Score: {score}", MEDIUM_FONT_SIZE, TEXT_COLOR,
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            render_text(RESTART_TEXT, SMALL_FONT_SIZE, TEXT_COLOR,
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        # Update display
        pygame.display.flip()

        # Maintain game speed
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()
"""
student_driven_snake.py - The primary game implementation that students will modify.

This file contains a working snake game that mirrors what students build in the echoes.
The implementation follows the EchoFrame pedagogical approach where students control
the game loop and game logic directly in their code rather than having it managed by the backend.
"""
import pygame
import sys
import random
import os
import time
import traceback
import importlib
import shutil
import tempfile
from io import StringIO
import eventlet
from flask_socketio import emit
from flask import request
import types
import builtins
import inspect
import threading
import importlib.util
import json
import multiprocessing

# Custom exception for file loading
class FileLoadedException(Exception):
    """Exception raised when files are loaded in a special way."""
    pass

# Dictionary to track active simulations by session ID
active_simulations = {}
# Dictionary to store client input by session ID
client_inputs = {}
# Dictionary to store student namespace by session ID
student_namespaces = {}
# Global socketio reference for use in handlers
global_socketio = None

# --- Constants ---
# These constants are the default values that will be used if not defined in student's code
CELL_SIZE = None
GRID_WIDTH = None
GRID_HEIGHT = None
SCREEN_WIDTH = None
SCREEN_HEIGHT = None

# Colors
BLACK = None
WHITE = None
GREEN = None
RED = None
BLUE = None
YELLOW = None
GRAY = None
GREY = None

# Game settings
FPS = None
FONT_SIZE = None
SNAKE_SPEED = None

# Direction constants
UP = None
DOWN = None
LEFT = None
RIGHT = None

# Element colors
SNAKE_COLOR = None
FOOD_COLOR = None
BG_COLOR = None
BACKGROUND_COLOR = None

# Position constants
CENTER = None
SCORE_POS = None
GAME_OVER_POS = None
RESTART_TEXT_POS = None
FINAL_SCORE_POS = None
TOP_LEFT = None
TOP_RIGHT = None
BOTTOM_LEFT = None
BOTTOM_RIGHT = None

# Text constants
GAME_OVER_TEXT = 'GAME OVER'
RESTART_TEXT = 'Press SPACE to restart'
SMALL_FONT_SIZE = 24
MEDIUM_FONT_SIZE = 36
LARGE_FONT_SIZE = 72
TEXT_COLOR = WHITE
GAME_OVER_COLOR = RED
BORDER_COLOR = WHITE

# Key constants - pygame key constants for easier student access
K_UP = 273  # pygame.K_UP
K_DOWN = 274  # pygame.K_DOWN
K_LEFT = 276  # pygame.K_LEFT
K_RIGHT = 275  # pygame.K_RIGHT
K_SPACE = 32  # pygame.K_SPACE
K_RETURN = 13  # pygame.K_RETURN
K_ESCAPE = 27  # pygame.K_ESCAPE

# Function to get the directory for a user's snake files
def get_user_snake_dir(username, echo_level=None, create=True):
    """
    Get the directory for a user's snake files.
    
    Args:
        username: The username of the snaker
        echo_level: Optional integer representing the echo level (0-9).
                   If provided, return the directory for that echo level.
        create: Boolean, whether to create the directory if it doesn't exist
        
    Returns:
        Path to the user's snake code directory or echo-specific directory
    """
    base_dir = os.path.join('user_data', 'snake_code')
    user_dir = os.path.join(base_dir, username)

    if create and not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
    
    # If echo level is provided, get the echo-specific directory
    if echo_level is not None and 0 <= echo_level < 10:
        echo_dir = os.path.join(user_dir, f'snake_echo_{echo_level+1}')
        if create and not os.path.exists(echo_dir):
            os.makedirs(echo_dir, exist_ok=True)
        return echo_dir
        
    return user_dir

# Custom module mock for pygame to prevent window opening
class MockPygame:
    """Mock pygame module to prevent window opening in preview mode."""
    class Surface:
        def __init__(self, size):
            self.size = size
            
        def fill(self, color):
            pass
            
        def blit(self, source, dest, area=None, special_flags=0):
            pass

    class Rect:
        def __init__(self, left, top, width, height):
            self.left = left
            self.top = top
            self.width = width
            self.height = height
            self.size = (width, height)
            self.topleft = (left, top)

        def colliderect(self, rect):
            return False

        def move(self, x, y):
            return MockPygame.Rect(self.left + x, self.top + y, self.width, self.height)

    class Event:
        def __init__(self, type, **kwargs):
            self.type = type
            for key, value in kwargs.items():
                setattr(self, key, value)

    class MockDraw:
        def rect(self, surface, color, rect, width=0):
            pass

        def circle(self, surface, color, center, radius, width=0):
            pass
            
        def line(self, surface, color, start_pos, end_pos, width=1):
            pass

    class MockDisplay:
        def set_mode(self, size, flags=0, depth=0, display=0, vsync=0):
            return MockPygame.Surface(size)

        def set_caption(self, caption):
            pass

        def flip(self):
            pass

        def update(self, *args):
            pass

    class MockTime:
        def Clock(self):
            return type('MockClock', (), {
                'tick': lambda fps: time.sleep(1/fps),
                'get_fps': lambda: 30
            })

    class MockFont:
        def __init__(self):
            pass

        def init(self):
            pass

        def SysFont(self, name, size):
            return type('MockFont', (), {
                'render': lambda text, antialias, color: MockPygame.Surface((100, 30))
            })
            
    class MockEvent:
        def get(self, *args, **kwargs):
            events = []
            return events

    # Constants
    QUIT = 12
    KEYDOWN = 2
    K_UP = 273
    K_DOWN = 274
    K_LEFT = 276
    K_RIGHT = 275
    K_SPACE = 32

    # Create instances of our mock classes
    display = MockDisplay()
    draw = MockDraw()
    time = MockTime()
    font = MockFont()
    event = MockEvent()

    def init(self=None):
        return 6, 0

    def quit(self=None):
        pass

# Function to determine the echo level based on files
def _determine_echo_level(files):
    """Determine which echo level the student is at based on their code."""
    echo_level = 0
    
    # Check for constants definition (Echo 1)
    for _, code in files.items():
        if 'GRID_WIDTH' in code and 'GRID_HEIGHT' in code and 'CELL_SIZE' in code:
            echo_level = max(echo_level, 1)
    
    # Check for game loop (Echo 2)
    for _, code in files.items():
        if 'pygame.init()' in code and 'while' in code and 'pygame.display.flip()' in code:
            echo_level = max(echo_level, 2)
    
    # Check for Snake class (Echo 3)
    for _, code in files.items():
        if 'class Snake' in code:
            echo_level = max(echo_level, 3)
            
    # Check for draw method (Echo 4)
    for _, code in files.items():
        if 'class Snake' in code and 'def draw' in code and 'pygame.draw.rect' in code:
            echo_level = max(echo_level, 4)
    
    # Check for Food class (Echo 5)
    for _, code in files.items():
        if 'class Food' in code:
            echo_level = max(echo_level, 5)
    
    # Check for snake growth (Echo 6)
    for _, code in files.items():
        if ('grow' in code or 'eat' in code) and 'food' in code.lower():
            echo_level = max(echo_level, 6)
    
    # Check for input handling (Echo 7)
    for _, code in files.items():
        if 'pygame.K_UP' in code or 'pygame.K_DOWN' in code:
            echo_level = max(echo_level, 7)
    
    # Check for collision detection (Echo 8)
    for _, code in files.items():
        if ('collision' in code or 'collide' in code) and ('wall' in code or 'self' in code):
            echo_level = max(echo_level, 8)
    
    # Check for game over (Echo 9)
    for _, code in files.items():
        if 'game over' in code.lower() or 'gameover' in code.lower() or 'restart' in code.lower():
            echo_level = max(echo_level, 9)
    
    return echo_level

# Functions to manage built-in constants
def _setup_builtins_constants(global_dict):
    """Add game constants to builtins so they're available in all modules."""
    for name, value in global_dict.items():
        if name.isupper():
            setattr(builtins, name, value)

def _cleanup_builtins_constants(global_dict):
    """Remove game constants from builtins."""
    for name in global_dict:
        if name.isupper() and hasattr(builtins, name):
            delattr(builtins, name)

# Function to stop the snake game for a session
def stop_student_snake(sid):
    """Stop the snake game for a specific session."""
    if sid in active_simulations:
        print(f"Stopping student snake game for session {sid}")
        active_simulations[sid] = False
        if sid in student_namespaces:
            del student_namespaces[sid]
        if sid in client_inputs:
            del client_inputs[sid]
        return True
    return False

# Function to handle direction input from client
def handle_direction_input(sid, direction):
    """Handle direction input from the client."""
    # Convert direction to string format and store both string and constant format
    # This ensures compatibility with both types of direction representations
    if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        client_inputs[sid] = direction
        print(f"[{sid}] Direction input registered: {direction}")
        
        # Debug - Check if the student's namespace has a snake object to control
        if sid in student_namespaces:
            ns = student_namespaces[sid]
            if 'snake' in ns:
                snake_obj = ns.get('snake')
                print(f"[{sid}] Found snake object: {type(snake_obj)}")
                # Check if the snake has a direction property
                if hasattr(snake_obj, 'direction'):
                    old_dir = snake_obj.direction
                    # Try to update the snake's direction directly (handle string format)
                    try:
                        # Check what type of direction the snake is using
                        # It could be a string like 'RIGHT' or a constant like RIGHT
                        if isinstance(old_dir, str):
                            # The snake uses string directions
                            snake_obj.direction = direction
                        else:
                            # The snake uses constant directions
                            # Map the string direction to the constant direction
                            if direction == 'UP' and 'UP' in ns:
                                snake_obj.direction = ns['UP']
                            elif direction == 'DOWN' and 'DOWN' in ns:
                                snake_obj.direction = ns['DOWN']
                            elif direction == 'LEFT' and 'LEFT' in ns:
                                snake_obj.direction = ns['LEFT']
                            elif direction == 'RIGHT' and 'RIGHT' in ns:
                                snake_obj.direction = ns['RIGHT']
                            
                        print(f"[{sid}] Updated snake direction from {old_dir} to {direction}")
                    except Exception as e:
                        print(f"[{sid}] Failed to update snake direction: {e}")
                else:
                    print(f"[{sid}] Snake object doesn't have a 'direction' attribute")
            else:
                print(f"[{sid}] No 'snake' object found in namespace with keys: {list(ns.keys())}")
        else:
            print(f"[{sid}] No namespace found for session {sid}")
            
        return True
    return False

# Function to send game state updates
def send_game_state_update(socketio, sid, game_state):
    """Send game state update to the client."""
    try:
        socketio.emit('game_state_update', game_state, room=sid)
    except Exception as e:
        print(f"Error sending game state update: {e}")

# Define a helper function to determine echo level
def determine_echo_level(sid, username, socketio_instance=None):
    """Determine the echo level for a user.
    
    Args:
        sid: The socket ID
        username: The username if available
        socketio_instance: The socketio instance if available
        
    Returns:
        int: The echo level (1-10)
    """
    echo_level = None
    socketio_to_use = socketio_instance or global_socketio
    
    print(f"[{sid}] DEBUG: Determining echo level...")
    
    # Direct mapping from quest ID to echo level
    quest_to_echo = {
        20: 1,  # Quest 20 = Echo 1
        21: 2,  # Quest 21 = Echo 2
        22: 3,  # Quest 22 = Echo 3
        23: 4,  # Quest 23 = Echo 4
        24: 5,  # Quest 24 = Echo 5
        25: 6,  # Quest 25 = Echo 6
        26: 7,  # Quest 26 = Echo 7
        27: 8,  # Quest 27 = Echo 8
        28: 9,  # Quest 28 = Echo 9
        29: 10  # Quest 29 = Echo 10
    }
    
    # Method 1: From app function - most reliable if username is available
    if username:
        try:
            from app import get_user_snake_echo_level
            echo_level = get_user_snake_echo_level(username)
            print(f"[{sid}] Retrieved echo level for {username}: {echo_level}")
            if echo_level is not None and echo_level >= 0:
                return echo_level + 1  # Convert 0-based to 1-based
        except Exception as e:
            print(f"[{sid}] Error getting echo level from app: {e}")
    
    # Method 2: Extract quest ID from request context if available
    try:
        from flask import has_request_context, request
        if has_request_context():
            # Get path from request
            path = request.path
            print(f"[{sid}] URL path from request: {path}")
            
            # Extract quest number using regex for more reliable parsing
            import re
            quest_match = re.search(r'/quest/(\d+)', path)
            if quest_match:
                quest_id = int(quest_match.group(1))
                print(f"[{sid}] Found quest ID in path: {quest_id}")
                # Special case handling for Quest 28 (Echo 9)
                if quest_id == 28:
                    print(f"[{sid}] Special case: Quest 28 maps to Echo 9")
                    return 9  # Echo 9
                if quest_id in quest_to_echo:
                    return quest_to_echo[quest_id]
            
            # Check query parameter as fallback
            if hasattr(request, 'args') and 'echo' in request.args:
                try:
                    echo_level = int(request.args.get('echo'))
                    print(f"[{sid}] Found echo level in query param: {echo_level}")
                    if 1 <= echo_level <= 10:
                        return echo_level
                except ValueError:
                    pass
                    
            # Check URL directly for echoframe-related paths
            url_path = request.path
            print(f"[{sid}] Checking URL path directly: {url_path}")
            
            # Check for quest in URL components
            url_parts = url_path.split('/')
            for i, part in enumerate(url_parts):
                if part == 'quest' and i+1 < len(url_parts):
                    try:
                        quest_id = int(url_parts[i+1])
                        print(f"[{sid}] Found quest ID {quest_id} in URL parts")
                        if quest_id in quest_to_echo:
                            return quest_to_echo[quest_id]
                    except (ValueError, IndexError):
                        pass
                        
            # Check URL query parameters
            if hasattr(request, 'args'):
                print(f"[{sid}] Checking URL query parameters: {request.args}")
                if 'quest' in request.args:
                    try:
                        quest_id = int(request.args.get('quest'))
                        print(f"[{sid}] Found quest ID {quest_id} in query param")
                        if quest_id in quest_to_echo:
                            return quest_to_echo[quest_id]
                    except ValueError:
                        pass
                
    except Exception as e:
        print(f"[{sid}] Error extracting quest ID from path: {e}")
    
    # Method 3: Check headers from socketio or session
    try:
        # Try to get quest ID from session
        from flask import session
        if hasattr(session, 'get'):
            current_quest = session.get('current_quest')
            print(f"[{sid}] Found current_quest in session: {current_quest}")
            if current_quest and isinstance(current_quest, int) and current_quest in quest_to_echo:
                return quest_to_echo[current_quest]
                
        # Check headers from socketio environ
        if socketio_to_use and hasattr(socketio_to_use, 'server'):
            for client_sid, client_session in socketio_to_use.server.environ.items():
                if client_sid == sid:
                    # Print all headers for debugging
                    print(f"[{sid}] All headers in socketio.server.environ: {client_session}")
                    
                    # Check various possible sources of the quest ID
                    for header_name in ['PATH_INFO', 'HTTP_REFERER', 'REQUEST_URI']:
                        header_value = client_session.get(header_name, '')
                        print(f"[{sid}] Header {header_name}: {header_value}")
                        
                        # Try to extract quest ID
                        import re
                        quest_match = re.search(r'/quest/(\d+)', header_value)
                        if quest_match:
                            quest_id = int(quest_match.group(1))
                            print(f"[{sid}] Found quest ID {quest_id} in {header_name}")
                            if quest_id in quest_to_echo:
                                return quest_to_echo[quest_id]
                    
                    # Check if we can extract directly from the URL
                    request_uri = client_session.get('REQUEST_URI', '')
                    if request_uri:
                        url_parts = request_uri.split('/')
                        for i, part in enumerate(url_parts):
                            if part == 'quest' and i+1 < len(url_parts):
                                try:
                                    quest_id = int(url_parts[i+1])
                                    print(f"[{sid}] Found quest ID {quest_id} in REQUEST_URI parts")
                                    if quest_id in quest_to_echo:
                                        return quest_to_echo[quest_id]
                                except (ValueError, IndexError):
                                    pass
                                    
                    # Try to get the flask session from the client_session
                    if 'flask.session' in client_session:
                        try:
                            flask_session = client_session['flask.session']
                            if isinstance(flask_session, dict):
                                current_quest = flask_session.get('current_quest')
                                print(f"[{sid}] Found current_quest in flask.session: {current_quest}")
                                if current_quest and isinstance(current_quest, int) and current_quest in quest_to_echo:
                                    return quest_to_echo[current_quest]
                        except Exception as e:
                            print(f"[{sid}] Error accessing flask.session: {e}")
    except Exception as e:
        print(f"[{sid}] Error checking headers or session: {e}")
    
    # Last resort: Try to extract quest info from url in referer
    try:
        if socketio_to_use and hasattr(socketio_to_use, 'server'):
            for client_sid, client_session in socketio_to_use.server.environ.items():
                if client_sid == sid:
                    referer = client_session.get('HTTP_REFERER', '')
                    if referer:
                        import re
                        for match in re.finditer(r'quest[=/](\d+)', referer):
                            try:
                                quest_id = int(match.group(1))
                                print(f"[{sid}] Found potential quest ID {quest_id} in referer URL")
                                if quest_id in quest_to_echo:
                                    return quest_to_echo[quest_id]
                            except (ValueError, IndexError):
                                pass
    except Exception as e:
        print(f"[{sid}] Error extracting from referer: {e}")
    
    # Default to Echo 1 as the starting point
    print(f"[{sid}] Defaulting to echo level 1")
    return 1

# Force an immediate game state update
def force_state_update(socketio, sid, student_namespace):
    """Force an immediate state update for the given session."""
    try:
        # Default fallback state
        default_state = {
            "snake": [[15, 10]],
            "food": [20, 10],
            "score": 0,
            "grid_width": 30,
            "grid_height": 20,
            "message_title": "Snake Echo Loading",
            "message_text": "Initializing...",
            "message_details": "Please wait while we load your game code",
            "message_hint": "Watch this space for updates",
            "echo_level": 1
        }
        
        # If we don't have a namespace for this session, nothing to update
        if sid not in student_namespaces:
            # Just send a default loading state
            print(f"[{sid}] Force state update requested but no namespace exists")
            socketio.emit('game_state_update', default_state, room=sid)
            return
        
        # Get the student's namespace
        ns = student_namespaces[sid]
        
        # Try to gather state from the namespace
        # This will vary based on the echo level
        
        # Get echo level (either from namespace or assuming based on available objects)
        echo_level = 1
        socketio_instance = socketio or global_socketio
        username = None
        
        # Try to get echo level from Flask session
        if hasattr(socketio_instance, 'server'):
            for client_sid, client_session in socketio_instance.server.environ.items():
                if client_sid == sid and 'flask.session' in client_session:
                    try:
                        flask_session = client_session['flask.session']
                        if isinstance(flask_session, dict) and 'snaker_name' in flask_session:
                            username = flask_session['snaker_name']
                            # Use a try/except to safely determine echo level
                            try:
                                echo_level = determine_echo_level(sid, username, socketio_instance)
                            except Exception as e:
                                print(f"[{sid}] Error determining echo level: {e}")
                            break
                    except:
                        pass
                
                # Special case check for quest/29 (Echo 10) in path or referer
                path = client_session.get('PATH_INFO', '')
                referer = client_session.get('HTTP_REFERER', '')
                
                if '/quest/29' in path or '/quest/29' in referer:
                    echo_level = 10
                    print(f"[{sid}] Special case: Found quest/29 in path or referer, forcing Echo 10")
                
                # Special case check for quest/28 (Echo 9) in path or referer
                if '/quest/28' in path or '/quest/28' in referer:
                    echo_level = 9  # Echo 9 specifically for Quest 28
                    print(f"[{sid}] Special case: Found quest/28 in path or referer, forcing Echo 9")
        
        # Check if all required constants exist with values
        required_constants = ['CELL_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'BLACK', 'WHITE', 'GREEN', 'RED']
        constants_exist = True
        for const in required_constants:
            if const not in ns or ns[const] is None:
                constants_exist = False
                print(f"[{sid}] Missing constant: {const}")
                break
        
        print(f"[{sid}] Force state update - Constants exist: {constants_exist}")
        
        # If constants are missing, provide a message about defining constants
        if not constants_exist:
            state = {
                "snake": [[15, 10]],
                "food": [20, 10],
                "score": 0,
                "grid_width": 30,
                "grid_height": 20,
                "message_title": f"Snake Echo {echo_level}",
                "message_text": "Waiting for setup...",
                "message_details": "Required: Define constants and create snake object",
                "message_hint": "Check the instructions for this echo level",
                "echo_level": echo_level
            }
            socketio.emit('game_state_update', state, room=sid)
            return
    except Exception as e:
        print(f"[{sid}] Error forcing state update: {e}")
        traceback.print_exc()

# Before we create the module system, let's check for common module patterns and provide stubs
def create_stub_modules(temp_dir, files):
    """Create stub modules for common imports students might use."""
    # --- Snake Class Stub ---
    # Check if 'snake_class.py' is referenced but not provided
    needs_snake_class = False
    snake_class_exists = 'snake_class.py' in files
    
    # Look for imports of snake_class in files
    for content in files.values():
        if 'import snake_class' in content or 'from snake_class import' in content:
            needs_snake_class = True
            break
    
    # Create snake_class.py stub if needed
    if needs_snake_class and not snake_class_exists:
        print("Creating stub for snake_class.py")
        snake_class_stub = """
# Auto-generated snake_class stub module
import pygame
import random

# Direction constants in case students import them from here
UP = 'UP' 
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

class Snake:
    def __init__(self):
        self.positions = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
        self.direction = RIGHT
        self.grow = False
        
    def draw(self, screen):
        for position in self.positions:
            x, y = position
            pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
    def update(self):
        head_x, head_y = self.positions[0]
        
        if self.direction == UP:
            new_head = [head_x, head_y - 1]
        elif self.direction == DOWN:
            new_head = [head_x, head_y + 1]
        elif self.direction == LEFT:
            new_head = [head_x - 1, head_y]
        else:  # RIGHT
            new_head = [head_x + 1, head_y]
            
        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        
    def change_direction(self, new_direction):
        self.direction = new_direction
            
    def check_collision(self):
        head = self.positions[0]
        body = self.positions[1:]
        for segment in body:
            if segment[0] == head[0] and segment[1] == head[1]:
                return True
        return False
        
    def grow_snake(self):
        self.grow = True
        
    def check_boundary_collision(self, grid_width, grid_height):
        head_x, head_y = self.positions[0]
        return head_x < 0 or head_x >= grid_width or head_y < 0 or head_y >= grid_height
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "snake_class.py"), "w") as f:
            f.write(snake_class_stub)
        
        # Add to files so it gets loaded
        files["snake_class.py"] = snake_class_stub
        
    # --- Food Class Stub ---
    # Check if 'food_class.py' or 'food.py' is referenced but not provided
    needs_food_class = False
    food_class_exists = 'food_class.py' in files or 'food.py' in files
    
    # Look for imports of food module in files
    for content in files.values():
        if ('import food_class' in content or 'from food_class import' in content or
            'import food' in content or 'from food import' in content):
            needs_food_class = True
            break
    
    # Create food_class.py stub if needed
    if needs_food_class and not food_class_exists:
        print("Creating stub for food_class.py")
        food_class_stub = """
# Auto-generated food_class stub module
import pygame
import random

class Food:
    def __init__(self):
        self.position = self.get_random_position()
        
    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
    def get_random_position(self):
        return [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        
    def reset(self, snake_positions=None):
        # Find a position not occupied by the snake
        new_pos = self.get_random_position()
        if snake_positions:
            # Try to find a position not occupied by the snake
            max_attempts = 100
            attempts = 0
            while new_pos in snake_positions and attempts < max_attempts:
                new_pos = self.get_random_position()
                attempts += 1
        self.position = new_pos
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "food_class.py"), "w") as f:
            f.write(food_class_stub)
        
        # Add to files so it gets loaded
        files["food_class.py"] = food_class_stub
        
        # For compatibility, create food.py with the full Food class implementation
        with open(os.path.join(temp_dir, "food.py"), "w") as f:
            f.write("""
# food.py: Contains the Food class definition
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
        
    def reset(self, snake_positions=None):
        # Find a position not occupied by the snake
        new_pos = self.get_random_position()
        if snake_positions:
            # Try to find a position not occupied by the snake
            max_attempts = 100
            attempts = 0
            while new_pos in snake_positions and attempts < max_attempts:
                new_pos = self.get_random_position()
                attempts += 1
        self.position = new_pos
""")
        # Set the content in files dictionary
        files["food.py"] = food_class_stub  # Use the same content we created for food_class.py
        
    # --- Game Utilities Stub ---
    # Check if game_utils.py is referenced but not provided
    needs_game_utils = False
    game_utils_exists = 'game_utils.py' in files or 'utils.py' in files
    
    # Look for imports of game_utils module in files
    for content in files.values():
        if ('import game_utils' in content or 'from game_utils import' in content or
            'import utils' in content or 'from utils import' in content):
            needs_game_utils = True
            break
    
    # Create game_utils.py stub if needed
    if needs_game_utils and not game_utils_exists:
        print("Creating stub for game_utils.py")
        game_utils_stub = """
# Auto-generated game_utils stub module
import pygame

def draw_grid(screen):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_text(screen, text, position, color=WHITE, font_size=FONT_SIZE):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)
    
def check_collision(pos1, pos2):
    return pos1[0] == pos2[0] and pos1[1] == pos2[1]
    
def game_over_screen(screen, score):
    draw_text(screen, "GAME OVER", (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
    draw_text(screen, f"SCORE: {score}", (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 10))
    draw_text(screen, "Press SPACE to Play Again", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "game_utils.py"), "w") as f:
            f.write(game_utils_stub)
        
        # Add to files so it gets loaded
        files["game_utils.py"] = game_utils_stub
        
        # Also create utils.py as an alias
        with open(os.path.join(temp_dir, "utils.py"), "w") as f:
            f.write("""
# Auto-generated utils.py stub module - redirects to game_utils
from game_utils import *
""")
        files["utils.py"] = "from game_utils import *"
        
    # --- Constants Module ---
    needs_constants = False
    constants_exists = 'constants.py' in files
    
    # Look for imports of constants in files
    for content in files.values():
        if 'import constants' in content or 'from constants import' in content:
            needs_constants = True
            break
    
    # Create constants.py stub if needed
    if needs_constants and not constants_exists:
        print("Creating stub for constants.py")
        constants_stub = """
# Auto-generated constants.py stub module
# Game dimensions
GRID_WIDTH = 30
GRID_HEIGHT = 30
CELL_SIZE = 15
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Game speed
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Font
FONT_SIZE = 36

# Directions
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
"""
        # Write the stub file
        with open(os.path.join(temp_dir, "constants.py"), "w") as f:
            f.write(constants_stub)
        
        # Add to files so it gets loaded
        files["constants.py"] = constants_stub

# Add this function after the create_stub_modules function
def ensure_globals_in_namespace(files, namespace, echo_level=None, sid=None):
    """
    Make sure all necessary global constants are available in the namespace.
    
    Args:
        files: Dict of filename -> content
        namespace: The namespace (dictionary) to populate
        echo_level: Optional echo level (1-10)
        sid: Optional socket session ID for logging
    """
    print(f"[{sid}] Ensuring globals in namespace")
    
    # For better debugging, log which constants are already defined
    constants_to_check = ['CELL_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'BLACK', 'WHITE', 'GREEN', 'RED', 'FPS']
    defined_constants = [const for const in constants_to_check if const in namespace]
    missing_constants = [const for const in constants_to_check if const not in namespace]
    
    print(f"[{sid}] Already defined constants: {defined_constants}")
    print(f"[{sid}] Missing constants: {missing_constants}")
    
    # If constants file exists, it should define these variables
    has_constants_file = False
    constants_content = ""
    
    for filename, content in files.items():
        if filename.lower() == 'constants.py':
            has_constants_file = True
            constants_content = content
            # Parse constants file content to extract values
            print(f"[{sid}] Found constants.py file, checking content")
            
            # For each missing constant, try to extract from the constants file
            for const in missing_constants:
                import re
                match = re.search(f"{const}\\s*=\\s*([^\\n]+)", content)
                if match:
                    try:
                        # Try to evaluate the constant value
                        const_value = eval(match.group(1), {}, {})
                        namespace[const] = const_value
                        print(f"[{sid}] Extracted {const} = {const_value} from constants.py")
                    except Exception as e:
                        print(f"[{sid}] Error evaluating {const}: {e}")
                else:
                    print(f"[{sid}] Constant {const} not found in constants.py")
    
    # If constants file doesn't exist, log a warning
    if not has_constants_file:
        print(f"[{sid}] Warning: No constants.py file found in student code!")
        print(f"[{sid}] Files found: {list(files.keys())}")
    
    # Use default values for missing constants based on echo level
    if 'CELL_SIZE' not in namespace:
        namespace['CELL_SIZE'] = 20
        print(f"[{sid}] Using default CELL_SIZE = 20")
        
    if 'GRID_WIDTH' not in namespace:
        namespace['GRID_WIDTH'] = 30
        print(f"[{sid}] Using default GRID_WIDTH = 30")
        
    if 'GRID_HEIGHT' not in namespace:
        namespace['GRID_HEIGHT'] = 20
        print(f"[{sid}] Using default GRID_HEIGHT = 20")
        
    if 'SCREEN_WIDTH' not in namespace:
        namespace['SCREEN_WIDTH'] = namespace['GRID_WIDTH'] * namespace['CELL_SIZE']
        print(f"[{sid}] Calculated SCREEN_WIDTH = {namespace['SCREEN_WIDTH']}")
        
    if 'SCREEN_HEIGHT' not in namespace:
        namespace['SCREEN_HEIGHT'] = namespace['GRID_HEIGHT'] * namespace['CELL_SIZE']
        print(f"[{sid}] Calculated SCREEN_HEIGHT = {namespace['SCREEN_HEIGHT']}")
    
    # Colors
    if 'BLACK' not in namespace: namespace['BLACK'] = (0, 0, 0)
    if 'WHITE' not in namespace: namespace['WHITE'] = (255, 255, 255)
    if 'GREEN' not in namespace: namespace['GREEN'] = (0, 255, 0)
    if 'RED' not in namespace: namespace['RED'] = (255, 0, 0)
    
    # Game settings
    if 'FPS' not in namespace: namespace['FPS'] = 10
    
    return namespace

# Define a minimalist placeholder when student code is empty or missing
game_code = """
# Error screen for when no student code is available
import pygame
import sys

# Initialize pygame
pygame.init()

# Set default screen size
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 400
screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
pygame.display.set_caption('Snake Echo - Error')
clock = pygame.time.Clock()

# Simple game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Fill the screen with a dark color
    screen.fill((40, 40, 60))
    
    # Display error message
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Missing Student Code", True, (255, 100, 100))
    title_rect = title.get_rect(center=(DEFAULT_WIDTH//2, 100))
    screen.blit(title, title_rect)
    
    # Display instructions
    font = pygame.font.SysFont(None, 32)
    
    msg1 = font.render("This echo requires you to write the snake code.", True, (220, 220, 220))
    msg1_rect = msg1.get_rect(center=(DEFAULT_WIDTH//2, 180))
    screen.blit(msg1, msg1_rect)
    
    msg2 = font.render("Please check the instructions and write your code", True, (220, 220, 220))
    msg2_rect = msg2.get_rect(center=(DEFAULT_WIDTH//2, 220))
    screen.blit(msg2, msg2_rect)
    
    msg3 = font.render("in the appropriate files.", True, (220, 220, 220))
    msg3_rect = msg3.get_rect(center=(DEFAULT_WIDTH//2, 260))
    screen.blit(msg3, msg3_rect)
    
    # Display hint
    hint_font = pygame.font.SysFont(None, 28)
    hint = hint_font.render("Remember: The code you write controls the snake game", True, (150, 255, 150))
    hint_rect = hint.get_rect(center=(DEFAULT_WIDTH//2, 330))
    screen.blit(hint, hint_rect)
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
"""

# --- Top-level student_process for multiprocessing (Windows fix) ---
def student_process(child_conn, temp_dir, student_path):
    import sys, importlib.util, traceback, os
    print('[DEBUG] student_process started')
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.display.set_mode = lambda *args, **kwargs: pygame.Surface((640, 480))
    pygame.display.flip = lambda *args, **kwargs: None
    sys.path.insert(0, temp_dir)
    # Inject custom get_user_direction
    def get_user_direction():
        ns = sys.modules['__main__'].__dict__
        print(f"[DEBUG get_user_direction] Called.")

        # Determine a fallback direction based on snake's current direction if possible
        fallback_direction = 'RIGHT' # Default fallback
        if 'snake' in ns:
            snake_obj = ns['snake']
            if hasattr(snake_obj, 'direction'):
                # This assumes student's snake.direction is a string 'UP', 'DOWN', etc.
                # If it's a tuple (dx, dy) or constant, this part would need adjustment
                # or the student code would rely purely on the received direction.
                if isinstance(snake_obj.direction, str) and snake_obj.direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    fallback_direction = snake_obj.direction

        # Send current game state
        try:
            snake_positions = [[15,10]] # Default
            if 'snake' in ns and hasattr(ns['snake'], 'positions'):
                snake_positions = list(ns['snake'].positions)
            elif 'snake' in ns and isinstance(ns['snake'], list): # Basic list of positions
                snake_positions = ns['snake']

            food_position = [20,10] # Default
            if 'food' in ns and hasattr(ns['food'], 'position'):
                food_position = list(ns['food'].position)
            elif 'food' in ns and isinstance(ns['food'], (list, tuple)): # Basic list/tuple
                food_position = list(ns['food'])

            game_state = {
                'grid_width': ns.get('GRID_WIDTH', 30),
                'grid_height': ns.get('GRID_HEIGHT', 20),
                'snake': snake_positions,
                'food': food_position,
                'score': ns.get('score', 0),
                'game_over': ns.get('game_over', False),
                'message_title': '', 'message_text': '', 'message_hint': ''
            }
            child_conn.send(game_state)
        except Exception as e:
            # Send error if state extraction fails
            child_conn.send({'error': f'Error in get_user_direction while extracting state: {traceback.format_exc()}'})

        # Wait for direction from parent process
        try:
            # Poll for a short time (e.g., up to 50ms, matching frame_delay)
            # This timeout should ideally be less than or equal to frame_delay in run_student_snake
            polled_value = child_conn.poll(0.04)
            print(f"[DEBUG get_user_direction] child_conn.poll(0.04) result: {polled_value}")
            if polled_value:
                new_direction = child_conn.recv()
                print(f"[DEBUG get_user_direction] Received new_direction: {new_direction}")
                if new_direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    print(f"[DEBUG get_user_direction] Returning NEWLY RECEIVED direction: {new_direction}")
            if child_conn.poll(0.04):
                new_direction = child_conn.recv()
                if new_direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    return new_direction
        except EOFError: # Pipe might have been closed
            pass # Will use fallback
        except Exception: # Other potential errors during recv (e.g., timeout, deserialization)
            pass # Will use fallback

        print(f"[DEBUG get_user_direction] Returning FALLBACK direction: {fallback_direction}")
        return fallback_direction
    import builtins
    builtins.get_user_direction = get_user_direction
    try:
        print('[DEBUG] student_process importing student code:', student_path)
        spec = importlib.util.spec_from_file_location("student_main", student_path)
        student_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(student_mod)
        print('[DEBUG] student_process finished student code')
    except Exception as e:
        child_conn.send({'error': traceback.format_exc()})
        print('[DEBUG] error sent (importing student code):', traceback.format_exc())

def run_student_snake(socketio, sid, files, pre_determined_echo_level=None):
    """
    Run the student's snake code in a subprocess, capturing game state as JSON after each frame.
    Inject a custom get_user_direction() that sends state to the parent process after each frame.
    On error, send error state to the client. All file/echo handling is dynamic and global.
    """
    import sys, importlib.util, traceback, time, multiprocessing, os, tempfile, shutil, json
    try:
        # --- PATCH: Enforce headless Pygame and suppress window creation ---
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        import pygame
        pygame.display.set_mode = lambda *args, **kwargs: pygame.Surface((640, 480))
        pygame.display.flip = lambda *args, **kwargs: None
        # ---------------------------------------------------------------

        # Setup: create a temp directory for the student's files
        temp_dir = tempfile.mkdtemp(prefix=f"snake_{sid}_")
        sys.path.insert(0, temp_dir)
        for filename, content in files.items():
            with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
        main_file = 'snake.py' if 'snake.py' in files else 'main.py'
        student_path = os.path.join(temp_dir, main_file)

        # Use multiprocessing Pipe for communication
        parent_conn, child_conn = multiprocessing.Pipe()

        # Start the student process (now top-level)
        proc = multiprocessing.Process(target=student_process, args=(child_conn, temp_dir, student_path))
        proc.start()
        max_frames = 200
        frame_delay = 0.05
        for _ in range(max_frames):
            if parent_conn.poll(timeout=frame_delay * 2):
                msg = parent_conn.recv()
                if isinstance(msg, dict) and 'error' in msg:
                    socketio.emit('preview_error', {'error': msg['error']}, room=sid)
                    break
                else:
                    socketio.emit('game_state_update', msg, room=sid)

                # Send the current direction from client_inputs to the student_process
                # Default to 'RIGHT' if no input has been registered for the session yet
                current_input = client_inputs.get(sid, 'RIGHT')
                print(f"[DEBUG run_student_snake SID: {sid}] Sending to student_process direction: {current_input}")
                parent_conn.send(current_input)
            if not proc.is_alive():
                break
        proc.terminate()
        proc.join(timeout=0.5)
        shutil.rmtree(temp_dir)
    except Exception as e:
        socketio.emit('preview_error', {'error': f'Internal error: {traceback.format_exc()}'}, room=sid)

# --- Standalone gameplay code below ---
# This code is only used when running the file directly (not when imported)
if __name__ == "__main__" and not os.environ.get('SDL_VIDEODRIVER') == 'dummy':
    # Set SDL_VIDEODRIVER to 'dummy' to prevent window from opening when testing
    os.environ['SDL_VIDEODRIVER'] = 'dummy' 
    
    # --- Initialization ---
    pygame.init()

    # --- Screen Setup ---
    window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Snake Echo')
    clock = pygame.time.Clock()

    # --- Game Variables ---
    score = 0
    game_over = False

    # Function to get user input from the frontend
    # (This is provided by the simulation framework)
    def get_user_direction():
        return 'RIGHT'  # Default direction if no input available

    # --- Game Text Rendering ---
    def render_text(text, size, color, position):
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

    # --- Snake Class ---
    class Snake:
        def __init__(self):
            # Initialize the snake at the center of the screen
            self.positions = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
            self.direction = RIGHT
            self.grow = False
        
        def draw(self, screen):
            # Draw the snake segments
            for position in self.positions:
                pygame.draw.rect(screen, GREEN, 
                                (position[0] * CELL_SIZE, position[1] * CELL_SIZE, 
                                 CELL_SIZE, CELL_SIZE))
        
        def update(self):
            # Create a new head position based on current direction
            head = self.positions[0].copy()
            
            # Update the head based on direction
            if self.direction == UP:
                head[1] -= 1
            elif self.direction == DOWN:
                head[1] += 1
            elif self.direction == LEFT:
                head[0] -= 1
            elif self.direction == RIGHT:
                head[0] += 1
            
            # Add the new head
            self.positions.insert(0, head)
            
            # Remove the tail unless we need to grow
            if not self.grow:
                self.positions.pop()
            else:
                self.grow = False
            
            # Wrap around behavior for edges
            if head[0] < 0:
                head[0] = GRID_WIDTH - 1
            elif head[0] >= GRID_WIDTH:
                head[0] = 0
            if head[1] < 0:
                head[1] = GRID_HEIGHT - 1
            elif head[1] >= GRID_HEIGHT:
                head[1] = 0
        
        def check_collision(self):
            # Check if snake collides with itself
            head = self.positions[0]
            body = self.positions[1:]
            for segment in body:
                if segment[0] == head[0] and segment[1] == head[1]:
                    return True
            return False
        
        def grow_snake(self):
            self.grow = True

    # --- Food Class ---
    class Food:
        def __init__(self):
            # Initialize food at a random position
            self.position = self.get_random_position()
            
        def draw(self, screen):
            # Draw the food
            pygame.draw.rect(screen, RED, 
                            (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, 
                             CELL_SIZE, CELL_SIZE))
            
        def get_random_position(self):
            # Place food at a random position on the grid
            return [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        
        def reposition(self, snake_positions):
            # Reposition food, ensuring it's not on the snake
            self.position = self.get_random_position()
            while self.position in snake_positions:
                self.position = self.get_random_position()

    # Create snake and food instances
    snake = Snake()
    food = Food()

    # --- Game Loop ---
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == K_SPACE and game_over:
                    # Reset the game
                    snake = Snake()
                    food = Food()
                    score = 0
                    game_over = False
        
        # Get direction from user input if available
        if not game_over:
            user_dir = get_user_direction()
            if user_dir == UP and snake.direction != DOWN:
                snake.direction = UP
            elif user_dir == DOWN and snake.direction != UP:
                snake.direction = DOWN
            elif user_dir == LEFT and snake.direction != RIGHT:
                snake.direction = LEFT
            elif user_dir == RIGHT and snake.direction != LEFT:
                snake.direction = RIGHT
        
        # Update game state if not game over
        if not game_over:
            # Update snake position
            snake.update()
            
            # Check for collision with food
            snake_head = snake.positions[0]
            food_pos = food.position
            if snake_head[0] == food_pos[0] and snake_head[1] == food_pos[1]:
                snake.grow_snake()
                food.reposition(snake.positions)
                score += 1
            
            # Check for collision with self
            if snake.check_collision():
                game_over = True
        
        # Draw everything
        screen.fill(BG_COLOR)
        
        # Draw snake and food
        snake.draw(screen)
        food.draw(screen)
        
        # Display score
        render_text(f"Score: {score}", SMALL_FONT_SIZE, TEXT_COLOR, 
                    (SCORE_POS[0] + 50, SCORE_POS[1] + 10))
        
        # Display game over message
        if game_over:
            render_text(GAME_OVER_TEXT, LARGE_FONT_SIZE, GAME_OVER_COLOR, 
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            render_text(f"Final Score: {score}", MEDIUM_FONT_SIZE, TEXT_COLOR, 
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            render_text(RESTART_TEXT, SMALL_FONT_SIZE, TEXT_COLOR, 
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Update display
        pygame.display.flip()
        
        # Maintain game speed
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()
