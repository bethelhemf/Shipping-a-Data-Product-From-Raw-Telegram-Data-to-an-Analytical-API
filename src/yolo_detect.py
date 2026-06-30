import os
import pandas as pd
from ultralytics import YOLO
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_detection():
    logging.info("--- Starting YOLO Object Detection Enrichment ---")
    
    # 1. Load YOLOv8 nano model (yolov8n.pt)
    try:
        model = YOLO('yolov8n.pt') 
        logging.info("YOLOv8 model loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load YOLO model: {e}")
        return

    image_root = 'data/raw/images'
    if not os.path.exists(image_root):
        logging.error(f"Image directory {image_root} not found!")
        return

    detection_data = []

    # 2. Process each channel folder
    for channel in os.listdir(image_root):
        channel_path = os.path.join(image_root, channel)
        if not os.path.isdir(channel_path):
            continue
            
        logging.info(f"Processing images for channel: {channel}")
        images = [f for f in os.listdir(channel_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        for img_name in images:
            img_path = os.path.join(channel_path, img_name)
            
            # Extract Message ID from filename (e.g., '123.jpg' -> 123)
            # We take the part before the dot and ensure it is the numeric ID
            try:
                message_id = img_name.split('.')[0].split('_')[-1]
            except:
                continue

            try:
                # Run YOLO inference
                results = model(img_path, conf=0.25, verbose=False)
                
                has_person = False
                has_product = False
                max_conf = 0
                all_labels = []

                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        label = model.names[cls_id]
                        conf = float(box.conf[0])
                        
                        all_labels.append(label)
                        if conf > max_conf:
                            max_conf = conf
                        
                        # Define what we count as a 'product' (medical containers)
                        if label == 'person':
                            has_person = True
                        if label in ['bottle', 'cup', 'bowl', 'vase', 'box']:
                            has_product = True

                # 3. Apply Classification Scheme
                if has_person and has_product:
                    category = 'promotional'
                elif has_product:
                    category = 'product_display'
                elif has_person:
                    category = 'lifestyle'
                else:
                    category = 'other'

                detection_data.append({
                    "message_id": int(message_id),
                    "channel_name": channel,
                    "detected_objects": ", ".join(set(all_labels)),
                    "confidence_score": round(max_conf, 2),
                    "image_category": category
                })

            except Exception as e:
                logging.warning(f"Could not process image {img_name}: {e}")

    # 4. Save results to CSV
    if detection_data:
        df = pd.DataFrame(detection_data)
        os.makedirs('data/raw', exist_ok=True)
        output_path = 'data/raw/yolo_detections.csv'
        df.to_csv(output_path, index=False)
        logging.info(f"SUCCESS: Created {output_path} with {len(df)} records.")
    else:
        logging.warning("No detections were made. CSV not created.")

if __name__ == "__main__":
    run_detection()