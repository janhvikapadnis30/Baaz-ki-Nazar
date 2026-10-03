import cv2
from ultralytics import YOLO

# Load pre-trained YOLOv8 model (downloads weights automatically)
model = YOLO("yolov8n.pt")

def process_frame(frame):
    # Perform object detection
    results = model(frame, verbose=False)
    
    person_detected = False
    
    # Process detected bounding boxes
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            # Label 0 in COCO dataset is 'person'
            if class_name == "person":
                person_detected = True
                
    # Basic Safety Rule Logic: Evaluate detection state
    # Example rule: Alert if a worker is detected without explicit verification
    status = "CRITICAL" if person_detected else "SAFE"
    violation = "PPE/Zone Violation Detected" if person_detected else "None"
    
    # Draw annotations on the frame
    annotated_frame = results[0].plot()
    
    return annotated_frame, status, violation