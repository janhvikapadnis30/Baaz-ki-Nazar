import io
import pandas as pd
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Baaz Ki Nazar", layout="wide", page_icon="🦅")

# Inject PWA Metadata
pwa_html = """
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#ff4b4b">
"""
st.markdown(pwa_html, unsafe_allow_html=True)

# Replace with your exact Render backend URL
API_URL = "https://baaz-ki-nazar.onrender.com"

st.title("🦅 Baaz Ki Nazar — Factory Floor Safety Monitoring")
st.subheader("AI Compliance Monitoring, Fire & Smoke Detection")

tab1, tab2 = st.tabs(["📸 On-Demand Inspection", "📊 Violation Analytics"])

with tab1:
    st.write("### Capture or Upload Snapshot")
    uploaded_file = st.file_uploader("Upload factory floor snapshot", type=["jpg", "jpeg", "png"])
    camera_file = st.camera_input("Take Snapshot")

    active_file = uploaded_file or camera_file

    if active_file is not None:
        image = Image.open(active_file)
        st.image(image, caption="Source Frame", use_container_width=True)

        if st.button("Analyze Frame"):
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            files = {"file": ("image.jpg", img_byte_arr.getvalue(), "image/jpeg")}

            with st.spinner("Scanning for PPE compliance, Fire, and Smoke..."):
                try:
                    response = requests.post(f"{API_URL}/detect/", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        violations = data.get("detected_violations", [])

                        if violations:
                            critical_hazards = [v for v in violations if v.get("severity") == "CRITICAL_HAZARD"]
                            gear_violations = [v for v in violations if v.get("severity") == "GEAR_VIOLATION"]

                            if critical_hazards:
                                st.error("🚨 CRITICAL HAZARD DETECTED! FIRE / SMOKE DETECTED ON FACTORY FLOOR!")
                                for hazard in critical_hazards:
                                    st.write(f"🔥 **{hazard['type']}** detected with **{hazard['confidence']*100:.1f}%** confidence.")

                            if gear_violations:
                                st.warning("⚠️ PPE Safety Gear Violations Detected:")
                                st.json(gear_violations)
                        else:
                            st.success("✅ Factory floor clear. No fire, smoke, or PPE violations detected.")
                    else:
                        st.error("Backend server connection issue.")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")

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
                    st.info("No records found.")
        except Exception as e:
            st.error(f"Could not fetch logs: {e}")
            
