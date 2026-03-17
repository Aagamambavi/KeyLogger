# Educational KeyLogger

A comprehensive Python-based keylogger for learning how system input monitoring works. Captures keyboard, mouse, and behavioral patterns with MongoDB storage and email reporting.

## ⚠️ Disclaimer

**FOR EDUCATIONAL USE ONLY** - Use only on your own device for learning security concepts. Unauthorized monitoring is illegal.

## Features

✅ **Keyboard Tracking**
- Captures all keyboard input
- Analyzes keystroke patterns and sequences
- Estimates typing speed (WPM)

✅ **Mouse Tracking**
- Tracks directional movement (up, down, left, right)
- Records duration in each direction
- Captures mouse clicks and buttons used

✅ **Pattern Analysis**
- Keyboard: Most common keys, bigrams, trigrams
- Mouse: Direction frequency and movement duration
- Typing speed metrics and keystroke intervals
- Click patterns and position tracking

✅ **Data Storage**
- MongoDB integration with automatic fallback to local JSON backup
- Handles connection errors gracefully
- Comprehensive session data with timestamps

✅ **Email Reporting**
- Sends formatted HTML reports after each session
- Includes all captured patterns and statistics
- Gmail SMTP integration

✅ **Session Management**
- Automatic idle detection (5-minute timeout)
- Manual session termination with Ctrl+C
- Clean shutdown and resource cleanup

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email (Optional)
Create `.env` file:
```
EMAIL_PASSWORD=your_gmail_app_password
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

See [SETUP.md](SETUP.md) for detailed Gmail setup instructions.

### 3. Run
```bash
python main.py
```

## Project Structure

```
KeyLogger/
├── main.py                 # Entry point
├── session_manager.py      # Session lifecycle management
├── input_tracker.py        # Mouse/keyboard event capture
├── pattern_analyzer.py     # Behavior pattern analysis
├── database.py             # MongoDB integration
├── email_reporter.py       # Email report generation
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── SETUP.md               # Detailed setup guide
└── README.md              # This file
```

## How It Works

1. **Event Capture** - `pynput` library captures low-level input events
2. **Pattern Analysis** - Events are aggregated and analyzed for patterns
3. **Data Storage** - Session data stored to MongoDB (with local fallback)
4. **Report Generation** - Session summary and patterns compiled into HTML email
5. **Session Timeout** - Sessions end after 5 minutes of inactivity

## Key Educational Concepts

This project demonstrates:
- **System Programming**: Low-level input event APIs
- **Data Analysis**: Statistical pattern detection
- **Database Integration**: MongoDB operations with error handling
- **Email Automation**: SMTP protocol and HTML formatting
- **Concurrency**: Threading for idle detection
- **Error Handling**: Graceful degradation when systems unavailable

## What Gets Captured

### Keyboard
- Individual key presses
- No timestamps (as requested)
- Raw keystroke data

### Mouse
- Direction changes (up/down/left/right)
- Duration in each direction
- Click events and buttons
- Click positions (sample)

### Analysis
- Typing speed (WPM estimate)
- Keystroke intervals
- Most common key sequences
- Movement patterns
- Click frequency by button

## Configuration

Edit `config.py` to adjust:
- `MAX_IDLE_TIME`: Time before auto-session end (default: 300s)
- `DIRECTION_THRESHOLD`: Pixels for direction change (default: 10px)
- `MONGODB_*`: Database connection settings

## Email Setup

To enable email reports:
1. Enable 2-Step Verification on your Gmail account
2. Generate an app password at https://myaccount.google.com/apppasswords
3. Add to `.env`: `EMAIL_PASSWORD=your_16_char_password`

See [SETUP.md](SETUP.md) for detailed instructions.

## MongoDB Setup

### Local Installation
- **Windows**: Download from mongodb.com, install as service
- **Mac**: `brew install mongodb-community && brew services start mongodb-community`
- **Linux**: `sudo apt-get install mongodb`

### Cloud (MongoDB Atlas)
- Free tier available at https://www.mongodb.com/cloud/atlas
- Update connection string in `.env`

Data stored in database `keylogger_db`, collection `sessions`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection fails | Ensure MongoDB is running, or use local backup |
| Email not sending | Check app password, enable 2-Step Verification |
| No events captured | Run as administrator, check pynput installation |
| Module not found | Run `pip install -r requirements.txt` |

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## File Outputs

- **keylogger.log** - Application logs
- **local_backups/** - JSON backup if MongoDB unavailable
- **MongoDB** - Session data if connected

## Performance

- Minimal CPU usage (event-driven architecture)
- Low memory footprint (~50MB typical)
- Efficient pattern analysis
- Non-blocking email sending

## Limitations

- Windows only (uses `pynput` which is cross-platform but optimized for Windows)
- Keyboard input without timestamps (as specified)
- Mouse accuracy depends on OS update frequency
- Doesn't capture application context

## Future Enhancements

Potential improvements for learning:
- Add timestamps to keyboard events
- Capture application windows/context
- Machine learning pattern classification
- Browser history integration
- Screenshot capability
- Encryption of stored data

## License & Legal

**Educational Use Only** - This tool is provided for learning security concepts. Unauthorized use is illegal. User assumes all legal responsibility.

## Questions?

Refer to [SETUP.md](SETUP.md) for detailed configuration and troubleshooting, or review the inline code comments for understanding implementation details.
