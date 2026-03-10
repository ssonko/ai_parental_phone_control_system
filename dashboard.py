
import streamlit as st
import pandas as pd
import requests
import sqlite3

import os
SERVER = os.environ.get("SERVER_URL", "http://localhost:8000")

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
    requests.post(f"{SERVER}/command", json={"device": "child_phone", "command": cmd})
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
    history = requests.get(f"{SERVER}/commands/history").json().get("data", [])
    if history:
        st.dataframe(history)
    else:
        st.info("No commands sent yet.")
except:
    st.warning("Could not load command history.")

st.subheader("Basic Safety Check")

if not df.empty and "message" in df:
    risky_words=["drug","fight","kill","nude"]
    flagged=df[df["message"].fillna("").str.lower().str.contains("|".join(risky_words))]
    st.write("Flagged Messages")
    st.dataframe(flagged.tail(10))
