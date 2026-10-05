from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), default="user")  # 'user', 'merchant', 'admin'
    is_active = Column(Boolean, default=True)
    logo_url = Column(Text, nullable=True)
    banner_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    social_instagram = Column(String(255), nullable=True)
    social_facebook = Column(String(255), nullable=True)
    social_twitter = Column(String(255), nullable=True)
    social_whatsapp = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tastes = relationship("UserTastePreference", back_populates="user", cascade="all, delete-orphan")
    location = relationship("UserLocation", back_populates="user", uselist=False, cascade="all, delete-orphan")

class TasteCategory(Base):
    __tablename__ = "taste_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=False, default="🏷️")
    description = Column(String(255), nullable=True)

    preferences = relationship("UserTastePreference", back_populates="category")

class UserTastePreference(Base):
    __tablename__ = "user_taste_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("taste_categories.id"), nullable=False)
    tags = Column(Text, default="")  # Tags separadas por coma, ej: "pizza,artesanal,2x1"
    max_distance_km = Column(Float, default=10.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tastes")
    category = relationship("TasteCategory", back_populates="preferences")

class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address_label = Column(String(255), nullable=True)
    fcm_token = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="location")

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(50), default="general")  # 'general', 'geo', 'notifications', 'merchants'
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
