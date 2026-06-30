from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List  # <--- ADD THIS LINE
from .database import get_db
from . import schemas

app = FastAPI(title="Kara Medical Data API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Kara Medical Analytical API."}

# Endpoint 1: Top Products
@app.get("/api/reports/top-products", response_model=List[schemas.ProductStat])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    # Use a raw string (r'') to fix the \s warning
    query = text(r"""
        SELECT word as product_name, count(*) as mention_count
        FROM (
            SELECT regexp_split_to_table(lower(message_text), '\s+') as word
            FROM staging.stg_telegram_messages
        ) t
        WHERE length(word) > 4 
        GROUP BY word
        ORDER BY mention_count DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    return result

# ... (Keep your other endpoints as they were)

# Endpoint 2: Channel Activity Trends
@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT channel_name, to_char(message_date, 'YYYY-MM-DD') as post_date, count(*) as post_count
        FROM staging.stg_telegram_messages
        WHERE channel_name = :name
        GROUP BY 1, 2
        ORDER BY post_date DESC
    """)
    result = db.execute(query, {"name": channel_name}).fetchall()
    return result

# Endpoint 3: Message Search
@app.get("/api/search/messages", response_model=List[schemas.MessageResponse])
def search_messages(query: str, limit: int = 20, db: Session = Depends(get_db)):
    search_query = text("""
        SELECT message_id, channel_name, message_text, views
        FROM staging.stg_telegram_messages
        WHERE message_text ILIKE :search
        LIMIT :limit
    """)
    result = db.execute(search_query, {"search": f"%{query}%", "limit": limit}).fetchall()
    return result

# Endpoint 4: Visual Content Stats (Uses YOLO mart)
@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStat])
def get_visual_stats(db: Session = Depends(get_db)):
    query = text("""
        SELECT channel_name, image_category, count(*) as count
        FROM marts.fct_image_detections
        GROUP BY 1, 2
        ORDER BY count DESC
    """)
    result = db.execute(query).fetchall()
    return result