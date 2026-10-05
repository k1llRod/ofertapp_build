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

class CategoryCreate(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = "🏷️"
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

class PromotionCreate(BaseModel):
    merchant_id: Optional[int] = None
    merchant_name: Optional[str] = None
    title: str
    description: str
    category_id: int
    original_price: float
    discount_percent: float
    image_url: Optional[str] = None
    gallery: Optional[List[str]] = []
    tags: List[str] = []
    latitude: float
    longitude: float
    address: str

class PromotionUpdate(BaseModel):
    merchant_id: Optional[int] = None
    merchant_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    gallery: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

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
    images: List[str] = []
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

class OrderCreate(BaseModel):
    promotion_id: int
    user_id: Optional[int] = None
    customer_name: str
    customer_email: str
    quantity: int = 1
    payment_method: str = "credit_card"
    card_number_masked: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    promotion_id: int
    promotion_title: str
    merchant_name: str
    customer_name: str
    customer_email: str
    quantity: int
    unit_price: float
    total_amount: float
    payment_method: str
    payment_status: str
    transaction_id: str
    qr_code_token: str
    created_at: str

# --- TRANSACTION SCHEMAS ---

class TransactionCreate(BaseModel):
    # Servicio involucrado (admite service, service_name, servicio)
    service: Optional[str] = None
    service_name: Optional[str] = None
    servicio: Optional[str] = None

    # Producto involucrado (admite product, product_name, producto)
    product: Optional[str] = None
    product_name: Optional[str] = None
    producto: Optional[str] = None

    # Usuario involucrado (admite user_id, user, usuario, user_name, user_email)
    user_id: Optional[int] = None
    user: Optional[str] = None
    usuario: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    # Datos financieros y operativos
    amount: Optional[float] = None
    monto: Optional[float] = None
    quantity: Optional[int] = 1
    payment_method: Optional[str] = "credit_card"
    status: Optional[str] = "completed"
    description: Optional[str] = None
    transaction_code: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    transaction_code: str
    service: str
    service_name: str
    product: str
    product_name: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user: Optional[str] = None
    amount: float
    quantity: int
    payment_method: str
    status: str
    description: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None

