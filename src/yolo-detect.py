import os
import pandas as pd
from ultralytics import YOLO

def run_detection():
    print("--- Starting YOLO Diagnostic ---")
    
    # 1. Load Model
    try:
        model = YOLO('yolov8n.pt')
        print("✅ YOLO Model Loaded Successfully")
    except Exception as e:
        print(f"❌ Failed to load YOLO model: {e}")
        return

    image_root = 'data/raw/images'
    print(f"Checking for images in: {os.path.abspath(image_root)}")

    if not os.path.exists(image_root):
        print(f"❌ ERROR: The directory {image_root} does not exist!")
        return

    results_list = []
    
    # 2. Walk through folders
    channels = os.listdir(image_root)
    print(f"Found {len(channels)} channel folders: {channels}")

    for channel in channels:
        channel_path = os.path.join(image_root, channel)
        if os.path.isdir(channel_path):
            images = [f for f in os.listdir(channel_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"  > Channel '{channel}': Found {len(images)} images.")

            for img_name in images:
                img_path = os.path.join(channel_path, img_name)
                
                # Get message_id (handle filenames like 'TikvahPharma_123.jpg' or '123.jpg')
                # We strip non-numeric parts to get the ID
                message_id_raw = img_name.split('.')[0].split('_')[-1]
                
                try:
                    results = model(img_path, conf=0.25, verbose=False)
                    
                    has_person = False
                    has_product = False
                    
                    for r in results:
                        for box in r.boxes:
                            label = model.names[int(box.cls[0])]
                            if label == 'person': has_person = True
                            if label in ['bottle', 'cup', 'bowl', 'vase', 'potted plant']: has_product = True

                    category = 'other'
                    if has_person and has_product: category = 'promotional'
                    elif has_product: category = 'product_display'
                    elif has_person: category = 'lifestyle'

                    results_list.append({
                        "message_id": message_id_raw,
                        "image_category": category
                    })
                except Exception as e:
                    print(f"    ⚠️ Error processing {img_name}: {e}")

    # 3. Save the File
    if results_list:
        df = pd.DataFrame(results_list)
        os.makedirs('data/raw', exist_ok=True)
        output_path = 'data/raw/yolo_detections.csv'
        df.to_csv(output_path, index=False)
        print(f"✅ SUCCESS! Created {output_path} with {len(results_list)} detections.")
    else:
        print("❌ FAILED: No detections were made. Is the image folder empty?")

if __name__ == "__main__":
    run_detection()