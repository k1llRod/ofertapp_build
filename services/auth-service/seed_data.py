from sqlalchemy.orm import Session
import models
from security import get_password_hash

INITIAL_CATEGORIES = [
    {"name": "Gastronomía", "slug": "gastronomia", "icon": "🍔", "description": "Restaurantes, cafeterías, postres y comida rápida"},
    {"name": "Tecnología", "slug": "tecnologia", "icon": "💻", "description": "Smartphones, computación, gadgets y accesorios"},
    {"name": "Moda y Calzado", "slug": "moda", "icon": "👗", "description": "Ropa, zapatos y accesorios de vestir"},
    {"name": "Entretenimiento", "slug": "entretenimiento", "icon": "🎟️", "description": "Cine, conciertos, parques y eventos"},
    {"name": "Belleza y Spa", "slug": "belleza", "icon": "💆", "description": "Peluquerías, barberías, masajes y cuidado personal"},
    {"name": "Deportes y Fitness", "slug": "deportes", "icon": "⚽", "description": "Gimnasios, suplementos y artículos deportivos"},
    {"name": "Hogar y Muebles", "slug": "hogar", "icon": "🛋️", "description": "Muebles, decoración y herramientas del hogar"},
    {"name": "Servicios Profesionales", "slug": "servicios", "icon": "🛠️", "description": "Talleres, consultorías y reparaciones"}
]

def seed_initial_data(db: Session):
    # 1. Seed Categories if empty
    if db.query(models.TasteCategory).count() == 0:
        for cat in INITIAL_CATEGORIES:
            db.add(models.TasteCategory(**cat))
        db.commit()

    # 2. Seed Demo Users if empty
    if db.query(models.User).count() == 0:
        # Comercio Demo
        merchant = models.User(
            email="comercio@ofertapp.com",
            hashed_password=get_password_hash("comercio123"),
            full_name="Pizzería Bella Napoli (Comercio Demo)",
            phone="+5491122334455",
            role="merchant"
        )
        db.add(merchant)

        # Usuario Normal Demo con gustos cargados
        user = models.User(
            email="usuario@ofertapp.com",
            hashed_password=get_password_hash("usuario123"),
            full_name="Juan Pérez (Usuario)",
            phone="+5491199887766",
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Ubicación Demo del usuario (Coordenadas de referencia céntricas)
        user_loc = models.UserLocation(
            user_id=user.id,
            latitude=-34.6037,
            longitude=-58.3816,
            address_label="Centro de la Ciudad",
            fcm_token="demo_token_juan_123"
        )
        db.add(user_loc)

        # Asignar gustos iniciales a Juan (Gastronomía y Tecnología)
        cat_gastro = db.query(models.TasteCategory).filter_by(slug="gastronomia").first()
        cat_tecno = db.query(models.TasteCategory).filter_by(slug="tecnologia").first()

        if cat_gastro:
            pref_gastro = models.UserTastePreference(
                user_id=user.id,
                category_id=cat_gastro.id,
                tags="pizza,artesanal,hamburguesas,cafe,2x1",
                max_distance_km=15.0
            )
            db.add(pref_gastro)

        if cat_tecno:
            pref_tecno = models.UserTastePreference(
                user_id=user.id,
                category_id=cat_tecno.id,
                tags="apple,auriculares,computacion,gamer",
                max_distance_km=25.0
            )
            db.add(pref_tecno)

        # Administrador Demo
        admin = models.User(
            email="admin@ofertapp.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador Global (Ofertapp)",
            phone="+5491100112233",
            role="admin"
        )
        db.add(admin)

        db.commit()

    # 3. Seed System Configurations if empty
    if db.query(models.SystemSetting).count() == 0:
        DEFAULT_SETTINGS = [
            {"key": "default_search_radius_km", "value": "10", "description": "Radio de búsqueda por defecto en el feed (km)", "category": "geo"},
            {"key": "max_search_radius_km", "value": "30", "description": "Radio máximo permitido para filtrar ofertas (km)", "category": "geo"},
            {"key": "default_map_lat", "value": "-34.6037", "description": "Latitud central por defecto en mapa", "category": "geo"},
            {"key": "default_map_lon", "value": "-58.3816", "description": "Longitud central por defecto en mapa", "category": "geo"},
            {"key": "auto_push_notifications", "value": "true", "description": "Habilitar despacho automático de alertas a usuarios afines", "category": "notifications"},
            {"key": "require_merchant_verification", "value": "false", "description": "Requerir verificación manual antes de publicar ofertas", "category": "merchants"},
            {"key": "max_promotions_per_merchant", "value": "20", "description": "Límite de promociones activas por comercio", "category": "merchants"},
            {"key": "allow_user_registration", "value": "true", "description": "Permitir auto-registro de nuevos usuarios y comercios", "category": "general"},
        ]
        for s in DEFAULT_SETTINGS:
            db.add(models.SystemSetting(**s))
        db.commit()
