"""
Configuration file for KeyLogger application
Handles MongoDB connection and email settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
MONGODB_DB = 'keylogger_db'
MONGODB_COLLECTION = 'sessions'

# Email Configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '')  # Email to send reports to
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # Use app-specific password
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587

# Session Configuration
MAX_IDLE_TIME = 300  # 5 minutes of inactivity ends session
SESSION_CHECK_INTERVAL = 1  # Check for idle every 1 second
