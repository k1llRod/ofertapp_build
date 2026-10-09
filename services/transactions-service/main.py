import os
import math
import uuid
import asyncio
from typing import List, Optional
import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, status, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from config import settings
from database import engine, Base, get_db, migrate_db
import models
import schemas
from seed_data import seed_initial_data
from security import (
    AuthUser,
    get_current_user,
    get_optional_current_user,
    require_admin,
    require_merchant_or_admin,
)

# Ejecutar migración automática de base de datos y creación de tablas
migrate_db()
Base.metadata.create_all(bind=engine)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Servicio de transacciones, catálogo de productos, registro de promociones, galería de fotos y pagos en línea",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/promotions/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/promotions/upload-image", tags=["Promotions"])
async def upload_promotion_image(file: UploadFile = File(...)):
    """Permite subir una imagen física para portada o galería de la promoción"""
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de imagen no permitido ({ext}). Formatos válidos: {', '.join(allowed_extensions)}"
        )

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen excede el tamaño máximo permitido de 10 MB"
        )

    filename = f"promo_{uuid.uuid4().hex[:12]}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    public_url = f"/api/v1/promotions/uploads/{filename}"
    return {"url": public_url, "filename": filename}

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

def get_promo_images_list(promo: models.Promotion) -> List[str]:
    """Retorna la lista unificada y limpia de imágenes de la promoción (principal + galería)"""
    imgs = []
    if promo.image_url and promo.image_url.strip():
        imgs.append(promo.image_url.strip())
    if promo.gallery:
        for g in promo.gallery.split(","):
            clean = g.strip()
            if clean and clean not in imgs:
                imgs.append(clean)
    if not imgs:
        imgs.append("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800")
    return imgs

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

EMOTICON_MAP = {
    ":d": "😃", ":D": "😃",
    ":)": "😊", ":-)": "😊",
    ";)": "😉", ";-)": "😉",
    ":p": "😋", ":P": "😋",
    ":o": "😮", ":O": "😮",
    "<3": "❤️",
    ":3": "😺",
    "xd": "😆", "XD": "😆",
    ":(": "🙁", ":/": "😕"
}

def clean_icon(icon_str: Optional[str]) -> str:
    if not icon_str:
        return "🏷️"
    icon_str = icon_str.strip()
    return EMOTICON_MAP.get(icon_str, icon_str)

def generate_unique_name(db: Session, base_name: str, current_id: Optional[int] = None) -> str:
    name = base_name.strip()
    candidate = name
    counter = 1
    while True:
        query = db.query(models.Category).filter(models.Category.name == candidate)
        if current_id:
            query = query.filter(models.Category.id != current_id)
        if not query.first():
            return candidate
        candidate = f"{name} ({counter})"
        counter += 1

def generate_unique_slug(db: Session, base_text: str, current_id: Optional[int] = None) -> str:
    import re
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', base_text.strip().lower()).strip('-')
    if not slug:
        slug = "categoria"
    
    candidate = slug
    counter = 1
    while True:
        query = db.query(models.Category).filter(models.Category.slug == candidate)
        if current_id:
            query = query.filter(models.Category.id != current_id)
        if not query.first():
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1

def sync_category_to_auth(cat_id: int, name: str, slug: str, icon: str, description: Optional[str] = None, delete: bool = False):
    try:
        import sqlite3
        auth_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth-service", "auth.db")
        if os.path.exists(auth_db_path):
            conn = sqlite3.connect(auth_db_path)
            cur = conn.cursor()
            if delete:
                cur.execute("DELETE FROM taste_categories WHERE id = ?", (cat_id,))
            else:
                cur.execute("SELECT id FROM taste_categories WHERE id = ?", (cat_id,))
                if cur.fetchone():
                    cur.execute("UPDATE taste_categories SET name = ?, slug = ?, icon = ?, description = ? WHERE id = ?", 
                                (name, slug, icon, description, cat_id))
                else:
                    cur.execute("INSERT INTO taste_categories (id, name, slug, icon, description) VALUES (?, ?, ?, ?, ?)",
                                (cat_id, name, slug, icon, description))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"[Warning] Failed to sync category to auth.db: {e}")

@app.get("/categories", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    """Obtiene el listado de categorías del catálogo"""
    return db.query(models.Category).all()

@app.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED, tags=["Categories"])
def create_category(cat_in: schemas.CategoryCreate, admin: AuthUser = Depends(require_admin), db: Session = Depends(get_db)):
    """[Admin] Crea una nueva categoría en el catálogo (Acceso total Admin)"""
    unique_name = generate_unique_name(db, cat_in.name)
    base_slug = cat_in.slug if cat_in.slug and cat_in.slug.strip() else unique_name
    unique_slug = generate_unique_slug(db, base_slug)
    icon_clean = clean_icon(cat_in.icon)

    new_cat = models.Category(
        name=unique_name,
        slug=unique_slug,
        icon=icon_clean,
        description=cat_in.description
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    sync_category_to_auth(new_cat.id, new_cat.name, new_cat.slug, new_cat.icon, new_cat.description)
    return new_cat

@app.put("/categories/{category_id}", response_model=schemas.CategoryResponse, tags=["Categories"])
def update_category(category_id: int, cat_in: schemas.CategoryUpdate, admin: AuthUser = Depends(require_admin), db: Session = Depends(get_db)):
    """[Admin] Modifica una categoría del catálogo (Acceso total Admin)"""
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if cat_in.name is not None and cat_in.name.strip():
        cat.name = generate_unique_name(db, cat_in.name, current_id=category_id)
    if cat_in.slug is not None and cat_in.slug.strip():
        cat.slug = generate_unique_slug(db, cat_in.slug, current_id=category_id)
    elif cat_in.name is not None and not cat.slug:
        cat.slug = generate_unique_slug(db, cat.name, current_id=category_id)
    if cat_in.icon is not None:
        cat.icon = clean_icon(cat_in.icon)
    if cat_in.description is not None:
        cat.description = cat_in.description
    db.commit()
    db.refresh(cat)
    sync_category_to_auth(cat.id, cat.name, cat.slug, cat.icon, cat.description)
    return cat

@app.delete("/categories/{category_id}", tags=["Categories"])
def delete_category(category_id: int, admin: AuthUser = Depends(require_admin), db: Session = Depends(get_db)):
    """[Admin] Elimina una categoría del catálogo (Acceso total Admin)"""
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    cat_name = cat.name
    db.delete(cat)
    db.commit()
    sync_category_to_auth(category_id, "", "", "", delete=True)
    return {"status": "ok", "message": f"Categoría {cat_name} eliminada con éxito"}

# --- PROMOTIONS ENDPOINTS ---

@app.post("/promotions", response_model=schemas.PromotionResponse, status_code=status.HTTP_201_CREATED, tags=["Promotions"])
async def create_promotion(
    promo_in: schemas.PromotionCreate,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(require_merchant_or_admin),
    db: Session = Depends(get_db)
):
    """
    Registra una nueva promoción en el catálogo con soporte para múltiples imágenes (galería).
    Reglas de perfil:
    - Admin: Acceso total para crear a nombre de cualquier comercio o general.
    - Merchant: Solo puede crear promociones bajo su propio id de comercio registrado.
    """
    category = db.query(models.Category).filter(models.Category.id == promo_in.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Categoría no encontrada")

    # Aplicar regla estricta de propiedad (ownership)
    if current_user.role == "merchant":
        assigned_merchant_id = current_user.id
        assigned_merchant_name = current_user.name if current_user.name else (promo_in.merchant_name or f"Comercio #{current_user.id}")
    elif current_user.role == "admin":
        assigned_merchant_id = promo_in.merchant_id if promo_in.merchant_id else current_user.id
        assigned_merchant_name = promo_in.merchant_name if promo_in.merchant_name else (current_user.name or "Comercio Afiliado")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Solo comercios y administradores pueden publicar ofertas."
        )

    discount = max(0.0, min(100.0, promo_in.discount_percent))
    promo_price = round(promo_in.original_price * (1.0 - (discount / 100.0)), 2)
    tags_str = ",".join([t.strip().lower() for t in promo_in.tags if t.strip()])

    gallery_str = ""
    if promo_in.gallery:
        gallery_str = ",".join([g.strip() for g in promo_in.gallery if g.strip()])

    new_promo = models.Promotion(
        merchant_id=assigned_merchant_id,
        merchant_name=assigned_merchant_name,
        title=promo_in.title,
        description=promo_in.description,
        category_id=promo_in.category_id,
        original_price=promo_in.original_price,
        discount_percent=discount,
        promo_price=promo_price,
        image_url=promo_in.image_url or "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800",
        gallery=gallery_str,
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
        images=get_promo_images_list(new_promo),
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
    Devuelve las promociones activas con galerías completas de fotos, ordenadas por cercanía geográfica y afinidad con gustos.
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
    default_lat = -34.6037
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
            "score": (2.0 if matches_taste else 0.0) - (dist * 0.1)
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
            images=get_promo_images_list(p),
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
    """Obtiene el detalle completo de una promoción (incluyendo todas sus fotos) e incrementa su contador de vistas"""
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
        images=get_promo_images_list(promo),
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

# --- PORTAL DE COMERCIO Y GESTIÓN DE PROMOCIONES ---

@app.get("/admin/promotions", response_model=List[schemas.PromotionResponse], tags=["Admin - Promotions"])
def get_all_promotions_admin(
    merchant_id: Optional[int] = Query(None, description="Filtrar por comercio específico"),
    admin: AuthUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """[Admin] Obtiene todas las promociones del sistema de todos los comercios para gestión total (Acceso total Admin)"""
    query = db.query(models.Promotion)
    if merchant_id:
        query = query.filter(models.Promotion.merchant_id == merchant_id)
    promos = query.order_by(models.Promotion.id.desc()).all()
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
            images=get_promo_images_list(p),
            tags=[t for t in p.tags.split(",") if t],
            latitude=p.latitude,
            longitude=p.longitude,
            address=p.address,
            is_active=p.is_active,
            views_count=p.views_count,
            distance_km=0.0,
            distance_label=f"Comercio #{p.merchant_id}",
            matches_taste=False,
            created_at=str(p.created_at)
        ))
    return result

@app.get("/merchants/{merchant_id}/promotions", response_model=List[schemas.PromotionResponse], tags=["Merchant Portal"])
def get_merchant_promotions(
    merchant_id: int,
    current_user: Optional[AuthUser] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las ofertas de un comercio.
    - Si el usuario logueado es Comercio, solo puede consultar las suyas propias.
    - Si es Administrador, tiene acceso total a consultar cualquier comercio.
    """
    if current_user and current_user.role == "merchant" and current_user.id != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: El usuario comercio solo puede consultar y gestionar sus propios registros creados."
        )

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
            images=get_promo_images_list(p),
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
def update_promotion(
    promo_id: int,
    promo_in: schemas.PromotionUpdate,
    current_user: AuthUser = Depends(require_merchant_or_admin),
    db: Session = Depends(get_db)
):
    """
    Permite modificar una oferta existente.
    - Administrador: Acceso total para modificar cualquier oferta.
    - Merchant: Solo puede modificar sus propios registros creados.
    """
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    # Validación de propiedad (ownership)
    if current_user.role == "merchant" and promo.merchant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: El usuario comercio solo puede modificar sus propios registros creados."
        )

    if promo_in.title is not None:
        promo.title = promo_in.title
    if promo_in.description is not None:
        promo.description = promo_in.description
    if promo_in.category_id is not None:
        promo.category_id = promo_in.category_id
    if promo_in.original_price is not None:
        promo.original_price = promo_in.original_price
    if promo_in.discount_percent is not None:
        promo.discount_percent = max(0.0, min(100.0, promo_in.discount_percent))
    
    # Recalcular precio promocional si se modificó precio o descuento
    promo.promo_price = round(promo.original_price * (1.0 - (promo.discount_percent / 100.0)), 2)

    if promo_in.image_url is not None:
        promo.image_url = promo_in.image_url
    if promo_in.gallery is not None:
        promo.gallery = ",".join([g.strip() for g in promo_in.gallery if g.strip()])
    if promo_in.tags is not None:
        promo.tags = ",".join([t.strip().lower() for t in promo_in.tags if t.strip()])
    if promo_in.latitude is not None:
        promo.latitude = promo_in.latitude
    if promo_in.longitude is not None:
        promo.longitude = promo_in.longitude
    if promo_in.address is not None:
        promo.address = promo_in.address
    if promo_in.is_active is not None:
        promo.is_active = promo_in.is_active

    # Si admin especifica cambiar el comercio o nombre
    if current_user.role == "admin":
        if promo_in.merchant_id:
            promo.merchant_id = promo_in.merchant_id
        if promo_in.merchant_name:
            promo.merchant_name = promo_in.merchant_name

    db.commit()
    db.refresh(promo)

    tags_list = [t for t in (promo.tags or "").split(",") if t]

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
        images=get_promo_images_list(promo),
        tags=tags_list,
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
def toggle_promotion_status(
    promo_id: int,
    current_user: AuthUser = Depends(require_merchant_or_admin),
    db: Session = Depends(get_db)
):
    """
    Pausa o activa una promoción.
    - Administrador: Acceso total.
    - Merchant: Solo puede pausar o activar sus propios registros creados.
    """
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    if current_user.role == "merchant" and promo.merchant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: El usuario comercio solo puede pausar o activar sus propios registros creados."
        )

    promo.is_active = not promo.is_active
    db.commit()
    return {"status": "ok", "promo_id": promo.id, "is_active": promo.is_active}

@app.delete("/promotions/{promo_id}", tags=["Merchant Portal"])
def delete_promotion(
    promo_id: int,
    current_user: AuthUser = Depends(require_merchant_or_admin),
    db: Session = Depends(get_db)
):
    """
    Elimina una oferta del catálogo.
    - Administrador: Acceso total para borrar cualquier oferta del sistema.
    - Merchant: Solo puede borrar sus propios registros creados.
    """
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    if current_user.role == "merchant" and promo.merchant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: El usuario comercio solo puede borrar sus propios registros creados."
        )

    db.delete(promo)
    db.commit()
    return {"status": "ok", "message": "Promoción eliminada con éxito"}

# --- PAGOS EN LÍNEA & ÓRDENES (CHECKOUT) ---

@app.post("/orders/checkout", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders & Payments"])
def checkout_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Procesa una compra o pago en línea de una promoción/producto/servicio.
    Genera número de orden, comprobante de pago, identificador de transacción y token QR para canje.
    """
    promo = db.query(models.Promotion).filter(models.Promotion.id == order_in.promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    if not promo.is_active:
        raise HTTPException(status_code=400, detail="Esta promoción no se encuentra activa en este momento")

    qty = max(1, order_in.quantity)
    total_amount = round(promo.promo_price * qty, 2)
    order_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    qr_token = f"OFRTP-{uuid.uuid4().hex[:16].upper()}"

    new_order = models.Order(
        order_number=order_num,
        promotion_id=promo.id,
        user_id=order_in.user_id,
        customer_name=order_in.customer_name,
        customer_email=order_in.customer_email,
        quantity=qty,
        unit_price=promo.promo_price,
        total_amount=total_amount,
        payment_method=order_in.payment_method,
        payment_status="completed",
        transaction_id=txn_id,
        qr_code_token=qr_token
    )
    db.add(new_order)
    promo.views_count += 1
    db.commit()
    db.refresh(new_order)

    return schemas.OrderResponse(
        id=new_order.id,
        order_number=new_order.order_number,
        promotion_id=promo.id,
        promotion_title=promo.title,
        merchant_name=promo.merchant_name,
        customer_name=new_order.customer_name,
        customer_email=new_order.customer_email,
        quantity=new_order.quantity,
        unit_price=new_order.unit_price,
        total_amount=new_order.total_amount,
        payment_method=new_order.payment_method,
        payment_status=new_order.payment_status,
        transaction_id=new_order.transaction_id,
        qr_code_token=new_order.qr_code_token,
        created_at=str(new_order.created_at)
    )

@app.get("/orders/{order_number}", response_model=schemas.OrderResponse, tags=["Orders & Payments"])
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Obtiene el comprobante y detalle de una compra online por su número de orden"""
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    promo = db.query(models.Promotion).filter(models.Promotion.id == order.promotion_id).first()
    return schemas.OrderResponse(
        id=order.id,
        order_number=order.order_number,
        promotion_id=order.promotion_id,
        promotion_title=promo.title if promo else "Promoción",
        merchant_name=promo.merchant_name if promo else "Comercio",
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total_amount=order.total_amount,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        transaction_id=order.transaction_id,
        qr_code_token=order.qr_code_token,
        created_at=str(order.created_at)
    )

@app.get("/admin/orders", response_model=List[schemas.OrderResponse], tags=["Admin - Orders"])
def get_all_orders_admin(admin: AuthUser = Depends(require_admin), db: Session = Depends(get_db)):
    """[Admin] Obtiene el historial completo de todas las órdenes de la plataforma (Acceso total Admin)"""
    orders = db.query(models.Order).order_by(models.Order.id.desc()).all()
    promo_ids = list(set([o.promotion_id for o in orders]))
    promos = db.query(models.Promotion).filter(models.Promotion.id.in_(promo_ids)).all() if promo_ids else []
    promo_map = {p.id: p for p in promos}
    res = []
    for o in orders:
        p = promo_map.get(o.promotion_id)
        res.append(schemas.OrderResponse(
            id=o.id,
            order_number=o.order_number,
            promotion_id=o.promotion_id,
            promotion_title=p.title if p else "Promoción",
            merchant_name=p.merchant_name if p else "Comercio",
            customer_name=o.customer_name,
            customer_email=o.customer_email,
            quantity=o.quantity,
            unit_price=o.unit_price,
            total_amount=o.total_amount,
            payment_method=o.payment_method,
            payment_status=o.payment_status,
            transaction_id=o.transaction_id,
            qr_code_token=o.qr_code_token,
            created_at=str(o.created_at)
        ))
    return res

@app.get("/merchants/{merchant_id}/orders", response_model=List[schemas.OrderResponse], tags=["Orders & Payments"])
def get_merchant_orders(
    merchant_id: int,
    current_user: AuthUser = Depends(require_merchant_or_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de compras y pagos en línea recibidos por el comercio.
    - Admin: Puede consultar los pedidos de cualquier comercio.
    - Merchant: Solo puede consultar los pedidos de sus propios registros creados.
    """
    if current_user.role == "merchant" and current_user.id != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: El usuario comercio solo puede consultar los pedidos de su propio comercio."
        )

    promos = db.query(models.Promotion).filter(models.Promotion.merchant_id == merchant_id).all()
    promo_ids = [p.id for p in promos]
    orders = db.query(models.Order).filter(models.Order.promotion_id.in_(promo_ids)).order_by(models.Order.id.desc()).all()
    promo_map = {p.id: p for p in promos}
    res = []
    for o in orders:
        p = promo_map.get(o.promotion_id)
        res.append(schemas.OrderResponse(
            id=o.id,
            order_number=o.order_number,
            promotion_id=o.promotion_id,
            promotion_title=p.title if p else "Promoción",
            merchant_name=p.merchant_name if p else "Comercio",
            customer_name=o.customer_name,
            customer_email=o.customer_email,
            quantity=o.quantity,
            unit_price=o.unit_price,
            total_amount=o.total_amount,
            payment_method=o.payment_method,
            payment_status=o.payment_status,
            transaction_id=o.transaction_id,
            qr_code_token=o.qr_code_token,
            created_at=str(o.created_at)
        ))
    return res

# --- TRANSACTIONS CORE ENDPOINTS (SERVICIO, PRODUCTO, USUARIO) ---

@app.post("/transactions", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def create_transaction(
    tx_in: schemas.TransactionCreate,
    current_user: Optional[AuthUser] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea y registra una nueva transacción en el sistema vinculando:
    - Servicio involucrado (service / service_name / servicio)
    - Producto involucrado (product / product_name / producto)
    - Usuario involucrado (user_id / user / usuario / user_email / user_name)
    - Monto, cantidad, método de pago y estado.
    """
    # 1. Determinar servicio
    service_val = tx_in.service or tx_in.service_name or tx_in.servicio
    if not service_val or not service_val.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'servicio' / 'service' es obligatorio para registrar la transacción."
        )

    # 2. Determinar producto
    product_val = tx_in.product or tx_in.product_name or tx_in.producto
    if not product_val or not product_val.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'producto' / 'product' es obligatorio para registrar la transacción."
        )

    # 3. Determinar usuario
    user_id = tx_in.user_id
    user_name = tx_in.user_name or tx_in.user or tx_in.usuario
    user_email = tx_in.user_email

    if current_user:
        if user_id is None:
            user_id = current_user.id
        if not user_name and current_user.name:
            user_name = current_user.name
        if not user_email and current_user.email:
            user_email = current_user.email

    amount_val = tx_in.amount if tx_in.amount is not None else (tx_in.monto if tx_in.monto is not None else 0.0)
    qty = max(1, tx_in.quantity or 1)
    tx_code = tx_in.transaction_code or f"TXN-{uuid.uuid4().hex[:10].upper()}"

    new_tx = models.Transaction(
        transaction_code=tx_code,
        service_name=service_val.strip(),
        product_name=product_val.strip(),
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        amount=round(float(amount_val), 2),
        quantity=qty,
        payment_method=tx_in.payment_method or "credit_card",
        status=tx_in.status or "completed",
        description=tx_in.description
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    return schemas.TransactionResponse(
        id=new_tx.id,
        transaction_code=new_tx.transaction_code,
        service=new_tx.service_name,
        service_name=new_tx.service_name,
        product=new_tx.product_name,
        product_name=new_tx.product_name,
        user_id=new_tx.user_id,
        user_name=new_tx.user_name,
        user_email=new_tx.user_email,
        user=new_tx.user_name or (f"Usuario #{new_tx.user_id}" if new_tx.user_id else None),
        amount=new_tx.amount,
        quantity=new_tx.quantity,
        payment_method=new_tx.payment_method,
        status=new_tx.status,
        description=new_tx.description,
        created_at=str(new_tx.created_at)
    )

@app.get("/transactions", response_model=List[schemas.TransactionResponse], tags=["Transactions"])
def list_transactions(
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    service: Optional[str] = Query(None, description="Filtrar por servicio"),
    product: Optional[str] = Query(None, description="Filtrar por producto"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lista las transacciones registradas en el sistema con soporte de filtros opcionales por usuario, servicio, producto y estado.
    """
    query = db.query(models.Transaction)
    if user_id is not None:
        query = query.filter(models.Transaction.user_id == user_id)
    if service:
        query = query.filter(models.Transaction.service_name.ilike(f"%{service}%"))
    if product:
        query = query.filter(models.Transaction.product_name.ilike(f"%{product}%"))
    if status:
        query = query.filter(models.Transaction.status == status)

    transactions = query.order_by(models.Transaction.id.desc()).offset(offset).limit(limit).all()

    return [
        schemas.TransactionResponse(
            id=t.id,
            transaction_code=t.transaction_code,
            service=t.service_name,
            service_name=t.service_name,
            product=t.product_name,
            product_name=t.product_name,
            user_id=t.user_id,
            user_name=t.user_name,
            user_email=t.user_email,
            user=t.user_name or (f"Usuario #{t.user_id}" if t.user_id else None),
            amount=t.amount,
            quantity=t.quantity,
            payment_method=t.payment_method,
            status=t.status,
            description=t.description,
            created_at=str(t.created_at)
        )
        for t in transactions
    ]

@app.get("/transactions/{transaction_id}", response_model=schemas.TransactionResponse, tags=["Transactions"])
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de una transacción por su ID numérico"""
    t = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return schemas.TransactionResponse(
        id=t.id,
        transaction_code=t.transaction_code,
        service=t.service_name,
        service_name=t.service_name,
        product=t.product_name,
        product_name=t.product_name,
        user_id=t.user_id,
        user_name=t.user_name,
        user_email=t.user_email,
        user=t.user_name or (f"Usuario #{t.user_id}" if t.user_id else None),
        amount=t.amount,
        quantity=t.quantity,
        payment_method=t.payment_method,
        status=t.status,
        description=t.description,
        created_at=str(t.created_at)
    )

@app.get("/transactions/code/{transaction_code}", response_model=schemas.TransactionResponse, tags=["Transactions"])
def get_transaction_by_code(transaction_code: str, db: Session = Depends(get_db)):
    """Obtiene el detalle de una transacción por su código único de transacción"""
    t = db.query(models.Transaction).filter(models.Transaction.transaction_code == transaction_code).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return schemas.TransactionResponse(
        id=t.id,
        transaction_code=t.transaction_code,
        service=t.service_name,
        service_name=t.service_name,
        product=t.product_name,
        product_name=t.product_name,
        user_id=t.user_id,
        user_name=t.user_name,
        user_email=t.user_email,
        user=t.user_name or (f"Usuario #{t.user_id}" if t.user_id else None),
        amount=t.amount,
        quantity=t.quantity,
        payment_method=t.payment_method,
        status=t.status,
        description=t.description,
        created_at=str(t.created_at)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
