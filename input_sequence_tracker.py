"""
Complete input sequence tracker
Tracks EVERY key press in exact order including spaces, backspaces, and special keys
"""

from datetime import datetime
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class InputSequenceTracker:
    """Tracks complete keyboard input sequence"""

    def __init__(self):
        """Initialize input sequence tracker"""
        self.key_sequence = []  # Complete sequence of all keys pressed in order
        self.sequence_counter = 0

    def record_key(self, key_char, is_special=False):
        """
        Record a single key press in sequence

        Args:
            key_char (str): The key character or name
            is_special (bool): Whether this is a special key
        """
        self.sequence_counter += 1

        # Determine key type and format for display
        key_lower = key_char.lower()

        if key_lower == ' ' or key_lower == 'space':
            key_type = 'SPACE'
            display_char = '[SPACE]'
        elif key_lower == 'backspace':
            key_type = 'BACKSPACE'
            display_char = '[BACKSPACE]'
        elif key_lower in ['enter', 'return']:
            key_type = 'ENTER'
            display_char = '[ENTER]'
        elif key_lower == 'tab':
            key_type = 'TAB'
            display_char = '[TAB]'
        elif is_special or any(s in key_lower for s in ['shift', 'ctrl', 'alt', 'cmd', 'home', 'end', 'pageup', 'pagedown', 'insert', 'delete']):
            key_type = 'SPECIAL'
            display_char = f'[{key_char.upper()}]'
        elif len(key_char) == 1 and key_char.isalpha():
            key_type = 'LETTER'
            display_char = key_char
        elif len(key_char) == 1 and key_char.isdigit():
            key_type = 'NUMBER'
            display_char = key_char
        elif len(key_char) == 1:
            key_type = 'SYMBOL'
            display_char = key_char
        else:
            key_type = 'SPECIAL'
            display_char = f'[{key_char.upper()}]'

        # Record in sequence
        self.key_sequence.append({
            'sequence': self.sequence_counter,
            'key': key_char.lower(),
            'type': key_type,
            'display': display_char,
            'timestamp': datetime.now()
        })

    def track_backspace(self, deleted_char=None):
        """
        Track backspace and what was deleted

        Args:
            deleted_char (str): The character that was deleted
        """
        self.sequence_counter += 1

        if deleted_char:
            display = f'[BACKSPACE - deleted "{deleted_char}"]'
        else:
            display = '[BACKSPACE]'

        self.key_sequence.append({
            'sequence': self.sequence_counter,
            'key': 'backspace',
            'type': 'BACKSPACE',
            'display': display,
            'deleted_char': deleted_char,
            'timestamp': datetime.now()
        })

    def get_sequence(self):
        """Get complete key sequence"""
        return self.key_sequence

    def get_sequence_table(self):
        """
        Get formatted sequence table for display

        Returns:
            list: List of dicts with sequence data
        """
        table_data = []
        for entry in self.key_sequence:
            table_data.append({
                'seq': entry['sequence'],
                'key_type': entry['type'],
                'key_display': entry['display'],
                'description': self._get_description(entry)
            })
        return table_data

    def _get_description(self, entry):
        """Get human-readable description of key"""
        key_type = entry['type']

        if key_type == 'LETTER':
            return f"Typed letter '{entry['display']}'"
        elif key_type == 'NUMBER':
            return f"Typed number '{entry['display']}'"
        elif key_type == 'SPACE':
            return "Pressed space"
        elif key_type == 'ENTER':
            return "Pressed enter"
        elif key_type == 'BACKSPACE':
            if entry.get('deleted_char'):
                return f"Backspace (deleted '{entry['deleted_char']}')"
            return "Backspace"
        elif key_type == 'TAB':
            return "Pressed tab"
        elif key_type == 'SPECIAL':
            key = entry['key'].upper()
            return f"Special key: {key}"
        elif key_type == 'SYMBOL':
            return f"Typed symbol '{entry['display']}'"
        else:
            return entry['display']

    def get_key_statistics(self):
        """Get statistics about keys pressed"""
        if not self.key_sequence:
            return {}

        letters = [e for e in self.key_sequence if e['type'] == 'LETTER']
        numbers = [e for e in self.key_sequence if e['type'] == 'NUMBER']
        spaces = [e for e in self.key_sequence if e['type'] == 'SPACE']
        backspaces = [e for e in self.key_sequence if e['type'] == 'BACKSPACE']
        special = [e for e in self.key_sequence if e['type'] == 'SPECIAL']
        symbols = [e for e in self.key_sequence if e['type'] == 'SYMBOL']

        return {
            'total_keys': len(self.key_sequence),
            'letters_pressed': len(letters),
            'numbers_pressed': len(numbers),
            'spaces_pressed': len(spaces),
            'backspaces_pressed': len(backspaces),
            'special_keys_pressed': len(special),
            'symbols_pressed': len(symbols)
        }

    def clear(self):
        """Clear sequence"""
        self.key_sequence = []
        self.sequence_counter = 0
