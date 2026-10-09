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
    
    image_url = Column(Text, nullable=True)
    gallery = Column(Text, nullable=True, default="")  # URLs de fotos adicionales separadas por coma
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
    orders = relationship("Order", back_populates="promotion", cascade="all, delete-orphan")

class PromotionView(Base):
    __tablename__ = "promotion_views"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

    promotion = relationship("Promotion", back_populates="views")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(50), default="completed")
    transaction_id = Column(String(100), nullable=False)
    qr_code_token = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    promotion = relationship("Promotion", back_populates="orders")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_code = Column(String(100), unique=True, index=True, nullable=False)

    # Servicio, Producto y Usuario
    service_name = Column(String(255), nullable=False, index=True)  # Servicio involucrado
    product_name = Column(String(255), nullable=False, index=True)  # Producto involucrado
    user_id = Column(Integer, nullable=True, index=True)            # Identificador del usuario
    user_name = Column(String(255), nullable=True)                  # Nombre del usuario / cliente
    user_email = Column(String(255), nullable=True)                 # Email del usuario / cliente

    # Detalles financieros y de operación
    amount = Column(Float, nullable=False, default=0.0)             # Monto total
    quantity = Column(Integer, default=1)                           # Cantidad de items
    payment_method = Column(String(50), default="credit_card")      # Método de pago
    status = Column(String(50), default="completed", index=True)    # completed, pending, cancelled
    description = Column(Text, nullable=True)                       # Descripción o nota

    created_at = Column(DateTime(timezone=True), server_default=func.now())

