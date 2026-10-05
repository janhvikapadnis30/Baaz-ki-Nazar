import io
import time
import pandas as pd
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Baaz Ki Nazar — CCTV AI Monitor", layout="wide", page_icon="🦅")

pwa_html = """
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#ff4b4b">
"""
st.markdown(pwa_html, unsafe_allow_html=True)

# Replace with your deployed Render URL
API_URL = "https://baaz-ki-nazar.onrender.com"

# Initialize Session State for Alert State Tracking
if "last_alert_signature" not in st.session_state:
    st.session_state.last_alert_signature = None
if "monitoring_active" not in st.session_state:
    st.session_state.monitoring_active = False

st.title("🦅 Baaz Ki Nazar — AI CCTV Safety Surveillance")
st.subheader("Continuous Factory Floor Monitoring & Real-time Alerting")

col_control1, col_control2 = st.columns([1, 4])

with col_control1:
    if st.button("▶️ Start Live Monitoring", type="primary"):
        st.session_state.monitoring_active = True
    if st.button("⏹️ Stop Monitoring"):
        st.session_state.monitoring_active = False

with col_control2:
    if st.session_state.monitoring_active:
        st.success("🟢 AI CCTV System ACTIVE — Scanning feed continuously...")
    else:
        st.warning("🔴 CCTV System STANDBY — Click 'Start Live Monitoring' to begin.")

tab1, tab2 = st.tabs(["🎥 Live Surveillance Stream", "📊 Real-Time Logs"])

# Fragment block auto-reruns every 1.5 seconds when monitoring is active
@st.fragment(run_every=1.5 if st.session_state.monitoring_active else None)
def live_cctv_scanner():
    st.write("### Camera Feed Analysis")
    
    # Input source: Webcam or Uploaded image
    camera_file = st.camera_input("Live Feed Source", key="cctv_feed")

    if camera_file is not None and st.session_state.monitoring_active:
        image = Image.open(camera_file)
        
        # Prepare byte stream
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        files = {"file": ("frame.jpg", img_byte_arr.getvalue(), "image/jpeg")}

        try:
            response = requests.post(f"{API_URL}/detect/", files=files, timeout=4)
            if response.status_code == 200:
                data = response.json()
                violations = data.get("detected_violations", [])

                # Generate a unique signature of the detected items in this frame
                current_signature = sorted([v["type"] for v in violations])

                # Check if frame state has changed compared to last frame
                if current_signature != st.session_state.last_alert_signature:
                    st.session_state.last_alert_signature = current_signature
                    
                    if violations:
                        st.toast("⚠️ NEW VIOLATION DETECTED!", icon="🚨")
                    else:
                        st.toast("✅ All Clear — Safety Compliant", icon="👍")

                # Display Current Real-time Alerts
                if violations:
                    critical_hazards = [v for v in violations if v.get("severity") == "CRITICAL_HAZARD"]
                    gear_violations = [v for v in violations if v.get("severity") == "GEAR_VIOLATION"]

                    if critical_hazards:
                        st.error("🚨 CRITICAL HAZARD DETECTED ON FACTORY FLOOR!")
                        for hazard in critical_hazards:
                            st.write(f"🔥 **{hazard['type']}** | Confidence: **{hazard['confidence']*100:.1f}%**")

                    if gear_violations:
                        st.warning("⚠️ PPE Gear Violations Active:")
                        st.json(gear_violations)
                else:
                    st.success("✅ Factory Floor Safe — No active hazards detected.")

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

with tab1:
    live_cctv_scanner()

with tab2:
    st.write("### Historical Log Analytics")
    if st.button("Refresh Logs"):
        try:
            res = requests.get(f"{API_URL}/logs/")
            if res.status_code == 200:
                logs = res.json().get("logs", [])
                if logs:
                    df = pd.DataFrame(logs, columns=["Timestamp", "Type", "Severity", "Confidence"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No logs recorded yet.")
        except Exception as e:
            st.error(f"Could not load logs: {e}")
