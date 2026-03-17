"""
Website activity tracker
Tracks which website was active and associates keyboard/mouse activity with each site
Creates a detailed timeline of activities per website
"""

from datetime import datetime
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class WebsiteActivityTracker:
    """Tracks website visits and associated user activities"""

    def __init__(self):
        """Initialize website activity tracker"""
        self.activity_timeline = []  # Complete timeline of all activities
        self.visited_urls = []  # All URLs visited in order (including redirects)
        self.url_visit_times = []  # Timestamps of each URL visit
        self.current_url = None
        self.current_url_start_time = None
        self.url_activities = defaultdict(list)  # URL -> list of activities on that URL
        self.url_visit_sequence = []  # Track ALL URL visits in order

    def update_active_website(self, window_title):
        """
        Update the current active website from window title
        Tracks ALL URLs including redirects and changes
        """
        if not window_title or len(window_title) < 3:
            return False

        url = self._extract_website_from_title(window_title)

        # If URL changed (including redirects)
        if url and url != self.current_url:
            # Record previous URL's end time
            if self.current_url and self.current_url_start_time:
                duration = (datetime.now() - self.current_url_start_time).total_seconds()
                self.activity_timeline.append({
                    'type': 'url_end',
                    'url': self.current_url,
                    'timestamp': datetime.now(),
                    'duration_seconds': duration
                })

            # Start tracking new URL
            self.current_url = url
            self.current_url_start_time = datetime.now()

            # Add to all visited URLs list (NEVER remove, always append)
            self.visited_urls.append(url)
            self.url_visit_times.append(self.current_url_start_time)
            self.url_visit_sequence.append({
                'url': url,
                'visit_time': self.current_url_start_time,
                'visit_number': len(self.visited_urls)
            })

            # Add to timeline
            self.activity_timeline.append({
                'type': 'url_visit',
                'url': url,
                'timestamp': self.current_url_start_time,
                'visit_number': len(self.visited_urls)
            })

            return True

        return False

    def record_typing_activity(self, words, url=None):
        """Record typing activity for current or specified URL"""
        site = url or self.current_url
        if site and words:
            self.activity_timeline.append({
                'type': 'typing',
                'url': site,
                'words': words,
                'timestamp': datetime.now()
            })
            self.url_activities[site].extend(words)

    def record_click_activity(self, url=None):
        """Record click activity"""
        site = url or self.current_url
        if site:
            self.activity_timeline.append({
                'type': 'click',
                'url': site,
                'timestamp': datetime.now()
            })

    def _extract_website_from_title(self, title):
        """
        Extract website/domain from window title
        Handles various browser formats
        """
        if not title or len(title) < 3:
            return None

        title_lower = title.lower()

        # Skip if doesn't look like a website
        if not any(pattern in title_lower for pattern in ['http://', 'https://', 'www.', '.com', '.org', '.net', '.io', '.edu', '.gov', '.co']):
            return None

        # Remove browser names that sometimes appear in titles
        browser_names = ['- google chrome', '— google chrome', '- mozilla firefox', '— mozilla firefox',
                        '- safari', '— safari', '- microsoft edge', '— microsoft edge',
                        '- chrome', '— chrome', '- firefox', '— firefox']

        cleaned_title = title
        for browser in browser_names:
            if browser in title_lower:
                cleaned_title = title[:title_lower.index(browser)].strip()
                break

        # Try to extract domain/URL
        website = self._parse_url_from_text(cleaned_title)
        return website if website else None

    def _parse_url_from_text(self, text):
        """Parse URL from text"""
        if not text:
            return None

        text = text.strip('/ ')
        text_lower = text.lower()

        # Check if it looks like a URL
        if not any(tld in text_lower for tld in ['.com', '.org', '.net', '.edu', '.gov', '.io', '.co', '.info', '.biz', '.tv']):
            return None

        # If contains protocol, extract from there
        if 'http' in text_lower:
            try:
                # Extract URL part
                if '://' in text:
                    url_part = text.split('://')[1]
                    domain = url_part.split('/')[0].split('?')[0]
                    return domain
            except:
                pass

        # Otherwise extract domain pattern
        if '.' in text:
            # Find the domain part
            words = text.split()
            for word in words:
                word_clean = word.strip('/ ')
                if '.' in word_clean and any(tld in word_clean.lower() for tld in
                                            ['.com', '.org', '.net', '.edu', '.gov', '.io', '.co']):
                    return word_clean.lower()

        return None

    def get_website_summary(self):
        """
        Get summary of activities per URL
        Returns organized data for AI summarization
        """
        summary = {}

        for url, activities in self.url_activities.items():
            word_count = len(activities)
            unique_words = len(set(activities))
            top_words = Counter(activities).most_common(10)

            summary[url] = {
                'total_words_typed': word_count,
                'unique_words': unique_words,
                'top_words': dict(top_words),
                'all_words': activities
            }

        return summary

    def get_activity_timeline(self):
        """Get detailed activity timeline"""
        return self.activity_timeline

    def get_websites_visited(self):
        """Get list of ALL websites/URLs visited in order (including redirects)"""
        return self.visited_urls

    def get_url_visit_sequence(self):
        """Get detailed sequence of URL visits with timestamps"""
        return self.url_visit_sequence

    def finalize_session(self):
        """Finalize session and close any open URL session"""
        if self.current_url and self.current_url_start_time:
            duration = (datetime.now() - self.current_url_start_time).total_seconds()
            self.activity_timeline.append({
                'type': 'url_end',
                'url': self.current_url,
                'timestamp': datetime.now(),
                'duration_seconds': duration
            })
