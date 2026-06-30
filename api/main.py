import logging
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .database import get_db
from . import schemas

# 1. Setup Logging - Crucial for "Production Ready" status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kara Medical Data API",
    description="A production-ready API for medical business insights in Ethiopia.",
    version="2.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Kara Medical Analytical API is running. Access /docs for interactive documentation."
    }

# --- ENDPOINT 1: TOP PRODUCTS ---
@app.get("/api/reports/top-products", response_model=List[schemas.ProductStat])
def get_top_products(limit: int = Query(10, gt=0, le=100), db: Session = Depends(get_db)):
    """Returns the most frequently mentioned medical terms extracted from channel messages."""
    try:
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
        
        if not result:
            logger.warning("Top products query returned no results.")
            raise HTTPException(status_code=404, detail="No medical product data found in warehouse.")
        
        return result
    except Exception as e:
        logger.error(f"Database error in get_top_products: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while querying warehouse.")

# --- ENDPOINT 2: CHANNEL ACTIVITY ---
@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """Returns the daily posting frequency for a specific channel."""
    try:
        query = text("""
            SELECT channel_name, to_char(message_date, 'YYYY-MM-DD') as post_date, count(*) as post_count
            FROM staging.stg_telegram_messages
            WHERE channel_name = :name
            GROUP BY 1, 2
            ORDER BY post_date DESC
        """)
        result = db.execute(query, {"name": channel_name}).fetchall()
        
        if not result:
            logger.info(f"No activity found for channel: {channel_name}")
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found or has no activity.")
            
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching activity for {channel_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving channel statistics.")

# --- ENDPOINT 3: MESSAGE SEARCH ---
@app.get("/api/search/messages", response_model=List[schemas.MessageResponse])
def search_messages(query: str = Query(..., min_length=3), limit: int = 20, db: Session = Depends(get_db)):
    """Search for specific medical keywords (e.g., 'insulin') within message text."""
    try:
        search_query = text("""
            SELECT message_id, channel_name, message_text, views
            FROM staging.stg_telegram_messages
            WHERE message_text ILIKE :search
            LIMIT :limit
        """)
        result = db.execute(search_query, {"search": f"%{query}%", "limit": limit}).fetchall()
        
        if not result:
            return [] # Returning empty list is standard for search
            
        return result
    except Exception as e:
        logger.error(f"Search error for query '{query}': {str(e)}")
        raise HTTPException(status_code=500, detail="Search engine currently unavailable.")

# --- ENDPOINT 4: VISUAL CONTENT STATS ---
@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStat])
def get_visual_stats(db: Session = Depends(get_db)):
    """Aggregates YOLO object detection results across all channels."""
    try:
        query = text("""
            SELECT channel_name, image_category, count(*) as count
            FROM marts.fct_image_detections
            GROUP BY 1, 2
            ORDER BY count DESC
        """)
        result = db.execute(query).fetchall()
        
        if not result:
            logger.error("fct_image_detections table appears to be empty.")
            raise HTTPException(status_code=404, detail="No visual content analysis available.")
            
        return result
    except Exception as e:
        logger.error(f"Error in visual content report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error fetching visual analytics.")