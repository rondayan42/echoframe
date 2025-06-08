import pygame
from pygame import mixer
import sys
import math
import random
import time
import json
import os
import traceback
import numpy
from datetime import datetime, timedelta
import logging
import textwrap

# --- Setup Basic Logging ---
log_file_path = os.path.join(os.path.dirname(__file__), 'slith_pet.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    filemode='a'
)
print(f"DEBUG: Logging to {log_file_path}")
logging.info("--- Slith Pet Script Started ---")

# --- Determine Script Directory for Absolute Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logging.info(f"Script directory: {SCRIPT_DIR}")

# --- Imports ---
try:
    from slith_sprites import SlithSprite, FoodItem, LoveItem, EntertainmentItem, WaterItem, draw_pixel_rect, draw_pixel_circle, draw_pixel_oval, draw_pixel_line
    logging.info("Successfully imported from slith_sprites.")
except ImportError as e:
    logging.error(f"Failed to import from slith_sprites: {e}. Make sure slith_sprites.py exists and has no errors.")
    def draw_pixel_rect(surface, color, rect, pixel_size): pygame.draw.rect(surface, color, rect)
    def draw_pixel_circle(surface, color, center, radius, pixel_size): pygame.draw.circle(surface, color, center, radius)
    def draw_pixel_oval(surface, color, rect, pixel_size): pygame.draw.ellipse(surface, color, rect)
    def draw_pixel_line(surface, color, start, end, pixel_size): pygame.draw.line(surface, color, start, end)
    logging.warning("draw_pixel_* helpers not found in slith_sprites, using basic pygame draw.")
    class SlithSprite:
        def __init__(self, stage): self.stage = stage; self.rect = pygame.Rect(0,0,50,50); self.x=0; self.y=0; self.pixel_size=2; self.state='idle'; self.accessories={}; self.last_head_pos=(0,0); self.last_head_size=0
        def update(self, frame): pass
        def draw(self, surface, accessories=None): pygame.draw.rect(surface, (255,255,0), self.rect)
        def set_state(self, state): self.state = state
        def set_back_turned(self, turned): pass
        def update_accessories(self, acc): self.accessories = acc
    class CareItem:
        def __init__(self,x,y,c,i): self.rect=pygame.Rect(x-15,y-15,30,30); self.x=x; self.y=y; self.hovered=False
        def update(self): pass
        def draw(self, surface): pygame.draw.rect(surface, self.rect)
    class FoodItem(CareItem): pass
    class LoveItem(CareItem): pass
    class EntertainmentItem(CareItem): pass
    class WaterItem(CareItem): pass

try:
    from slith_constants import (
        WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLORS, STAGES, VITALS,
        ANIMATION_STATES, PIXEL_SCALE, UI, STORE_ITEMS, ACCESSORY_SLOTS,
        MAX_PATIENCE, FEED_PATIENCE_GAIN, CLEAN_PATIENCE_GAIN, PET_PATIENCE_GAIN,
        FEED_COOLDOWN, CLEAN_COOLDOWN, PET_COOLDOWN, SAVE_INTERVAL, UPDATE_INTERVAL,
        BITS_INITIAL_AMOUNT, BITS_MINIGAME_PATIENCE_MULTIPLIER,
        MOOD_HAPPY_THRESHOLD, MOOD_NEUTRAL_THRESHOLD
    )
    logging.info("Successfully imported from slith_constants.")
except ImportError as e:
    logging.error(f"Failed to import from slith_constants: {e}. Using fallback values.")
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS = 600, 700, 60
    COLORS = {'bg': (20, 12, 28), 'bg_dark': (10, 8, 16), 'neon': (255, 221, 0), 'accent': (255, 105, 180), 'text':(220, 220, 255), 'danger': (255,0,0), 'warning':(255,165,0), 'food':(255,100,100), 'water':(80,160,255), 'entertainment':(170,100,255), 'love':(255,100,255), 'egg_shell': (210, 180, 140), 'grid':(40,40,60), 'highlight':(0,255,200), 'terminal':(0,200,80), 'hacker_text':(0,255,0)}
    STAGES = { i: {'name': f'Stage {i}'} for i in range(11) }
    VITALS = {'patience_messages': {0:["..."]}, 'decay_rates':{'patience': 4, 'food': 5, 'water': 5, 'entertainment': 3, 'love': 2}}
    ANIMATION_STATES = ['idle', 'happy', 'sad', 'back_turned']
    PIXEL_SCALE = 2
    UI = {'panel_margin': 10, 'panel_padding': 8, 'border_thickness': 2, 'button_padding': 6, 'progress_height': 15, 'progress_border': 2, 'grid_size': 10, 'speech_bubble_width': 450, 'speech_bubble_height': 100, 'speech_bubble_margin': 30}
    STORE_ITEMS = {
        'top_hat': { 'name': 'Top Hat', 'description': 'A fancy black top hat.', 'price': 100, 'type': 'accessory', 'slot': 'head' },
        'corpo_rat': { 'name': 'Corpo Rat', 'description': 'Slows patience decay.', 'price': 150, 'type': 'food', 'effect': {'patience_decay_multiplier': 0.5, 'duration': 14400}}
    }
    ACCESSORY_SLOTS = ['head', 'glasses', 'neck', 'back']
    MAX_PATIENCE=100; FEED_PATIENCE_GAIN=20; CLEAN_PATIENCE_GAIN=15; PET_PATIENCE_GAIN=10
    FEED_COOLDOWN=3600; CLEAN_COOLDOWN=7200; PET_COOLDOWN=600; SAVE_INTERVAL=60; UPDATE_INTERVAL=1
    BITS_INITIAL_AMOUNT=50; BITS_MINIGAME_PATIENCE_MULTIPLIER=2
    MOOD_HAPPY_THRESHOLD=70; MOOD_NEUTRAL_THRESHOLD=30

try:
    from slith_utils import update_pet_vitals as util_update_pet_vitals, determine_slith_stage, format_time_delta
    from slith_utils import draw_text as util_draw_text, draw_progress_bar as util_draw_progress_bar
    logging.info("Successfully imported from slith_utils.")
except ImportError:
    logging.warning("slith_utils not found or missing functions. Using placeholder draw/update functions.")
    def util_update_pet_vitals(pet_data): return pet_data
    def determine_slith_stage(completed_quests_list, snake_intro_seen, total_beginner=None):
        return 0
    def format_time_delta(seconds):
        if seconds < 60: return f"{int(seconds)}s"
        elif seconds < 3600: return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else: return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
    def util_draw_text(surface, text, font, color, x, y, centered=True, **kwargs):
        surf = font.render(text, True, color); rect = surf.get_rect()
        if centered: rect.center = (x, y)
        else: rect.topleft = (x, y)
        surface.blit(surf, rect)
    def util_draw_progress_bar(surface, x, y, width, height, percentage, color, **kwargs):
        pygame.draw.rect(surface, (50,50,50), (x, y, width, height))
        fill_w = int(width * (percentage / 100)); pygame.draw.rect(surface, color, (x, y, fill_w, height))

try:
    from slith_dialogue import DialogueManager, SNAKE_CARETAKER_INTRO
    logging.info("Successfully imported DialogueManager.")
except ImportError as e:
    logging.error(f"Failed to import DialogueManager: {e}. Dialogue intro will not work.")
    class DialogueManager:
        def __init__(self, *args, **kwargs): self.active = False; self.font=None; self.npc_font=None; self.box_rect=pygame.Rect(0,0,100,50); self.text_area_rect=pygame.Rect(0,0,100,50); self.text_margin_x=5; self.text_margin_y=5; self.line_height=10
        def start_dialogue(self, *args, **kwargs): pass
        def stop_dialogue(self): pass
        def handle_input(self, event): return False
        def draw(self, surface): pass
        def _render_text_with_markup(self, *args): pass
    SNAKE_CARETAKER_INTRO = [("Error", "Dialogue module failed to load.")]

try:
    from slith_minigames import NodeDefenderGame, TerminalTyperGame, NeonJetpackGame, SignalTracerGame
    minigame_classes = {
        'NodeDefenderGame': NodeDefenderGame,
        'TerminalTyperGame': TerminalTyperGame,
        'NeonJetpackGame': NeonJetpackGame,
        'SignalTracerGame': SignalTracerGame
    }
    for name, cls in minigame_classes.items():
        if not hasattr(cls, 'run'):
            logging.error(f"Minigame class {name} missing 'run' method.")
            raise ImportError(f"Invalid {name} class")
    MINIGAMES_AVAILABLE = True
    logging.info("Successfully imported minigame classes: NodeDefenderGame, TerminalTyperGame, NeonJetpackGame, SignalTracerGame")
except ImportError as e:
    logging.warning(f"slith_minigames.py import failed: {e}. Minigames will be disabled.")
    MINIGAMES_AVAILABLE = False
    class BaseMinigame:
        def __init__(self, screen, clock): pass
        def run(self): return 0, 0
    NodeDefenderGame = TerminalTyperGame = NeonJetpackGame = SignalTracerGame = BaseMinigame

# --- Storage Path & Load/Save Functions ---
STORAGE_DIR = os.path.join(SCRIPT_DIR, 'user_data')
logging.info(f"User data storage directory: {STORAGE_DIR}")

def load_pet_data_direct(username):
    filename = os.path.join(STORAGE_DIR, f"{username}.json")
    default_vitals = {'food': 100, 'water': 100, 'entertainment': 100, 'love': 100, 'patience': 100}
    default_pet_state = {
        'stage': 0, 'unlocked': False, 'vitals': default_vitals.copy(),
        'last_interaction': datetime.now().isoformat(), 'last_check': datetime.now().isoformat(),
        'snaker_bits': BITS_INITIAL_AMOUNT,
        'accessories': {slot: None for slot in ACCESSORY_SLOTS},
        'inventory': {'food': {}, 'accessories': {}},
        'active_food_effects': [], 'intro_completed': False,
        'last_update_time': time.time(),
        'last_interaction_times': {},
        'high_scores': {'node_defender': 0, 'terminal_typer': 0, 'neon_jetpack': 0, 'signal_tracer': 0}
    }
    default_user_data = { 'slith_pet': default_pet_state, 'completed': [], 'snake_intro_seen': False }
    if not os.path.exists(filename):
        logging.warning(f"Load: Pet data file not found for {username} at {filename}. Returning defaults.")
        return default_user_data
    try:
        with open(filename, 'r', encoding='utf-8') as f: data = json.load(f)
        logging.info(f"Load: Successfully read JSON from {filename}")
        merged_data = default_user_data.copy(); merged_data.update(data)
        if 'slith_pet' not in merged_data or not isinstance(merged_data['slith_pet'], dict):
            merged_data['slith_pet'] = default_pet_state
        else:
            pet_state = default_pet_state.copy(); pet_state.update(merged_data['slith_pet'])
            merged_data['slith_pet'] = pet_state
            if not isinstance(pet_state.get('vitals'), dict): pet_state['vitals'] = default_vitals.copy()
            else: vitals_loaded = default_vitals.copy(); vitals_loaded.update(pet_state['vitals']); pet_state['vitals'] = vitals_loaded
            if not isinstance(pet_state.get('accessories'), dict): pet_state['accessories'] = {slot: None for slot in ACCESSORY_SLOTS}
            else: acc_loaded = {slot: None for slot in ACCESSORY_SLOTS}; acc_loaded.update(pet_state['accessories']); pet_state['accessories'] = acc_loaded
            if not isinstance(pet_state.get('inventory'), dict): pet_state['inventory'] = {'food': {}, 'accessories': {}}
            if not isinstance(pet_state.get('inventory', {}).get('food'), dict): pet_state['inventory']['food'] = {}
            if not isinstance(pet_state.get('inventory', {}).get('accessories'), dict): pet_state['inventory']['accessories'] = {}
            if not isinstance(pet_state.get('active_food_effects'), list): pet_state['active_food_effects'] = []
            if not isinstance(pet_state.get('last_interaction_times'), dict): pet_state['last_interaction_times'] = {}
            if not isinstance(pet_state.get('high_scores'), dict): pet_state['high_scores'] = default_pet_state['high_scores'].copy()
        if 'completed' not in merged_data or not isinstance(merged_data['completed'], list): merged_data['completed'] = []
        if 'snake_intro_seen' not in merged_data or not isinstance(merged_data['snake_intro_seen'], bool): merged_data['snake_intro_seen'] = False
        logging.info(f"Load: Returning loaded/merged data for {username}")
        return merged_data
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Load: Error loading pet data for {username}: {e}. Returning defaults.")
        return default_user_data
    except Exception as e:
        logging.error(f"Load: Unexpected error loading data for {username}: {e}", exc_info=True)
        return default_user_data

def save_pet_data_direct(username, user_data):
    filename = os.path.join(STORAGE_DIR, f"{username}.json")
    try:
        if 'slith_pet' in user_data and isinstance(user_data['slith_pet'], dict):
            if 'last_update_time' not in user_data['slith_pet']: user_data['slith_pet']['last_update_time'] = time.time()
            if 'vitals' not in user_data['slith_pet'] or not isinstance(user_data['slith_pet']['vitals'], dict):
                 user_data['slith_pet']['vitals'] = {'food': 100, 'water': 100, 'entertainment': 100, 'love': 100, 'patience': 100}
        os.makedirs(STORAGE_DIR, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f: json.dump(user_data, f, indent=2)
        logging.info(f"Save: Saved pet data for {username} to {filename}")
    except IOError as e:
        logging.error(f"Save: Error saving pet data for {username}: {e}")
    except Exception as e:
        logging.error(f"Save: Unexpected error saving data for {username}: {e}", exc_info=True)

def generate_beep(frequency=440, duration_ms=100, volume=0.1, sample_rate=44100):
    sound = None
    try:
        if not mixer.get_init():
             logging.warning("Mixer not initialized in generate_beep. Initializing now.")
             mixer.init()
             if not mixer.get_init():
                  logging.error("Failed to initialize mixer even after trying in generate_beep.")
                  return None
        num_samples = int(sample_rate * duration_ms / 1000.0)
        buf = numpy.zeros((num_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        for i in range(num_samples):
            t = float(i) / sample_rate
            sine_val = math.sin(2.0 * math.pi * frequency * t)
            sample_val = int(max_sample * volume * sine_val)
            buf[i][0] = sample_val; buf[i][1] = sample_val
        sound = pygame.sndarray.make_sound(buf)
    except Exception as e:
        logging.error(f"Error generating sound: {e}", exc_info=True)
    return sound

class SlithPetGame:
    def __init__(self, username, initial_user_data):
        logging.info(f"Initializing SlithPetGame for user: {username}...")
        self.username = username
        mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        mixer.init()
        pygame.font.init()
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.DOUBLEBUF)
        pygame.display.set_caption('Slith Pet')
        self.clock = pygame.time.Clock()
        self.user_data = initial_user_data
        self.pet_state = self.user_data.get('slith_pet', {})
        self.current_stage = self.pet_state.get('stage', 0)
        self.vitals = self.pet_state.get('vitals', {'food': 100, 'water': 100, 'entertainment': 100, 'love': 100, 'patience': 100})
        self.snaker_bits = self.pet_state.get('snaker_bits', BITS_INITIAL_AMOUNT)
        self.accessories = self.pet_state.get('accessories', {slot: None for slot in ACCESSORY_SLOTS})
        self.inventory = self.pet_state.get('inventory', {'food': {}, 'accessories': {}})
        self.active_food_effects = self.pet_state.get('active_food_effects', [])
        self.intro_completed = self.pet_state.get('intro_completed', False)
        self.high_scores = self.pet_state.get('high_scores', {'node_defender': 0, 'terminal_typer': 0, 'neon_jetpack': 0, 'signal_tracer': 0})
        self.last_update_time = self.pet_state.get('last_update_time', time.time())
        self.last_save_time = time.time()
        self.last_interaction_times = self.pet_state.get("last_interaction_times", {})
        font_filename = 'PressStart2P-Regular.ttf'
        font_path = os.path.join(SCRIPT_DIR, font_filename)
        self.replay_intro_button_rect = pygame.Rect(10, 10, 120, 25)
        self.replay_intro_active = False
        try:
            self.title_font = pygame.font.Font(font_path, 16)
            self.regular_font = pygame.font.Font(font_path, 10)
            self.small_font = pygame.font.Font(font_path, 8)
        except:
            self.title_font = pygame.font.Font(None, 36)
            self.regular_font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 16)
        self.background_image = None
        try:
            bg_path = os.path.join(SCRIPT_DIR, 'static', 'img', 'pet_background.png')
            self.background_image = pygame.image.load(bg_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (self.window_width, self.window_height))
        except:
            pass
        self.music_muted = False
        if mixer.get_init():
            try:
                music_path = os.path.join(SCRIPT_DIR, 'static', 'audio', 'pet_bgm.wav')
                mixer.music.load(music_path)
                mixer.music.set_volume(0.4)
                mixer.music.play(-1)
            except:
                pass
        self.click_sound = generate_beep(880, 50, 0.1)
        self.happy_sound = generate_beep(1200, 150, 0.15)
        self.close_sound = generate_beep(440, 80, 0.1)
        self.error_sound = generate_beep(220, 200, 0.1)
        self.bit_sound = generate_beep(1500, 70, 0.1)
        self.slith = SlithSprite(self.current_stage)
        self.slith.x = self.window_width // 2
        self.slith.y = self.window_height // 2 + 50
        self.slith.update_accessories(self.accessories)
        item_y = self.window_height - 50
        item_spacing = 100
        total_items_width = 4 * item_spacing
        item_start_x = (self.window_width - total_items_width) // 2 + item_spacing // 2
        try:
            # Try with 2 arguments (x, y)
            self.items = {
                'food': FoodItem(item_start_x + 0 * item_spacing, item_y),
                'water': WaterItem(item_start_x + 1 * item_spacing, item_y),
                'entertainment': EntertainmentItem(item_start_x + 2 * item_spacing, item_y),
                'love': LoveItem(item_start_x + 3 * item_spacing, item_y)
            }
        except TypeError:
            # If that fails, try with the original approach but log it
            logging.warning("Trying alternative initialization for care items")
            self.items = {}
            try:
                self.items['food'] = FoodItem(item_start_x + 0 * item_spacing, item_y, COLORS.get('food'), 0)
            except TypeError:
                logging.error("Cannot initialize FoodItem - check its constructor")
                self.items['food'] = None
            try:
                self.items['water'] = WaterItem(item_start_x + 1 * item_spacing, item_y, COLORS.get('water'), 1)
            except TypeError:
                logging.error("Cannot initialize WaterItem - check its constructor")
                self.items['water'] = None
            try:
                self.items['entertainment'] = EntertainmentItem(item_start_x + 2 * item_spacing, item_y, COLORS.get('entertainment'), 2)
            except TypeError:
                logging.error("Cannot initialize EntertainmentItem - check its constructor")
                self.items['entertainment'] = None
            try:
                self.items['love'] = LoveItem(item_start_x + 3 * item_spacing, item_y, COLORS.get('love'), 3)
            except TypeError:
                logging.error("Cannot initialize LoveItem - check its constructor")
                self.items['love'] = None
        self.dialogue_manager = DialogueManager(self.window_width, self.window_height, font_path=font_path, font_size=10)
        self.game_state = 'main'
        self.running = True
        self.message = self.get_mood_message()
        self.message_timer = 0
        self.show_celebration = False
        self.celebration_timer = 0
        self.animation_timer = 0
        self.animation_frame = 0
        self.return_button_rect = pygame.Rect(10, self.window_height - 40, 100, 30)
        mute_button_size = 30
        self.mute_button_rect = pygame.Rect(self.window_width - mute_button_size - 10, 10, mute_button_size, mute_button_size)
        button_y = self.window_height - 140
        button_w = 110; button_h = 30; button_spacing = 120
        button_start_x = (self.window_width - (3 * button_w + 2 * (button_spacing-button_w))) // 2
        self.store_button_rect = pygame.Rect(button_start_x, button_y, button_w, button_h)
        self.inventory_button_rect = pygame.Rect(button_start_x + button_spacing, button_y, button_w, button_h)
        self.minigame_button_rect = pygame.Rect(button_start_x + 2 * button_spacing, button_y, button_w, button_h)
        self.store_back_button_rect = pygame.Rect(self.window_width - 150, self.window_height - 50, 100, 30)
        self.inventory_back_button_rect = pygame.Rect(self.window_width - 150, self.window_height - 50, 100, 30)
        self.minigame_back_button_rect = pygame.Rect(50, self.window_height - 80, 100, 40)
        self.minigame_play_button_rect = pygame.Rect(self.window_width - 150, self.window_height - 80, 100, 40)
        tab_y = 100; tab_w = 100; tab_h = 30
        self.inventory_food_tab_rect = pygame.Rect(50, tab_y, tab_w, tab_h)
        self.inventory_acc_tab_rect = pygame.Rect(50 + tab_w + 10, tab_y, tab_w, tab_h)
        categories = ['all', 'food', 'accessory']
        self.store_category_rects = {cat: pygame.Rect(50 + i*120, 100, 100, 30) for i, cat in enumerate(categories)}
        self.button_hover = None
        self.store_selected_category = 'all'
        self.store_scroll_offset = 0
        self.store_items_per_page = 4
        self.minigame_selected_index = 0
        self.inventory_selected_tab = 'food'
        self.inventory_scroll_offset = 0
        self.inventory_items_per_page = 5
        if self.pet_state.pop('just_hatched', False):
            self.show_celebration = True
            self.celebration_timer = 5 * FPS
            self.message = "Slith is breaking through..."
            if self.happy_sound: self.happy_sound.play()
            save_pet_data_direct(self.username, self.user_data)
        elif not self.intro_completed:
            self.start_intro_if_needed()

    def _update_mood(self):
        patience_val = self.vitals.get('patience', 100)
        new_mood = "neutral"
        if patience_val >= MOOD_HAPPY_THRESHOLD: new_mood = "happy"
        elif patience_val < MOOD_NEUTRAL_THRESHOLD: new_mood = "sad"
        if hasattr(self, 'slith') and self.slith.state != 'back_turned':
            if new_mood == "happy": self.slith.set_state('happy')
            elif new_mood == "sad": self.slith.set_state('sad')
            else: self.slith.set_state('idle')

    def get_patience_decay_multiplier(self):
        modifier = 1.0
        now = time.time()
        valid_effects = []
        modifier_effect_found = False
        for effect in self.active_food_effects:
            try:
                expiry_time = datetime.fromisoformat(effect.get('expires', '')).timestamp() if isinstance(effect.get('expires'), str) else effect.get('expires', 0)
                if expiry_time > now:
                    valid_effects.append(effect)
                    if effect.get('type') == 'patience_decay_multiplier':
                        current_effect_value = effect.get('value', 1.0)
                        if not modifier_effect_found or current_effect_value < modifier:
                            modifier = current_effect_value
                            modifier_effect_found = True
                else:
                    logging.info(f"Food effect expired: {effect.get('source_item')}")
            except (ValueError, TypeError) as e:
                logging.warning(f"Error processing food effect expiry '{effect.get('expires')}': {e}")
        self.active_food_effects = valid_effects
        if self.game_state == 'playing_minigame':
            modifier *= BITS_MINIGAME_PATIENCE_MULTIPLIER
        return modifier

    def update_patience(self):
        if self.game_state in ['dialogue']:
            self.last_update_time = time.time()
            return False
        now = time.time()
        time_diff_seconds = now - self.last_update_time
        if time_diff_seconds <= 0.1:
            return False
        base_hourly_decay = VITALS.get('decay_rates', {}).get('patience', 4)
        base_per_second_decay = base_hourly_decay / 3600.0
        decay_modifier = self.get_patience_decay_multiplier()
        effective_per_second_decay = base_per_second_decay * decay_modifier
        decay_amount = effective_per_second_decay * time_diff_seconds
        state_changed = False
        if decay_amount > 0:
            current_patience = self.vitals.get('patience', 100)
            new_patience = max(0, current_patience - decay_amount)
            if abs(new_patience - current_patience) > 0.01:
                self.vitals['patience'] = new_patience
                self._update_mood()
                state_changed = True
        self.last_update_time = now
        return state_changed

    def _can_interact(self, action):
        now = time.time()
        last_time = self.last_interaction_times.get(action, 0)
        cooldown_map = {"feed": FEED_COOLDOWN, "clean": CLEAN_COOLDOWN, "pet": PET_COOLDOWN}
        cooldown = cooldown_map.get(action, 0)
        return now - last_time >= cooldown

    def _record_interaction(self, action):
        self.last_interaction_times[action] = time.time()

    def feed(self):
        if self.vitals['food'] < 100:
            self.vitals['food'] = min(100, self.vitals['food'] + 25)
            self.vitals['patience'] = min(MAX_PATIENCE, self.vitals['patience'] + FEED_PATIENCE_GAIN // 4)
            self.message = "Yum! Standard rations."
            self.message_timer = 2 * FPS
            if self.happy_sound: self.happy_sound.play()
            self.slith.set_state('happy')
            logging.info(f"{self.username} used standard feed.")
            return True, "Standard feed given."
        else:
            self.message = "Not hungry for standard rations."
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, "Not hungry."

    def clean(self):
        if not self._can_interact("clean"):
            remaining = CLEAN_COOLDOWN - (time.time() - self.last_interaction_times.get("clean", 0))
            self.message = f"Cleaning on cooldown ({format_time_delta(remaining)} left)."
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, "Clean action is on cooldown."
        self.vitals['patience'] = min(MAX_PATIENCE, self.vitals['patience'] + CLEAN_PATIENCE_GAIN)
        self._record_interaction("clean")
        self.message = "Feeling refreshed!"
        self.message_timer = 2 * FPS
        if self.happy_sound: self.happy_sound.play()
        self.slith.set_state('happy')
        logging.info(f"{self.username} cleaned Slith.")
        return True, "Slith feels refreshed!"

    def pet(self):
        if not self._can_interact("pet"):
            remaining = PET_COOLDOWN - (time.time() - self.last_interaction_times.get("pet", 0))
            self.message = f"Petting on cooldown ({format_time_delta(remaining)} left)."
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, "Pet action is on cooldown."
        self.vitals['love'] = min(100, self.vitals['love'] + 15)
        self.vitals['patience'] = min(MAX_PATIENCE, self.vitals['patience'] + PET_PATIENCE_GAIN)
        self._record_interaction("pet")
        self.message = "Slith seems happier!"
        self.message_timer = 2 * FPS
        if self.happy_sound: self.happy_sound.play()
        self.slith.set_state('happy')
        logging.info(f"{self.username} petted Slith.")
        return True, "Slith seems happier!"

    def add_bits(self, amount):
        if amount <= 0: return False, "Amount must be positive."
        self.snaker_bits += amount
        logging.info(f"{self.username} gained {amount} snaker_bits. Total: {self.snaker_bits}")
        if self.bit_sound: self.bit_sound.play()
        return True, f"Gained {amount} snaker_bits!"

    def spend_bits(self, amount):
        if amount <= 0: return False, "Amount must be positive."
        if self.snaker_bits >= amount:
            self.snaker_bits -= amount
            logging.info(f"{self.username} spent {amount} snaker_bits. Remaining: {self.snaker_bits}")
            return True, f"Spent {amount} snaker_bits."
        else:
            logging.warning(f"{self.username} attempted to spend {amount} bits, but only has {self.snaker_bits}.")
            if self.error_sound: self.error_sound.play()
            self.message = "Not enough snaker_bits!"
            self.message_timer = 2 * FPS
            return False, "Not enough snaker_bits."

    def add_to_inventory(self, item_id, quantity=1):
        if item_id not in STORE_ITEMS: return False, "Invalid item ID."
        item_info = STORE_ITEMS[item_id]
        item_type = item_info['type']
        if item_type == 'food':
            self.inventory['food'][item_id] = self.inventory['food'].get(item_id, 0) + quantity
        elif item_type == 'accessory':
            if item_id not in self.inventory['accessories']:
                self.inventory['accessories'][item_id] = {'owned': True}
        else:
            return False, "Unknown item type."
        logging.info(f"{self.username} added {quantity}x {item_id} ({item_type}) to inventory.")
        return True, f"Added {item_info['name']} to inventory."

    def buy_item(self, item_id):
        if item_id not in STORE_ITEMS: return False, "Item not found in store."
        item_info = STORE_ITEMS[item_id]
        price = item_info['price']
        if item_info['type'] == 'accessory' and item_id in self.inventory.get('accessories', {}):
            self.message = f"Already own {item_info['name']}."
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, f"You already own {item_info['name']}."
        success, message = self.spend_bits(price)
        if not success: return False, message
        add_success, add_message = self.add_to_inventory(item_id)
        if not add_success:
            self.add_bits(price)
            logging.error(f"Failed to add {item_id} to inventory for {self.username} after purchase. Refunded.")
            self.message = f"Purchase failed: {add_message}"
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, f"Purchase failed: {add_message}"
        logging.info(f"{self.username} purchased {item_id} for {price} bits.")
        self.message = f"Purchased {item_info['name']}!"
        self.message_timer = 2 * FPS
        if self.happy_sound: self.happy_sound.play()
        return True, f"Successfully purchased {item_info['name']}!"

    def use_food_item(self, item_id):
        if item_id not in STORE_ITEMS or STORE_ITEMS[item_id]['type'] != 'food':
            return False, "Invalid food item ID."
        if item_id not in self.inventory.get('food', {}) or self.inventory['food'][item_id] <= 0:
            self.message = "You don't have that food."
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, "You don't have this food item."
        self.inventory['food'][item_id] -= 1
        if self.inventory['food'][item_id] == 0:
            del self.inventory['food'][item_id]
        item_info = STORE_ITEMS[item_id]
        effect = item_info.get('effect')
        applied_effect = False
        if effect and 'patience_decay_multiplier' in effect and 'duration' in effect:
            now_dt = datetime.now()
            expires_dt = now_dt + timedelta(seconds=effect['duration'])
            expires_iso = expires_dt.isoformat()
            new_effect = {'type': 'patience_decay_multiplier', 'value': effect['patience_decay_multiplier'], 'expires': expires_iso, 'source_item': item_id}
            self.active_food_effects = [e for e in self.active_food_effects if e.get('type') != 'patience_decay_multiplier']
            self.active_food_effects.append(new_effect)
            logging.info(f"{self.username} used {item_id}. Effect applied: {new_effect}")
            self.message = f"Ate {item_info['name']}! Effect active."
            applied_effect = True
        else:
            logging.warning(f"Food item {item_id} used but has no valid effect.")
            self.vitals['food'] = min(100, self.vitals['food'] + 5)
            self.vitals['patience'] = min(MAX_PATIENCE, self.vitals['patience'] + 2)
            self.message = f"Ate {item_info['name']}."
        self.message_timer = 2 * FPS
        if self.happy_sound: self.happy_sound.play()
        return True, f"Used {item_info['name']}. Effect applied: {applied_effect}"

    def equip_accessory(self, item_id):
        if item_id not in STORE_ITEMS or STORE_ITEMS[item_id]['type'] != 'accessory':
            return False, "Invalid accessory item ID."
        if item_id not in self.inventory.get('accessories', {}):
            self.message = "You don't own that."
            self.message_timer = 2 * FPS
            if self.error_sound: self.error_sound.play()
            return False, "You do not own this accessory."
        item_info = STORE_ITEMS[item_id]
        slot = item_info.get('slot', 'unknown')
        currently_equipped = self.accessories.get(slot)
        if currently_equipped == item_id:
            self.accessories[slot] = None
            message = f"Unequipped {item_info['name']}."
            logging.info(f"{self.username} unequipped {item_id} from slot {slot}.")
        else:
            self.accessories[slot] = item_id
            message = f"Equipped {item_info['name']}."
            logging.info(f"{self.username} equipped {item_id} in slot {slot}.")
        self.message = message
        self.message_timer = 2 * FPS
        if self.click_sound: self.click_sound.play()
        if hasattr(self, 'slith'): self.slith.update_accessories(self.accessories)
        return True, message

    def start_minigame(self, game_id):
        if not MINIGAMES_AVAILABLE:
            self.message = "Minigames module not loaded. Check slith_minigames.py."
            self.message_timer = 2*FPS
            if self.error_sound: self.error_sound.play()
            logging.error(f"Minigame start failed for {self.username}: MINIGAMES_AVAILABLE is False")
            return False, "Minigames disabled."
        if self.vitals.get('patience', 0) <= 0:
            logging.warning(f"{self.username} tried to start minigame with zero patience.")
            self.message = "Slith is too tired to play games!"
            self.message_timer = 2*FPS
            if self.error_sound: self.error_sound.play()
            return False, "Slith is too tired (Patience is 0)."
        self.game_state = 'playing_minigame'
        self.last_update_time = time.time()
        logging.info(f"{self.username} starting minigame: {game_id}")
        self.message = f"Starting {game_id.replace('_', ' ').title()}..."
        self.message_timer = 1*FPS
        score = 0
        bits_earned = 0
        game_class = None
        game_map = {
            'node_defender': NodeDefenderGame,
            'terminal_typer': TerminalTyperGame,
            'neon_jetpack': NeonJetpackGame,
            'signal_tracer': SignalTracerGame
        }
        game_class = game_map.get(game_id)
        if game_class:
            try:
                if mixer.get_init():
                    mixer.music.pause()
                game_instance = game_class(self.screen, self.clock)
                score, bits_earned = game_instance.run()
                logging.info(f"Minigame {game_id} completed with score {score}, bits {bits_earned}")
                if mixer.get_init() and not self.music_muted:
                    mixer.music.unpause()
            except Exception as e:
                logging.error(f"Error running minigame {game_id}: {e}", exc_info=True)
                self.message = f"Error in {game_id.replace('_', ' ').title()}!"
                self.message_timer = 3*FPS
                if self.error_sound: self.error_sound.play()
                if mixer.get_init() and not self.music_muted:
                    mixer.music.unpause()
        else:
            logging.error(f"Unknown minigame ID: {game_id}")
            self.message = "Unknown minigame!"
            self.message_timer = 2*FPS
            if self.error_sound: self.error_sound.play()
        self.end_minigame(game_id, score, bits_earned)
        return True, f"Minigame {game_id} started!"

    def end_minigame(self, game_id, score=0, bits_earned=0):
        self.update_patience()
        self.game_state = 'main'
        self.last_update_time = time.time()
        logging.info(f"{self.username} ended minigame {game_id} with score {score}, bits earned {bits_earned}")
        high_score_beaten = self.update_high_score(game_id, score)
        if bits_earned > 0:
            self.add_bits(bits_earned)
            self.message = f"Game over! Earned {bits_earned} bits!"
            if high_score_beaten:
                self.message += " New high score!"
            self.message_timer = 3 * FPS
            return True, f"Minigame ended! Earned {bits_earned} snaker_bits!"
        else:
            self.message = "Game over!"
            if high_score_beaten:
                self.message += " New high score!"
            self.message_timer = 2 * FPS
            return True, "Minigame ended."

    def update_high_score(self, game_id, score):
        if game_id not in self.high_scores:
            self.high_scores[game_id] = 0
        current_high = self.high_scores.get(game_id, 0)
        if score > current_high:
            self.high_scores[game_id] = score
            logging.info(f"New high score for {game_id}: {score}")
            return True
        return False

    def start_intro_if_needed(self):
        if not self.intro_completed and self.game_state != 'dialogue':
            logging.info(f"Starting intro dialogue for {self.username}")
            self.game_state = 'dialogue'
            self.dialogue_manager.start_dialogue(SNAKE_CARETAKER_INTRO, patience_multiplier=BITS_MINIGAME_PATIENCE_MULTIPLIER)
            return True
        return False

    def complete_intro(self):
        logging.info(f"Intro dialogue completed for {self.username}")
        self.intro_completed = True
        self.game_state = 'main'

    def get_minigame_list(self):
        return [
            {'id': 'node_defender', 'name': 'Node Defender', 'description': 'Protect the network from invaders!'},
            {'id': 'terminal_typer', 'name': 'Terminal Typer', 'description': 'Hack the system with speed typing!'},
            {'id': 'neon_jetpack', 'name': 'Neon Jetpack', 'description': 'Soar through a cyberpunk city!'},
            {'id': 'signal_tracer', 'name': 'Signal Tracer', 'description': 'Navigate the grid to trace signals!'}
        ]

    def get_mood_message(self):
        patience = self.vitals.get('patience', 100)
        if patience >= MOOD_HAPPY_THRESHOLD:
            return random.choice(["I'm thriving!", "Life's good!", "Feeling great!"])
        elif patience >= MOOD_NEUTRAL_THRESHOLD:
            return random.choice(["I'm okay.", "Just chilling.", "All good."])
        else:
            return random.choice(["I'm tired...", "Need a boost.", "Feeling low."])

    def save_current_state(self):
        """Save current game state to persistent storage"""
        self.pet_state['stage'] = self.current_stage
        self.pet_state['vitals'] = self.vitals.copy()
        self.pet_state['snaker_bits'] = self.snaker_bits
        self.pet_state['accessories'] = self.accessories.copy()
        self.pet_state['inventory'] = self.inventory.copy()
        self.pet_state['active_food_effects'] = self.active_food_effects.copy()
        self.pet_state['intro_completed'] = self.intro_completed
        self.pet_state['last_update_time'] = self.last_update_time
        self.pet_state['last_interaction_times'] = self.last_interaction_times.copy()
        self.pet_state['high_scores'] = self.high_scores.copy()
        self.user_data['slith_pet'] = self.pet_state
        save_pet_data_direct(self.username, self.user_data)
        logging.info(f"Saved game state for user: {self.username}")

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        if self.game_state == 'dialogue' and self.dialogue_manager:
            self.dialogue_manager.update()
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = self.get_mood_message()
            if self.slith.state not in ['back_turned', 'sad'] and self.message_timer == 0:
                self.slith.set_state('idle')
        if self.celebration_timer > 0:
            self.celebration_timer -= 1
            if self.celebration_timer == 0:
                self.show_celebration = False
        effects_changed = self.update_food_effects()
        patience_changed = self.update_patience()
        if patience_changed or effects_changed:
            self._update_mood()
        self.slith.update(self.animation_frame)
        any_vital_zero = any(v <= 0 for k,v in self.vitals.items() if k != 'patience')
        self.slith.set_back_turned(any_vital_zero)
        for item in self.items.values():
            item.update()
        now = time.time()
        if now - self.last_save_time >= SAVE_INTERVAL:
            self.save_current_state()
            self.last_save_time = now

            

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Quit event received.")
                self.running = False
                if self.close_sound:
                    self.close_sound.play()
                    pygame.time.wait(100)
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.mute_button_rect.collidepoint(event.pos):
                    self.music_muted = not self.music_muted
                    if self.music_muted:
                        mixer.music.pause()
                        logging.info("Music paused.")
                    else:
                        mixer.music.unpause()
                        logging.info("Music unpaused.")
                    if self.click_sound:
                        self.click_sound.play()
                    continue
            if self.game_state == 'dialogue':
                self.dialogue_manager.update()
                dialogue_continues = self.dialogue_manager.handle_input(event)
                if not dialogue_continues:
                    self.complete_intro()
                continue
            elif self.game_state == 'main':
                self.handle_main_events(event, mouse_pos)
            elif self.game_state == 'store':
                self.handle_store_events(event, mouse_pos)
            elif self.game_state == 'minigame_menu':
                self.handle_minigame_menu_events(event, mouse_pos)
            elif self.game_state == 'inventory':
                self.handle_inventory_events(event, mouse_pos)
        self.button_hover = None
        if self.mute_button_rect.collidepoint(mouse_pos):
            self.button_hover = 'mute'
        elif self.game_state == 'main':
            if self.return_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'return'
            elif self.store_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'store'
            elif self.inventory_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'inventory'
            elif self.minigame_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'minigame'
            for item in self.items.values():
                item.hovered = item.rect.collidepoint(mouse_pos)
        elif self.game_state == 'store':
            if self.store_back_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'store_back'
            filtered_items = self.filter_store_items(self.store_selected_category)
            visible_items = filtered_items[self.store_scroll_offset : self.store_scroll_offset + self.store_items_per_page]
            item_base_y = 150
            item_height = 100
            for i, (item_id, item) in enumerate(visible_items):
                item_y = item_base_y + i * item_height
                item_box_width = 500
                item_box_x = (self.window_width - item_box_width) // 2
                buy_btn_rect = pygame.Rect(item_box_x + item_box_width - 110, item_y + (item_height - 10 - 30)//2, 100, 30)
                if buy_btn_rect.collidepoint(mouse_pos):
                    self.button_hover = f"store_buy_{i}"
        elif self.game_state == 'minigame_menu':
            if self.minigame_back_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'minigame_back'
            elif self.minigame_play_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'minigame_play'
        elif self.game_state == 'inventory':
            if self.inventory_back_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'inventory_back'
            elif self.inventory_food_tab_rect.collidepoint(mouse_pos):
                self.button_hover = 'inventory_food_tab'
            elif self.inventory_acc_tab_rect.collidepoint(mouse_pos):
                self.button_hover = 'inventory_acc_tab'

        self.button_hover = None
        if self.mute_button_rect.collidepoint(mouse_pos):
            self.button_hover = 'mute'
        elif self.game_state == 'main':
            if self.replay_intro_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'replay_intro'
        elif self.return_button_rect.collidepoint(mouse_pos):
                self.button_hover = 'return'

    def handle_main_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_ui = False
            if self.items['food'].rect.collidepoint(event.pos):
                self.feed()
                clicked_ui=True
            elif self.items['water'].rect.collidepoint(event.pos):
                if self.vitals['water'] < 100:
                    self.vitals['water'] = min(100, self.vitals['water'] + 25)
                    self.message = "Refreshing!"
                    self.message_timer = 2*FPS
                    self.slith.set_state('happy')
                    if self.happy_sound: self.happy_sound.play()
                else:
                    self.message = "Not thirsty."
                    self.message_timer = 2*FPS
                    if self.error_sound: self.error_sound.play()
                clicked_ui=True
            elif self.items['entertainment'].rect.collidepoint(event.pos):
                if self.vitals['entertainment'] < 100:
                    self.vitals['entertainment'] = min(100, self.vitals['entertainment'] + 25)
                    self.message = "Fun time!"
                    self.message_timer = 2*FPS
                    self.slith.set_state('happy')
                    if self.happy_sound: self.happy_sound.play()
                else:
                    self.message = "Not bored."
                    self.message_timer = 2*FPS
                    if self.error_sound: self.error_sound.play()
                clicked_ui=True
            elif self.items['love'].rect.collidepoint(event.pos):
                self.pet()
                clicked_ui=True
            elif self.store_button_rect.collidepoint(event.pos):
                self.game_state = 'store'
                clicked_ui=True
                logging.info("Entering Store state.")
            elif self.inventory_button_rect.collidepoint(event.pos):
                self.game_state = 'inventory'
                clicked_ui=True
                logging.info("Entering Inventory state.")
            elif self.minigame_button_rect.collidepoint(event.pos):
                self.game_state = 'minigame_menu'
                clicked_ui=True
                logging.info("Entering Minigame Menu state.")
            elif self.return_button_rect.collidepoint(event.pos):
                logging.info("Return button clicked in main state.")
                self.running = False
                clicked_ui=True
                if self.close_sound:
                    self.close_sound.play()
                    pygame.time.wait(100)
            if clicked_ui and self.click_sound:
                self.click_sound.play()
            if self.replay_intro_button_rect.collidepoint(event.pos):
                self.game_state = 'dialogue'
                self.dialogue_manager.start_dialogue(SNAKE_CARETAKER_INTRO, BITS_MINIGAME_PATIENCE_MULTIPLIER)
                clicked_ui = True
            logging.info("Replaying intro dialogue")
            if clicked_ui and self.click_sound:
                        self.click_sound.play()


    def handle_store_events(self, event, mouse_pos):
        categories = ['all', 'food', 'accessory']
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = 'main'
                logging.info("Exiting Store state (ESC).")
            elif event.key == pygame.K_UP:
                self.store_scroll_offset = max(0, self.store_scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                filtered_items = self.filter_store_items(self.store_selected_category)
                max_scroll = max(0, len(filtered_items) - self.store_items_per_page)
                self.store_scroll_offset = min(max_scroll, self.store_scroll_offset + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.store_back_button_rect.collidepoint(event.pos):
                self.game_state = 'main'
                logging.info("Exiting Store state (Back button).")
                if self.close_sound:
                    self.close_sound.play()
                return
            for category, rect in self.store_category_rects.items():
                if rect.collidepoint(event.pos):
                    if self.store_selected_category != category:
                        self.store_selected_category = category
                        self.store_scroll_offset = 0
                        if self.click_sound: self.click_sound.play()
                    return
            filtered_items = self.filter_store_items(self.store_selected_category)
            visible_items = filtered_items[self.store_scroll_offset : self.store_scroll_offset + self.store_items_per_page]
            item_base_y = 150
            item_height = 100
            button_width=100
            button_height=30
            for i, (item_id, item) in enumerate(visible_items):
                item_y = item_base_y + i * item_height
                item_box_width = 500
                item_box_x = (self.window_width - item_box_width) // 2
                buy_btn_rect = pygame.Rect(item_box_x + item_box_width - 110, item_y + (item_height - 10 - button_height)//2, button_width, button_height)
                if buy_btn_rect.collidepoint(event.pos):
                    owned = item_id in self.inventory.get('food', {}) or item_id in self.inventory.get('accessories', {})
                    if owned:
                        if item['type'] == 'accessory':
                            self.equip_accessory(item_id)
                        elif item['type'] == 'food':
                            self.use_food_item(item_id)
                    else:
                        self.buy_item(item_id)
                    if self.click_sound: self.click_sound.play()
                    return
    def handle_minigame_menu_events(self, event, mouse_pos):
        games = self.get_minigame_list()
        button_width = 450  # Current width of the game buttons
        button_height = 70  # Current height of game buttons
        button_spacing = 20  # Space between buttons
        total_height = (len(games) * button_height) + ((len(games) - 1) * button_spacing)   
        start_x = (self.window_width - button_width) // 2
        start_y = (self.window_height - total_height) // 2
        self.minigame_rects = []
        for i in range(len(games)):
            button_x = start_x
            button_y = start_y + (i * (button_height + button_spacing))
            self.minigame_rects.append(pygame.Rect(button_x, button_y, button_width, button_height))
        patience_zero = self.vitals.get('patience', 0) <= 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = 'main'
                logging.info("Exiting Minigame Menu state (ESC).")
            elif event.key == pygame.K_UP:
                self.minigame_selected_index = (self.minigame_selected_index - 1) % len(games) if games else 0
                if self.click_sound: self.click_sound.play()
            elif event.key == pygame.K_DOWN:
                self.minigame_selected_index = (self.minigame_selected_index + 1) % len(games) if games else 0
                if self.click_sound: self.click_sound.play()
            elif event.key == pygame.K_RETURN and not patience_zero and games:
                self.start_minigame(games[self.minigame_selected_index]['id'])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.minigame_back_button_rect.collidepoint(event.pos):
                self.game_state = 'main'
                logging.info("Exiting Minigame Menu state (Back button).")
                if self.close_sound:
                    self.close_sound.play()
            elif self.minigame_play_button_rect.collidepoint(event.pos) and not patience_zero and games:
                self.start_minigame(games[self.minigame_selected_index]['id'])
            else:
                for i, rect in enumerate(self.minigame_rects):
                    if rect.collidepoint(event.pos):
                        if self.minigame_selected_index != i:
                            self.minigame_selected_index = i
                            if self.click_sound: self.click_sound.play()
                            break
                         
    def handle_inventory_events(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = 'main'
                logging.info("Exiting Inventory state (ESC).")
            elif event.key == pygame.K_UP:
                self.inventory_scroll_offset = max(0, self.inventory_scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                items_in_tab = self.inventory.get(self.inventory_selected_tab, {})
                max_scroll = max(0, len(items_in_tab) - self.inventory_items_per_page)
                self.inventory_scroll_offset = min(max_scroll, self.inventory_scroll_offset + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.inventory_back_button_rect.collidepoint(event.pos):
                self.game_state = 'main'
                logging.info("Exiting Inventory state (Back button).")
                if self.close_sound:
                    self.close_sound.play()
            elif self.inventory_food_tab_rect.collidepoint(event.pos):
                if self.inventory_selected_tab != 'food':
                    self.inventory_selected_tab = 'food'
                    self.inventory_scroll_offset = 0
                    if self.click_sound: self.click_sound.play()
            elif self.inventory_acc_tab_rect.collidepoint(event.pos):
                if self.inventory_selected_tab != 'accessories':
                    self.inventory_selected_tab = 'accessories'
                    self.inventory_scroll_offset = 0
                    if self.click_sound: self.click_sound.play()
            else:
                items_in_tab = self.inventory.get(self.inventory_selected_tab, {})
                visible_item_ids = list(items_in_tab.keys())[self.inventory_scroll_offset : self.inventory_scroll_offset + self.inventory_items_per_page]
                item_base_y = 150
                item_height = 60
                button_width=100
                button_height=30
                for i, item_id in enumerate(visible_item_ids):
                    item_y = item_base_y + i * item_height
                    item_box_width = 500
                    item_box_x = (self.window_width - item_box_width) // 2
                    action_btn_rect = pygame.Rect(item_box_x + item_box_width - 110, item_y + (item_height - 5 - button_height)//2, button_width, button_height)
                    if action_btn_rect.collidepoint(event.pos):
                        if self.inventory_selected_tab == 'food':
                            self.use_food_item(item_id)
                        elif self.inventory_selected_tab == 'accessories':
                            self.equip_accessory(item_id)
                        if self.click_sound: self.click_sound.play()
                        break

    def update_food_effects(self):
        now_dt = datetime.now()
        initial_count = len(self.active_food_effects)
        updated_effects = []
        changed = False
        for effect in self.active_food_effects:
            try:
                expires_dt = datetime.fromisoformat(effect.get('expires', ''))
                if expires_dt > now_dt:
                    updated_effects.append(effect)
                else:
                    logging.info(f"Removed expired food effect for {self.username}: {effect.get('source_item')}")
                    changed = True
            except (ValueError, TypeError):
                logging.warning(f"Removing invalid or old format food effect: {effect}")
                changed = True
        if changed:
            self.active_food_effects = updated_effects
            return True
        return False

    def filter_store_items(self, category):
        """Filter store items by category"""
        filtered_items = []
        for item_id, item_info in STORE_ITEMS.items():
            if category == 'all' or item_info.get('type') == category:
                filtered_items.append((item_id, item_info))
        return filtered_items

    def draw(self):
        try:
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(COLORS.get('bg', (20, 12, 28)))
            if self.game_state == 'dialogue':
                self.dialogue_manager.draw(self.screen)
            elif self.game_state == 'main':
                self.draw_main_ui()
            elif self.game_state == 'store':
                self.draw_store_ui()
            elif self.game_state == 'minigame_menu':
                self.draw_minigame_menu()
            elif self.game_state == 'inventory':
                self.draw_inventory_ui()
            self.draw_mute_button()
            if self.show_celebration and self.game_state != 'dialogue':
                self.draw_celebration()
            pygame.display.flip()
        except Exception as draw_error:
            logging.error(f"Error during draw phase (State: {self.game_state}): {draw_error}", exc_info=True)
            self.running = False

    def draw_main_ui(self):
        title_color = COLORS.get('accent')
        info_color_1 = COLORS.get('accent')
        info_color_2 = COLORS.get('neon')
        text_color = COLORS.get('text')
        button_text_color = COLORS.get('danger')
        bits_color = COLORS.get('neon')
        util_draw_text(self.screen, 'SLITH PET', self.title_font, title_color, self.window_width // 2, 30, centered=True)
        util_draw_text(self.screen, f"STAGE {self.current_stage}", self.regular_font, info_color_1, self.window_width // 2, 60, centered=True)
        stage_name = STAGES.get(self.current_stage, {}).get('name', 'Unknown')
        util_draw_text(self.screen, f"{stage_name.upper()}", self.regular_font, info_color_1, self.window_width // 2, 80, centered=True)
        bits_text = f"SNAKER_BITS: {self.snaker_bits}"
        util_draw_text(self.screen, bits_text, self.regular_font, bits_color, self.window_width - 10, 60, centered=False, right_aligned=True)
        self.slith.draw(self.screen, accessories=self.accessories)
        bubble_width = 500
        bubble_height = 40
        bubble_x = (self.window_width - bubble_width) // 2
        bubble_y = self.slith.rect.bottom + 5
        if bubble_y + bubble_height > self.window_height - 130:
            bubble_y = self.slith.rect.top - bubble_height - 5
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        pygame.draw.rect(self.screen, COLORS.get('bg_dark'), bubble_rect, 0, 5)
        pygame.draw.rect(self.screen, COLORS.get('neon'), bubble_rect, 2, 5)
        util_draw_text(self.screen, self.message.upper(), self.regular_font, text_color, bubble_rect.centerx, bubble_rect.centery + 2, centered=True)
        vital_start_x = 50
        vital_start_y = 100
        vital_width = 120
        vital_height = 16
        vital_spacing = 25
        vital_label_width = 75
        vitals_to_draw = ['patience', 'food', 'water', 'entertainment', 'love']
        for i, vital in enumerate(vitals_to_draw):
            value = self.vitals.get(vital, 0)
            vital_color = COLORS.get('neon')
            if vital == 'patience':
                if value < MOOD_NEUTRAL_THRESHOLD:
                    vital_color = COLORS.get('danger')
                elif value < MOOD_HAPPY_THRESHOLD:
                    vital_color = COLORS.get('warning')
            else:
                if value <= 0:
                    vital_color = COLORS.get('danger')
                elif value < 30:
                    vital_color = COLORS.get('danger')
                elif value < 70:
                    vital_color = COLORS.get('warning')
            vital_label = f"{vital.upper()}:"
            util_draw_text(self.screen, vital_label, self.small_font, text_color, vital_start_x + vital_label_width, vital_start_y + i * vital_spacing, centered=False, right_aligned=True)
            util_draw_progress_bar(self.screen, vital_start_x + vital_label_width + 5, vital_start_y + i * vital_spacing - 4, vital_width, vital_height, value, vital_color, use_pixel_font=True, pixel_font=self.small_font)
        for item in self.items.values():
            item.draw(self.screen)
        btn_color = COLORS.get('neon')
        hover_color = COLORS.get('accent')
        store_border = hover_color if self.button_hover == 'store' else btn_color
        pygame.draw.rect(self.screen, COLORS.get('bg'), self.store_button_rect, 0, 3)
        pygame.draw.rect(self.screen, store_border, self.store_button_rect, 2, 3)
        util_draw_text(self.screen, "STORE", self.small_font, store_border, self.store_button_rect.centerx, self.store_button_rect.centery + 2, centered=True)
        inv_border = hover_color if self.button_hover == 'inventory' else btn_color
        pygame.draw.rect(self.screen, COLORS.get('bg'), self.inventory_button_rect, 0, 3)
        pygame.draw.rect(self.screen, inv_border, self.inventory_button_rect, 2, 3)
        util_draw_text(self.screen, "INVENTORY", self.small_font, inv_border, self.inventory_button_rect.centerx, self.inventory_button_rect.centery + 2, centered=True)
        min_border = hover_color if self.button_hover == 'minigame' else btn_color
        pygame.draw.rect(self.screen, COLORS.get('bg'), self.minigame_button_rect, 0, 3)
        pygame.draw.rect(self.screen, min_border, self.minigame_button_rect, 2, 3)
        util_draw_text(self.screen, "MINIGAMES", self.small_font, min_border, self.minigame_button_rect.centerx, self.minigame_button_rect.centery + 2, centered=True)
        return_border = hover_color if self.button_hover == 'return' else COLORS.get('danger')
        pygame.draw.rect(self.screen, COLORS.get('bg'), self.return_button_rect, 0, 3)
        pygame.draw.rect(self.screen, return_border, self.return_button_rect, 2, 3)
        util_draw_text(self.screen, "CLOSE", self.small_font, return_border, self.return_button_rect.centerx, self.return_button_rect.centery + 2, centered=True)
        replay_border = COLORS.get('accent') if self.button_hover == 'replay_intro' else COLORS.get('neon')
        pygame.draw.rect(self.screen, COLORS.get('bg'), self.replay_intro_button_rect, 0, 3)
        pygame.draw.rect(self.screen, replay_border, self.replay_intro_button_rect, 2, 3)
        util_draw_text(self.screen, "REPLAY INTRO", self.small_font, replay_border, 
                  self.replay_intro_button_rect.centerx, 
                  self.replay_intro_button_rect.centery + 2, 
                  centered=True)
    def draw_store_ui(self):
        self.screen.fill(COLORS.get('bg_dark'))
        text_color = COLORS.get('text')
        neon_color = COLORS.get('neon')
        accent_color = COLORS.get('accent')
        dark_bg = COLORS.get('bg_dark')
        util_draw_text(self.screen, "STORE", self.title_font, accent_color, self.window_width // 2, 50, centered=True)
        util_draw_text(self.screen, f"SNAKER_BITS: {self.snaker_bits}", self.regular_font, neon_color, self.window_width - 10, 50, centered=False, right_aligned=True)
        for category, rect in self.store_category_rects.items():
            tab_color = accent_color if self.store_selected_category == category else neon_color
            pygame.draw.rect(self.screen, dark_bg, rect, 0, 3)
            pygame.draw.rect(self.screen, tab_color, rect, 2, 3)
            util_draw_text(self.screen, category.upper(), self.small_font, tab_color, rect.centerx, rect.centery + 2, centered=True)
        filtered_items = self.filter_store_items(self.store_selected_category)
        visible_items = filtered_items[self.store_scroll_offset : self.store_scroll_offset + self.store_items_per_page]
        item_base_y = 150
        item_height = 100
        item_box_width = 500
        item_box_x = (self.window_width - item_box_width) // 2
        button_width = 100
        button_height = 30
        for i, (item_id, item) in enumerate(visible_items):
            item_y = item_base_y + i * item_height
            item_rect = pygame.Rect(item_box_x, item_y, item_box_width, item_height - 10)
            pygame.draw.rect(self.screen, dark_bg, item_rect, 0, 5)
            pygame.draw.rect(self.screen, neon_color, item_rect, 2, 5)
            util_draw_text(self.screen, item['name'].upper(), self.regular_font, neon_color, item_rect.left + 20, item_rect.top + 15, False)
            util_draw_text(self.screen, item['description'], self.small_font, text_color, item_rect.left + 20, item_rect.top + 35, False)
            price_text = f"{item['price']} BITS"
            util_draw_text(self.screen, price_text, self.small_font, neon_color, item_rect.right - 20, item_rect.top + 15, False, right_aligned=True)
            owned = item_id in self.inventory.get('food', {}) or item_id in self.inventory.get('accessories', {})
            button_text = "USE" if owned else "BUY"
            buy_btn_rect = pygame.Rect(item_box_x + item_box_width - 110, item_y + (item_height - 10 - button_height)//2, button_width, button_height)
            btn_border = accent_color if self.button_hover == f"store_buy_{i}" else neon_color
            pygame.draw.rect(self.screen, dark_bg, buy_btn_rect, 0, 3)
            pygame.draw.rect(self.screen, btn_border, buy_btn_rect, 2, 3)
            util_draw_text(self.screen, button_text, self.small_font, btn_border, buy_btn_rect.centerx, buy_btn_rect.centery + 2, centered=True)
        back_border = accent_color if self.button_hover == 'store_back' else COLORS.get('danger')
        pygame.draw.rect(self.screen, dark_bg, self.store_back_button_rect, 0, 3)
        pygame.draw.rect(self.screen, back_border, self.store_back_button_rect, 2, 3)
        util_draw_text(self.screen, "BACK", self.small_font, back_border, self.store_back_button_rect.centerx, self.store_back_button_rect.centery + 2, centered=True)

    def draw_minigame_menu(self):
        """Draw the minigame selection menu screen."""
        self.screen.fill(COLORS.get('bg_dark', (10, 8, 16)))
        text_color = COLORS.get('text', (220, 220, 255))
        neon_color = COLORS.get('neon', (255, 221, 0))
        accent_color = COLORS.get('accent', (255, 105, 180))
        danger_color = COLORS.get('danger', (255, 50, 50))
        dark_bg = COLORS.get('bg_dark', (10, 8, 16))
        warning_color = COLORS.get('warning', (255, 165, 0))
        
        # Add scanline effect
        for y in range(0, self.window_height, 10 * PIXEL_SCALE):
            alpha = 50 + 20 * math.sin(time.time() * 2 + y)
            pygame.draw.line(self.screen, (*COLORS['grid'][:3], int(alpha)), 
                        (0, y), (self.window_width, y), PIXEL_SCALE)
        
        # Draw title
        util_draw_text(self.screen, "MINIGAMES", self.title_font, 
                    accent_color, self.window_width // 2, 50, centered=True)
        
        # Draw bits counter
        util_draw_text(self.screen, f"SNAKER_BITS: {self.snaker_bits}", self.regular_font, 
                    neon_color, self.window_width - 10, 50, 
                    centered=False, right_aligned=True)
        
        # Check if minigames are available
        patience_zero = self.vitals.get('patience', 0) <= 0
        
        # Draw warning box
        warning_rect = pygame.Rect(50, 100, self.window_width - 100, 50)
        if not MINIGAMES_AVAILABLE:
            pygame.draw.rect(self.screen, dark_bg, warning_rect, 0, 5)
            pygame.draw.rect(self.screen, danger_color, warning_rect, 2, 5)
            util_draw_text(self.screen, "MINIGAMES UNAVAILABLE!", self.regular_font, 
                        danger_color, self.window_width // 2, 115, True)
            util_draw_text(self.screen, "CHECK SLITH_MINIGAMES.PY", self.small_font, 
                        text_color, self.window_width // 2, 135, True)
        elif patience_zero:
            pygame.draw.rect(self.screen, dark_bg, warning_rect, 0, 5)
            pygame.draw.rect(self.screen, danger_color, warning_rect, 2, 5)
            util_draw_text(self.screen, "CANNOT PLAY: NO PATIENCE!", self.regular_font, 
                        danger_color, self.window_width // 2, 115, True)
            util_draw_text(self.screen, "RESTORE PATIENCE TO PLAY", self.small_font, 
                        text_color, self.window_width // 2, 135, True)
        else:
            pygame.draw.rect(self.screen, dark_bg, warning_rect, 0, 5)
            pygame.draw.rect(self.screen, warning_color, warning_rect, 2, 5)
            util_draw_text(self.screen, f"PATIENCE DRAINS x{BITS_MINIGAME_PATIENCE_MULTIPLIER} FASTER!", 
                        self.regular_font, warning_color, self.window_width // 2, 115, True)
            util_draw_text(self.screen, "PLAYING GAMES MAKES SLITH TIRED FASTER", 
                        self.small_font, text_color, self.window_width // 2, 135, True)
        
        # Get list of games
        games = self.get_minigame_list()
        
        # Define button dimensions and positioning
        button_width = 450
        button_height = 70
        button_spacing = 20
        total_height = (len(games) * button_height) + ((len(games) - 1) * button_spacing)
        
        # Define positioning with left offset option
        left_offset = 0  # Adjust this value to move buttons left
        start_x = (self.window_width - button_width) // 2 - left_offset
        start_y = (self.window_height - total_height) // 2
        
        # Create rectangles for each game button
        self.minigame_rects = []
        for i, game in enumerate(games):
            # Calculate position for this button
            button_x = start_x
            button_y = start_y + (i * (button_height + button_spacing))
            
            # Store the rectangle
            game_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.minigame_rects.append(game_rect)
            
            # Draw button background
            is_selected = i == self.minigame_selected_index
            pygame.draw.rect(self.screen, dark_bg, game_rect, 0, 5)
            
            # Draw button border
            border_color = accent_color if is_selected else neon_color
            pygame.draw.rect(self.screen, border_color, game_rect, 2, 5)
            
            # Draw game name
            util_draw_text(self.screen, game['name'], self.regular_font, 
                        border_color, game_rect.left + 20, game_rect.top + 20, False)
            
            # Draw game description
            util_draw_text(self.screen, game['description'], self.small_font, 
                        text_color, game_rect.left + 20, game_rect.top + 45, False)
            
            # Show high score if applicable
            high_score = self.high_scores.get(game['id'], 0)
            if high_score > 0:
                score_text = f"HIGH: {high_score}"
                util_draw_text(self.screen, score_text, self.small_font, 
                            neon_color, game_rect.right - 20, game_rect.top + 20, 
                            False, right_aligned=True)
        
        # Draw control buttons
        back_border = accent_color if self.button_hover == 'minigame_back' else danger_color
        pygame.draw.rect(self.screen, dark_bg, self.minigame_back_button_rect, 0, 3)
        pygame.draw.rect(self.screen, back_border, self.minigame_back_button_rect, 2, 3)
        util_draw_text(self.screen, "BACK", self.small_font, back_border, 
                    self.minigame_back_button_rect.centerx, 
                    self.minigame_back_button_rect.centery + 2, centered=True)
        
        play_btn_color = accent_color if self.button_hover == 'minigame_play' else neon_color
        if patience_zero:
            play_btn_color = COLORS.get('text_dark', (120, 120, 160))
        pygame.draw.rect(self.screen, dark_bg, self.minigame_play_button_rect, 0, 3)
        pygame.draw.rect(self.screen, play_btn_color, self.minigame_play_button_rect, 2, 3)
        util_draw_text(self.screen, "PLAY", self.small_font, play_btn_color, 
                    self.minigame_play_button_rect.centerx, 
                    self.minigame_play_button_rect.centery + 2, centered=True)
    def draw_inventory_ui(self):
        self.screen.fill(COLORS.get('bg_dark'))
        text_color = COLORS.get('text')
        neon_color = COLORS.get('neon')
        accent_color = COLORS.get('accent')
        dark_bg = COLORS.get('bg_dark')
        util_draw_text(self.screen, "INVENTORY", self.title_font, accent_color, self.window_width // 2, 50, centered=True)
        util_draw_text(self.screen, f"SNAKER_BITS: {self.snaker_bits}", self.regular_font, neon_color, self.window_width - 10, 50, centered=False, right_aligned=True)
        
        # Draw tabs
        food_tab_color = accent_color if self.inventory_selected_tab == 'food' else neon_color
        acc_tab_color = accent_color if self.inventory_selected_tab == 'accessories' else neon_color
        pygame.draw.rect(self.screen, dark_bg, self.inventory_food_tab_rect, 0, 3)
        pygame.draw.rect(self.screen, food_tab_color, self.inventory_food_tab_rect, 2, 3)
        util_draw_text(self.screen, "FOOD", self.small_font, food_tab_color, self.inventory_food_tab_rect.centerx, self.inventory_food_tab_rect.centery + 2, centered=True)
        pygame.draw.rect(self.screen, dark_bg, self.inventory_acc_tab_rect, 0, 3)
        pygame.draw.rect(self.screen, acc_tab_color, self.inventory_acc_tab_rect, 2, 3)
        util_draw_text(self.screen, "ACCESSORIES", self.small_font, acc_tab_color, self.inventory_acc_tab_rect.centerx, self.inventory_acc_tab_rect.centery + 2, centered=True)
        
        # Draw inventory items
        items_in_tab = self.inventory.get(self.inventory_selected_tab, {})
        if items_in_tab:
            visible_item_ids = list(items_in_tab.keys())[self.inventory_scroll_offset : self.inventory_scroll_offset + self.inventory_items_per_page]
            item_base_y = 150
            item_height = 60
            item_box_width = 500
            item_box_x = (self.window_width - item_box_width) // 2
            button_width = 100
            button_height = 30
            
            for i, item_id in enumerate(visible_item_ids):
                if item_id not in STORE_ITEMS:
                    continue
                    
                item_info = STORE_ITEMS[item_id]
                item_y = item_base_y + i * item_height
                item_rect = pygame.Rect(item_box_x, item_y, item_box_width, item_height - 5)
                pygame.draw.rect(self.screen, dark_bg, item_rect, 0, 5)
                pygame.draw.rect(self.screen, neon_color, item_rect, 2, 5)
                
                # Item name and info
                util_draw_text(self.screen, item_info['name'].upper(), self.regular_font, neon_color, item_rect.left + 20, item_rect.centery, False)
                
                # Quantity for food, status for accessories
                if self.inventory_selected_tab == 'food':
                    quantity = items_in_tab.get(item_id, 0)
                    util_draw_text(self.screen, f"QTY: {quantity}", self.small_font, text_color, item_rect.left + 250, item_rect.centery, False)
                    button_text = "USE"
                else:
                    equipped = self.accessories.get(item_info.get('slot')) == item_id
                    slot_text = f"SLOT: {item_info.get('slot', 'unknown').upper()}"
                    util_draw_text(self.screen, slot_text, self.small_font, text_color, item_rect.left + 250, item_rect.centery, False)
                    button_text = "UNEQUIP" if equipped else "EQUIP"
                
                # Action button
                action_btn_rect = pygame.Rect(item_box_x + item_box_width - 110, item_y + (item_height - 5 - button_height)//2, button_width, button_height)
                pygame.draw.rect(self.screen, dark_bg, action_btn_rect, 0, 3)
                pygame.draw.rect(self.screen, neon_color, action_btn_rect, 2, 3)
                util_draw_text(self.screen, button_text, self.small_font, neon_color, action_btn_rect.centerx, action_btn_rect.centery + 2, centered=True)
        else:
            # No items message
            message = f"No {self.inventory_selected_tab} in inventory."
            util_draw_text(self.screen, message, self.regular_font, text_color, self.window_width // 2, 200, centered=True)
        
        # Draw back button
        back_border = accent_color if self.button_hover == 'inventory_back' else COLORS.get('danger')
        pygame.draw.rect(self.screen, dark_bg, self.inventory_back_button_rect, 0, 3)
        pygame.draw.rect(self.screen, back_border, self.inventory_back_button_rect, 2, 3)
        util_draw_text(self.screen, "BACK", self.small_font, back_border, self.inventory_back_button_rect.centerx, self.inventory_back_button_rect.centery + 2, centered=True)

    def draw_mute_button(self):
        """Draw the mute button in the corner"""
        border_color = COLORS.get('accent') if self.button_hover == 'mute' else COLORS.get('neon')
        pygame.draw.rect(self.screen, COLORS.get('bg'), self.mute_button_rect, 0, 3)
        pygame.draw.rect(self.screen, border_color, self.mute_button_rect, 2, 3)
    
        # Draw mute icon
        icon_margin = 5 * PIXEL_SCALE
        icon_rect = pygame.Rect(
            self.mute_button_rect.left + icon_margin,
            self.mute_button_rect.top + icon_margin,
            self.mute_button_rect.width - 2 * icon_margin,
            self.mute_button_rect.height - 2 * icon_margin
        )
        
        if self.music_muted:
            # Draw muted speaker icon (X)
            pygame.draw.line(self.screen, border_color, 
                          (icon_rect.left, icon_rect.top),
                          (icon_rect.right, icon_rect.bottom), 2)
            pygame.draw.line(self.screen, border_color, 
                          (icon_rect.left, icon_rect.bottom),
                          (icon_rect.right, icon_rect.top), 2)
        else:
            # Draw speaker icon
            pygame.draw.rect(self.screen, border_color, 
                          (icon_rect.left, icon_rect.centery - icon_rect.height//4,
                            icon_rect.width//2, icon_rect.height//2), 0)
            # Sound waves
            pygame.draw.arc(self.screen, border_color,
                          (icon_rect.centerx, icon_rect.top,
                           icon_rect.width//2, icon_rect.height),
                          -math.pi/4, math.pi/4, 2)

    def draw_celebration(self):
        """Draw a celebration effect when Slith evolves"""
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent dark overlay
        self.screen.blit(overlay, (0, 0))
        
        # Draw celebratory text
        current_stage = STAGES.get(self.current_stage, {}).get('name', f'Stage {self.current_stage}')
        message = f"Congratulations! Slith evolved to {current_stage}!"
        util_draw_text(self.screen, message, self.title_font, COLORS.get('neon'), 
                     self.window_width // 2, self.window_height // 2 - 30, True)
        
        # Instructions to continue
        util_draw_text(self.screen, "Click anywhere to continue", self.regular_font, 
                     COLORS.get('accent'), self.window_width // 2, 
                     self.window_height // 2 + 30, True)
        
        # Maybe add some particle effects for fun
        for _ in range(5):
            angle = random.random() * math.pi * 2
            speed = random.uniform(30, 100) * PIXEL_SCALE
            x = random.randint(0, self.window_width)
            y = random.randint(0, self.window_height // 2)
            color = random.choice([COLORS.get('neon'), COLORS.get('accent'), COLORS.get('warning')])
            if hasattr(self, 'particles'):
                self.particles.append({
                    'x': x, 'y': y, 'speed_x': math.cos(angle) * speed, 
                    'speed_y': math.sin(angle) * speed, 'color': color,
                    'size': random.uniform(2, 4), 'timer': 0, 'duration': random.uniform(0.5, 1.0),
                    'alpha': random.randint(150, 255)
                })


# Main Game Loop Function 
def main():
    """Main entry point for the Slith Pet game"""
    # Command-line argument handling
    import argparse
    import traceback
    
    parser = argparse.ArgumentParser(description='Run the Slith Pet game')
    parser.add_argument('username', nargs='?', type=str, default='default_user', help='Username for the pet data')
    
    try:
        args = parser.parse_args()
        username = args.username
    except Exception as e:
        # If argument parsing fails, use a default username
        logging.warning(f"Argument parsing error: {e}. Using 'default_user'")
        username = 'default_user'
    
    # Set up logging
    logging.info(f"Starting Slith Pet game for user: {username}")
    print(f"Starting game for user: {username}")
    
    # Ensure storage directory exists
    os.makedirs(STORAGE_DIR, exist_ok=True)
    
    # Load user data or create default
    try:
        user_data = load_pet_data_direct(username)
        logging.info(f"Loaded user data: {user_data.keys()}")
    except Exception as e:
        logging.critical(f"Error loading user data: {e}")
        print(f"Error loading user data: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    # Create and start the game
    try:
        logging.info("Creating SlithPetGame instance...")
        game = SlithPetGame(username, user_data)
        logging.info("SlithPetGame instance created successfully.")
    except Exception as e:
        logging.critical(f"Error creating game instance: {e}")
        print(f"Error creating game instance: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    # Main game loop
    try:
        logging.info("Entering main game loop...")
        while game.running:
            game.handle_events()
            game.update()
            game.draw()
            game.clock.tick(FPS)
    except Exception as e:
        logging.critical(f"Error in main game loop: {e}")
        print(f"Error in main game loop: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            # Save final state before exit
            game.save_current_state()
            logging.info(f"Game session ended for user: {username}")
        except Exception as e:
            logging.error(f"Error saving final state: {e}")
            print(f"Error saving final state: {e}")
        finally:
            pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_message = f"Critical error: {str(e)}\n{traceback.format_exc()}"
        logging.critical(error_message)
        
        # Also write to a simple text file for easy access
        with open(os.path.join(SCRIPT_DIR, 'error_log.txt'), 'w') as f:
            f.write(error_message)
        
        print("\n\n" + "="*50)
        print("CRITICAL ERROR: Game failed to start!")
        print(error_message)
        print("="*50)
        print("\nError details have been saved to error_log.txt")
        
        # Keep the terminal window open
        input("\nPress Enter to exit...")
        
        pygame.quit()
        sys.exit(1)
        