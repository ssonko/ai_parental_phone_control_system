
import streamlit as st
import pandas as pd
import requests
import sqlite3
import os

SERVER = os.environ.get("SERVER_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "changeme123")
HEADERS = {"x-api-key": API_KEY}

# --- Login gate ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Parent Dashboard Login")
    key = st.text_input("API Key", type="password")
    if st.button("Login"):
        if key == API_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid API key")
    st.stop()

st.title("📱 Parent Monitoring Dashboard")

conn = sqlite3.connect("parent_monitor.db")
df = pd.read_sql("SELECT * FROM logs", conn)

st.subheader("📍 Last Known Location")
if not df.empty and "lat" in df:
    coords=df.dropna(subset=["lat","lon"])
    if not coords.empty:
        st.map(coords[['lat','lon']].tail(1))

st.subheader("Recent Activity")
st.dataframe(df.tail(20))

st.subheader("Top Apps Used")
if not df.empty:
    st.bar_chart(df['app'].value_counts())

st.subheader("Remote Controls")

def send(cmd):
    requests.post(f"{SERVER}/command", json={"device": "child_phone", "command": cmd}, headers=HEADERS)
    st.success(f"Command sent: `{cmd}`")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔒 Lock Phone"):
        send("lock_phone")
with col2:
    if st.button("🌐 Disable Internet"):
        send("disable_internet")
with col3:
    if st.button("✅ Enable Internet"):
        send("enable_internet")

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("📸 Take Screenshot"):
        send("take_screenshot")
with col5:
    if st.button("🔔 Ring Phone"):
        send("ring_phone")
with col6:
    if st.button("📍 Request Location"):
        send("get_location")

col7, col8, col9 = st.columns(3)
with col7:
    if st.button("🔇 Mute Phone"):
        send("mute_phone")
with col8:
    if st.button("🔊 Unmute Phone"):
        send("unmute_phone")
with col9:
    if st.button("🔄 Reboot Device"):
        send("reboot_device")

st.subheader("Custom Command")
custom = st.text_input("Command name", placeholder="e.g. clear_cache")
if st.button("Send Custom Command") and custom.strip():
    send(custom.strip())

st.subheader("Command History")
try:
    history = requests.get(f"{SERVER}/commands/history", headers=HEADERS).json().get("data", [])
    if history:
        st.dataframe(history)
    else:
        st.info("No commands sent yet.")
except:
    st.warning("Could not load command history.")

st.subheader("Blocked Apps")
try:
    blocked = requests.get(f"{SERVER}/blocked-apps", headers=HEADERS).json().get("data", [])
    if blocked:
        for pkg in blocked:
            col_pkg, col_rm = st.columns([4, 1])
            col_pkg.code(pkg)
            if col_rm.button("Remove", key=f"rm_{pkg}"):
                requests.delete(f"{SERVER}/blocked-apps/{pkg}", headers=HEADERS)
                st.rerun()
    else:
        st.info("No apps blocked.")
except:
    st.warning("Could not load blocked apps.")

new_pkg = st.text_input("Package name to block", placeholder="e.g. com.example.app")
if st.button("Block App") and new_pkg.strip():
    requests.post(f"{SERVER}/blocked-apps", json={"package": new_pkg.strip()}, headers=HEADERS)
    st.success(f"Blocked: {new_pkg.strip()}")
    st.rerun()

st.subheader("Basic Safety Check")

if not df.empty and "message" in df:
    risky_words=["drug","fight","kill","nude"]
    flagged=df[df["message"].fillna("").str.lower().str.contains("|".join(risky_words))]
    st.write("Flagged Messages")
    st.dataframe(flagged.tail(10))
