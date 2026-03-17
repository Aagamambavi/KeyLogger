"""
Pattern analysis module for KeyLogger
Analyzes patterns in keyboard, mouse, and click behavior
"""

from collections import Counter, defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """Analyzes patterns in captured input data"""

    def __init__(self):
        """Initialize pattern analyzer"""
        pass

    def analyze(self, mouse_events, keyboard_events, words=None, phrases=None, window_events=None, urls=None, special_keys=None):
        """
        Analyze all captured events for patterns

        Args:
            mouse_events (list): List of mouse events
            keyboard_events (list): List of keyboard events
            words (list): List of extracted words
            phrases (list): List of extracted phrases
            window_events (list): List of window change events
            urls (list): List of extracted URLs

        Returns:
            dict: Dictionary containing analyzed patterns
        """
        patterns = {
            'keyboard_patterns': self._analyze_keyboard(keyboard_events),
            'mouse_patterns': self._analyze_mouse(mouse_events),
            'click_patterns': self._analyze_clicks(mouse_events),
            'typing_speed': self._calculate_typing_speed(keyboard_events),
            'mouse_movement_stats': self._analyze_movement_stats(mouse_events),
            'word_patterns': self._analyze_words(words) if words else {},
            'phrase_patterns': self._analyze_phrases(phrases) if phrases else {},
            'website_visits': self._analyze_websites(urls) if urls else {},
            'special_keys': self._analyze_special_keys(special_keys) if special_keys else {}
        }
        return patterns

    def _analyze_keyboard(self, events):
        """
        Analyze keyboard patterns
        Tracks most common keys and key sequences
        """
        if not events:
            return {}

        # Count individual key frequencies
        keys = [e['key'] for e in events]
        key_frequency = Counter(keys)

        # Analyze bigrams (two-key sequences)
        bigrams = []
        for i in range(len(keys) - 1):
            bigram = (keys[i], keys[i + 1])
            bigrams.append(bigram)

        bigram_frequency = Counter(bigrams)

        # Analyze trigrams (three-key sequences)
        trigrams = []
        for i in range(len(keys) - 2):
            trigram = (keys[i], keys[i + 1], keys[i + 2])
            trigrams.append(trigram)

        trigram_frequency = Counter(trigrams)

        return {
            'total_keys_pressed': len(events),
            'unique_keys': len(key_frequency),
            'most_common_keys': dict(key_frequency.most_common(10)),
            'most_common_bigrams': {str(k): v for k, v in bigram_frequency.most_common(10)},
            'most_common_trigrams': {str(k): v for k, v in trigram_frequency.most_common(5)},
            'key_distribution': dict(key_frequency)
        }

    def _analyze_mouse(self, events):
        """
        Analyze mouse movement patterns
        Tracks direction frequencies and durations
        """
        direction_events = [e for e in events if e['type'] == 'mouse_direction']

        if not direction_events:
            return {}

        directions = [e['direction'] for e in direction_events]
        direction_frequency = Counter(directions)

        # Calculate average duration per direction
        direction_duration = defaultdict(list)
        for event in direction_events:
            direction_duration[event['direction']].append(event['duration_ms'])

        avg_duration = {
            direction: sum(durations) / len(durations)
            for direction, durations in direction_duration.items()
        }

        return {
            'total_direction_changes': len(direction_events),
            'direction_frequency': dict(direction_frequency),
            'avg_duration_per_direction': avg_duration,
            'most_common_direction': direction_frequency.most_common(1)[0][0] if direction_frequency else None,
            'total_movement_time_ms': sum(e['duration_ms'] for e in direction_events)
        }

    def _analyze_clicks(self, events):
        """
        Analyze mouse click patterns
        Tracks button frequencies and positions
        """
        click_events = [e for e in events if e['type'] == 'mouse_click']

        if not click_events:
            return {}

        buttons = [e['button'] for e in click_events]
        button_frequency = Counter(buttons)

        # Analyze click positions (group by proximity)
        positions = [e['position'] for e in click_events]

        return {
            'total_clicks': len(click_events),
            'button_frequency': dict(button_frequency),
            'most_common_button': button_frequency.most_common(1)[0][0] if button_frequency else None,
            'click_positions_sample': positions[:20]  # Sample of click positions
        }

    def _calculate_typing_speed(self, events):
        """
        Calculate typing speed metrics
        Measures average keystroke interval
        """
        if len(events) < 2:
            return {}

        # Get timestamps
        timestamps = [e['timestamp'] for e in events]

        # Calculate intervals between keystrokes
        intervals = []
        for i in range(len(timestamps) - 1):
            interval = (timestamps[i + 1] - timestamps[i]).total_seconds() * 1000  # in ms
            intervals.append(interval)

        if not intervals:
            return {}

        avg_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)

        # Calculate WPM estimate (assuming 5 chars per word, counting only printable chars)
        printable_keys = [e for e in events if len(e['key']) == 1]
        if len(printable_keys) > 0 and timestamps:
            total_time_seconds = (timestamps[-1] - timestamps[0]).total_seconds()
            if total_time_seconds > 0:
                wpm = (len(printable_keys) / 5) / (total_time_seconds / 60)
            else:
                wpm = 0
        else:
            wpm = 0

        return {
            'avg_keystroke_interval_ms': round(avg_interval, 2),
            'min_keystroke_interval_ms': round(min_interval, 2),
            'max_keystroke_interval_ms': round(max_interval, 2),
            'estimated_wpm': round(wpm, 2)
        }

    def _analyze_movement_stats(self, events):
        """
        Analyze general movement statistics
        """
        direction_events = [e for e in events if e['type'] == 'mouse_direction']

        if not direction_events:
            return {}

        durations = [e['duration_ms'] for e in direction_events]

        return {
            'avg_movement_duration_ms': round(sum(durations) / len(durations), 2) if durations else 0,
            'longest_movement_ms': max(durations) if durations else 0,
            'shortest_movement_ms': min(durations) if durations else 0
        }

    def _analyze_words(self, words):
        """
        Analyze word patterns
        Tracks most common words typed
        Ensures accurate counts without duplication
        """
        if not words:
            return {
                'total_words_typed': 0,
                'unique_words': 0,
                'most_common_words': {},
                'word_distribution': {}
            }

        # Remove duplicates that may have been added multiple times
        # Use order-preserving deduplication at sequence level
        unique_words = []
        seen = set()

        # Only count each word occurrence once per typed sequence
        for word in words:
            if word not in seen or len(unique_words) < 100:  # Allow some repetition for actual repeated typing
                unique_words.append(word)
                seen.add(word)

        word_frequency = Counter(unique_words)

        return {
            'total_words_typed': len(unique_words),
            'unique_words': len(word_frequency),
            'most_common_words': dict(word_frequency.most_common(15)),
            'word_distribution': dict(word_frequency)
        }

    def _analyze_phrases(self, phrases):
        """
        Analyze phrase patterns
        Returns only meaningful phrases that appear 2+ times
        Filters out single occurrences
        """
        if not phrases:
            return {
                'total_phrases_typed': 0,
                'most_common_2word': {},
                'most_common_3word': {},
                'most_common_4word': {}
            }

        phrase_frequency = Counter(phrases)

        # Separate by phrase length and filter by frequency (must appear 2+ times)
        two_word = {p: f for p, f in phrase_frequency.items() if len(p.split()) == 2 and f >= 2}
        three_word = {p: f for p, f in phrase_frequency.items() if len(p.split()) == 3 and f >= 2}
        four_word = {p: f for p, f in phrase_frequency.items() if len(p.split()) == 4 and f >= 2}

        return {
            'total_phrases_typed': len([p for p, f in phrase_frequency.items() if f >= 2]),
            'most_common_2word': dict(Counter(two_word).most_common(10)),
            'most_common_3word': dict(Counter(three_word).most_common(10)),
            'most_common_4word': dict(Counter(four_word).most_common(5))
        }

    def _analyze_special_keys(self, special_keys):
        """
        Analyze special key patterns
        Tracks which special keys (Ctrl, Tab, Shift, etc.) were used
        Counts actual key presses, not held events
        """
        if not special_keys:
            return {}

        # Filter to only actual key press events (from keyboard_events with is_special=True)
        # The special_keys list should already be deduplicated by KeyboardTracker
        special_key_frequency = Counter(special_keys)

        return {
            'total_special_keys': len(special_keys),
            'unique_special_keys': len(special_key_frequency),
            'most_common_special_keys': dict(special_key_frequency.most_common(10)),
            'special_key_distribution': dict(special_key_frequency)
        }

    def _analyze_websites(self, urls):
        """
        Analyze website visits
        Tracks which websites were visited
        """
        if not urls:
            return {}

        # Count URL visits
        url_frequency = Counter(urls)

        # Extract domain names
        domains = {}
        for url, count in url_frequency.items():
            try:
                # Simple domain extraction
                if 'http' in url:
                    domain = url.split('//')[1].split('/')[0] if '//' in url else url.split('/')[0]
                else:
                    domain = url.split('/')[0]
                domains[domain] = domains.get(domain, 0) + count
            except:
                domains[url] = count

        return {
            'total_urls_visited': len(urls),
            'unique_urls': len(url_frequency),
            'url_visits': dict(url_frequency),
            'domain_visits': domains,
            'most_visited_domains': dict(Counter(domains).most_common(10))
        }

    def generate_summary(self, patterns):
        """
        Generate a human-readable summary of patterns

        Args:
            patterns (dict): Patterns dictionary from analyze()

        Returns:
            str: Formatted summary
        """
        summary = "\n=== PATTERN ANALYSIS SUMMARY ===\n"

        # Keyboard summary
        kb = patterns.get('keyboard_patterns', {})
        if kb:
            summary += f"\n[KEYBOARD]\n"
            summary += f"  Total keys pressed: {kb.get('total_keys_pressed', 0)}\n"
            summary += f"  Unique keys: {kb.get('unique_keys', 0)}\n"
            most_common = kb.get('most_common_keys', {})
            if most_common:
                top_key = list(most_common.items())[0]
                summary += f"  Most pressed key: {top_key[0]} ({top_key[1]} times)\n"

        # Typing speed summary
        typing = patterns.get('typing_speed', {})
        if typing:
            summary += f"\n[TYPING SPEED]\n"
            summary += f"  Estimated WPM: {typing.get('estimated_wpm', 0)}\n"
            summary += f"  Avg keystroke interval: {typing.get('avg_keystroke_interval_ms', 0)}ms\n"

        # Mouse summary
        mouse = patterns.get('mouse_patterns', {})
        if mouse:
            summary += f"\n[MOUSE MOVEMENT]\n"
            summary += f"  Total direction changes: {mouse.get('total_direction_changes', 0)}\n"
            summary += f"  Most common direction: {mouse.get('most_common_direction', 'N/A')}\n"
            summary += f"  Total movement time: {mouse.get('total_movement_time_ms', 0):.0f}ms\n"

        # Clicks summary
        clicks = patterns.get('click_patterns', {})
        if clicks:
            summary += f"\n[MOUSE CLICKS]\n"
            summary += f"  Total clicks: {clicks.get('total_clicks', 0)}\n"
            most_button = clicks.get('most_common_button', 'N/A')
            summary += f"  Most used button: {most_button}\n"

        # Special keys summary
        special = patterns.get('special_keys', {})
        if special and special.get('total_special_keys', 0) > 0:
            summary += f"\n[SPECIAL KEYS PRESSED]\n"
            summary += f"  Total special key presses: {special.get('total_special_keys', 0)}\n"
            summary += f"  Unique special keys: {special.get('unique_special_keys', 0)}\n"
            most_special = special.get('most_common_special_keys', {})
            if most_special:
                top_3 = list(most_special.items())[:3]
                summary += f"  Most used special keys:\n"
                for key, count in top_3:
                    summary += f"    - {key}: {count} times\n"

        # Words summary
        words = patterns.get('word_patterns', {})
        if words:
            summary += f"\n[WORDS TYPED]\n"
            summary += f"  Total words typed: {words.get('total_words_typed', 0)}\n"
            summary += f"  Unique words: {words.get('unique_words', 0)}\n"
            most_common_words = words.get('most_common_words', {})
            if most_common_words:
                top_5 = list(most_common_words.items())[:5]
                summary += f"  Top 5 most typed words:\n"
                for word, count in top_5:
                    summary += f"    - {word}: {count} times\n"

        # Phrases summary
        phrases = patterns.get('phrase_patterns', {})
        if phrases:
            summary += f"\n[PHRASES TYPED]\n"
            summary += f"  Total phrases typed: {phrases.get('total_phrases_typed', 0)}\n"
            two_word = phrases.get('most_common_2word', {})
            if two_word:
                top_phrase = list(two_word.items())[0] if two_word else None
                if top_phrase:
                    summary += f"  Most common phrase: '{top_phrase[0]}' ({top_phrase[1]} times)\n"

        # Websites summary
        sites = patterns.get('website_visits', {})
        if sites and sites.get('most_visited_domains'):
            summary += f"\n[WEBSITES VISITED]\n"
            summary += f"  Total unique URLs: {sites.get('unique_urls', 0)}\n"
            domains = sites.get('most_visited_domains', {})
            if domains:
                top_3 = list(domains.items())[:3]
                summary += f"  Top visited domains:\n"
                for domain, count in top_3:
                    summary += f"    - {domain}: {count} visits\n"

        return summary
