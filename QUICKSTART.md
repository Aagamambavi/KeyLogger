# Quick Start Guide

Get your educational keylogger running in 5 minutes!

## Step 1: Install Python Packages (1 minute)

```bash
cd KeyLogger
pip install -r requirements.txt
```

Expected output:
```
Successfully installed pynput-1.7.6 pymongo-4.6.1 python-dotenv-1.0.0
```

## Step 2: Configure Email (2 minutes) - OPTIONAL

### If you have Gmail:

1. Go to https://myaccount.google.com/apppasswords (you must have 2-Step Verification enabled)
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password

4. Create `.env` file in KeyLogger folder:
```
EMAIL_PASSWORD=paste_your_16_char_password_here
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

### If you skip this:
- Program runs fine without email
- Just won't send email reports (still saves to MongoDB/local files)

## Step 3: Start MongoDB (1 minute) - OPTIONAL

### On Windows:
```bash
# If MongoDB installed as service, it auto-starts
# Or manually start:
net start MongoDB

# Or if MongoDB not installed, skip - program handles this gracefully
```

### Alternative (Skip this step):
- Don't install MongoDB
- Program will save to local JSON files instead
- Perfect for learning, no setup required

## Step 4: Run the Program (1 minute)

```bash
python main.py
```

You should see:
```
============================================================
KeyLogger Setup - Educational Monitoring Tool
============================================================

============================================================
EDUCATIONAL KEYLOGGER
============================================================

[!] IMPORTANT DISCLAIMER:
    This tool is for EDUCATIONAL PURPOSES ONLY
    Use only on YOUR OWN device with YOUR CONSENT
    Unauthorized monitoring is ILLEGAL

==================================================
Starting KeyLogger Session
==================================================
[+] Session started at 2026-03-16 14:23:45
[!] Session will end after 300 seconds of inactivity
[!] Press Ctrl+C to manually end session

[+] Mouse tracking started
[+] Keyboard tracking started
[*] Monitoring user activity...
[*] Press Ctrl+C to end session manually
```

## Step 5: Use Your Computer Normally

The keylogger runs silently in background:
- Move your mouse
- Type some text
- Click around
- Use for 5+ minutes (or press Ctrl+C to end manually)

## Step 6: Session Ends Automatically

After 5 minutes of no activity (or press Ctrl+C), you'll see:

```
==================================================
Session Report Summary
==================================================
[✓] Database Storage: Success (or Failed/Offline)
[✓] Email Report: Success (or Failed)
[*] Session ended at 2026-03-16 14:28:45
==================================================
```

## What Just Happened?

✅ **Captured:**
- All your keyboard presses
- Mouse movements and directions
- All clicks

✅ **Analyzed:**
- Typing speed (WPM)
- Most common keys
- Key sequences (bigrams, trigrams)
- Mouse direction patterns
- Click frequency

✅ **Stored:**
- MongoDB database (if running)
- Local JSON backup (if MongoDB unavailable)
- Email report (if configured)

✅ **Logged:**
- keylogger.log file with all details

## View Your Data

### Check Local Files:
```bash
# See backed up sessions
dir local_backups

# See logs
type keylogger.log
```

### Check MongoDB:
```bash
# Open MongoDB client
mongosh

# List databases
show dbs

# Use keylogger database
use keylogger_db

# View sessions
db.sessions.find().pretty()

# Count sessions
db.sessions.countDocuments()
```

### Check Email:
Look for report email from `ambaviaagam@gmail.com` in your inbox (may be in Spam if first time)

## Common Issues

### "Failed to connect to MongoDB"
**This is OK!** Program automatically uses local backup files.
```bash
dir local_backups  # See your backup files
```

### "Gmail authentication failed"
Check:
1. 2-Step Verification enabled on Gmail
2. App password is exactly 16 characters
3. `.env` file has correct password

Or just skip email - program works fine without it.

### "No events captured"
Try running as Administrator:
```bash
# Right-click command prompt → Run as administrator
# Then: python main.py
```

## Next Steps

1. **Read the code** - Each module has extensive comments explaining how it works
2. **Check SETUP.md** - Detailed configuration and troubleshooting
3. **Review README.md** - Full documentation
4. **Explore the database** - See what patterns were detected
5. **Modify for learning** - Try adding features (more event types, different analysis, etc.)

## Educational Value

You now have hands-on experience with:
- **Input event capture** - How operating system delivers input to programs
- **Pattern analysis** - Statistical analysis of user behavior
- **Database integration** - Storing and retrieving large datasets
- **Email automation** - SMTP and message formatting
- **Error handling** - Graceful fallbacks when systems unavailable
- **Threading** - Concurrent task execution

## File Structure Created

```
KeyLogger/
├── main.py              # Start here
├── session_manager.py   # Understand session flow
├── input_tracker.py     # Learn about event capture
├── pattern_analyzer.py  # See pattern detection logic
├── database.py          # Database/backup handling
├── email_reporter.py    # Email generation
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── keylogger.log        # Created after first run
├── local_backups/       # Created if MongoDB unavailable
└── README.md            # Full documentation
```

## Remember

⚠️ **This is for YOUR device only**
- Only run on computers you own
- Only monitor your own input
- Unauthorized monitoring is illegal
- For educational learning only

Enjoy learning how keyloggers work! 🎓
