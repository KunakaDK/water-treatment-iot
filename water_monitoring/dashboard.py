import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("WATER_API_URL", "http://127.0.0.1:8000").rstrip("/")
st.set_page_config(page_title="Water Plant Monitor", page_icon="💧", layout="wide")
st.title("Water Treatment Plant – Monitoring Dashboard")
st.caption("Portfolio demonstration using synthetic telemetry. Not connected to or validated for a real treatment plant.")

try:
    summary_response = requests.get(f"{API_URL}/summary", timeout=4)
    summary_response.raise_for_status()
    summary = summary_response.json()
    response = requests.get(f"{API_URL}/telemetry?limit=500", timeout=4)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
except requests.RequestException as exc:
    st.error(f"Cannot reach API at {API_URL}: {exc}. Start the API and seed demo data first.")
    st.stop()

if df.empty:
    st.info("No telemetry yet. Run: python -m water_monitoring.cli seed --count 200")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df = df.sort_values("timestamp")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", summary["records"])
c2.metric("Average outlet flow", f"{summary['average_outlet_flow_m3_h']:.1f} m³/h" if summary["average_outlet_flow_m3_h"] is not None else "—")
c3.metric("Average pH", f"{summary['average_ph']:.2f}" if summary["average_ph"] is not None else "—")
c4.metric("Indicative specific energy", f"{summary['average_specific_energy_kwh_m3']:.3f} kWh/m³" if summary["average_specific_energy_kwh_m3"] is not None else "—")

st.subheader("Process trends")
left, right = st.columns(2)
with left:
    st.line_chart(df.set_index("timestamp")[["inlet_flow_m3_h", "outlet_flow_m3_h"]])
    st.line_chart(df.set_index("timestamp")[["tank_level_pct"]])
with right:
    st.line_chart(df.set_index("timestamp")[["ph", "turbidity_ntu"]])
    st.line_chart(df.set_index("timestamp")[["pump_power_kw"]])

try:
    alarm_data = requests.get(f"{API_URL}/alarms/latest", timeout=4).json()
    st.subheader("Latest illustrative alarms")
    if alarm_data["alarms"]:
        for alarm in alarm_data["alarms"]:
            st.warning(f"{alarm['code']} – {alarm['message']} (value: {alarm['value']})")
    else:
        st.success("No illustrative alarm for the latest record.")
except requests.RequestException:
    st.info("Latest alarms are temporarily unavailable.")

st.subheader("Recent telemetry")
st.dataframe(df.sort_values("timestamp", ascending=False).head(30), use_container_width=True, hide_index=True)
