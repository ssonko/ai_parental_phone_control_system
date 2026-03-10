
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import os

app = FastAPI()

API_KEY = os.environ.get("API_KEY", "changeme123")

def require_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

DEVICE_ID = "child_phone"

BEDTIME_HOUR = 22
WAKE_HOUR = 6

BLOCKED_APPS = [
    "com.zhiliaoapp.musically",
    "com.snapchat.android",
    "org.telegram.messenger",
    "com.instagram.android"
]

conn = sqlite3.connect("parent_monitor.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs(
device TEXT,
lat REAL,
lon REAL,
battery INTEGER,
app TEXT,
message TEXT,
timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS commands(
device TEXT,
command TEXT,
status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_apps(
package TEXT UNIQUE
)
""")

conn.commit()

class DeviceReport(BaseModel):
    device: str
    lat: float | None = None
    lon: float | None = None
    battery: int | None = None
    app: str | None = None
    message: str | None = None
    timestamp: datetime

class CommandRequest(BaseModel):
    device: str
    command: str

def send_command(device, command):
    cursor.execute(
        "INSERT INTO commands VALUES (?,?,?)",
        (device, command, "pending")
    )
    conn.commit()

@app.post("/command")
def command(req: CommandRequest, _=Depends(require_key)):
    send_command(req.device, req.command)
    return {"status":"sent"}

@app.get("/get-command/{device}")
def get_command(device: str):

    cursor.execute(
        "SELECT rowid, command FROM commands WHERE device=? AND status='pending' LIMIT 1",
        (device,)
    )

    row = cursor.fetchone()

    if row:
        cursor.execute(
            "UPDATE commands SET status='done' WHERE rowid=?",
            (row[0],)
        )
        conn.commit()
        return {"command": row[1]}

    return {"command": None}

@app.post("/report")
def report(data: DeviceReport):

    cursor.execute(
        "INSERT INTO logs VALUES (?,?,?,?,?,?,?)",
        (
            data.device,
            data.lat,
            data.lon,
            data.battery,
            data.app,
            data.message,
            str(data.timestamp)
        )
    )
    conn.commit()

    return {"status":"logged"}

@app.get("/logs")
def get_logs():
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100")
    return {"data": cursor.fetchall()}

@app.get("/location")
def get_location():
    cursor.execute("""
    SELECT lat, lon, timestamp
    FROM logs
    WHERE lat IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
    """)
    return {"location": cursor.fetchone()}

@app.get("/apps")
def apps():
    cursor.execute("""
    SELECT app, COUNT(*) as count
    FROM logs
    GROUP BY app
    ORDER BY count DESC
    """)
    return {"data": cursor.fetchall()}

# bedtime scheduler
scheduler = BackgroundScheduler()

def bedtime_on():
    send_command(DEVICE_ID,"disable_internet")

def bedtime_off():
    send_command(DEVICE_ID,"enable_internet")

scheduler.add_job(bedtime_on, 'cron', hour=BEDTIME_HOUR)
scheduler.add_job(bedtime_off, 'cron', hour=WAKE_HOUR)
scheduler.start()

@app.get("/commands/history")
def commands_history(_=Depends(require_key)):
    cursor.execute("SELECT device, command, status FROM commands ORDER BY rowid DESC LIMIT 50")
    rows = cursor.fetchall()
    return {"data": [{"device": r[0], "command": r[1], "status": r[2]} for r in rows]}

class AppBlock(BaseModel):
    package: str

@app.get("/blocked-apps")
def get_blocked_apps(_=Depends(require_key)):
    cursor.execute("SELECT package FROM blocked_apps")
    return {"data": [r[0] for r in cursor.fetchall()]}

@app.post("/blocked-apps")
def add_blocked_app(body: AppBlock, _=Depends(require_key)):
    try:
        cursor.execute("INSERT INTO blocked_apps VALUES (?)", (body.package,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    return {"status": "added"}

@app.delete("/blocked-apps/{package:path}")
def remove_blocked_app(package: str, _=Depends(require_key)):
    cursor.execute("DELETE FROM blocked_apps WHERE package=?", (package,))
    conn.commit()
    return {"status": "removed"}

@app.get("/")
def root():
    return {"status":"advanced parental control server running"}
