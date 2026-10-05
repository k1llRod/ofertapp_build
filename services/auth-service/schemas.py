from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: Optional[str] = "user"  # "user" o "merchant"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    bio: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    social_whatsapp: Optional[str] = None
    website: Optional[str] = None

    class Config:
        from_attributes = True

# User Profile & Password Schemas
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    bio: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    social_whatsapp: Optional[str] = None
    website: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: Optional[str] = None

# Tastes Schemas
class TasteCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    description: Optional[str]

    class Config:
        from_attributes = True

class TastePreferenceItem(BaseModel):
    category_id: int
    tags: List[str] = []
    max_distance_km: float = 10.0

class TastePreferenceResponse(BaseModel):
    id: int
    category_id: int
    category_name: str
    category_icon: str
    tags: List[str]
    max_distance_km: float

class UpdateUserTastesRequest(BaseModel):
    preferences: List[TastePreferenceItem]

# Location & Geotargeting Schemas
class UserLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    address_label: Optional[str] = None
    fcm_token: Optional[str] = None

class UserLocationResponse(BaseModel):
    latitude: float
    longitude: float
    address_label: Optional[str]
    updated_at: Optional[str]

# Query for notifications matching
class MatchAudienceRequest(BaseModel):
    category_id: int
    tags: List[str] = []
    latitude: float
    longitude: float
    max_radius_km: Optional[float] = 15.0

class MatchedUser(BaseModel):
    user_id: int
    email: str
    full_name: str
    fcm_token: Optional[str]
    distance_km: float
    matched_reason: str

class MatchAudienceResponse(BaseModel):
    matched_users: List[MatchedUser]
    count: int

# Admin & Configuration Schemas
class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str] = None
    category: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SystemSettingUpdate(BaseModel):
    key: str
    value: str

class UserRoleUpdate(BaseModel):
    role: str  # 'user', 'merchant', 'admin'
    is_active: Optional[bool] = True

class CategoryCreate(BaseModel):
    name: str
    slug: str
    icon: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

class UserCreateAdmin(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    bio: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    social_whatsapp: Optional[str] = None
    website: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    bio: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    social_whatsapp: Optional[str] = None
    website: Optional[str] = None

class SystemSettingCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    category: Optional[str] = "general"
