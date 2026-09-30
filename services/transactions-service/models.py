from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=False, default="🏷️")
    description = Column(String(255), nullable=True)

    promotions = relationship("Promotion", back_populates="category")

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False, index=True)
    merchant_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    original_price = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False)
    promo_price = Column(Float, nullable=False)
    
    image_url = Column(String(500), nullable=True)
    tags = Column(Text, default="")  # ej: "pizza,artesanal,2x1"
    
    # Coordenadas geográficas del comercio/promoción
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="promotions")
    views = relationship("PromotionView", back_populates="promotion", cascade="all, delete-orphan")

class PromotionView(Base):
    __tablename__ = "promotion_views"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

    promotion = relationship("Promotion", back_populates="views")
