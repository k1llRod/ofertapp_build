import os
import urllib.parse
import httpx
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

from config import settings

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API Gateway de Ofertapp: Punto de entrada único, routing dinámico, verificación de seguridad y CORS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def forward_request(target_url: str, request: Request) -> Response:
    """Reenvía la petición HTTP entrante al microservicio de destino"""
    # Copiar headers y filtrar/codificar valores no-ASCII para evitar fallos en httpx
    headers = {}
    for k, v in request.headers.items():
        if k.lower() in ("host", "content-length"):
            continue
        try:
            v.encode("ascii")
            headers[k] = v
        except UnicodeEncodeError:
            headers[k] = urllib.parse.quote(v)

    # Validar JWT opcionalmente para inyectar headers X-User-Id y X-User-Role
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            role = payload.get("role")
            email = payload.get("email")
            name = payload.get("name")
            if user_id:
                headers["x-user-id"] = str(user_id)
            if role:
                headers["x-user-role"] = str(role)
            if email:
                headers["x-user-email"] = str(email)
            if name:
                headers["x-user-name"] = urllib.parse.quote(str(name))
        except JWTError:
            pass  # Si el token es inválido, el microservicio downstream devolverá 401 si la ruta lo requiere

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body
            )
            # Filtrar headers hop-by-hop y de longitud/compresión para que Starlette los calcule adecuadamente
            excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
            filtered_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded_headers}
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=filtered_headers
            )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"El microservicio de destino ({target_url}) no está disponible en este momento."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el API Gateway: {str(e)}"
        )

# --- RUTAS DE PROXY REVERSO ---

# 1. Auth, Gustos y Admin Auth (auth-service)
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Auth"])
async def proxy_auth(path: str, request: Request):
    target = f"{settings.AUTH_SERVICE_URL}/auth/{path}"
    return await forward_request(target, request)

@app.api_route("/api/v1/tastes/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Tastes"])
async def proxy_tastes(path: str, request: Request):
    target = f"{settings.AUTH_SERVICE_URL}/tastes/{path}"
    return await forward_request(target, request)

@app.api_route("/api/v1/location/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Location"])
async def proxy_location(path: str, request: Request):
    target = f"{settings.AUTH_SERVICE_URL}/location/{path}"
    return await forward_request(target, request)

# Rutas de administración para transacciones / catálogo
@app.api_route("/api/v1/admin/promotions", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Admin - Promotions"])
async def proxy_admin_promotions(request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/admin/promotions"
    return await forward_request(target, request)

@app.api_route("/api/v1/admin/orders", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Admin - Orders"])
async def proxy_admin_orders(request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/admin/orders"
    return await forward_request(target, request)

@app.api_route("/api/v1/admin/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Admin"])
async def proxy_admin(path: str, request: Request):
    target = f"{settings.AUTH_SERVICE_URL}/admin/{path}"
    return await forward_request(target, request)

# 2. Transacciones, Promociones y Categorías (transactions-service)
@app.api_route("/api/v1/promotions", methods=["GET", "POST"], tags=["Promotions"])
async def proxy_promotions_root(request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/promotions"
    return await forward_request(target, request)

@app.api_route("/api/v1/promotions/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Promotions"])
async def proxy_promotions(path: str, request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/promotions/{path}"
    return await forward_request(target, request)

@app.api_route("/api/v1/merchants/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Merchant Portal"])
async def proxy_merchants(path: str, request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/merchants/{path}"
    return await forward_request(target, request)

@app.api_route("/api/v1/categories", methods=["GET", "POST"], tags=["Categories"])
async def proxy_categories_root(request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/categories"
    return await forward_request(target, request)

@app.api_route("/api/v1/categories/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Categories"])
async def proxy_categories(path: str, request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/categories/{path}"
    return await forward_request(target, request)

# 2.1 Órdenes y Pagos en Línea (transactions-service)
@app.api_route("/api/v1/orders", methods=["GET", "POST"], tags=["Orders & Payments"])
async def proxy_orders_root(request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/orders"
    return await forward_request(target, request)

@app.api_route("/api/v1/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Orders & Payments"])
async def proxy_orders(path: str, request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/orders/{path}"
    return await forward_request(target, request)

# 2.2 Transacciones Directas (transactions-service)
@app.api_route("/api/v1/transactions", methods=["GET", "POST"], tags=["Transactions"])
async def proxy_transactions_root(request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/transactions"
    return await forward_request(target, request)

@app.api_route("/api/v1/transactions/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Transactions"])
async def proxy_transactions(path: str, request: Request):
    target = f"{settings.TRANSACTIONS_SERVICE_URL}/transactions/{path}"
    return await forward_request(target, request)

# 3. Notificaciones y Alertas (notifications-services)
@app.api_route("/api/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Notifications"])
async def proxy_notifications(path: str, request: Request):
    target = f"{settings.NOTIFICATIONS_SERVICE_URL}/notifications/{path}"
    return await forward_request(target, request)

# 4. Reportes Automáticos (reports-service)
@app.api_route("/api/v1/reports/{path:path}", methods=["GET", "POST"], tags=["Reports"])
async def proxy_reports(path: str, request: Request):
    target = f"{settings.REPORTS_SERVICE_URL}/reports/{path}"
    return await forward_request(target, request)

# --- HEALTH & STATUS ---

@app.get("/health", tags=["Health"])
async def health_check():
    """Comprueba el estado del API Gateway y la conectividad con los 4 microservicios"""
    services_status = {}
    service_urls = {
        "auth-service": f"{settings.AUTH_SERVICE_URL}/health",
        "transactions-service": f"{settings.TRANSACTIONS_SERVICE_URL}/health",
        "notifications-services": f"{settings.NOTIFICATIONS_SERVICE_URL}/health",
        "reports-service": f"{settings.REPORTS_SERVICE_URL}/health",
    }

    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in service_urls.items():
            try:
                res = await client.get(url)
                services_status[name] = "ok" if res.status_code == 200 else f"error ({res.status_code})"
            except Exception:
                services_status[name] = "offline / unreachable"

    all_ok = all(v == "ok" for v in services_status.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "gateway": "online",
        "services": services_status
    }

# --- WEB VISUALIZER ---

@app.get("/app", response_class=HTMLResponse, tags=["Web"])
async def serve_app():
    index_file = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return "App visualizer not found"

@app.get("/", response_class=HTMLResponse, tags=["Web"])
async def root():
    return '<script>window.location.href="/app";</script>'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
