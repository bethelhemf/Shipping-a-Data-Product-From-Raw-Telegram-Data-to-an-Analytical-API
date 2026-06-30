from pydantic import BaseModel
from typing import List, Optional

class ProductStat(BaseModel):
    product_name: str
    mention_count: int

class ChannelActivity(BaseModel):
    channel_name: str
    post_date: str
    post_count: int

class MessageResponse(BaseModel):
    message_id: int
    channel_name: Optional[str]
    message_text: str
    views: int

class VisualStat(BaseModel):
    channel_name: str
    image_category: str
    count: int