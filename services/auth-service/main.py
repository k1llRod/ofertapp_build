import math
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database import engine, Base, get_db
import models
import schemas
from security import verify_password, get_password_hash, create_access_token, get_current_user
from seed_data import seed_initial_data

# Crear tablas en arranque
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Servicio de autenticación, usuarios, perfilado de gustos y geolocalización",
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
    return {"status": "ok", "service": "auth-service"}

# --- AUTH ENDPOINTS ---

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado")
    
    new_user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role if user_in.role in ["user", "merchant", "admin"] else "user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "email": user.email})
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )

@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- TASTES & PREFERENCES ENDPOINTS ---

@app.get("/tastes/categories", response_model=List[schemas.TasteCategoryResponse], tags=["Tastes"])
def list_categories(db: Session = Depends(get_db)):
    """Lista las categorías disponibles para clasificar gustos y ofertas"""
    return db.query(models.TasteCategory).all()

@app.get("/tastes/me", response_model=List[schemas.TastePreferenceResponse], tags=["Tastes"])
def get_my_tastes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Devuelve los gustos y categorías favoritas configuradas por el usuario actual"""
    preferences = db.query(models.UserTastePreference).filter(
        models.UserTastePreference.user_id == current_user.id
    ).all()

    result = []
    for pref in preferences:
        tags_list = [t.strip().lower() for t in pref.tags.split(",") if t.strip()]
        result.append(schemas.TastePreferenceResponse(
            id=pref.id,
            category_id=pref.category_id,
            category_name=pref.category.name if pref.category else "General",
            category_icon=pref.category.icon if pref.category else "🏷️",
            tags=tags_list,
            max_distance_km=pref.max_distance_km
        ))
    return result

@app.put("/tastes/me", response_model=List[schemas.TastePreferenceResponse], tags=["Tastes"])
def update_my_tastes(
    request: schemas.UpdateUserTastesRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza la base de datos de gustos e intereses del usuario"""
    # Eliminar gustos anteriores y recrear
    db.query(models.UserTastePreference).filter(
        models.UserTastePreference.user_id == current_user.id
    ).delete()

    for item in request.preferences:
        tags_str = ",".join([t.strip().lower() for t in item.tags if t.strip()])
        new_pref = models.UserTastePreference(
            user_id=current_user.id,
            category_id=item.category_id,
            tags=tags_str,
            max_distance_km=item.max_distance_km
        )
        db.add(new_pref)

    db.commit()
    return get_my_tastes(current_user=current_user, db=db)

@app.delete("/tastes/me/{category_id}", response_model=List[schemas.TastePreferenceResponse], tags=["Tastes"])
def delete_my_taste_category(
    category_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina una categoría específica de las preferencias de gustos del usuario autenticado"""
    db.query(models.UserTastePreference).filter(
        models.UserTastePreference.user_id == current_user.id,
        models.UserTastePreference.category_id == category_id
    ).delete()
    db.commit()
    return get_my_tastes(current_user=current_user, db=db)

# --- USER LOCATION & PROXIMITY ---

@app.post("/location/update", response_model=schemas.UserLocationResponse, tags=["Location"])
def update_user_location(
    loc_data: schemas.UserLocationUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza la ubicación GPS actual del usuario y su token FCM"""
    user_loc = db.query(models.UserLocation).filter(models.UserLocation.user_id == current_user.id).first()
    if not user_loc:
        user_loc = models.UserLocation(user_id=current_user.id)
        db.add(user_loc)

    user_loc.latitude = loc_data.latitude
    user_loc.longitude = loc_data.longitude
    if loc_data.address_label:
        user_loc.address_label = loc_data.address_label
    if loc_data.fcm_token:
        user_loc.fcm_token = loc_data.fcm_token

    db.commit()
    db.refresh(user_loc)
    return schemas.UserLocationResponse(
        latitude=user_loc.latitude,
        longitude=user_loc.longitude,
        address_label=user_loc.address_label,
        updated_at=str(user_loc.updated_at)
    )

# --- INTERNAL: AUDIENCE MATCHING (FOR NOTIFICATIONS SERVICE) ---

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@app.post("/internal/match-audience", response_model=schemas.MatchAudienceResponse, tags=["Internal"])
def match_audience(req: schemas.MatchAudienceRequest, db: Session = Depends(get_db)):
    """
    Endpoint consumido por notifications-services:
    Encuentra usuarios que tengan la categoría/tags en su perfil de gustos
    Y que se encuentren a una distancia menor a su radio máximo configurado.
    """
    users = db.query(models.User).filter(models.User.is_active == True).all()
    matched_results = []
    promo_tags_set = set([t.strip().lower() for t in req.tags])

    for user in users:
        # 1. Verificar si coincide con algún gusto
        matching_prefs = [p for p in user.tastes if p.category_id == req.category_id]
        has_category_match = len(matching_prefs) > 0
        has_tag_match = False
        reasons = []

        if has_category_match:
            reasons.append("Coincide con tu categoría favorita")

        # Verificar tags
        for p in user.tastes:
            user_tags = set([t.strip().lower() for t in p.tags.split(",") if t.strip()])
            if promo_tags_set.intersection(user_tags):
                has_tag_match = True
                reasons.append(f"Etiquetas de interés: {', '.join(promo_tags_set.intersection(user_tags))}")

        if not (has_category_match or has_tag_match):
            continue

        # 2. Verificar distancia si el usuario tiene ubicación registrada
        dist_km = 0.0
        fcm_token = None
        if user.location:
            dist_km = haversine_distance(
                req.latitude, req.longitude,
                user.location.latitude, user.location.longitude
            )
            fcm_token = user.location.fcm_token

            # Evaluar si la distancia entra en el radio
            max_allowed = req.max_radius_km
            if matching_prefs and matching_prefs[0].max_distance_km:
                max_allowed = matching_prefs[0].max_distance_km

            if dist_km > max_allowed:
                continue
        else:
            # Si no tiene ubicación registrada, asumimos match por gustos
            dist_km = 1.0

        matched_results.append(schemas.MatchedUser(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            fcm_token=fcm_token,
            distance_km=dist_km,
            matched_reason=" y ".join(reasons) if reasons else "Afinidad con tus gustos"
        ))

    return schemas.MatchAudienceResponse(
        matched_users=matched_results,
        count=len(matched_results)
    )

# --- ADMIN & CONFIGURATION CRUD ENDPOINTS ---

# 1. CRUD USUARIOS (Create, Read, Update, Delete)
@app.post("/admin/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Admin - Users CRUD"])
def admin_create_user(user_in: schemas.UserCreateAdmin, db: Session = Depends(get_db)):
    """[C - Create] Crea un nuevo usuario o comercio directamente desde el panel de administración"""
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado")
    
    new_user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role if user_in.role in ["user", "merchant", "admin"] else "user",
        is_active=user_in.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/admin/users", response_model=List[schemas.UserResponse], tags=["Admin - Users CRUD"])
def list_all_users(db: Session = Depends(get_db)):
    """[R - Read List] Lista todos los usuarios y comercios con sus roles y estados"""
    return db.query(models.User).order_by(models.User.id.asc()).all()

@app.get("/admin/users/{user_id}", response_model=schemas.UserResponse, tags=["Admin - Users CRUD"])
def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    """[R - Read Detail] Obtiene la información detallada de un usuario específico"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.put("/admin/users/{user_id}", response_model=schemas.UserResponse, tags=["Admin - Users CRUD"])
def update_user_info(user_id: int, req: schemas.UserUpdate, db: Session = Depends(get_db)):
    """[U - Update] Modifica los datos completos de un usuario (nombre, email, teléfono, rol, estado)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if req.full_name is not None:
        user.full_name = req.full_name
    if req.email is not None:
        user.email = req.email
    if req.phone is not None:
        user.phone = req.phone
    if req.role is not None and req.role in ["user", "merchant", "admin"]:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active

    db.commit()
    db.refresh(user)
    return user

@app.put("/admin/users/{user_id}/role", response_model=schemas.UserResponse, tags=["Admin - Users CRUD"])
def update_user_role(user_id: int, req: schemas.UserRoleUpdate, db: Session = Depends(get_db)):
    """[U - Update Role] Administra los permisos y roles de un usuario ('admin', 'merchant', 'user')"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if req.role in ["user", "merchant", "admin"]:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active

    db.commit()
    db.refresh(user)
    return user

@app.delete("/admin/users/{user_id}", tags=["Admin - Users CRUD"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """[D - Delete] Elimina un usuario del sistema y sus datos relacionados"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"status": "ok", "message": f"Usuario {user.full_name} eliminado correctamente"}


# 2. CRUD CATEGORÍAS (Create, Read, Update, Delete)
@app.post("/admin/categories", response_model=schemas.TasteCategoryResponse, status_code=status.HTTP_201_CREATED, tags=["Admin - Categories CRUD"])
def create_category(cat_in: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """[C - Create] Crea una nueva categoría para clasificar ofertas y gustos"""
    existing = db.query(models.TasteCategory).filter(models.TasteCategory.slug == cat_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="El slug de categoría ya existe")

    new_cat = models.TasteCategory(
        name=cat_in.name,
        slug=cat_in.slug,
        icon=cat_in.icon,
        description=cat_in.description
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@app.get("/admin/categories/{category_id}", response_model=schemas.TasteCategoryResponse, tags=["Admin - Categories CRUD"])
def get_category_detail(category_id: int, db: Session = Depends(get_db)):
    """[R - Read Detail] Obtiene los detalles de una categoría"""
    cat = db.query(models.TasteCategory).filter(models.TasteCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat

@app.put("/admin/categories/{category_id}", response_model=schemas.TasteCategoryResponse, tags=["Admin - Categories CRUD"])
def update_category(category_id: int, cat_in: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    """[U - Update] Modifica los datos de una categoría (nombre, slug, icono, descripción)"""
    cat = db.query(models.TasteCategory).filter(models.TasteCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if cat_in.name is not None:
        cat.name = cat_in.name
    if cat_in.slug is not None:
        cat.slug = cat_in.slug
    if cat_in.icon is not None:
        cat.icon = cat_in.icon
    if cat_in.description is not None:
        cat.description = cat_in.description

    db.commit()
    db.refresh(cat)
    return cat

@app.delete("/admin/categories/{category_id}", tags=["Admin - Categories CRUD"])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """[D - Delete] Elimina una categoría del sistema"""
    cat = db.query(models.TasteCategory).filter(models.TasteCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(cat)
    db.commit()
    return {"status": "ok", "message": f"Categoría {cat.name} eliminada con éxito"}


# 3. CRUD CONFIGURACIONES DEL SISTEMA (Create, Read, Update, Delete)
@app.post("/admin/settings", response_model=schemas.SystemSettingResponse, status_code=status.HTTP_201_CREATED, tags=["Admin - Settings CRUD"])
def create_system_setting(setting_in: schemas.SystemSettingCreate, db: Session = Depends(get_db)):
    """[C - Create] Registra un nuevo parámetro operativo del sistema"""
    existing = db.query(models.SystemSetting).filter(models.SystemSetting.key == setting_in.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="La clave de configuración ya existe")

    new_setting = models.SystemSetting(
        key=setting_in.key,
        value=setting_in.value,
        description=setting_in.description,
        category=setting_in.category or "general"
    )
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting

@app.get("/admin/settings", response_model=List[schemas.SystemSettingResponse], tags=["Admin - Settings CRUD"])
def get_system_settings(db: Session = Depends(get_db)):
    """[R - Read List] Obtiene el listado completo de configuraciones del sistema"""
    return db.query(models.SystemSetting).order_by(models.SystemSetting.id.asc()).all()

@app.get("/admin/settings/{key}", response_model=schemas.SystemSettingResponse, tags=["Admin - Settings CRUD"])
def get_system_setting_detail(key: str, db: Session = Depends(get_db)):
    """[R - Read Detail] Obtiene el valor y descripción de una configuración por su clave"""
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return setting

@app.put("/admin/settings/{key}", response_model=schemas.SystemSettingResponse, tags=["Admin - Settings CRUD"])
def update_system_setting(key: str, req: schemas.SystemSettingUpdate, db: Session = Depends(get_db)):
    """[U - Update] Modifica el valor de una configuración del sistema"""
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if not setting:
        setting = models.SystemSetting(key=key, value=req.value, description=f"Configuración para {key}")
        db.add(setting)
    else:
        setting.value = req.value

    db.commit()
    db.refresh(setting)
    return setting

@app.delete("/admin/settings/{key}", tags=["Admin - Settings CRUD"])
def delete_system_setting(key: str, db: Session = Depends(get_db)):
    """[D - Delete] Elimina una configuración personalizada del sistema"""
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    db.delete(setting)
    db.commit()
    return {"status": "ok", "message": f"Configuración {key} eliminada"}

# 4. GUSTOS - DELETE INDIVIDUAL
@app.delete("/tastes/me/{category_id}", tags=["Tastes"])
def delete_taste_preference(category_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """[D - Delete] Elimina una categoría específica de la lista de gustos del usuario"""
    deleted = db.query(models.UserTastePreference).filter(
        models.UserTastePreference.user_id == current_user.id,
        models.UserTastePreference.category_id == category_id
    ).delete()
    db.commit()
    return {"status": "ok", "deleted_count": deleted}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
