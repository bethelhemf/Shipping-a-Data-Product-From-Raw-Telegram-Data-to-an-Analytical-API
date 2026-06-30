import os
import json
import pandas as pd
from sqlalchemy import create_engine, text

# USE THE SAME PASSWORD AS STEP 2
engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

def load():
    base_path = 'data/raw/telegram_messages'
    all_msgs = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    all_msgs.extend(json.load(f))
    
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()

    pd.DataFrame(all_msgs).to_sql('telegram_messages', engine, schema='raw', if_exists='replace', index=False)
    print("SUCCESS: Raw data is now in PostgreSQL!")
    def load_yolo_results():
    csv_path = 'data/raw/yolo_detections.csv'
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.to_sql('yolo_detections', engine, schema='raw', if_exists='replace', index=False)
        print("SUCCESS: YOLO detections loaded to PostgreSQL!")

# Call this function at the bottom of your script
if __name__ == "__main__":
    load() # Your existing load
    load_yolo_results() # The new enrichment load

load()
