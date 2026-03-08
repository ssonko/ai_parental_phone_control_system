
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3

app = FastAPI()

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
def command(req: CommandRequest):
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

@app.get("/")
def root():
    return {"status":"advanced parental control server running"}
