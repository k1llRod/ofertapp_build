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
        "description": "Disfruta de dos pizzas grandes al horno de leña tradicional con fermentación lenta de 48hs. Incluye 2 variedades a elección entre Muzzarella clásica, Napolitana con albahaca fresca de huerta, Fugazzeta rellena o Pepperoni especial, más una bebida de 1.5L. Elaboradas con masa madre, salsa de tomates San Marzano y quesos de primera calidad. Válido tanto para consumo en el salón como para retiro en local.",
        "category_slug": "gastronomia",
        "original_price": 120.0,
        "discount_percent": 50.0,
        "promo_price": 60.0,
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800",
        "gallery": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800,https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800,https://images.unsplash.com/photo-1590947132387-155cc02f3212?w=800",
        "tags": "pizza,artesanal,2x1,cena,italiana",
        "latitude": -34.6042,
        "longitude": -58.3820,
        "address": "Av. Corrientes 1250, Centro"
    },
    {
        "merchant_id": 1,
        "merchant_name": "TechZone Express",
        "title": "Auriculares Bluetooth Noise Cancelling",
        "description": "Auriculares inalámbricos over-ear de alta fidelidad con cancelación activa de ruido híbrida (ANC) de hasta -38dB. Equipados con drivers de 40mm de titanio acústico, Bluetooth 5.3 de ultra baja latencia, micrófono cuádruple con reducción de ruido ambiental (ENC) para llamadas ultra claras y hasta 35 horas continuas de batería con carga rápida USB-C (10 min de carga = 4 horas de reproducción). Incluye estuche rígido protector y cable auxiliar 3.5mm.",
        "category_slug": "tecnologia",
        "original_price": 350.0,
        "discount_percent": 35.0,
        "promo_price": 227.5,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800",
        "gallery": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800,https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800,https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=800",
        "tags": "auriculares,bluetooth,audio,apple,gamer",
        "latitude": -34.6015,
        "longitude": -58.3790,
        "address": "Florida 680, Galería Pacífico"
    },
    {
        "merchant_id": 1,
        "merchant_name": "Café de Especialidad Origen",
        "title": "Combo Desayuno: Flat White + Croissant",
        "description": "Comienza tu día con la mejor experiencia cafetera de la ciudad. Nuestro combo incluye un Flat White doble shot elaborado con granos arábica seleccionados de origen Huila (Colombia), tostados artesanalmente en nuestro local, combinado con leche texturizada a punto óptimo. Acompañado de un croissant francés 100% manteca, horneado en el día con costra crocante y miga aireada. Opciones de leche vegetal disponibles sin cargo.",
        "category_slug": "gastronomia",
        "original_price": 45.0,
        "discount_percent": 30.0,
        "promo_price": 31.5,
        "image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800",
        "gallery": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800,https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800,https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800",
        "tags": "cafe,desayuno,croissant,artesanal,merienda",
        "latitude": -34.6060,
        "longitude": -58.3850,
        "address": "Lavalle 840, Centro"
    },
    {
        "merchant_id": 1,
        "merchant_name": "Barber & Co Studio",
        "title": "Corte de Cabello + Perfilado de Barba",
        "description": "Servicio premium completo de barbería clásica y estilismo masculino. Incluye diagnóstico capilar personalizado, corte degradado o clásico a elección con tijera y navaja, lavado relajante con shampoo revitalizante, toalla caliente aromática con aceites esenciales, perfilado milimétrico de barba con navaja de filo descartable y peinado con pomada mate fijadora de acabado natural. Duración: 45 minutos.",
        "category_slug": "belleza",
        "original_price": 70.0,
        "discount_percent": 25.0,
        "promo_price": 52.5,
        "image_url": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800",
        "gallery": "https://images.unsplash.com/photo-1621605815971-fbc98d665033?w=800,https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=800,https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=800",
        "tags": "barberia,corte,barba,estetica",
        "latitude": -34.5980,
        "longitude": -58.3870,
        "address": "Santa Fe 1420, Recoleta"
    },
    {
        "merchant_id": 1,
        "merchant_name": "FitLife Gym & Training",
        "title": "Pase Libre Mensual con 40% OFF",
        "description": "Acceso ilimitado a todas nuestras áreas de entrenamiento durante 30 días continuos. Incluye sala de musculación equipada con máquinas biomecánicas de última generación, peso libre, zona cardio completa, clases grupales guiadas por instructores certificados (Cross-training, Spinning indoor, Funcional, Yoga y Pilates), vestuarios con duchas y lockers privados, más evaluación inicial con rutina personalizada en nuestra app móvil.",
        "category_slug": "deportes",
        "original_price": 250.0,
        "discount_percent": 40.0,
        "promo_price": 150.0,
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
        "gallery": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800,https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800,https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800",
        "tags": "gimnasio,fitness,spinning,musculacion",
        "latitude": -34.6100,
        "longitude": -58.3750,
        "address": "Belgrano 920, San Telmo"
    },
    {
        "merchant_id": 1,
        "merchant_name": "Urban Sneaker House",
        "title": "30% en Zapatillas Urbanas de Colección",
        "description": "Liquidación exclusiva de temporada en calzado urbano de estilo retro y streetwear. Modelos de primera línea con capellada de cuero vacuno y gamuza premium, suela de caucho vulcanizado de alta durabilidad y plantilla acolchada ergonómica con tecnología memory foam para máximo confort durante todo el día. Gran variedad de colores y todos los talles disponibles del 37 al 45.",
        "category_slug": "moda",
        "original_price": 450.0,
        "discount_percent": 30.0,
        "promo_price": 315.0,
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800",
        "gallery": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800,https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800,https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?w=800",
        "tags": "zapatillas,moda,calzado,urban,ropa",
        "latitude": -34.5950,
        "longitude": -58.3900,
        "address": "Arenales 1800, Barrio Norte"
    }
]

INITIAL_TRANSACTIONS = [
    {
        "transaction_code": "TXN-DEMO-0001",
        "service_name": "Gastronomía",
        "product_name": "2x1 en Pizzas Artesanales + Bebida",
        "user_id": 1,
        "user_name": "Juan Perez",
        "user_email": "usuario@ofertapp.com",
        "amount": 6000.0,
        "quantity": 1,
        "payment_method": "credit_card",
        "status": "completed",
        "description": "Compra de promoción de pizza artesanal con entrega a domicilio"
    },
    {
        "transaction_code": "TXN-DEMO-0002",
        "service_name": "Tecnología",
        "product_name": "Auriculares Bluetooth Noise Cancelling",
        "user_id": 1,
        "user_name": "Juan Perez",
        "user_email": "usuario@ofertapp.com",
        "amount": 29250.0,
        "quantity": 1,
        "payment_method": "mercadopago",
        "status": "completed",
        "description": "Adquisición con descuento de temporada"
    },
    {
        "transaction_code": "TXN-DEMO-0003",
        "service_name": "Belleza y Spa",
        "product_name": "Corte de Cabello + Perfilado de Barba",
        "user_id": 2,
        "user_name": "Carlos Gomez",
        "user_email": "carlos@ofertapp.com",
        "amount": 10500.0,
        "quantity": 1,
        "payment_method": "transfer",
        "status": "completed",
        "description": "Reserva de servicio de barbería con canje QR"
    }
]

def seed_initial_data(db: Session):
    # 1. Categorías
    if db.query(models.Category).count() == 0:
        for cat in INITIAL_CATEGORIES:
            db.add(models.Category(**cat))
        db.commit()

    # 2. Promociones Demo
    existing_count = db.query(models.Promotion).count()
    if existing_count == 0:
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
                gallery=promo.get("gallery", ""),
                tags=promo["tags"],
                latitude=promo["latitude"],
                longitude=promo["longitude"],
                address=promo["address"],
                is_active=True,
                views_count=15
            )
            db.add(new_p)
        db.commit()
    else:
        # Actualizar descripciones ricas, galerías de fotos y precios en bolivianos en promociones demo existentes
        for promo in DEMO_PROMOTIONS:
            p = db.query(models.Promotion).filter(models.Promotion.title == promo["title"]).first()
            if p:
                p.description = promo["description"]
                p.image_url = promo["image_url"]
                p.gallery = promo.get("gallery", "")
                p.original_price = promo["original_price"]
                p.discount_percent = promo["discount_percent"]
                p.promo_price = promo["promo_price"]
        db.commit()

    # 3. Transacciones Iniciales
    if db.query(models.Transaction).count() == 0:
        for tx in INITIAL_TRANSACTIONS:
            db.add(models.Transaction(**tx))
        db.commit()
