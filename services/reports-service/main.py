from typing import List, Optional
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Servicio de reportes automáticos y métricas de promociones, gustos y demanda urbana",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "reports-service"}

@app.get("/reports/dashboard-summary", tags=["Reports"])
async def get_dashboard_summary():
    """Genera un reporte consolidado de actividad, vistas y promociones activas en la ciudad"""
    promos = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.TRANSACTIONS_SERVICE_URL}/promotions/feed")
            if resp.status_code == 200:
                promos = resp.json().get("items", [])
    except Exception as e:
        print(f"[REPORTS WARNING] No se pudo obtener promociones: {e}")

    total_promos = len(promos)
    total_views = sum(p.get("views_count", 0) for p in promos)
    avg_discount = (sum(p.get("discount_percent", 0) for p in promos) / total_promos) if total_promos > 0 else 0.0

    category_counts = {}
    for p in promos:
        cat = p.get("category_name", "Otras")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    top_promos = sorted(promos, key=lambda x: x.get("views_count", 0), reverse=True)[:5]

    return {
        "status": "success",
        "generated_at": "2026-09-25T12:00:00Z",
        "kpis": {
            "total_active_promotions": total_promos,
            "total_promotions_views": total_views,
            "average_discount_percentage": round(avg_discount, 1),
            "estimated_city_savings_currency": "ARS"
        },
        "promotions_by_category": category_counts,
        "top_viewed_promotions": [
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "merchant_name": p.get("merchant_name"),
                "views": p.get("views_count", 0),
                "discount": f"{p.get('discount_percent')}% OFF"
            }
            for p in top_promos
        ]
    }

@app.get("/reports/merchant/{merchant_id}", tags=["Reports"])
async def get_merchant_report(merchant_id: int):
    """Genera un reporte individual de efectividad para un comercio específico"""
    promos = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.TRANSACTIONS_SERVICE_URL}/promotions/feed")
            if resp.status_code == 200:
                all_promos = resp.json().get("items", [])
                promos = [p for p in all_promos if p.get("merchant_id") == merchant_id]
    except Exception as e:
        print(f"[REPORTS WARNING] {e}")

    total_views = sum(p.get("views_count", 0) for p in promos)
    return {
        "merchant_id": merchant_id,
        "total_promotions_published": len(promos),
        "total_interactions_views": total_views,
        "conversion_index_estimate": f"{round(total_views * 0.12, 1)} clientes potenciales alcanzados",
        "promotions": [
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "discount": p.get("discount_percent"),
                "views": p.get("views_count", 0)
            }
            for p in promos
        ]
    }

@app.get("/reports/zone-demand", tags=["Reports"])
def get_zone_demand():
    """Reporte de gustos y demanda de ofertas por zona de la ciudad"""
    return {
        "zones": [
            {
                "zone_name": "Zona Centro / Microcentro",
                "top_tastes": ["Gastronomía (Almuerzos, Café)", "Tecnología"],
                "active_offers_density": "Alta",
                "average_user_search_radius_km": 3.5
            },
            {
                "zone_name": "Zona Norte / Recoleta / Palermo",
                "top_tastes": ["Gastronomía (Cenas, Bares)", "Moda y Calzado", "Belleza y Spa"],
                "active_offers_density": "Media-Alta",
                "average_user_search_radius_km": 5.0
            },
            {
                "zone_name": "Zona Sur / San Telmo",
                "top_tastes": ["Deportes y Fitness", "Entretenimiento", "Gastronomía"],
                "active_offers_density": "Media",
                "average_user_search_radius_km": 6.5
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
