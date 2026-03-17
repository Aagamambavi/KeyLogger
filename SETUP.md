# KeyLogger Setup Guide

## Overview
This is an educational keylogger for learning how system monitoring works. It captures keyboard input, mouse movements, and behavioral patterns.

## Prerequisites
- Python 3.8+
- MongoDB (optional, for database storage)
- Gmail account with app password enabled

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email (Gmail)

To enable email reports, you need a Gmail app password:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to **App passwords**
4. Select "Mail" and "Windows Computer" (or your OS)
5. Google will generate a 16-character password
6. Copy this password

### 3. Create .env File

The program will create a `.env` template on first run. Edit it with your credentials:

```bash
# .env
EMAIL_PASSWORD=your_16_character_app_password
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

### 4. Setup MongoDB (Optional)

If you want database storage:

**Windows:**
1. Download MongoDB Community Edition from https://www.mongodb.com/try/download/community
2. Run the installer and follow prompts
3. MongoDB will install as a Windows Service
4. Verify it's running: `mongosh` in command prompt

**Alternative - MongoDB Atlas (Cloud):**
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string and update `.env`:
```
MONGODB_HOST=your-cluster-url.mongodb.net
```

### 5. Run the Application

```bash
python main.py
```

## How It Works

### Components

**input_tracker.py**
- `MouseTracker`: Captures mouse movements and direction changes
- `KeyboardTracker`: Captures all keyboard input
- Uses `pynput` library for low-level event capture

**pattern_analyzer.py**
- Analyzes keyboard patterns (most common keys, key sequences)
- Analyzes mouse patterns (direction frequency, movement duration)
- Calculates typing speed (WPM estimate)
- Detects common bigrams/trigrams in typing

**database.py**
- `DatabaseManager`: Handles MongoDB connection
- Automatic fallback to local backup files if MongoDB unavailable
- Stores full session data with timestamps

**email_reporter.py**
- `EmailReporter`: Sends session summaries via email
- Creates HTML formatted reports with pattern analysis
- Graceful error handling for SMTP issues

**session_manager.py**
- `SessionManager`: Orchestrates the entire session
- Idle detection (ends session after 5 minutes of inactivity)
- Aggregates all events and coordinates report generation

**main.py**
- Entry point
- Environment setup and validation
- Main monitoring loop
- Keyboard interrupt handling

## Usage

### Starting a Session
```bash
python main.py
```

The program will:
1. Check MongoDB connection
2. Begin capturing input
3. End automatically after 5 minutes of inactivity
4. Generate and store session report
5. Send email report (if configured)

### Ending Manually
Press `Ctrl+C` during a session to end it manually.

## Data Storage

### MongoDB
If MongoDB is running, data is stored in:
- Database: `keylogger_db`
- Collection: `sessions`
- Each document contains full session with all events and pattern analysis

### Local Backup
If MongoDB fails/unavailable, data is stored in:
```
local_backups/session_YYYYMMDD_HHMMSS.json
```

### Logs
Application logs saved to:
```
keylogger.log
```

## Pattern Analysis Features

### Keyboard Patterns
- Total keys pressed and unique keys
- Most common individual keys
- Most common two-key sequences (bigrams)
- Most common three-key sequences (trigrams)
- Complete key distribution histogram

### Mouse Patterns
- Direction frequency (up, down, left, right)
- Average duration in each direction
- Total movement time
- Click button distribution

### Typing Speed
- Estimated WPM (words per minute)
- Average keystroke interval
- Min/max keystroke intervals

### Movement Statistics
- Average movement duration
- Longest/shortest movements

## Email Report Format

Reports include:
- Session start time and duration
- Total events captured
- Keyboard analysis (WPM, key frequencies)
- Mouse analysis (directions, clicks)
- Pattern summary
- Timestamp and status

## Troubleshooting

### "Failed to connect to MongoDB"
- **Solution 1**: Start MongoDB service
  - Windows: `net start MongoDB` or start from Services
  - Mac: `brew services start mongodb-community`
  - Linux: `sudo systemctl start mongod`

- **Solution 2**: Use local backup (program handles this automatically)

### "Gmail authentication failed"
- Check your app password is correct (16 characters)
- Verify 2-Step Verification is enabled
- Regenerate app password

### "No events captured"
- Ensure pynput is installed: `pip install pynput`
- Try running as administrator (some systems need elevated privileges)
- Check keylogger.log for errors

### "ModuleNotFoundError"
- Reinstall dependencies: `pip install -r requirements.txt`

## Security Notes

⚠️ **Important**:
- This tool captures **all keyboard input** including passwords
- Store reports securely
- Never share credentials or reports with others
- Only run on devices you own and have permission to monitor
- Consider disabling features on sensitive input (passwords, payments)

## Educational Purpose

This keylogger demonstrates:
1. **System-level event capture** - How OS delivers input events
2. **Pattern analysis** - Statistical analysis of user behavior
3. **Data persistence** - Database integration and backup strategies
4. **Email automation** - SMTP protocols and HTML formatting
5. **Threading** - Concurrent event capture and idle detection
6. **Error handling** - Graceful degradation (local backup when DB fails)
7. **Data structures** - Using dictionaries, lists, and sets for efficient analysis

## Learning Resources

- `pynput` documentation: https://pynput.readthedocs.io/
- MongoDB Python: https://pymongo.readthedocs.io/
- SMTP in Python: https://docs.python.org/3/library/smtplib.html

## License & Disclaimer

**FOR EDUCATIONAL USE ONLY**

Unauthorized monitoring of computer systems is illegal in most jurisdictions. Use this tool only:
- On your own device
- With explicit permission of device owner
- For learning security concepts
- In isolated/lab environments

The author assumes no liability for misuse.
