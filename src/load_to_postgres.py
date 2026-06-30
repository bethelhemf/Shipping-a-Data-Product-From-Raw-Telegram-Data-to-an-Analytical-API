import os
import json
import pandas as pd
from sqlalchemy import create_engine, text

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
engine = create_engine(DB_URL)

def load():
    """Loads Telegram JSON messages into Postgres."""
    base_path = 'data/raw/telegram_messages'
    all_msgs = []
    
    if not os.path.exists(base_path):
        return

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    all_msgs.extend(json.load(f))
    
    if all_msgs:
        # --- THE FIX STARTS HERE ---
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
            # We manually drop the table with CASCADE to clear dependencies (views)
            conn.execute(text("DROP TABLE IF EXISTS raw.telegram_messages CASCADE;"))
            conn.commit()
        # --- THE FIX ENDS HERE ---

        df = pd.DataFrame(all_msgs)
        # Now 'replace' will work because the table is already gone
        df.to_sql('telegram_messages', engine, schema='raw', if_exists='replace', index=False)
        print("SUCCESS: Loaded messages to raw.telegram_messages")

def load_yolo():
    """Loads YOLO detection CSV into Postgres."""
    csv_path = 'data/raw/yolo_detections.csv'
    
    if os.path.exists(csv_path):
        # --- THE FIX STARTS HERE ---
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
            # Clear yolo table and dependencies
            conn.execute(text("DROP TABLE IF EXISTS raw.yolo_detections CASCADE;"))
            conn.commit()
        # --- THE FIX ENDS HERE ---
            
        df = pd.read_csv(csv_path)
        df.to_sql('yolo_detections', engine, schema='raw', if_exists='replace', index=False)
        print("SUCCESS: YOLO detections loaded to raw.yolo_detections")

if __name__ == "__main__":
    load()
    load_yolo()