# slith_dialogue.py
import pygame
import textwrap # For wrapping long lines of text
import os

# --- Constants ---
# Colors (adapt to your game's palette)
BOX_COLOR = (255, 221, 0, 130)  # Yellow with increased transparency
BORDER_COLOR = (255, 105, 180)  # Neon pink for main dialogue box
TEXT_COLOR = (255, 0, 180)      # Pink text
NPC_NAME_COLOR = (255, 255, 0)  # Yellow
HIGHLIGHT_COLOR = (0, 255, 255) # Cyan for bits
ITEM_COLOR = (200, 200, 255)    # Light purple/blue for items

# --- Dialogue Content ---
# Structure: List of tuples (speaker, text)
# Use placeholders like {BITS_MULTIPLIER} which we can replace dynamically if needed
SNAKE_CARETAKER_INTRO = [
    ("M0r7iu5 (Snake Caretaker)", "Yo, Operator! Heard you scored one of those sick cyber-serpent eggs. Totally brutal choice! Name's M0r7iu5. Used to shred at the digital nests where these gnarly little dudes hatch."),
    ("M0r7iu5 (Snake Caretaker)", "That's **Slith** you've got there. Needs some heavy maintenance, ya know? Main thing is **Patience**. Keep that meter cranked, or they get totally wasted and bummed out."),
    ("M0r7iu5 (Snake Caretaker)", "Feedin', cleanin', pettin' - all the usual headbangin' stuff helps. Check the console for cooldowns."),
    ("M0r7iu5 (Snake Caretaker)", "But here's the killer new riff: Slith digs **Minigames**! Sick way to bond... and earn some wicked cash."),
    ("M0r7iu5 (Snake Caretaker)", "Just don't get thrashed. While shreddin' those games, Slith's **Patience gets totally slammed** - like {multiplier} times faster, man. Can't rock out if Patience hits zero, poor thing's too fried."),
    ("M0r7iu5 (Snake Caretaker)", "Crush the games, earn the loot. We call 'em '<currency>snaker_bits</currency>'. Metal AF!"),
    ("M0r7iu5 (Snake Caretaker)", "Blast those <currency>snaker_bits</currency> at the **Store**. Score epic grub like <item>Corpo Rat</item> or even the <item>King Rat</item> - keeps that Patience drain from going ballistic."),
    ("M0r7iu5 (Snake Caretaker)", "Can also score... accessories. Yeah, hats, glasses, bandanas. Give Slith some headbanger style. Saw one rockin' a tiny <item>Crown</item> once. Cost a monster pile of bits, that beast."),
    ("M0r7iu5 (Snake Caretaker)", "I am an artist, and the ring is my canvas. Just like in the digital arena, it's all about the performance."),
    ("M0r7iu5 (Snake Caretaker)", "Alright, time to thrash! Keep Slith stoked, crush some games, earn your bits, maybe deck out with some killer gear. Any questions, check the system logs. Rock on, Operator!")
]

class DialogueManager:
    """Handles rendering and progression of dialogue sequences in Pygame."""

    def __init__(self, screen_width, screen_height, font_path=None, font_size=16):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Portrait and dialogue box dimensions
        self.box_height = int(screen_height * 0.25)  # Reduced from 0.30
        self.box_y = screen_height - self.box_height - 20  # Moved up from 30 to 20
        self.box_width = int(screen_width * 0.75)  # Reduced from 0.80
        self.box_x = (screen_width - self.box_width) // 2
        self.box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        
        # Portrait dimensions
        self.portrait_width = int(self.box_height * 0.8)  # Reduced from 0.9
        self.portrait_height = self.portrait_width 
        self.portrait_x = self.box_x + self.box_width - self.portrait_width - 15  # Adjusted from 20
        self.portrait_y = self.box_y + 15
        
        # Text area within the box (adjusted to account for portrait)
        self.text_margin_x = 15  # Reduced from 20
        self.text_margin_y = 12  # Reduced from 15
        self.name_height = 20  # Reduced from 25
        self.text_area_rect = pygame.Rect(
            self.box_rect.left + self.text_margin_x,
            self.box_rect.top + self.text_margin_y + self.name_height,
            self.box_width - self.portrait_width - 3 * self.text_margin_x,
            self.box_height - 2 * self.text_margin_y - self.name_height - 10
        )

        # Name display rectangle - Position at the bottom of the portrait
        self.name_rect = pygame.Rect(
            self.portrait_x,
            self.portrait_y + self.portrait_height - self.name_height + 20,
            self.portrait_width,
            self.name_height
        )

        # Border width
        self.border_width = 2

        # Font setup
        try:
            # Use a monospace font if available, otherwise default
            self.font = pygame.font.Font(font_path or pygame.font.match_font('couriernew, consolas, monospace'), font_size)
            self.npc_font = pygame.font.Font(font_path or pygame.font.match_font('couriernew, consolas, monospace'), font_size + 2) # Slightly larger for name
        except IOError:
            print(f"Warning: Font '{font_path}' not found. Using default Pygame font.")
            self.font = pygame.font.Font(None, font_size + 2) # Default font if path fails
            self.npc_font = pygame.font.Font(None, font_size + 4)

        # Increase line height for better readability
        self.line_height = int(self.font.get_linesize() * 1.6)  # Increased from 1.4 to 1.6

        # Load portrait image
        self.portrait = None
        try:
            portrait_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'snake_caretaker.png')
            self.portrait = pygame.image.load(portrait_path)
            self.portrait = pygame.transform.scale(self.portrait, (self.portrait_width, self.portrait_height))
        except:
            print("Warning: Could not load portrait image. Using fallback.")
            # Create a fallback portrait (simple colored rectangle)
            self.portrait = pygame.Surface((self.portrait_width, self.portrait_height))
            self.portrait.fill((50, 100, 150))

        # State
        self.active = False
        self.dialogue_sequence = []
        self.current_line_index = 0
        self.current_speaker = ""
        self.current_text = ""
        self.wrapped_lines = []
        self.patience_multiplier = 1.0 # Default, can be set externally
        
        # Typing effect parameters - slowed down
        self.typing_index = 0
        self.typing_speed = 1  # 1 character per update
        self.typing_complete = False
        self.typing_timer = 0
        self.typing_timer_max = 3  # Delay between characters (higher = slower)
        self.typing_sound_interval = 2  # Sound frequency
        
        # Beep sound with fallback
        self.beep_sound = None
        try:
            # Try to load the beep sound
            beep_path = os.path.join(os.path.dirname(__file__), 'static', 'audio', 'beep.wav')
            if os.path.exists(beep_path):
                self.beep_sound = pygame.mixer.Sound(beep_path)
                self.beep_sound.set_volume(0.1)  # Lower volume
            else:
                # Fallback to generic beep sound if file not found
                print(f"Warning: Beep sound file not found at {beep_path}. Using fallback sound.")
                self.beep_sound = self.generate_beep_sound()
        except Exception as e:
            print(f"Warning: Could not load typing sound effect: {e}")
            try:
                # Try to generate a beep sound programmatically
                self.beep_sound = self.generate_beep_sound()
            except:
                print("Could not generate beep sound.")

    def generate_beep_sound(self):
        """Generate a simple beep sound if file loading fails"""
        try:
            import numpy
            from pygame import sndarray
            
            sample_rate = 22050
            duration = 0.05  # 50ms
            volume = 0.1
            
            # Create a buffer of 16-bit signed integers
            buf = numpy.zeros((int(sample_rate * duration), 2), dtype=numpy.int16)
            
            # Maximum amplitude for 16-bit audio
            max_sample = 2**(16 - 1) - 1
            
            # Generate a simple sine wave at 880Hz
            for i in range(len(buf)):
                t = float(i) / sample_rate
                sine_val = numpy.sin(2.0 * numpy.pi * 880 * t)
                sample_val = int(max_sample * volume * sine_val)
                buf[i][0] = sample_val
                buf[i][1] = sample_val
            
            # Create a sound object from the buffer
            sound = sndarray.make_sound(buf)
            return sound
        except Exception as e:
            print(f"Could not generate beep sound: {e}")
            return None

    def start_dialogue(self, sequence, patience_multiplier=1.5):
        """Starts a new dialogue sequence."""
        if not sequence:
            print("Error: Tried to start empty dialogue sequence.")
            return
        self.dialogue_sequence = sequence
        self.patience_multiplier = patience_multiplier # Store the multiplier
        self.current_line_index = 0
        self.active = True
        self._load_current_line()
        # Reset typing effect
        self.typing_index = 0
        self.typing_complete = False
        print("Dialogue started.")

    def stop_dialogue(self):
        """Stops the current dialogue."""
        self.active = False
        self.current_line_index = 0
        self.dialogue_sequence = []
        print("Dialogue ended.")

    def next_line(self):
        """Advances to the next line in the sequence."""
        if not self.active:
            return False # Not in dialogue

        # If still typing, complete the current line instantly
        if not self.typing_complete:
            self.typing_index = len(self.current_text)
            self.typing_complete = True
            self._wrap_text()
            return True

        # Move to next line
        self.current_line_index += 1
        if self.current_line_index >= len(self.dialogue_sequence):
            self.stop_dialogue()
            return False # End of dialogue
        else:
            self._load_current_line()
            # Reset typing effect
            self.typing_index = 0
            self.typing_complete = False
            return True # More lines remain

    def _load_current_line(self):
        """Loads speaker and text for the current index and wraps text."""
        if not self.active or self.current_line_index >= len(self.dialogue_sequence):
            return

        self.current_speaker, raw_text = self.dialogue_sequence[self.current_line_index]

        # Replace placeholders
        formatted_text = raw_text.replace("{multiplier}", str(self.patience_multiplier))

        self.current_text = formatted_text # Store the processed text
        self._wrap_text()

    def _wrap_text(self):
        """Wraps the current text to fit the dialogue box width with improved line calculation."""
        self.wrapped_lines = []
        
        # Use a more conservative estimate for characters per line
        # This helps prevent overruns and overlapping
        chars_per_line = int(self.text_area_rect.width / (self.font.size("m")[0] * 1.1))
        if chars_per_line <= 0: 
            chars_per_line = 10  # Avoid division by zero or negative
        
        # Calculate max visible lines to avoid overrunning the box
        max_lines = (self.text_area_rect.height // self.line_height) - 1
        
        # Use textwrap for basic wrapping
        if self.typing_complete:
            # If typing is complete, wrap the entire text
            wrapped = textwrap.wrap(self.current_text, width=chars_per_line, replace_whitespace=False)
            # Take only as many lines as can fit in the box
            self.wrapped_lines = wrapped[:max_lines]
        else:
            # If still typing, only wrap the visible portion
            visible_text = self.current_text[:self.typing_index]
            wrapped = textwrap.wrap(visible_text, width=chars_per_line, replace_whitespace=False)
            # Take only as many lines as can fit in the box
            self.wrapped_lines = wrapped[:max_lines]

    def update(self):
        """Update typing effect and animation"""
        if not self.active:
            return
            
        # Update typing effect with improved timing
        if not self.typing_complete:
            self.typing_timer += 1
            if self.typing_timer >= self.typing_timer_max:  # Use max timer value
                self.typing_timer = 0
                
                # Only advance the typing index if there are more characters to show
                if self.typing_index < len(self.current_text):
                    # Get the next character
                    next_char = self.current_text[self.typing_index]
                    
                    # Play beep sound for non-space characters
                    if self.beep_sound and next_char.strip():
                        self.beep_sound.play()
                    
                    # Advance typing index
                    self.typing_index += self.typing_speed
                    
                    # Check if typing is complete
                    if self.typing_index >= len(self.current_text):
                        self.typing_index = len(self.current_text)
                        self.typing_complete = True
                    
                    # Update wrapped text based on current visible portion
                    self._wrap_text()

    def handle_input(self, event):
        """Processes Pygame events to advance dialogue."""
        if not self.active:
            return False # Dialogue not active

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse click
                return self.next_line() # Returns True if dialogue continues, False if it ended
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]: # Space, Enter, or E key
                return self.next_line() # Returns True if dialogue continues, False if it ended
        return True # Event handled (or ignored), dialogue still active

    def _render_text_with_markup(self, surface, text, start_pos, max_width):
        """Renders a single line of text, handling simple markup with better alignment."""
        x, y = start_pos
        original_x = x  # Store original starting x position
        current_x = x
        words = text.split(' ')
        current_color = TEXT_COLOR
        is_bold = False

        for word in words:
            plain_word = word
            word_color = current_color
            temp_bold = is_bold

            # Basic Markup Handling
            if word.startswith("**") and word.endswith("**") and len(word) > 4:
                plain_word = word[2:-2]
                temp_bold = True
            elif word.startswith("<currency>") and word.endswith("</currency>"):
                plain_word = word[10:-11]
                word_color = HIGHLIGHT_COLOR
            elif word.startswith("<item>") and word.endswith("</item>"):
                plain_word = word[6:-7]
                word_color = ITEM_COLOR

            # Add space if not the first word on the line
            display_word = plain_word
            if current_x > original_x:
                 display_word = " " + plain_word

            # Add text shadow for better readability against yellow background
            shadow_color = (0, 0, 30)  # Very dark blue shadow
            shadow_surface = self.font.render(display_word, True, shadow_color)
            surface.blit(shadow_surface, (current_x + 1, y + 1))  # Shadow offset by 1px
            
            # Then draw the regular text on top
            word_surface = self.font.render(display_word, True, word_color)
            
            # Check if word would extend beyond max width and needs to wrap
            if current_x + word_surface.get_width() > original_x + max_width:
                # Move to next line
                y += self.line_height
                current_x = original_x
                # Remove leading space since we're at start of line now
                display_word = plain_word
                word_surface = self.font.render(display_word, True, word_color)
                # Redraw shadow at new position
                shadow_surface = self.font.render(display_word, True, shadow_color)
                surface.blit(shadow_surface, (current_x + 1, y + 1))
            
            if temp_bold:
                # Simple bold effect by rendering again slightly offset
                 bold_surface = self.font.render(display_word, True, word_color)
                 surface.blit(bold_surface, (current_x + 1, y)) # Offset bold

            surface.blit(word_surface, (current_x, y))
            current_x += word_surface.get_width()

    def draw_pixelated_border(self, surface, rect, color, width=2):
        """Draw a pixelated border around a rectangle."""
        # Top border
        pygame.draw.rect(surface, color, (rect.left, rect.top, rect.width, width))
        # Bottom border
        pygame.draw.rect(surface, color, (rect.left, rect.bottom - width, rect.width, width))
        # Left border
        pygame.draw.rect(surface, color, (rect.left, rect.top, width, rect.height))
        # Right border
        pygame.draw.rect(surface, color, (rect.right - width, rect.top, width, rect.height))

    def draw(self, surface):
        """Draws the dialogue box and current text onto the target surface."""
        if not self.active:
            return

        # Create a semi-transparent overlay for the entire screen
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent dark overlay
        surface.blit(overlay, (0, 0))

        # Draw the box background
        box_surface = pygame.Surface(self.box_rect.size, pygame.SRCALPHA)
        box_surface.fill(BOX_COLOR)
        surface.blit(box_surface, self.box_rect.topleft)

        # Draw pixelated border for main dialogue box
        self.draw_pixelated_border(surface, self.box_rect, BORDER_COLOR, self.border_width)

        # Draw the portrait
        if self.portrait:
            # Just draw the portrait itself
            surface.blit(self.portrait, (self.portrait_x, self.portrait_y))
            
            # Draw a border around just the portrait
            portrait_rect = pygame.Rect(
                self.portrait_x,
                self.portrait_y,
                self.portrait_width,
                self.portrait_height
            )
            self.draw_pixelated_border(surface, portrait_rect, BORDER_COLOR, self.border_width)

        # Draw name box separately (below the portrait)
        name_box = pygame.Surface(self.name_rect.size, pygame.SRCALPHA)
        name_box.fill(BOX_COLOR)
        surface.blit(name_box, self.name_rect)
        self.draw_pixelated_border(surface, self.name_rect, BORDER_COLOR, self.border_width)

        # Draw Speaker Name
        if self.current_speaker:
            # Extract just the name part (before parenthesis if any)
            display_name = self.current_speaker.split('(')[0].strip()
            name_surface = self.npc_font.render(display_name, True, NPC_NAME_COLOR)
            name_pos = (self.name_rect.left + (self.name_rect.width - name_surface.get_width()) // 2,
                        self.name_rect.top + (self.name_rect.height - name_surface.get_height()) // 2)
            surface.blit(name_surface, name_pos)

        # Draw the visible text (with typing effect)
        text_y = self.text_area_rect.top
        for i, line in enumerate(self.wrapped_lines):
            if text_y + self.line_height > self.text_area_rect.bottom:
                break # Stop if text exceeds box height
            
            # Render line by line with markup handling
            self._render_text_with_markup(
                surface, line, 
                (self.text_area_rect.left, text_y), 
                self.text_area_rect.width
            )
            text_y += self.line_height

        # Draw "continue" indicator if typing is complete
        if self.typing_complete:
            indicator_text = "[Click or Press SPACE to continue]"
            indicator_surface = self.font.render(indicator_text, True, BORDER_COLOR)
            
            # Position at bottom center of text area
            indicator_x = self.text_area_rect.left + (self.text_area_rect.width // 2) - (indicator_surface.get_width() // 2)
            indicator_y = self.box_rect.bottom - indicator_surface.get_height() - 10
            
            # Simple blink effect
            if int(pygame.time.get_ticks() / 500) % 2 == 0: # Blink every 500ms
                surface.blit(indicator_surface, (indicator_x, indicator_y))