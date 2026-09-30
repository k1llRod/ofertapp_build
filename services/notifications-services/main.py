from typing import List, Optional
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database import engine, Base, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Servicio de alertas y notificaciones push geolocalizadas según gustos del usuario",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_distance(distance_km: float) -> str:
    if distance_km < 1.0:
        return f"{int(distance_km * 1000)} m"
    return f"{distance_km:.1f} km"

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        # Semilla de notificación demo para el usuario 2 si está vacío
        if db.query(models.Notification).count() == 0:
            demo_notif = models.Notification(
                user_id=2,  # Juan Pérez (Usuario demo)
                promotion_id=1,
                title="🍕 ¡Nueva oferta de tu interés: 50% OFF!",
                message="Pizzería Bella Napoli publicó '2x1 en Pizzas Artesanales + Bebida' a solo 350 m de tu ubicación. ¡Coincide con tus gustos de Gastronomía!",
                category_name="Gastronomía",
                distance_km=0.35,
                discount_percent=50.0,
                is_read=False
            )
            db.add(demo_notif)
            db.commit()
    finally:
        db.close()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "notifications-services"}

@app.post("/events/promotion-created", tags=["Events"])
async def handle_promotion_created(event: schemas.PromotionCreatedEvent, db: Session = Depends(get_db)):
    """
    Consumidor de evento: Cuando se registra una nueva oferta,
    busca en auth-service a los usuarios que tengan gustos afines y se encuentren cerca,
    y genera alertas push / in-app personalizadas.
    """
    matched_users = []
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(
                f"{settings.AUTH_SERVICE_URL}/internal/match-audience",
                json={
                    "category_id": event.category_id,
                    "tags": event.tags,
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "max_radius_km": 15.0
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                matched_users = data.get("matched_users", [])
    except Exception as e:
        print(f"[NOTIF ERROR] Error al consultar usuarios afines en auth-service: {e}")

    alerts_created = 0
    for u in matched_users:
        user_id = u["user_id"]
        dist = u.get("distance_km", 0.0)
        dist_str = format_distance(dist)
        reason = u.get("matched_reason", "Afinidad con tus gustos")

        notif = models.Notification(
            user_id=user_id,
            promotion_id=event.promotion_id,
            title=f"🏷️ ¡Nueva oferta: {int(event.discount_percent)}% OFF en {event.category_name}!",
            message=f"{event.merchant_name} publicó '{event.title}' a solo {dist_str} de ti en {event.address}. ({reason})",
            category_name=event.category_name,
            distance_km=dist,
            discount_percent=event.discount_percent,
            is_read=False
        )
        db.add(notif)
        alerts_created += 1

        # Simulación de envío Push vía FCM
        print(f"[PUSH DISPATCH] Enviando notificación a {u['full_name']} (token: {u.get('fcm_token')}): {notif.title}")

    db.commit()
    return {
        "status": "success",
        "promotion_id": event.promotion_id,
        "matched_audience_count": len(matched_users),
        "alerts_dispatched": alerts_created
    }

@app.get("/notifications/user/{user_id}", response_model=schemas.NotificationListResponse, tags=["Notifications"])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial de notificaciones y alertas de un usuario"""
    notifs = db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).all()

    unread_count = sum(1 for n in notifs if not n.is_read)

    items = [
        schemas.NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            promotion_id=n.promotion_id,
            title=n.title,
            message=n.message,
            category_name=n.category_name,
            distance_km=n.distance_km,
            discount_percent=n.discount_percent,
            is_read=n.is_read,
            created_at=str(n.created_at)
        )
        for n in notifs
    ]

    return schemas.NotificationListResponse(
        total=len(items),
        unread_count=unread_count,
        items=items
    )

@app.put("/notifications/{notification_id}/read", tags=["Notifications"])
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    """Marca una alerta individual como leída"""
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notif.is_read = True
    db.commit()
    return {"status": "ok", "message": "Notificación marcada como leída"}

@app.put("/notifications/user/{user_id}/read-all", tags=["Notifications"])
def mark_all_as_read(user_id: int, db: Session = Depends(get_db)):
    """Marca todas las notificaciones de un usuario como leídas"""
    db.query(models.Notification).filter(models.Notification.user_id == user_id).update({"is_read": True})
    db.commit()
    return {"status": "ok", "message": "Todas las notificaciones fueron marcadas como leídas"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
