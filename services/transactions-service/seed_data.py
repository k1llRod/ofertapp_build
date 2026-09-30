from sqlalchemy.orm import Session
import models

INITIAL_CATEGORIES = [
    {"name": "Gastronomía", "slug": "gastronomia", "icon": "🍔", "description": "Restaurantes, cafeterías y comida"},
    {"name": "Tecnología", "slug": "tecnologia", "icon": "💻", "description": "Smartphones, accesorios y computación"},
    {"name": "Moda y Calzado", "slug": "moda", "icon": "👗", "description": "Indumentaria y calzado"},
    {"name": "Entretenimiento", "slug": "entretenimiento", "icon": "🎟️", "description": "Cines, teatro y espectáculos"},
    {"name": "Belleza y Spa", "slug": "belleza", "icon": "💆", "description": "Barberías, estética y masajes"},
    {"name": "Deportes y Fitness", "slug": "deportes", "icon": "⚽", "description": "Gimnasios y artículos deportivos"},
    {"name": "Hogar y Muebles", "slug": "hogar", "icon": "🛋️", "description": "Muebles y decoración"},
    {"name": "Servicios Profesionales", "slug": "servicios", "icon": "🛠️", "description": "Reparaciones y servicios"}
]

DEMO_PROMOTIONS = [
    {
        "merchant_id": 1,
        "merchant_name": "Pizzería Bella Napoli",
        "title": "2x1 en Pizzas Artesanales + Bebida",
        "description": "Disfruta de dos pizzas grandes al horno de leña a elección más una gaseosa de 1.5L. Válido de lunes a jueves.",
        "category_slug": "gastronomia",
        "original_price": 12000.0,
        "discount_percent": 50.0,
        "promo_price": 6000.0,
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600",
        "tags": "pizza,artesanal,2x1,cena,italiana",
        "latitude": -34.6042,
        "longitude": -58.3820,
        "address": "Av. Corrientes 1250, Centro"
    },
    {
        "merchant_id": 1,
        "merchant_name": "TechZone Express",
        "title": "Auriculares Bluetooth Noise Cancelling",
        "description": "Auriculares inalámbricos con cancelación de ruido activa, 30hs de batería y sonido Hi-Res.",
        "category_slug": "tecnologia",
        "original_price": 45000.0,
        "discount_percent": 35.0,
        "promo_price": 29250.0,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
        "tags": "auriculares,bluetooth,audio,apple,gamer",
        "latitude": -34.6015,
        "longitude": -58.3790,
        "address": "Florida 680, Galería Pacífico"
    },
    {
        "merchant_id": 1,
        "merchant_name": "Café de Especialidad Origen",
        "title": "Combo Desayuno: Flat White + Croissant",
        "description": "Comienza tu mañana con un café de grano seleccionado de Colombia y un croissant francés recién horneado.",
        "category_slug": "gastronomia",
        "original_price": 5500.0,
        "discount_percent": 30.0,
        "promo_price": 3850.0,
        "image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600",
        "tags": "cafe,desayuno,croissant,artesanal,merienda",
        "latitude": -34.6060,
        "longitude": -58.3850,
        "address": "Lavalle 840, Centro"
    },
    {
        "merchant_id": 1,
        "merchant_name": "Barber & Co Studio",
        "title": "Corte de Cabello + Perfilado de Barba",
        "description": "Servicio premium con toalla caliente, perfilado con navaja tradicional y peinado con pomada mate.",
        "category_slug": "belleza",
        "original_price": 14000.0,
        "discount_percent": 25.0,
        "promo_price": 10500.0,
        "image_url": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=600",
        "tags": "barberia,corte,barba,estetica",
        "latitude": -34.5980,
        "longitude": -58.3870,
        "address": "Santa Fe 1420, Recoleta"
    },
    {
        "merchant_id": 1,
        "merchant_name": "FitLife Gym & Training",
        "title": "Pase Libre Mensual con 40% OFF",
        "description": "Acceso ilimitado a sala de musculación, clases de funcional, spinning y vestuarios completos.",
        "category_slug": "deportes",
        "original_price": 35000.0,
        "discount_percent": 40.0,
        "promo_price": 21000.0,
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600",
        "tags": "gimnasio,fitness,spinning,musculacion",
        "latitude": -34.6100,
        "longitude": -58.3750,
        "address": "Belgrano 920, San Telmo"
    },
    {
        "merchant_id": 1,
        "merchant_name": "Urban Sneaker House",
        "title": "30% en Zapatillas Urbanas de Colección",
        "description": "Aprovecha liquidación de temporada en calzado urbano de primeras marcas. Todos los talles.",
        "category_slug": "moda",
        "original_price": 85000.0,
        "discount_percent": 30.0,
        "promo_price": 59500.0,
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600",
        "tags": "zapatillas,moda,calzado,urban,ropa",
        "latitude": -34.5950,
        "longitude": -58.3900,
        "address": "Arenales 1800, Barrio Norte"
    }
]

def seed_initial_data(db: Session):
    # 1. Categorías
    if db.query(models.Category).count() == 0:
        for cat in INITIAL_CATEGORIES:
            db.add(models.Category(**cat))
        db.commit()

    # 2. Promociones Demo
    if db.query(models.Promotion).count() == 0:
        for promo in DEMO_PROMOTIONS:
            category = db.query(models.Category).filter_by(slug=promo["category_slug"]).first()
            if not category:
                continue

            new_p = models.Promotion(
                merchant_id=promo["merchant_id"],
                merchant_name=promo["merchant_name"],
                title=promo["title"],
                description=promo["description"],
                category_id=category.id,
                original_price=promo["original_price"],
                discount_percent=promo["discount_percent"],
                promo_price=promo["promo_price"],
                image_url=promo["image_url"],
                tags=promo["tags"],
                latitude=promo["latitude"],
                longitude=promo["longitude"],
                address=promo["address"],
                is_active=True,
                views_count=15
            )
            db.add(new_p)
        db.commit()
