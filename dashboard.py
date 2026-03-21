
import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(
    page_title="ParentShield AI",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SERVER = os.environ.get("SERVER_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "changeme123")
HEADERS = {"x-api-key": API_KEY}

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600&family=Share+Tech+Mono&display=swap');

/* ── Base ── */
.stApp {
    background: radial-gradient(ellipse at 20% 20%, #07101f 0%, #030609 60%, #07101f 100%);
    font-family: 'Rajdhani', sans-serif;
    color: #c8dff0;
}
.stApp::before {
    content:'';
    position:fixed; inset:0;
    background-image:
        linear-gradient(rgba(0,212,255,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.035) 1px, transparent 1px);
    background-size: 44px 44px;
    pointer-events:none; z-index:0;
}

/* Hide chrome */
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:0.8rem; padding-bottom:2rem; }

/* Scrollbar */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:#030609; }
::-webkit-scrollbar-thumb { background:linear-gradient(#00d4ff,#7b2fff); border-radius:3px; }

/* Fonts */
h1,h2,h3 { font-family:'Orbitron',monospace !important; }

/* ── Inputs ── */
.stTextInput input, .stPasswordInput input {
    background: rgba(0,212,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.28) !important;
    border-radius: 4px !important;
    color: #c8dff0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
}
.stTextInput input:focus, .stPasswordInput input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 14px rgba(0,212,255,0.35), inset 0 0 6px rgba(0,212,255,0.06) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stPasswordInput input::placeholder {
    color: rgba(0,212,255,0.3) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.10), rgba(0,60,100,0.18)) !important;
    border: 1px solid rgba(0,212,255,0.42) !important;
    border-radius: 4px !important;
    color: #00d4ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    transition: all 0.22s cubic-bezier(.4,0,.2,1) !important;
    width: 100% !important;
    padding: 0.58rem 0.5rem !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::after {
    content:'';
    position:absolute; inset:0;
    background:linear-gradient(135deg,rgba(0,212,255,0.08),transparent);
    opacity:0; transition:opacity 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.22), rgba(0,100,160,0.3)) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.45), inset 0 0 10px rgba(0,212,255,0.08) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active { transform:translateY(0) !important; }

/* Danger buttons */
.btn-danger .stButton > button {
    border-color: rgba(255,50,70,0.45) !important;
    color: #ff5060 !important;
    background: linear-gradient(135deg, rgba(255,50,70,0.07), rgba(100,0,15,0.15)) !important;
}
.btn-danger .stButton > button:hover {
    border-color: #ff5060 !important;
    box-shadow: 0 0 20px rgba(255,50,70,0.45) !important;
    color: #fff !important;
    background: linear-gradient(135deg, rgba(255,50,70,0.2), rgba(160,0,25,0.28)) !important;
}
/* Success buttons */
.btn-success .stButton > button {
    border-color: rgba(0,255,128,0.42) !important;
    color: #00ff88 !important;
    background: linear-gradient(135deg, rgba(0,255,128,0.07), rgba(0,70,35,0.15)) !important;
}
.btn-success .stButton > button:hover {
    border-color: #00ff88 !important;
    box-shadow: 0 0 20px rgba(0,255,128,0.45) !important;
    color: #fff !important;
    background: linear-gradient(135deg, rgba(0,255,128,0.18), rgba(0,100,50,0.28)) !important;
}
/* Warning buttons */
.btn-warn .stButton > button {
    border-color: rgba(255,180,0,0.42) !important;
    color: #ffb400 !important;
    background: linear-gradient(135deg, rgba(255,180,0,0.07), rgba(80,50,0,0.15)) !important;
}
.btn-warn .stButton > button:hover {
    border-color: #ffb400 !important;
    box-shadow: 0 0 20px rgba(255,180,0,0.45) !important;
    color: #fff !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(0,25,50,0.35) 100%) !important;
    border: 1px solid rgba(0,212,255,0.22) !important;
    border-radius: 8px !important;
    padding: 1rem 1.1rem !important;
    position: relative; overflow: hidden;
}
[data-testid="stMetric"]::after {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,212,255,0.5),transparent);
}
[data-testid="stMetricLabel"] {
    color: rgba(0,212,255,0.6) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.15em !important;
}
[data-testid="stMetricValue"] {
    color: #fff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 1.55rem !important;
    text-shadow: 0 0 14px rgba(0,212,255,0.5) !important;
}
[data-testid="stMetricDelta"] { font-family:'Rajdhani',sans-serif !important; font-size:0.82rem !important; }

/* ── Dataframes ── */
.stDataFrame { border: 1px solid rgba(0,212,255,0.18) !important; border-radius:8px !important; overflow:hidden; }
[data-testid="stDataFrame"] > div { background:rgba(3,10,22,0.85) !important; }

/* ── Alerts ── */
.stAlert { border-radius:6px !important; font-family:'Rajdhani',sans-serif !important; border-left-width:3px !important; font-size:0.9rem !important; }

/* ── Misc ── */
.stSelectbox div, .stTextArea textarea {
    background:rgba(0,212,255,0.04) !important;
    border:1px solid rgba(0,212,255,0.28) !important;
    color:#c8dff0 !important;
    font-family:'Share Tech Mono',monospace !important;
}

/* ── Animations ── */
@keyframes pulse    { 0%,100%{opacity:1} 50%{opacity:0.35} }
@keyframes shimmer  { from{background-position:0%} to{background-position:200%} }
@keyframes scanFade { from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:translateY(0)} }
@keyframes orbFloat { from{transform:translate(0,0) scale(1)} to{transform:translate(16px,16px) scale(1.08)} }
@keyframes gridScroll { from{background-position:0 0} to{background-position:0 44px} }
@keyframes shieldPulse {
    0%,100%{ filter:drop-shadow(0 0 10px rgba(0,212,255,0.4)); transform:scale(1); }
    50%    { filter:drop-shadow(0 0 26px rgba(0,212,255,0.85)); transform:scale(1.07); }
}
@keyframes cardAppear {
    from{ opacity:0; transform:translateY(28px) scale(0.97); }
    to  { opacity:1; transform:translateY(0)    scale(1); }
}
@keyframes borderGlow {
    0%,100%{ box-shadow:0 0 8px rgba(0,212,255,0.2); }
    50%    { box-shadow:0 0 22px rgba(0,212,255,0.5),0 0 40px rgba(123,47,255,0.15); }
}

/* ══ LOGIN PAGE STYLES ══ */
/* Floating orbs */
.orb { position:fixed;border-radius:50%;filter:blur(70px);pointer-events:none;z-index:0; }
.orb1 { width:340px;height:340px;background:rgba(0,212,255,0.09);top:-100px;left:-100px;
         animation:orbFloat 7s ease-in-out infinite alternate; }
.orb2 { width:280px;height:280px;background:rgba(123,47,255,0.11);bottom:-80px;right:-80px;
         animation:orbFloat 9s ease-in-out infinite alternate-reverse; }
.orb3 { width:200px;height:200px;background:rgba(0,255,128,0.06);top:45%;left:65%;
         animation:orbFloat 5s ease-in-out infinite alternate; }

/* Card frame */
.lc {
    position:relative;
    background:linear-gradient(145deg,rgba(0,212,255,0.08) 0%,rgba(5,12,28,0.97) 50%,rgba(123,47,255,0.07) 100%);
    border:1px solid rgba(0,212,255,0.3);
    border-radius:14px;
    padding:2.2rem 2rem 1.4rem;
    backdrop-filter:blur(24px);
    box-shadow:0 0 50px rgba(0,212,255,0.09),0 0 90px rgba(123,47,255,0.05),
               inset 0 1px 0 rgba(0,212,255,0.2);
    animation:cardAppear 0.5s cubic-bezier(.2,.8,.4,1) forwards,
              borderGlow 4s ease-in-out 0.5s infinite;
}
/* Corner brackets */
.lc-c { position:absolute;width:16px;height:16px; }
.lc-tl { top:-1px;left:-1px;border-top:2px solid #00d4ff;border-left:2px solid #00d4ff;border-radius:3px 0 0 0; }
.lc-tr { top:-1px;right:-1px;border-top:2px solid #00d4ff;border-right:2px solid #00d4ff;border-radius:0 3px 0 0; }
.lc-bl { bottom:-1px;left:-1px;border-bottom:2px solid #00d4ff;border-left:2px solid #00d4ff;border-radius:0 0 0 3px; }
.lc-br { bottom:-1px;right:-1px;border-bottom:2px solid #00d4ff;border-right:2px solid #00d4ff;border-radius:0 0 3px 0; }

/* Shield icon */
.ls { font-size:3.6rem;display:block;text-align:center;margin-bottom:0.4rem;
      animation:shieldPulse 3.5s ease-in-out infinite; }
/* Title */
.lt {
    font-family:'Orbitron',monospace; font-size:1.65rem; font-weight:900;
    background:linear-gradient(135deg,#00d4ff 0%,#7b2fff 55%,#00d4ff 100%);
    background-size:200%;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    letter-spacing:0.07em; text-align:center; margin-bottom:0.2rem;
    animation:shimmer 5s linear infinite;
}
/* Tagline */
.ltag {
    font-family:'Rajdhani',sans-serif; font-size:0.68rem;
    color:rgba(0,212,255,0.4); letter-spacing:0.3em; text-transform:uppercase;
    text-align:center; margin-bottom:1.6rem;
}
/* Auth separator */
.las {
    display:flex; align-items:center; gap:8px; margin-bottom:0.8rem;
    font-family:'Orbitron',monospace; font-size:0.57rem;
    color:rgba(0,212,255,0.5); letter-spacing:0.2em; text-transform:uppercase;
}
.las::before,.las::after {
    content:''; flex:1; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,212,255,0.35));
}
.las::after { background:linear-gradient(90deg,rgba(0,212,255,0.35),transparent); }

/* Status bar */
.lss {
    display:flex; justify-content:center; gap:24px; margin-top:1.2rem;
    font-family:'Share Tech Mono',monospace; font-size:0.58rem;
    color:rgba(0,212,255,0.28); letter-spacing:0.1em; text-transform:uppercase;
}
.lsd {
    display:inline-block; width:5px; height:5px; border-radius:50%;
    background:#00ff88; box-shadow:0 0 7px #00ff88; margin-right:5px;
    animation:pulse 2s infinite; vertical-align:middle;
}

/* ══ REMOTE CONTROL BUTTON ICONS ══ */
.ctrl-btn .stButton > button {
    color: #ffffff !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.06em !important;
}
.ctrl-btn .stButton > button:hover { color: #ffffff !important; }
.btn-danger.ctrl-btn .stButton > button  { color:#ffffff !important; }
.btn-success.ctrl-btn .stButton > button { color:#ffffff !important; }
.btn-warn.ctrl-btn .stButton > button    { color:#ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
def icon_box(symbol, color="#00d4ff"):
    return f"""<span style="
        display:inline-flex; align-items:center; justify-content:center;
        width:28px; height:28px; border-radius:5px; flex-shrink:0;
        background:linear-gradient(135deg,{color}18,{color}08);
        border:1px solid {color}44;
        font-family:'Share Tech Mono',monospace; font-size:0.75rem;
        color:{color}; text-shadow:0 0 8px {color};
    ">{symbol}</span>"""

def section_header(symbol, title, subtitle="", color="#00d4ff"):
    ib = icon_box(symbol, color)
    sub = f"<div style='font-size:0.72rem;color:rgba(180,220,255,0.4);margin-top:2px;letter-spacing:0.04em;'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
    <div style="
        display:flex; align-items:center; gap:12px;
        padding:0.7rem 1.1rem; margin:1.3rem 0 0.5rem;
        background:linear-gradient(90deg,{color}12 0%,transparent 100%);
        border-left:2px solid {color};
        border-radius:0 6px 6px 0;
        animation:scanFade 0.4s ease;
    ">
        {ib}
        <div>
            <div style="font-family:'Orbitron',monospace;font-size:0.78rem;font-weight:700;
                        color:{color};letter-spacing:0.12em;text-transform:uppercase;">{title}</div>
            {sub}
        </div>
    </div>
    """, unsafe_allow_html=True)

def neon_divider(color="rgba(0,212,255,0.35)"):
    st.markdown(f"""
    <div style="height:1px;background:linear-gradient(90deg,transparent,{color},transparent);margin:1.1rem 0;"></div>
    """, unsafe_allow_html=True)

def blocked_pill(pkg):
    return f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;
                background:rgba(255,50,70,0.06);border:1px solid rgba(255,50,70,0.22);
                border-radius:5px;padding:0.38rem 0.8rem;color:#ff7080;
                display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="color:#ff3040;font-size:0.65rem;">&#x2297;</span> {pkg}
    </div>"""

# ══════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Orbs rendered once — CSS classes defined in global block above
    st.markdown("""
    <div class="orb orb1"></div>
    <div class="orb orb2"></div>
    <div class="orb orb3"></div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 1.15, 1])
    with col_c:
        # Card frame — pure HTML, no <style> tags
        st.markdown("""
        <div class="lc">
            <div class="lc-c lc-tl"></div><div class="lc-c lc-tr"></div>
            <div class="lc-c lc-bl"></div><div class="lc-c lc-br"></div>
            <span class="ls">&#x1F6E1;&#xFE0F;</span>
            <div class="lt">PARENTSHIELD AI</div>
            <div class="ltag">&#x25C6; Next-Gen Child Safety Platform &#x25C6;</div>
            <div class="las">Secure Authentication</div>
        </div>
        """, unsafe_allow_html=True)

        key = st.text_input("api_key", type="password", label_visibility="collapsed",
                            placeholder="&#x2B21;  Enter API key...")
        if st.button("\u23e3  AUTHENTICATE", use_container_width=True):
            if key == API_KEY:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("\u26d4  Access denied — invalid credentials")

        st.markdown("""
        <div class="lss">
            <span><span class="lsd"></span>ONLINE</span>
            <span>&bull; AES-256 &bull;</span>
            <span>&bull; v2.0.0 &bull;</span>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════
#  MAIN DASHBOARD HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:0.5rem 0;margin-bottom:0.4rem;">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:38px;height:38px;border-radius:8px;
                    background:linear-gradient(135deg,rgba(0,212,255,0.18),rgba(123,47,255,0.15));
                    border:1px solid rgba(0,212,255,0.35);
                    display:flex;align-items:center;justify-content:center;
                    font-family:'Share Tech Mono',monospace;font-size:1.1rem;
                    color:#00d4ff;text-shadow:0 0 10px #00d4ff;
                    box-shadow:0 0 14px rgba(0,212,255,0.2);">
            &#x25C6;
        </div>
        <div>
            <div style="font-family:'Orbitron',monospace;font-size:1.15rem;font-weight:900;
                        background:linear-gradient(135deg,#00d4ff,#7b2fff);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        letter-spacing:0.06em;">PARENTSHIELD AI</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
                        color:rgba(0,212,255,0.38);letter-spacing:0.18em;">
                REAL-TIME CHILD SAFETY MONITOR
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:20px;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.58rem;
                    color:rgba(0,212,255,0.35);letter-spacing:0.1em;">
            DEVICE&nbsp;<span style="color:#00d4ff;">CHILD_PHONE</span>
        </div>
        <div style="display:flex;align-items:center;gap:7px;">
            <div style="width:7px;height:7px;border-radius:50%;background:#00ff88;
                        box-shadow:0 0 8px #00ff88;animation:pulse 2s infinite;"></div>
            <span style="font-family:'Orbitron',monospace;font-size:0.55rem;
                         color:#00ff88;letter-spacing:0.15em;">ONLINE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

neon_divider()

# ══════════════════════════════════════════════════════════
#  DATA FETCH
# ══════════════════════════════════════════════════════════
try:
    logs_data = requests.get(f"{SERVER}/logs", headers=HEADERS).json().get("data", [])
    df = pd.DataFrame(logs_data, columns=["device","lat","lon","battery","app","message","timestamp"])
except Exception:
    df = pd.DataFrame()

risky_words = ["drug","fight","kill","nude"]

# ══════════════════════════════════════════════════════════
#  KPI ROW
# ══════════════════════════════════════════════════════════
m1, m2, m3, m4 = st.columns(4)
with m1:
    batt = df["battery"].dropna().iloc[-1] if not df.empty and "battery" in df.columns and not df["battery"].dropna().empty else "—"
    st.metric("BATTERY LVL", f"{batt}%" if batt != "—" else "—")
with m2:
    apps = df["app"].nunique() if not df.empty and "app" in df.columns else 0
    st.metric("APPS TRACKED", apps)
with m3:
    events = len(df) if not df.empty else 0
    st.metric("TOTAL EVENTS", events)
with m4:
    flags = int(df["message"].fillna("").str.lower().str.contains("|".join(risky_words)).sum()) if not df.empty and "message" in df.columns else 0
    st.metric("SAFETY FLAGS", flags, delta="CLEAR" if not flags else f"{flags} REVIEW")

neon_divider()

# ══════════════════════════════════════════════════════════
#  LOCATION + ACTIVITY
# ══════════════════════════════════════════════════════════
col_map, col_act = st.columns([1, 1.65])

with col_map:
    section_header("&#x25CE;", "GPS Location", "Last known coordinates")
    if not df.empty and "lat" in df.columns:
        coords = df.dropna(subset=["lat","lon"])
        if not coords.empty:
            st.map(coords[['lat','lon']].tail(1), use_container_width=True)
        else:
            st.info("No GPS fix available.")
    else:
        st.info("Awaiting location data...")

with col_act:
    section_header("&#x2630;", "Activity Log", "Last 20 recorded events")
    if not df.empty:
        st.dataframe(
            df.tail(20).copy(),
            use_container_width=True,
            height=310,
            column_config={
                "battery": st.column_config.NumberColumn("Battery %", format="%d%%"),
                "timestamp": st.column_config.TextColumn("Timestamp"),
            }
        )
    else:
        st.info("No activity recorded yet.")

neon_divider()

# ══════════════════════════════════════════════════════════
#  ANALYTICS + SAFETY
# ══════════════════════════════════════════════════════════
col_chart, col_flags = st.columns([1.3, 1])

with col_chart:
    section_header("&#x25A6;", "App Analytics", "Usage frequency by application")
    if not df.empty and "app" in df.columns and df["app"].notna().any():
        chart_data = df["app"].value_counts().reset_index()
        chart_data.columns = ["App", "Sessions"]
        st.bar_chart(chart_data.set_index("App"), use_container_width=True, height=260)
    else:
        st.info("No app data yet.")

with col_flags:
    section_header("&#x25B2;", "Safety Alerts", "Flagged content detection", color="#ff5060")
    if not df.empty and "message" in df.columns:
        flagged = df[df["message"].fillna("").str.lower().str.contains("|".join(risky_words))]
        if not flagged.empty:
            st.dataframe(flagged[["timestamp","app","message"]].tail(10),
                         use_container_width=True, height=260)
        else:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        height:200px;border:1px solid rgba(0,255,128,0.18);border-radius:10px;
                        background:rgba(0,255,128,0.025);">
                <div style="font-family:'Share Tech Mono',monospace;font-size:2rem;
                            color:#00ff88;text-shadow:0 0 18px #00ff88;">&#x2713;</div>
                <div style="font-family:'Orbitron',monospace;font-size:0.62rem;
                            color:#00ff88;letter-spacing:0.18em;margin-top:0.6rem;">ALL CLEAR</div>
                <div style="font-size:0.72rem;color:rgba(0,255,128,0.4);margin-top:0.3rem;">
                    No flagged messages detected
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No messages to analyze.")

neon_divider()

# ══════════════════════════════════════════════════════════
#  REMOTE CONTROLS
# ══════════════════════════════════════════════════════════
section_header("&#x25C8;", "Remote Control", "Dispatch commands to device")

def send(cmd):
    requests.post(f"{SERVER}/command", json={"device":"child_phone","command":cmd}, headers=HEADERS)
    st.toast(f"Command dispatched → `{cmd}`", icon="⚡")

controls = [
    # (label,                      command,            style)
    ("\u29BF  LOCK DEVICE",         "lock_phone",       "danger"),
    ("\u2298  KILL NETWORK",        "disable_internet", "danger"),
    ("\u2295  RESTORE NET",         "enable_internet",  "success"),
    ("\u25A6  CAPTURE SCREEN",      "take_screenshot",  "default"),
    ("\u25CE  PING DEVICE",         "ring_phone",       "warn"),
    ("\u2316  GET LOCATION",        "get_location",     "default"),
    ("\u29B8  MUTE AUDIO",          "mute_phone",       "default"),
    ("\u29BE  UNMUTE AUDIO",        "unmute_phone",     "default"),
    ("\u27F3  REBOOT SYS",          "reboot_device",    "danger"),
]

ctrl_cols = st.columns(3)
for idx, (label, cmd, style) in enumerate(controls):
    with ctrl_cols[idx % 3]:
        wrap = f'btn-{style} ctrl-btn' if style in ("danger","success","warn") else "ctrl-btn"
        st.markdown(f'<div class="{wrap}">', unsafe_allow_html=True)
        if st.button(label, key=f"ctrl_{cmd}", use_container_width=True):
            send(cmd)
        st.markdown('</div>', unsafe_allow_html=True)

neon_divider()

# ══════════════════════════════════════════════════════════
#  CUSTOM COMMAND + HISTORY
# ══════════════════════════════════════════════════════════
col_cust, col_hist = st.columns([1, 1.6])

with col_cust:
    section_header("&#x232A;_", "Custom Command", "Send any raw command string")
    custom = st.text_input("CMD", placeholder="> clear_cache", label_visibility="collapsed")
    if st.button("\u21a3  TX DISPATCH", use_container_width=True) and custom.strip():
        send(custom.strip())

with col_hist:
    section_header("&#x21BA;", "Command History", "Previously dispatched commands")
    try:
        history = requests.get(f"{SERVER}/commands/history", headers=HEADERS).json().get("data", [])
        if history:
            st.dataframe(history, use_container_width=True, height=210)
        else:
            st.info("No commands in history.")
    except Exception:
        st.warning("Could not reach command history endpoint.")

neon_divider()

# ══════════════════════════════════════════════════════════
#  BLOCKED APPS
# ══════════════════════════════════════════════════════════
section_header("&#x2297;", "App Blocklist", "Blocked package management", color="#ff5060")

col_bl, col_ba = st.columns([1.6, 1])

with col_bl:
    try:
        blocked = requests.get(f"{SERVER}/blocked-apps", headers=HEADERS).json().get("data", [])
        if blocked:
            for pkg in blocked:
                c1, c2 = st.columns([5, 1])
                c1.markdown(blocked_pill(pkg), unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if st.button("&#x2715;", key=f"rm_{pkg}", use_container_width=True):
                        requests.delete(f"{SERVER}/blocked-apps/{pkg}", headers=HEADERS)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No apps currently on blocklist.")
    except Exception:
        st.warning("Could not load blocked apps.")

with col_ba:
    section_header("&#x2295;", "Add to Blocklist", "Enter package identifier")
    new_pkg = st.text_input("PKG", placeholder="com.example.app", label_visibility="collapsed")
    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
    if st.button("\u2298  BLOCK APP", use_container_width=True) and new_pkg.strip():
        requests.post(f"{SERVER}/blocked-apps", json={"package": new_pkg.strip()}, headers=HEADERS)
        st.success(f"Blocked: `{new_pkg.strip()}`")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════
neon_divider()
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:0.4rem 0 1rem;opacity:0.35;">
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;
                 color:rgba(0,212,255,0.6);letter-spacing:0.15em;">
        PARENTSHIELD AI &nbsp;&#x25C6;&nbsp; v2.0.0
    </span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;
                 color:rgba(0,212,255,0.6);letter-spacing:0.15em;">
        AES-256 ENCRYPTED &nbsp;&#x25C6;&nbsp; ALL SYSTEMS NOMINAL
    </span>
</div>
""", unsafe_allow_html=True)
