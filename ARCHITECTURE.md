# Architecture & Design Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     KeyLogger Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Session Manager (Orchestrator)         │   │
│  │  - Session lifecycle (start/end)                     │   │
│  │  - Idle detection & timeout                          │   │
│  │  - Event aggregation                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                    │                    │         │
│           ▼                    ▼                    ▼         │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐  │
│  │  Input Trackers │ │ Pattern Analyzer │ │   Database   │  │
│  │                 │ │                  │ │   Manager    │  │
│  │ • Mouse Events  │ │ • Key patterns   │ │              │  │
│  │ • Key Events    │ │ • Typing speed   │ │ • MongoDB    │  │
│  │ • Click Events  │ │ • Mouse patterns │ │ • Local JSON │  │
│  └─────────────────┘ └──────────────────┘ └──────────────┘  │
│           │                                        │          │
│           └────────────────┬─────────────────────┬─┘          │
│                            │                     │            │
│                            ▼                     ▼            │
│                   ┌──────────────────────────────────┐        │
│                   │    Email Reporter                │        │
│                   │  - Format HTML report            │        │
│                   │  - Send via SMTP                 │        │
│                   └──────────────────────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌──────────┐      ┌──────────────┐
    │ Logs   │          │ Database │      │ Email Report │
    └────────┘          └──────────┘      └──────────────┘
```

## Module Breakdown

### 1. Main Entry Point (`main.py`)

**Purpose:** Application initialization and main event loop

**Responsibilities:**
- Environment setup (.env validation)
- Welcome/disclaimer messages
- Create SessionManager instance
- Run main monitoring loop
- Handle graceful shutdown (Ctrl+C)

**Flow:**
```
main()
  ├─ setup_environment()      # Validate .env file
  ├─ display_welcome()        # Show disclaimers
  ├─ SessionManager()          # Create manager
  ├─ start_session()          # Begin monitoring
  ├─ while session_active:    # Event loop
  │   └─ record_activity()    # Update idle timer
  └─ cleanup()                # Close connections
```

**Key Points:**
- Runs indefinitely until Ctrl+C or idle timeout
- Minimal logic - delegates to SessionManager
- Clean exception handling with logging

---

### 2. Session Manager (`session_manager.py`)

**Purpose:** Orchestrates the entire session lifecycle

**Components:**
- Instantiates all trackers (Mouse, Keyboard)
- Manages session timing
- Coordinates report generation
- Handles idle detection

**Key Classes:**
```python
SessionManager:
  ├─ MouseTracker      # Input capture
  ├─ KeyboardTracker   # Input capture
  ├─ PatternAnalyzer   # Behavior analysis
  ├─ DatabaseManager   # Storage
  ├─ EmailReporter     # Reporting
  └─ Idle Checker      # Background thread
```

**Session Lifecycle:**
```
start_session()
  ├─ Initialize trackers
  ├─ Start idle detection thread
  └─ Begin event capture

[Background: Idle Checker Thread]
  ├─ Check inactivity every 1 second
  └─ Call end_session() if idle > MAX_IDLE_TIME

end_session()
  ├─ Stop trackers
  ├─ Analyze patterns
  ├─ Store to database
  ├─ Send email report
  └─ Display summary
```

**Activity Tracking:**
- `last_activity_time` updated when events captured
- Idle time = current_time - last_activity_time
- Session ends when idle > 300 seconds

---

### 3. Input Trackers (`input_tracker.py`)

**Purpose:** Capture low-level input events

#### MouseTracker

**How it works:**
```
pynput.mouse.Listener
  ├─ on_move(x, y)           # Called on every mouse movement
  │   ├─ Calculate direction (up/down/left/right)
  │   ├─ Detect direction change
  │   └─ Record duration in previous direction
  │
  └─ on_click(x, y, button)  # Called on button press
      └─ Record button and position
```

**Direction Detection Algorithm:**
```python
def _get_direction(from_pos, to_pos):
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]

    if abs(dx) > abs(dy):
        return 'right' if dx > 0 else 'left'
    else:
        return 'down' if dy > 0 else 'up'
```

**Data Structure:**
```json
Mouse Direction Event:
{
  "type": "mouse_direction",
  "direction": "right",
  "duration_ms": 1250.5,
  "timestamp": "2026-03-16T14:23:45"
}

Mouse Click Event:
{
  "type": "mouse_click",
  "button": "Button.left",
  "position": [500, 300],
  "timestamp": "2026-03-16T14:23:46"
}
```

#### KeyboardTracker

**How it works:**
```
pynput.keyboard.Listener
  ├─ on_press(key)       # Key pressed
  │   ├─ Get key character/name
  │   ├─ Check if already pressed (avoid duplicates)
  │   └─ Record key event
  │
  └─ on_release(key)     # Key released
      └─ Remove from pressed_keys set
```

**Data Structure:**
```json
Keyboard Event:
{
  "type": "key_press",
  "key": "a",           # Single character or "space", "enter", etc.
  "timestamp": "2026-03-16T14:23:46"
}
```

---

### 4. Pattern Analyzer (`pattern_analyzer.py`)

**Purpose:** Extract meaningful patterns from raw events

**Analysis Types:**

#### Keyboard Analysis
```
Frequency Analysis:
  ├─ Individual key frequencies
  ├─ Bigrams (two-key sequences)
  └─ Trigrams (three-key sequences)

Example Output:
{
  "total_keys_pressed": 542,
  "unique_keys": 28,
  "most_common_keys": {
    "space": 67,
    "e": 45,
    "a": 38
  },
  "most_common_bigrams": {
    "('e', 'space')": 12,
    "('space', 't')": 10
  }
}
```

**Implementation:**
```python
from collections import Counter

keys = ['a', 'b', 'c', 'a', 'b']
key_frequency = Counter(keys)  # {'a': 2, 'b': 2, 'c': 1}

bigrams = [('a','b'), ('b','c'), ('c','a'), ('a','b')]
bigram_freq = Counter(bigrams)  # {('a','b'): 2, ...}
```

#### Typing Speed Analysis
```
Algorithm:
  1. Get all keyboard event timestamps
  2. Calculate intervals between consecutive keystrokes
  3. Average interval = total time / number of keystrokes
  4. Estimate WPM: (printable_chars / 5) / (total_seconds / 60)

Example:
  Total keys: 100 (80 printable)
  Time: 60 seconds
  WPM = (80 / 5) / (60 / 60) = 16 / 1 = 16 WPM
```

#### Mouse Movement Analysis
```
Direction Frequency:
  Count occurrences of each direction (up/down/left/right)

Duration Per Direction:
  Track how long mouse moved in each direction
  Average = sum(durations) / count

Output:
{
  "total_direction_changes": 147,
  "direction_frequency": {
    "right": 52,
    "left": 45,
    "down": 30,
    "up": 20
  },
  "avg_duration_per_direction": {
    "right": 850.5,
    "left": 720.3
  }
}
```

#### Click Pattern Analysis
```
Button Frequency:
  Count clicks by button type

Spatial Distribution:
  Track where clicks occur (sample positions)
```

---

### 5. Database Manager (`database.py`)

**Purpose:** Handle data persistence with failover

**Architecture:**
```
Data Flow:
  Session Data (dict)
    ↓
  DatabaseManager
    ├─ Try: Connect to MongoDB
    │   ├─ Ping server (5-second timeout)
    │   ├─ Insert session document
    │   └─ Return True
    │
    └─ Except: Connection Failed
        ├─ Log error
        ├─ Create local_backups/ directory
        ├─ Save to JSON file
        └─ Return False
```

**MongoDB Schema:**
```javascript
db.keylogger_db.sessions
{
  _id: ObjectId(),
  start_time: "2026-03-16T14:23:45",
  end_time: "2026-03-16T14:28:46",
  duration_seconds: 300.5,
  total_events: 1250,
  mouse_events_count: 847,
  keyboard_events_count: 403,
  events: [
    {...},
    {...}
  ],
  patterns: {
    keyboard_patterns: {...},
    mouse_patterns: {...},
    ...
  }
}
```

**Local Backup Format (JSON):**
```
local_backups/
├─ session_20260316_142345.json
├─ session_20260316_142546.json
└─ session_20260316_145123.json
```

**Connection Handling:**
```python
try:
    client = MongoClient(
        host='localhost',
        port=27017,
        serverSelectionTimeoutMS=5000  # 5 second timeout
    )
    client.admin.command('ping')  # Test connection
    self.connected = True
except ServerSelectionTimeoutError:
    # Fallback to local storage
    self.connected = False
    self._store_locally(data)
```

---

### 6. Email Reporter (`email_reporter.py`)

**Purpose:** Generate and send session reports

**SMTP Flow:**
```
send_session_report()
  ├─ Build HTML email body
  ├─ Create MIME message
  ├─ Connect to Gmail SMTP (smtp.gmail.com:587)
  ├─ STARTTLS encryption
  ├─ Authenticate with app password
  ├─ Send message
  └─ Close connection
```

**HTML Report Structure:**
```
Email Report
├─ Session metadata (time, duration)
├─ Input summary (events captured)
├─ Keyboard analysis
│   ├─ Total keys pressed
│   ├─ Most common keys
│   └─ Typing speed (WPM)
├─ Mouse movement analysis
│   ├─ Direction frequency
│   └─ Total movement time
└─ Mouse click analysis
    └─ Click frequency by button
```

**Gmail Authentication:**
```
Why app password instead of regular password?
  └─ Gmail requires 2-Step Verification + app password
     for programmatic access (security feature)

Steps for user:
  1. Enable 2-Step Verification
  2. Go to myaccount.google.com/apppasswords
  3. Select "Mail" and "Windows Computer"
  4. Copy 16-character password to .env
  5. Application uses this for SMTP login
```

---

### 7. Configuration (`config.py`)

**Purpose:** Centralized settings management

**Settings:**
```python
# MongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'keylogger_db'
MONGODB_COLLECTION = 'sessions'

# Email
EMAIL_ADDRESS = 'ambaviaagam@gmail.com'
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Session
MAX_IDLE_TIME = 300  # 5 minutes
SESSION_CHECK_INTERVAL = 1  # Check every 1 second
```

**Environment Variables (.env):**
```
EMAIL_PASSWORD=your_gmail_app_password
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

---

## Data Flow Diagrams

### Complete Session Flow

```
START
  │
  ├─ Initialize SessionManager
  │   ├─ Create MouseTracker
  │   ├─ Create KeyboardTracker
  │   ├─ Create DatabaseManager (test connection)
  │   └─ Create EmailReporter
  │
  ├─ start_session()
  │   ├─ Set session_active = True
  │   ├─ Start MouseTracker listener
  │   ├─ Start KeyboardTracker listener
  │   └─ Start Idle Checker thread
  │
  ├─ MAIN LOOP (while session_active)
  │   │
  │   └─ Every 0.1 seconds:
  │       ├─ MouseTracker captures events
  │       ├─ KeyboardTracker captures events
  │       └─ Update last_activity_time
  │
  ├─ IDLE CHECK THREAD (parallel)
  │   │
  │   └─ Every 1 second:
  │       ├─ idle_time = now() - last_activity_time
  │       └─ If idle_time > 300s:
  │           └─ Call end_session()
  │
  ├─ User presses Ctrl+C OR idle timeout reached
  │   │
  │   └─ end_session()
  │       ├─ Set session_active = False
  │       ├─ Stop MouseTracker
  │       ├─ Stop KeyboardTracker
  │       ├─ Get all events from trackers
  │       ├─ PatternAnalyzer.analyze(events)
  │       ├─ DatabaseManager.insert_session(session_data)
  │       │   ├─ Try MongoDB insert
  │       │   └─ If failed: Local JSON backup
  │       ├─ EmailReporter.send_session_report()
  │       └─ Display final summary
  │
  └─ cleanup()
      └─ DatabaseManager.close()
```

### Event Capture Timing

```
Timeline: 500ms interval shown

t=0ms     │
          ├─ Mouse at (100, 100)
          │
t=100ms   ├─ User starts typing 'h'
          │  └─ KeyboardTracker.on_press('h')
          │     └─ events.append({type: 'key_press', key: 'h'})
          │
t=150ms   ├─ Mouse moves to (150, 120)
          │  └─ MouseTracker.on_move(150, 120)
          │     └─ Detect direction = 'right'
          │
t=200ms   ├─ User types 'e'
          │  └─ KeyboardTracker.on_press('e')
          │
t=300ms   ├─ User releases 'h'
          │  └─ KeyboardTracker.on_release('h')
          │
t=400ms   ├─ User clicks mouse button
          │  └─ MouseTracker.on_click(150, 120, Button.left, pressed=True)
          │     └─ events.append({type: 'mouse_click', button: 'left'})
          │
t=500ms   └─ Mouse continues moving (still 'right')
              └─ MouseTracker.on_move(180, 140)

All events with timestamps → analyze() → patterns
```

---

## Threading Model

**Main Thread:**
- Runs main event loop
- Periodically checks session_active
- Handles Ctrl+C interrupt

**Input Event Thread (pynput internal):**
- MouseTracker listener thread (background)
- KeyboardTracker listener thread (background)
- Non-blocking event delivery to handlers

**Idle Checker Thread:**
- Runs check_idle() in daemon mode
- Sleeps 1 second between checks
- Sets session_active = False when idle timeout reached

```
Main Thread ─────────────────────────────────
  │
  ├─ MouseTracker ────────────────────────── (background)
  │   └─ event listener (pynput internal thread)
  │
  ├─ KeyboardTracker ─────────────────────── (background)
  │   └─ event listener (pynput internal thread)
  │
  └─ Idle Checker Thread ─────────────────── (daemon)
      └─ Checks every 1 second, ends session if timeout
```

---

## Error Handling Strategy

### MongoDB Connection Failure
```
Scenario: MongoDB not running
  ├─ Connection attempt with 5-second timeout
  ├─ Catches ServerSelectionTimeoutError
  ├─ Sets self.connected = False
  ├─ User warned in console
  └─ Later data automatically backed up to JSON
```

### Email Send Failure
```
Scenarios:
  ├─ No EMAIL_PASSWORD configured
  │   └─ Skip email, continue with database storage
  │
  ├─ Gmail authentication failure
  │   └─ Log error, continue with database storage
  │
  └─ SMTP connection error
      └─ Log error, continue with database storage
```

### Event Capture Errors
```
Scenario: pynput raises exception
  ├─ Caught in on_press/on_move/on_click handlers
  ├─ Logged to keylogger.log
  ├─ Event skipped, continue monitoring
  └─ Session continues unaffected
```

---

## Performance Characteristics

| Component | Impact | Notes |
|-----------|--------|-------|
| MouseTracker | ~2-5% CPU | Event-driven, minimal processing |
| KeyboardTracker | ~1-2% CPU | Event-driven, lightweight |
| PatternAnalyzer | Spike at session end | One-time calculation, ~100ms |
| DatabaseManager | 10-50ms | Network call, async possible |
| EmailReporter | 2-5s | SMTP connection, slowest component |
| Memory | ~50MB | Stores events in memory during session |

**Optimization opportunities:**
- Batch database writes
- Async email sending
- Stream pattern analysis instead of at-end

---

## Security Considerations

⚠️ **What this captures:**
- All keyboard input (including passwords!)
- All mouse movement (no app context)
- All clicks

⚠️ **Storage security:**
- Events stored in plain JSON locally
- MongoDB connection not encrypted (unless you setup SSL)
- Email sent via TLS/STARTTLS

⚠️ **Recommendations:**
- Encrypt local backup files
- Use MongoDB Atlas with authentication
- Consider storing only processed patterns, not raw events
- Implement PII filtering

---

## Extensibility

**To add new event types:**
1. Create new handler in input_tracker.py
2. Append events to appropriate list with `type` field
3. Update pattern_analyzer.py to process new type
4. Add analysis to email_reporter.py template

**To add new outputs:**
1. Create new reporter class (e.g., CloudReporter)
2. Implement send() method
3. Call from SessionManager.end_session()

**To add filtering:**
1. Modify event handlers to skip certain keys/positions
2. Add decision logic before events.append()

---

## Testing Approach

**Manual Testing:**
```bash
# 1. Test without MongoDB (local backup)
# 2. Test without email (skip .env EMAIL_PASSWORD)
# 3. Test Ctrl+C during session
# 4. Test idle timeout (wait 5+ minutes)
# 5. Check generated logs and backups
```

**To verify patterns:**
```bash
# Check what was captured
cat local_backups/session_*.json | python -m json.tool
```

---

This completes the full architecture! All modules work together to create a complete input monitoring and analysis system. 🎓
