import streamlit as st
import cv2
import numpy as np
from detector import process_frame
from database import log_event, get_logs

st.set_page_config(page_title="Baaz Ki Nazar - Safety Dashboard", layout="wide")

st.title("🦅 Baaz Ki Nazar — Factory Floor Safety Monitoring")
st.write("Take a snapshot or upload an image to inspect for safety violations.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📹 Capture or Upload Image")
    
    # 1. Option to use webcam directly via the browser
    img_file_buffer = st.camera_input("Take a picture from your camera")
    
    # 2. Backup option to upload an image file
    uploaded_file = st.file_uploader("Or upload an image", type=["jpg", "jpeg", "png"])

    image_bytes = None
    if img_file_buffer is not None:
        image_bytes = img_file_buffer.getvalue()
    elif uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()

    if image_bytes is not None:
        # Convert image bytes to OpenCV format
        file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Run detection on the captured/uploaded image
        annotated_frame, status, violation = process_frame(frame)

        # Display analyzed image
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, caption="Analyzed Image", use_container_width=True)

        # Update and Log Status
        if status == "CRITICAL":
            log_event(violation, status)
            st.session_state["latest_status"] = (status, violation)
        else:
            st.session_state["latest_status"] = (status, "None")

with col2:
    st.subheader("⚠️ Safety Status")
    
    if "latest_status" in st.session_state:
        status, violation = st.session_state["latest_status"]
        if status == "CRITICAL":
            st.error(f"STATUS: {status}\n\nViolation: {violation}")
        else:
            st.success(f"STATUS: {status}")
    else:
        st.info("STATUS: Awaiting input")
        
    st.subheader("📋 Incident History")
    logs = get_logs()
    st.dataframe(logs, column_config={"0": "ID", "1": "Timestamp", "2": "Violation", "3": "Status"})
