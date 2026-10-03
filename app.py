import streamlit as st
import cv2
from detector import process_frame
from database import log_event, get_logs

st.set_page_config(page_title="Baaz Ki Nazar - Safety Dashboard", layout="wide")

st.title("🦅 Baaz Ki Nazar — Factory Floor Safety Monitoring")
st.write("Click the button below to capture a snapshot and inspect for safety violations.")

col1, col2 = st.columns([2, 1])

# Initialize session state variables to store the image and detection results across button clicks
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "status" not in st.session_state:
    st.session_state.status = "SAFE"
if "violation" not in st.session_state:
    st.session_state.violation = "None"

with col1:
    st.subheader("📹 Single Frame Capture")
    
    # 1. Click this button to capture one frame from the camera
    if st.button("📸 Capture & Analyze Frame"):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()  # Immediately release the camera after capturing one frame
        
        if ret:
            # Run detection on the single captured frame
            annotated_frame, status, violation = process_frame(frame)
            
            # Store results in session state
            st.session_state.captured_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            st.session_state.status = status
            st.session_state.violation = violation
            
            # Log event if a violation is detected
            if status == "CRITICAL":
                log_event(violation, status)
        else:
            st.error("Failed to capture image from camera.")

    # 2. Display the captured snapshot
    if st.session_state.captured_image is not None:
        st.image(st.session_state.captured_image, caption="Analyzed Snapshot", use_container_width=True)
    else:
        st.info("Click 'Capture & Analyze Frame' to take a snapshot.")

with col2:
    st.subheader("⚠️ Safety Status")
    
    # Display status for the captured frame
    if st.session_state.status == "CRITICAL":
        st.error(f"STATUS: {st.session_state.status}\n\nViolation: {st.session_state.violation}")
    else:
        st.success(f"STATUS: {st.session_state.status}")
        
    st.subheader("📋 Incident History")
    logs = get_logs()
    st.dataframe(logs, column_config={"0": "ID", "1": "Timestamp", "2": "Violation", "3": "Status"})