# AI Parental Control System

A self-hosted parental monitoring and control system built with **Python, FastAPI, and Streamlit**, with phone automation via **Tasker**.

Designed for parents monitoring their own child's device with full consent.

---

## Features

### Location Tracking
Tracks GPS location on every poll and displays it on a live map in the dashboard.

### App Usage Monitoring
Logs which apps are active on the phone and shows top apps by usage frequency.

### Message Monitoring
Captures message previews from notifications and flags risky keywords such as drugs, violence, and explicit content.

### App Blocklist
Block specific apps by package name from the dashboard. Default blocked apps:
- TikTok (`com.zhiliaoapp.musically`)
- Snapchat (`com.snapchat.android`)
- Telegram (`org.telegram.messenger`)
- Instagram (`com.instagram.android`)

### Remote Device Control
Full remote control from the dashboard:

| Command | Action |
|---|---|
| Lock Device | Locks screen immediately |
| Unlock Device | Releases parent lock |
| Kill Network | Disables WiFi + mobile data |
| Restore Net | Re-enables WiFi + mobile data |
| Capture Screen | Takes screenshot and uploads to server |
| Ping Device | Plays alarm sound |
| Get Location | Forces fresh location report |
| Mute Audio | Sets phone to silent |
| Unmute Audio | Restores normal audio |
| Reboot System | Reboots device (requires root) |

### Persistent Hard Lock
When Lock Device is triggered:
- Sets a `%PARENT_LOCK` flag on the device
- Disables WiFi and mobile data simultaneously
- Locks the screen via Device Admin
- Re-locks instantly every time the screen turns on until Unlock Device is sent from the dashboard

No commercial parental app combines all three in a single command.

### Usage Points System
Reward-based screen time system:
- Award points to the child for good behaviour with a custom reason
- 10 points = 1 minute of screen time
- Redeem points from the dashboard to unlock the phone for a set number of minutes
- Phone automatically re-locks when the time expires via the server scheduler
- Full points history with reasons and timestamps

### Bedtime Mode
Automatically disables internet on a schedule via APScheduler:
- 10:00 PM → Internet Off
- 6:00 AM → Internet On

Configurable via `BEDTIME_HOUR` and `WAKE_HOUR` in `server.py`.

### Screenshot Capture
Remote screenshot is taken on the device, base64 encoded, and uploaded to the server via HTTP POST. Latest screenshot is retrievable via `/screenshot/latest`.

### Command History
All dispatched commands are logged with device, command name, and status (pending/done).

### Child Profile
Set the child's name and age once from the dashboard. The age is used by the AI system to tailor all recommendations to the specific developmental stage.

### AI Threat Intelligence
Claude AI automatically analyses app risks based on the child's age and current trends:
- Identifies risky apps, platforms, and games popular with kids that age
- Flags apps with anonymous strangers, unmoderated content, predatory design, or self-harm risks
- Detects trending social media, video, and messaging apps gaining popularity with minors
- Each recommendation shows risk level (HIGH / MEDIUM / LOW), specific reason, and Android package name
- One-click BLOCK applies the app directly to the blocklist
- Runs automatically every Monday at 3 AM via the scheduler
- Can also be triggered manually from the dashboard at any time
- Skipped recommendations are dismissed and not shown again

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Database | SQLite |
| Scheduler | APScheduler |
| AI Engine | Claude (claude-sonnet-4-6) via Anthropic SDK |
| Dashboard | Streamlit, Pandas |
| Phone Automation | Tasker (Android) |
| Hosting | Railway |

---

## Project Structure

```
parental_control_advanced_project/
├── server.py        # FastAPI backend — all endpoints, scheduler, DB
├── dashboard.py     # Streamlit dashboard — UI and controls
├── parent_monitor.db  # SQLite database (auto-created)
└── screenshot_*.jpg   # Uploaded screenshots (auto-created)
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/report` | Device check-in (location, battery, app) |
| GET | `/get-command/{device}` | Phone polls for pending command |
| POST | `/command` | Dashboard dispatches a command |
| GET | `/commands/history` | Recent command log |
| GET | `/logs` | Full activity log |
| GET | `/location` | Latest GPS location |
| GET | `/apps` | App usage summary |
| GET | `/blocked-apps` | List blocked apps |
| POST | `/blocked-apps` | Add app to blocklist |
| DELETE | `/blocked-apps/{package}` | Remove app from blocklist |
| GET | `/points/{device}` | Get points balance and history |
| POST | `/points/award` | Award points to device |
| POST | `/points/redeem` | Redeem points for screen time |
| POST | `/screenshot` | Receive screenshot upload from device |
| GET | `/screenshot/latest` | Retrieve latest screenshot |
| GET | `/profile/{device}` | Get child profile (name, age) |
| POST | `/profile` | Set child profile |
| POST | `/ai/analyze` | Trigger AI threat scan immediately |
| GET | `/ai/recommendations/{device}` | Get all AI recommendations |
| POST | `/ai/apply/{rec_id}` | Apply recommendation to blocklist |
| DELETE | `/ai/recommendations/{rec_id}` | Dismiss a recommendation |

All write endpoints require `x-api-key` header.

---

## Tasker Setup (Android)

Two tasks required on the child's phone:

**ParentalControl_Poll** — runs every 30 seconds:
1. Reports location, battery, and active app to `/report`
2. Polls `/get-command` for pending commands
3. Executes the command (lock, mute, screenshot, etc.)

**EnforceLock** — triggered by Display State = On profile:
1. Checks if `%PARENT_LOCK` = 1
2. If yes, immediately re-locks the screen

### Required Permissions
- Device Admin — for Lock action
- Root — for `svc wifi/data disable` and reboot
- Accessibility Service — for screenshot capture

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | `changeme123` | Authentication key — change before deploying |
| `SERVER_URL` | `http://localhost:8000` | Backend URL used by dashboard |
| `ANTHROPIC_API_KEY` | — | Required for AI Threat Intelligence feature |
