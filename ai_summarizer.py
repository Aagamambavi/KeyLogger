"""
AI Summarizer module for KeyLogger
Uses Claude AI to generate intelligent session summaries
"""

import logging
from collections import Counter
import os

logger = logging.getLogger(__name__)


class SessionSummarizer:
    """Uses Claude AI to summarize keylogger sessions"""

    def __init__(self):
        """Initialize Claude client"""
        self.client = None
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

        try:
            # Get API key from environment
            api_key = os.getenv('ANTHROPIC_API_KEY')

            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set in .env file")
                print("[!] WARNING: ANTHROPIC_API_KEY not configured. AI summaries will be disabled.")
                return

            # Import and initialize Anthropic client
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            print("[+] Anthropic client initialized successfully")

        except ImportError:
            logger.error("Anthropic SDK not installed")
            print("[-] Anthropic SDK not found. Install with: pip install anthropic")
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {e}")
            print(f"[!] Could not initialize AI summarizer: {e}")

    def generate_summary(self, session_data, patterns):
        """
        Generate detailed AI summary of the session with per-website breakdowns

        Args:
            session_data (dict): Session data including events and website activities
            patterns (dict): Analyzed patterns from PatternAnalyzer

        Returns:
            str: AI-generated summary with per-website details
        """
        if not self.client:
            return self._generate_fallback_summary(session_data, patterns)

        try:
            # Prepare detailed context with per-website information
            summary_context = self._prepare_context(session_data, patterns)

            # Create detailed prompt for Claude with comprehensive context
            prompt = f"""Analyze this keylogger session and provide a DETAILED summary with SPECIFIC information about what the user did on EACH website visited.

{summary_context}

CRITICAL: You MUST provide for EACH website:
1. The website name
2. EXACTLY what the user was doing (e.g., searching for, reading, entering data, etc.)
3. What they typed or entered on that specific website
4. What actions they took

Format EXACTLY as:
SESSION SUMMARY:
[1 sentence overall summary]

DETAILED PER-WEBSITE BREAKDOWN:
Website 1: [domain]
- Activity: [what they were specifically doing]
- Typing: [what they typed on this site]
- Actions: [what they did - searched, clicked, navigated, etc.]

Website 2: [domain]
- Activity: [what they were specifically doing]
- Typing: [what they typed on this site]
- Actions: [what they did]

[Continue for each website]

IMPORTANT: Be very specific and use the actual words typed and websites visited to determine exactly what each user was doing on each site."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,  # Increased for detailed per-website summaries
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = message.content[0].text
            print("[+] AI summary generated successfully")
            return summary

        except Exception as e:
            print(f"[-] Error generating AI summary: {e}")
            logger.error(f"Error generating AI summary: {e}")
            return self._generate_fallback_summary(session_data, patterns)

    def _prepare_context(self, session_data, patterns):
        """
        Prepare detailed context with per-website activity breakdown

        Args:
            session_data (dict): Session data with website activities
            patterns (dict): Analyzed patterns

        Returns:
            str: Formatted context for Claude with website-specific data
        """
        duration = session_data.get('duration_seconds', 0)
        words = session_data.get('words_extracted', [])
        urls = session_data.get('urls_detected', [])
        websites_visited = session_data.get('websites_visited', [])
        website_activities = session_data.get('website_activities', {})

        # Get most common words (top 20 for better context)
        word_freq = Counter(words).most_common(20)
        words_text = ", ".join([f"{w}" for w, c in word_freq])
        words_summary = ", ".join([f"{w} ({c}x)" for w, c in word_freq[:10]])

        # Get typing patterns
        kb_patterns = patterns.get('keyboard_patterns', {})
        typing = patterns.get('typing_speed', {})
        special_keys = patterns.get('special_keys', {})

        # Get website info with more detail
        websites = patterns.get('website_visits', {})
        domains = websites.get('most_visited_domains', {})
        all_urls = websites.get('url_visits', {})

        # Format websites with visit counts
        domain_details = []
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            domain_details.append(f"  - {domain}: {count} visits")
        domains_text = "\n".join(domain_details) if domain_details else "  No domains tracked"

        # Get phrases (top ones only)
        phrase_patterns = patterns.get('phrase_patterns', {})
        two_word = phrase_patterns.get('most_common_2word', {})
        three_word = phrase_patterns.get('most_common_3word', {})

        phrases_list = []
        for phrase, count in list(two_word.items())[:5]:
            if count > 1:  # Only show phrases that appeared multiple times
                phrases_list.append(f'"{phrase}" ({count}x)')
        for phrase, count in list(three_word.items())[:3]:
            if count > 1:
                phrases_list.append(f'"{phrase}" ({count}x)')

        phrases_text = "\n  ".join(phrases_list) if phrases_list else "No significant phrases"

        # Get activity level
        click_count = patterns.get('click_patterns', {}).get('total_clicks', 0)
        movement_time = patterns.get('mouse_patterns', {}).get('total_movement_time_ms', 0)

        # Build per-website detailed context
        per_website_context = ""
        if websites_visited and website_activities:
            per_website_context = "\nPER-WEBSITE ACTIVITY BREAKDOWN:\n"
            for website in websites_visited:
                if website in website_activities:
                    activity = website_activities[website]
                    top_words_on_site = Counter(activity['all_words']).most_common(5)
                    top_words_text = ", ".join([f"{w}" for w, _ in top_words_on_site])

                    per_website_context += f"\nWebsite: {website}\n"
                    per_website_context += f"  - Words typed: {activity['total_words_typed']}\n"
                    per_website_context += f"  - Unique words: {activity['unique_words']}\n"
                    per_website_context += f"  - Top words typed: {top_words_text}\n"

        context = f"""
SESSION DETAILS (for accurate summary):

TIME AND DURATION:
- Total session time: {duration/60:.1f} minutes ({int(duration)} seconds)
- Active engagement: {'High' if click_count > 20 else 'Medium' if click_count > 5 else 'Low'}

WEBSITES VISITED:
- Total websites: {len(websites_visited)}
- Websites in order: {' → '.join(websites_visited) if websites_visited else 'None tracked'}
{per_website_context}

TYPING AND INPUT:
- Total key presses: {kb_patterns.get('total_keys_pressed', 0)}
- Typing speed: {typing.get('estimated_wpm', 0):.1f} WPM
- Most frequently typed words: {words_summary}
- Special key presses (Ctrl, Shift, Alt): {special_keys.get('total_special_keys', 0)}

COMMON PHRASES DETECTED:
  {phrases_text}

MOUSE AND CLICK ACTIVITY:
- Total mouse clicks: {click_count}
- Total mouse movement time: {movement_time/1000:.1f} seconds
"""
        return context

    def _generate_fallback_summary(self, session_data, patterns):
        """
        Generate a fallback summary if Claude API fails

        Args:
            session_data (dict): Session data
            patterns (dict): Analyzed patterns

        Returns:
            str: Fallback summary
        """
        duration = session_data.get('duration_seconds', 0)
        words = session_data.get('words_extracted', [])
        urls = session_data.get('urls_detected', [])

        word_freq = Counter(words).most_common(3)
        top_words = ", ".join([w for w, c in word_freq])

        summary = f"""
Session Summary (AI Summarizer Unavailable)
=============================================

Duration: {duration/60:.1f} minutes of tracked activity

Primary Activities:
- Total keystrokes: {session_data.get('keyboard_events_count', 0)}
- Websites visited: {len(urls)} unique URLs
- Top typed words: {top_words if top_words else 'General typing'}

Website Visits:
{self._format_websites(urls)}

Typing Pattern:
- Estimated speed: {patterns.get('typing_speed', {}).get('estimated_wpm', 0):.1f} WPM
- Most common phrases: {', '.join(list(patterns.get('phrase_patterns', {}).get('most_common_2word', {}).keys())[:3])}
"""
        return summary

    def _format_websites(self, urls):
        """Format websites for display"""
        if not urls:
            return "  - No websites detected"

        formatted = []
        for url in urls[:10]:
            # Extract domain from URL
            try:
                domain = url.split('//')[1].split('/')[0] if '//' in url else url.split('/')[0]
                formatted.append(f"  - {domain}")
            except:
                formatted.append(f"  - {url}")

        return "\n".join(formatted)
