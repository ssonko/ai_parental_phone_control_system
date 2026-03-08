
import streamlit as st
import pandas as pd
import requests
import sqlite3

SERVER="http://localhost:8000"

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

col1,col2,col3=st.columns(3)

with col1:
    if st.button("🔒 Lock Phone"):
        requests.post(f"{SERVER}/command",json={"device":"child_phone","command":"lock_phone"})

with col2:
    if st.button("🌐 Disable Internet"):
        requests.post(f"{SERVER}/command",json={"device":"child_phone","command":"disable_internet"})

with col3:
    if st.button("✅ Enable Internet"):
        requests.post(f"{SERVER}/command",json={"device":"child_phone","command":"enable_internet"})

st.subheader("Basic Safety Check")

if not df.empty and "message" in df:
    risky_words=["drug","fight","kill","nude"]
    flagged=df[df["message"].fillna("").str.lower().str.contains("|".join(risky_words))]
    st.write("Flagged Messages")
    st.dataframe(flagged.tail(10))
