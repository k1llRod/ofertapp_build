import math
import asyncio
from typing import List, Optional
import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database import engine, Base, get_db
import models
import schemas
from seed_data import seed_initial_data

# Crear tablas en arranque
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Servicio de transacciones, catálogo de productos, registro de promociones y geo-búsqueda",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_initial_data(db)
    finally:
        db.close()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "transactions-service"}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def format_distance_label(distance_km: float) -> str:
    if distance_km < 1.0:
        meters = int(distance_km * 1000)
        return f"a {meters} m"
    return f"a {distance_km:.1f} km"

async def dispatch_promo_created_event(promo_data: dict):
    """Notifica al servicio de notificaciones sobre la nueva oferta para que despache alertas por gustos"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"{settings.NOTIFICATIONS_SERVICE_URL}/events/promotion-created"
            response = await client.post(url, json=promo_data)
            print(f"[EVENT DISPATCH] Event sent to notifications service. Status: {response.status_code}")
    except Exception as e:
        print(f"[EVENT DISPATCH WARNING] No se pudo conectar con notifications-services: {e}")

# --- CATEGORIES ENDPOINTS ---

@app.get("/categories", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    """Obtiene el listado de categorías del catálogo"""
    return db.query(models.Category).all()

# --- PROMOTIONS ENDPOINTS ---

@app.post("/promotions", response_model=schemas.PromotionResponse, status_code=status.HTTP_201_CREATED, tags=["Promotions"])
async def create_promotion(
    promo_in: schemas.PromotionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registra una nueva promoción en el catálogo (interfaz de comercios).
    Calcula el precio promocional y notifica al servicio de alertas para usuarios con gustos afines.
    """
    category = db.query(models.Category).filter(models.Category.id == promo_in.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Categoría no encontrada")

    discount = max(0.0, min(100.0, promo_in.discount_percent))
    promo_price = round(promo_in.original_price * (1.0 - (discount / 100.0)), 2)
    tags_str = ",".join([t.strip().lower() for t in promo_in.tags if t.strip()])

    new_promo = models.Promotion(
        merchant_id=promo_in.merchant_id,
        merchant_name=promo_in.merchant_name,
        title=promo_in.title,
        description=promo_in.description,
        category_id=promo_in.category_id,
        original_price=promo_in.original_price,
        discount_percent=discount,
        promo_price=promo_price,
        image_url=promo_in.image_url or "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=600",
        tags=tags_str,
        latitude=promo_in.latitude,
        longitude=promo_in.longitude,
        address=promo_in.address,
        is_active=True,
        views_count=0
    )

    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)

    # Disparar evento asíncrono para generar alertas a los usuarios por gustos y cercanía
    event_payload = {
        "promotion_id": new_promo.id,
        "title": new_promo.title,
        "merchant_name": new_promo.merchant_name,
        "category_id": new_promo.category_id,
        "category_name": category.name,
        "discount_percent": new_promo.discount_percent,
        "promo_price": new_promo.promo_price,
        "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
        "latitude": new_promo.latitude,
        "longitude": new_promo.longitude,
        "address": new_promo.address
    }
    background_tasks.add_task(dispatch_promo_created_event, event_payload)

    return schemas.PromotionResponse(
        id=new_promo.id,
        merchant_id=new_promo.merchant_id,
        merchant_name=new_promo.merchant_name,
        title=new_promo.title,
        description=new_promo.description,
        category_id=new_promo.category_id,
        category_name=category.name,
        category_icon=category.icon,
        original_price=new_promo.original_price,
        discount_percent=new_promo.discount_percent,
        promo_price=new_promo.promo_price,
        image_url=new_promo.image_url,
        tags=[t for t in tags_str.split(",") if t],
        latitude=new_promo.latitude,
        longitude=new_promo.longitude,
        address=new_promo.address,
        is_active=new_promo.is_active,
        views_count=new_promo.views_count,
        distance_km=0.0,
        distance_label="Recién creada",
        matches_taste=True,
        created_at=str(new_promo.created_at)
    )

@app.get("/promotions/feed", response_model=schemas.PromotionFeedResponse, tags=["Promotions"])
def get_promotions_feed(
    lat: Optional[float] = Query(None, description="Latitud GPS actual del usuario"),
    lon: Optional[float] = Query(None, description="Longitud GPS actual del usuario"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoría específica"),
    taste_tags: Optional[str] = Query(None, description="Tags de gusto del usuario separados por coma"),
    taste_categories: Optional[str] = Query(None, description="IDs de categorías de gusto del usuario separados por coma"),
    max_distance_km: Optional[float] = Query(None, description="Radio máximo de búsqueda en km"),
    search: Optional[str] = Query(None, description="Buscador de promociones por texto libre (título, descripción, comercio o etiquetas)"),
    db: Session = Depends(get_db)
):
    """
    Pantalla principal del usuario:
    Devuelve las promociones activas ordenadas por cercanía geográfica y afinidad con sus gustos.
    Permite filtrar por buscador libre en caso de no tener gustos configurados.
    """
    query = db.query(models.Promotion).filter(models.Promotion.is_active == True)

    if category_id:
        query = query.filter(models.Promotion.category_id == category_id)

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            (models.Promotion.title.ilike(term)) |
            (models.Promotion.description.ilike(term)) |
            (models.Promotion.merchant_name.ilike(term)) |
            (models.Promotion.tags.ilike(term))
        )

    promos = query.all()

    # Procesar gustos del usuario
    user_taste_tags = set([t.strip().lower() for t in taste_tags.split(",") if t.strip()]) if taste_tags else set()
    user_taste_cats = set([int(c.strip()) for c in taste_categories.split(",") if c.strip().isdigit()]) if taste_categories else set()

    processed_items = []
    default_lat = -34.6037  # Centro de referencia por defecto si no envía GPS
    default_lon = -58.3816
    user_lat = lat if lat is not None else default_lat
    user_lon = lon if lon is not None else default_lon

    for p in promos:
        promo_tags = [t.strip().lower() for t in p.tags.split(",") if t.strip()]
        promo_tags_set = set(promo_tags)

        # 1. Calcular distancia
        dist = haversine_distance(user_lat, user_lon, p.latitude, p.longitude)
        if max_distance_km and dist > max_distance_km:
            continue

        # 2. Evaluar afinidad con gustos del usuario
        matches_category = p.category_id in user_taste_cats
        matches_tags = bool(user_taste_tags.intersection(promo_tags_set))
        matches_taste = matches_category or matches_tags

        processed_items.append({
            "model": p,
            "distance_km": dist,
            "matches_taste": matches_taste,
            "score": (2.0 if matches_taste else 0.0) - (dist * 0.1)  # Mayor score a gustos coincidentes y cercanía
        })

    # Ordenar: primero gustos coincidentes + menor distancia
    processed_items.sort(key=lambda x: (not x["matches_taste"], x["distance_km"]))

    result = []
    for item in processed_items:
        p = item["model"]
        dist = item["distance_km"]
        result.append(schemas.PromotionResponse(
            id=p.id,
            merchant_id=p.merchant_id,
            merchant_name=p.merchant_name,
            title=p.title,
            description=p.description,
            category_id=p.category_id,
            category_name=p.category.name if p.category else "General",
            category_icon=p.category.icon if p.category else "🏷️",
            original_price=p.original_price,
            discount_percent=p.discount_percent,
            promo_price=p.promo_price,
            image_url=p.image_url,
            tags=[t for t in p.tags.split(",") if t],
            latitude=p.latitude,
            longitude=p.longitude,
            address=p.address,
            is_active=p.is_active,
            views_count=p.views_count,
            distance_km=dist,
            distance_label=format_distance_label(dist),
            matches_taste=item["matches_taste"],
            created_at=str(p.created_at)
        ))

    return schemas.PromotionFeedResponse(
        total=len(result),
        items=result,
        applied_filters={
            "user_coordinates": {"lat": user_lat, "lon": user_lon},
            "category_id": category_id,
            "max_distance_km": max_distance_km,
            "user_taste_tags_count": len(user_taste_tags)
        }
    )

@app.get("/promotions/{promo_id}", response_model=schemas.PromotionResponse, tags=["Promotions"])
def get_promotion_detail(promo_id: int, lat: Optional[float] = None, lon: Optional[float] = None, db: Session = Depends(get_db)):
    """Obtiene el detalle de una promoción e incrementa su contador de vistas"""
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    # Incrementar vistas
    promo.views_count += 1
    db.commit()

    dist = None
    dist_label = None
    if lat is not None and lon is not None:
        dist = haversine_distance(lat, lon, promo.latitude, promo.longitude)
        dist_label = format_distance_label(dist)

    return schemas.PromotionResponse(
        id=promo.id,
        merchant_id=promo.merchant_id,
        merchant_name=promo.merchant_name,
        title=promo.title,
        description=promo.description,
        category_id=promo.category_id,
        category_name=promo.category.name if promo.category else "General",
        category_icon=promo.category.icon if promo.category else "🏷️",
        original_price=promo.original_price,
        discount_percent=promo.discount_percent,
        promo_price=promo.promo_price,
        image_url=promo.image_url,
        tags=[t for t in promo.tags.split(",") if t],
        latitude=promo.latitude,
        longitude=promo.longitude,
        address=promo.address,
        is_active=promo.is_active,
        views_count=promo.views_count,
        distance_km=dist,
        distance_label=dist_label,
        matches_taste=False,
        created_at=str(promo.created_at)
    )

# --- PORTAL DE COMERCIO (GESTIÓN DE SUS PROMOCIONES) ---

@app.get("/merchants/{merchant_id}/promotions", response_model=List[schemas.PromotionResponse], tags=["Merchant Portal"])
def get_merchant_promotions(merchant_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las ofertas de un comercio (activas y pausadas) para el panel del portal"""
    promos = db.query(models.Promotion).filter(models.Promotion.merchant_id == merchant_id).order_by(models.Promotion.id.desc()).all()
    result = []
    for p in promos:
        result.append(schemas.PromotionResponse(
            id=p.id,
            merchant_id=p.merchant_id,
            merchant_name=p.merchant_name,
            title=p.title,
            description=p.description,
            category_id=p.category_id,
            category_name=p.category.name if p.category else "General",
            category_icon=p.category.icon if p.category else "🏷️",
            original_price=p.original_price,
            discount_percent=p.discount_percent,
            promo_price=p.promo_price,
            image_url=p.image_url,
            tags=[t for t in p.tags.split(",") if t],
            latitude=p.latitude,
            longitude=p.longitude,
            address=p.address,
            is_active=p.is_active,
            views_count=p.views_count,
            distance_km=0.0,
            distance_label="Tu Local",
            matches_taste=False,
            created_at=str(p.created_at)
        ))
    return result

@app.put("/promotions/{promo_id}", response_model=schemas.PromotionResponse, tags=["Merchant Portal"])
def update_promotion(promo_id: int, promo_in: schemas.PromotionCreate, db: Session = Depends(get_db)):
    """Permite al comercio o administrador modificar una oferta existente (título, precio, coordenadas, etc.)"""
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    discount = max(0.0, min(100.0, promo_in.discount_percent))
    promo_price = round(promo_in.original_price * (1.0 - (discount / 100.0)), 2)
    tags_str = ",".join([t.strip().lower() for t in promo_in.tags if t.strip()])

    promo.title = promo_in.title
    promo.description = promo_in.description
    promo.category_id = promo_in.category_id
    promo.original_price = promo_in.original_price
    promo.discount_percent = discount
    promo.promo_price = promo_price
    if promo_in.image_url:
        promo.image_url = promo_in.image_url
    promo.tags = tags_str
    promo.latitude = promo_in.latitude
    promo.longitude = promo_in.longitude
    promo.address = promo_in.address

    db.commit()
    db.refresh(promo)

    return schemas.PromotionResponse(
        id=promo.id,
        merchant_id=promo.merchant_id,
        merchant_name=promo.merchant_name,
        title=promo.title,
        description=promo.description,
        category_id=promo.category_id,
        category_name=promo.category.name if promo.category else "General",
        category_icon=promo.category.icon if promo.category else "🏷️",
        original_price=promo.original_price,
        discount_percent=promo.discount_percent,
        promo_price=promo.promo_price,
        image_url=promo.image_url,
        tags=[t for t in tags_str.split(",") if t],
        latitude=promo.latitude,
        longitude=promo.longitude,
        address=promo.address,
        is_active=promo.is_active,
        views_count=promo.views_count,
        distance_km=0.0,
        distance_label="Actualizada",
        matches_taste=False,
        created_at=str(promo.created_at)
    )

@app.patch("/promotions/{promo_id}/toggle-status", tags=["Merchant Portal"])
def toggle_promotion_status(promo_id: int, db: Session = Depends(get_db)):
    """Pausa o activa una promoción desde el portal de comercio"""
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    promo.is_active = not promo.is_active
    db.commit()
    return {"status": "ok", "promo_id": promo.id, "is_active": promo.is_active}

@app.delete("/promotions/{promo_id}", tags=["Merchant Portal"])
def delete_promotion(promo_id: int, db: Session = Depends(get_db)):
    """Elimina una oferta del catálogo"""
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    db.delete(promo)
    db.commit()
    return {"status": "ok", "message": "Promoción eliminada con éxito"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
