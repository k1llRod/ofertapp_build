from typing import List, Optional
from pydantic import BaseModel

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    description: Optional[str]

    class Config:
        from_attributes = True

class PromotionCreate(BaseModel):
    merchant_id: int
    merchant_name: str
    title: str
    description: str
    category_id: int
    original_price: float
    discount_percent: float
    image_url: Optional[str] = None
    tags: List[str] = []
    latitude: float
    longitude: float
    address: str

class PromotionResponse(BaseModel):
    id: int
    merchant_id: int
    merchant_name: str
    title: str
    description: str
    category_id: int
    category_name: str
    category_icon: str
    original_price: float
    discount_percent: float
    promo_price: float
    image_url: Optional[str]
    tags: List[str]
    latitude: float
    longitude: float
    address: str
    is_active: bool
    views_count: int
    distance_km: Optional[float] = None
    distance_label: Optional[str] = None
    matches_taste: bool = False
    created_at: str

class PromotionFeedResponse(BaseModel):
    total: int
    items: List[PromotionResponse]
    applied_filters: dict
