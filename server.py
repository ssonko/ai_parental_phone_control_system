
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import os
import json
from openai import OpenAI

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS points(
device TEXT,
amount INTEGER,
reason TEXT,
timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS child_profile(
device TEXT PRIMARY KEY,
name TEXT,
age INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
device TEXT,
sender TEXT,
message TEXT,
matched_keywords TEXT,
timestamp TEXT,
reviewed INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_recommendations(
id INTEGER PRIMARY KEY AUTOINCREMENT,
device TEXT,
app_name TEXT,
package TEXT,
reason TEXT,
risk_level TEXT,
action TEXT,
category TEXT,
timestamp TEXT,
applied INTEGER DEFAULT 0
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

ALERT_KEYWORDS = [
    # violence
    "kill","murder","stab","shoot","beat up","fight","weapon","gun","knife",
    # drugs
    "drug","weed","cocaine","pills","molly","xanax","lean","smoke","vape",
    # sexual
    "nude","nudes","send pics","sex","porn","meet up","come over","alone",
    # self harm
    "suicide","self harm","cut myself","end it","hate myself","want to die",
    # bullying
    "ugly","loser","nobody likes","kill yourself","kys","freak",
    # predatory
    "secret","don't tell","just us","keep this between","how old are you","snapchat me",
]

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

    if data.message and data.app == "SMS":
        msg_lower = data.message.lower()
        matched = [kw for kw in ALERT_KEYWORDS if kw in msg_lower]
        if matched:
            sender = ""
            if "FROM:" in data.message:
                try:
                    sender = data.message.split("FROM:")[1].split(" MSG:")[0].strip()
                except Exception:
                    pass
            cursor.execute(
                "INSERT INTO alerts (device, sender, message, matched_keywords, timestamp) VALUES (?,?,?,?,?)",
                (data.device, sender, data.message, ", ".join(matched), str(data.timestamp))
            )

    conn.commit()
    return {"status":"logged"}

@app.get("/alerts")
def get_alerts(_=Depends(require_key)):
    cursor.execute("SELECT id, device, sender, message, matched_keywords, timestamp, reviewed FROM alerts ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    return {"data": [
        {"id": r[0], "device": r[1], "sender": r[2], "message": r[3],
         "matched_keywords": r[4], "timestamp": r[5], "reviewed": r[6]}
        for r in rows
    ]}

@app.post("/alerts/{alert_id}/reviewed")
def mark_reviewed(alert_id: int, _=Depends(require_key)):
    cursor.execute("UPDATE alerts SET reviewed=1 WHERE id=?", (alert_id,))
    conn.commit()
    return {"status": "marked reviewed"}

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

def run_ai_analysis(device=DEVICE_ID):
    cursor.execute("SELECT age, name FROM child_profile WHERE device=?", (device,))
    row = cursor.fetchone()
    age = row[0] if row else 13
    name = row[1] if row else "the child"

    cursor.execute("SELECT package FROM blocked_apps")
    already_blocked = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT package FROM ai_recommendations WHERE device=? AND applied=1", (device,))
    already_applied = [r[0] for r in cursor.fetchall()]
    exclude = list(set(already_blocked + already_applied))

    ai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = f"""You are a child digital safety expert. A parent needs help protecting their {age}-year-old child ({name}) on Android.

Provide a JSON array of apps, platforms, or digital threats to block or monitor for a {age}-year-old in {datetime.now().year}.

Consider:
- Age-appropriate restrictions for a {age}-year-old
- Popular social media, video, gaming, and messaging apps used by kids this age
- Apps known for predatory behaviour, anonymous strangers, unmoderated content, or self-harm risks
- Trending platforms gaining popularity with children that carry risks
- Apps with excessive screen time mechanics or addictive design targeting minors

Exclude these already-blocked packages: {exclude}

Return ONLY a valid JSON array, no other text:
[
  {{
    "app_name": "App Name",
    "package": "com.example.package",
    "reason": "Specific risk for a {age}-year-old",
    "risk_level": "high|medium|low",
    "action": "block|monitor",
    "category": "social_media|video|gaming|messaging|other"
  }}
]

Include 10-15 real apps with correct Android package names. Prioritise high-risk items first."""

    response = ai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        response_format={"type": "json_object"}
    )

    raw = json.loads(response.choices[0].message.content)
    recs = raw if isinstance(raw, list) else next(iter(raw.values()))
    for rec in recs:
        pkg = rec.get("package", "")
        if not pkg or pkg in exclude:
            continue
        cursor.execute("""
            INSERT INTO ai_recommendations
            (device, app_name, package, reason, risk_level, action, category, timestamp, applied)
            VALUES (?,?,?,?,?,?,?,?,0)
        """, (
            device,
            rec.get("app_name", ""),
            pkg,
            rec.get("reason", ""),
            rec.get("risk_level", "medium"),
            rec.get("action", "monitor"),
            rec.get("category", "other"),
            str(datetime.now())
        ))
    conn.commit()

scheduler.add_job(bedtime_on, 'cron', hour=BEDTIME_HOUR)
scheduler.add_job(bedtime_off, 'cron', hour=WAKE_HOUR)
scheduler.add_job(run_ai_analysis, 'cron', day_of_week='mon', hour=3)
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

class PointsAward(BaseModel):
    device: str
    amount: int
    reason: str = ""

class PointsRedeem(BaseModel):
    device: str
    minutes: int

@app.get("/points/{device}")
def get_points(device: str, _=Depends(require_key)):
    cursor.execute("SELECT COALESCE(SUM(amount),0) FROM points WHERE device=?", (device,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT amount, reason, timestamp FROM points WHERE device=? ORDER BY rowid DESC LIMIT 20", (device,))
    history = [{"amount": r[0], "reason": r[1], "timestamp": r[2]} for r in cursor.fetchall()]
    return {"total": total, "history": history}

@app.post("/points/award")
def award_points(body: PointsAward, _=Depends(require_key)):
    cursor.execute(
        "INSERT INTO points VALUES (?,?,?,?)",
        (body.device, body.amount, body.reason, str(datetime.now()))
    )
    conn.commit()
    return {"status": "awarded", "amount": body.amount}

@app.post("/points/redeem")
def redeem_points(body: PointsRedeem, _=Depends(require_key)):
    from datetime import timedelta
    cursor.execute("SELECT COALESCE(SUM(amount),0) FROM points WHERE device=?", (body.device,))
    total = cursor.fetchone()[0]
    cost = body.minutes * 10
    if total < cost:
        raise HTTPException(status_code=400, detail=f"Not enough points. Need {cost}, have {total}.")
    cursor.execute(
        "INSERT INTO points VALUES (?,?,?,?)",
        (body.device, -cost, f"Redeemed {body.minutes} min screen time", str(datetime.now()))
    )
    conn.commit()
    send_command(body.device, "unlock_phone")
    relock_time = datetime.now() + timedelta(minutes=body.minutes)
    scheduler.add_job(
        send_command, 'date',
        run_date=relock_time,
        args=[body.device, "lock_phone"],
        id=f"relock_{body.device}",
        replace_existing=True,
        misfire_grace_time=60,
    )
    return {"status": "redeemed", "minutes": body.minutes, "points_spent": cost, "remaining": total - cost}

class ChildProfile(BaseModel):
    device: str
    name: str
    age: int

@app.get("/profile/{device}")
def get_profile(device: str, _=Depends(require_key)):
    cursor.execute("SELECT name, age FROM child_profile WHERE device=?", (device,))
    row = cursor.fetchone()
    return {"name": row[0], "age": row[1]} if row else {"name": None, "age": None}

@app.post("/profile")
def set_profile(body: ChildProfile, _=Depends(require_key)):
    cursor.execute("INSERT OR REPLACE INTO child_profile VALUES (?,?,?)",
                   (body.device, body.name, body.age))
    conn.commit()
    return {"status": "saved"}

@app.post("/ai/analyze")
def trigger_ai_analysis(_=Depends(require_key)):
    try:
        run_ai_analysis()
        return {"status": "analysis complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/recommendations/{device}")
def get_recommendations(device: str, _=Depends(require_key)):
    cursor.execute("""
        SELECT id, app_name, package, reason, risk_level, action, category, timestamp, applied
        FROM ai_recommendations WHERE device=?
        ORDER BY CASE risk_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, timestamp DESC
    """, (device,))
    rows = cursor.fetchall()
    return {"data": [
        {"id": r[0], "app_name": r[1], "package": r[2], "reason": r[3],
         "risk_level": r[4], "action": r[5], "category": r[6], "timestamp": r[7], "applied": r[8]}
        for r in rows
    ]}

@app.post("/ai/apply/{rec_id}")
def apply_recommendation(rec_id: int, _=Depends(require_key)):
    cursor.execute("SELECT package FROM ai_recommendations WHERE id=?", (rec_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        cursor.execute("INSERT INTO blocked_apps VALUES (?)", (row[0],))
    except sqlite3.IntegrityError:
        pass
    cursor.execute("UPDATE ai_recommendations SET applied=1 WHERE id=?", (rec_id,))
    conn.commit()
    return {"status": "applied"}

@app.delete("/ai/recommendations/{rec_id}")
def dismiss_recommendation(rec_id: int, _=Depends(require_key)):
    cursor.execute("DELETE FROM ai_recommendations WHERE id=?", (rec_id,))
    conn.commit()
    return {"status": "dismissed"}

@app.get("/")
def root():
    return {"status":"advanced parental control server running"}
