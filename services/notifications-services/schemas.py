from typing import List, Optional
from pydantic import BaseModel

class PromotionCreatedEvent(BaseModel):
    promotion_id: int
    title: str
    merchant_name: str
    category_id: int
    category_name: str
    discount_percent: float
    promo_price: float
    tags: List[str] = []
    latitude: float
    longitude: float
    address: str

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    promotion_id: int
    title: str
    message: str
    category_name: Optional[str]
    distance_km: Optional[float]
    discount_percent: Optional[float]
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: List[NotificationResponse]
