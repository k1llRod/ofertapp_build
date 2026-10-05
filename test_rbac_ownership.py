import httpx
import sys

# Asegurar codificación utf-8 para salida en terminal Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

API_BASE = "http://127.0.0.1:8000/api/v1"

def print_result(test_name: str, passed: bool, detail: str = ""):
    icon = "✅" if passed else "❌"
    print(f"{icon} [{test_name}]: {detail}")
    if not passed:
        sys.exit(1)

def run_tests():
    print("\n=======================================================")
    print(">> INICIANDO BATERÍA DE PRUEBAS RBAC Y CONTROL DE PROPIEDAD")
    print("=======================================================\n")

    client = httpx.Client(timeout=10.0)

    # 1. Login Admin
    admin_login = client.post(f"{API_BASE}/auth/login", json={"email": "admin@ofertapp.com", "password": "admin123"})
    assert admin_login.status_code == 200, f"Error login admin: {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print_result("1. Autenticación Administrador", True, f"Admin token generado. Rol: {admin_login.json()['role']}")

    # 2. Login Merchant 1 (comercio@ofertapp.com)
    m1_login = client.post(f"{API_BASE}/auth/login", json={"email": "comercio@ofertapp.com", "password": "comercio123"})
    assert m1_login.status_code == 200, f"Error login merchant: {m1_login.text}"
    m1_data = m1_login.json()
    m1_id = m1_data["user_id"]
    m1_token = m1_data["access_token"]
    m1_headers = {"Authorization": f"Bearer {m1_token}"}
    print_result("2. Autenticación Comercio 1", True, f"Merchant 1 (ID: {m1_id}, Email: {m1_data['email']})")

    # 3. Create or login Merchant 2 (comercio2@ofertapp.com)
    m2_reg = client.post(f"{API_BASE}/auth/register", json={
        "email": "comercio2@ofertapp.com",
        "password": "password123",
        "full_name": "Hamburguesería Vikinga",
        "role": "merchant"
    })
    m2_login = client.post(f"{API_BASE}/auth/login", json={"email": "comercio2@ofertapp.com", "password": "password123"})
    assert m2_login.status_code == 200, f"Error login merchant 2: {m2_login.text}"
    m2_data = m2_login.json()
    m2_id = m2_data["user_id"]
    m2_token = m2_data["access_token"]
    m2_headers = {"Authorization": f"Bearer {m2_token}"}
    print_result("3. Autenticación Comercio 2", True, f"Merchant 2 (ID: {m2_id}, Email: {m2_data['email']})")

    # 4. Login Usuario Normal
    u_login = client.post(f"{API_BASE}/auth/login", json={"email": "usuario@ofertapp.com", "password": "usuario123"})
    assert u_login.status_code == 200, f"Error login user: {u_login.text}"
    u_token = u_login.json()["access_token"]
    u_headers = {"Authorization": f"Bearer {u_token}"}
    print_result("4. Autenticación Consumidor", True, f"Usuario (Rol: {u_login.json()['role']})")

    # 5. TEST: Usuario normal no puede crear promociones
    res = client.post(f"{API_BASE}/promotions", headers=u_headers, json={
        "title": "Oferta no autorizada",
        "description": "Desc",
        "category_id": 1,
        "original_price": 100,
        "discount_percent": 20,
        "latitude": -34.6,
        "longitude": -58.38,
        "address": "Calle 1"
    })
    print_result("5. Consumidor bloqueado de crear promociones", res.status_code == 403, f"Status code: {res.status_code} ({res.text})")

    # 6. TEST: Comercio 1 y 2 bloqueados de endpoints de Administración
    res_users = client.get(f"{API_BASE}/admin/users", headers=m1_headers)
    res_cats = client.post(f"{API_BASE}/admin/categories", headers=m1_headers, json={"name": "Test", "slug": "test", "icon": "⚡"})
    res_settings = client.put(f"{API_BASE}/admin/settings/max_distance", headers=m1_headers, json={"key": "max_distance", "value": "100"})
    blocked_admin = (res_users.status_code == 403) and (res_cats.status_code == 403) and (res_settings.status_code == 403)
    print_result("6. Comercios bloqueados de endpoints de Admin (/admin/users, /admin/categories, /admin/settings)", blocked_admin, f"Statuses: users={res_users.status_code}, cats={res_cats.status_code}, settings={res_settings.status_code}")

    # 7. TEST: Comercio 1 crea una promoción para sí mismo
    promo_m1 = client.post(f"{API_BASE}/promotions", headers=m1_headers, json={
        "title": "Pizza Especial Bella Napoli",
        "description": "Muzzarella con jamón y morrones",
        "category_id": 1,
        "original_price": 100.0,
        "discount_percent": 30.0,
        "latitude": -34.6037,
        "longitude": -58.3816,
        "address": "Av. Corrientes 1250"
    })
    assert promo_m1.status_code in (200, 201), f"Error creando promo m1: {promo_m1.text}"
    p1_data = promo_m1.json()
    p1_id = p1_data["id"]
    print_result("7. Comercio 1 crea su propia promoción", p1_data["merchant_id"] == m1_id, f"Promo ID: {p1_id}, Merchant ID asignado: {p1_data['merchant_id']}")

    # 8. TEST: Comercio 2 crea una promoción para sí mismo
    promo_m2 = client.post(f"{API_BASE}/promotions", headers=m2_headers, json={
        "title": "Combo Viking Burger Doble",
        "description": "Doble carne smash y queso cheddar",
        "category_id": 1,
        "original_price": 80.0,
        "discount_percent": 25.0,
        "latitude": -34.6050,
        "longitude": -58.3850,
        "address": "Av. Santa Fe 2200"
    })
    assert promo_m2.status_code in (200, 201), f"Error creando promo m2: {promo_m2.text}"
    p2_data = promo_m2.json()
    p2_id = p2_data["id"]
    print_result("8. Comercio 2 crea su propia promoción", p2_data["merchant_id"] == m2_id, f"Promo ID: {p2_id}, Merchant ID asignado: {p2_data['merchant_id']}")

    # 9. TEST AISLAMIENTO: Comercio 1 NO PUEDE ver las promociones de Comercio 2
    res_spy_promos = client.get(f"{API_BASE}/merchants/{m2_id}/promotions", headers=m1_headers)
    print_result("9. Comercio 1 bloqueado de consultar promociones de Comercio 2", res_spy_promos.status_code == 403, f"Status code: {res_spy_promos.status_code} ({res_spy_promos.text})")

    # 10. TEST AISLAMIENTO: Comercio 1 NO PUEDE ver las órdenes/ventas de Comercio 2
    res_spy_orders = client.get(f"{API_BASE}/merchants/{m2_id}/orders", headers=m1_headers)
    print_result("10. Comercio 1 bloqueado de consultar ventas/órdenes de Comercio 2", res_spy_orders.status_code == 403, f"Status code: {res_spy_orders.status_code} ({res_spy_orders.text})")

    # 11. TEST CONTROL DE PROPIEDAD: Comercio 1 NO PUEDE modificar la promoción de Comercio 2
    res_hack_edit = client.put(f"{API_BASE}/promotions/{p2_id}", headers=m1_headers, json={
        "title": "Hackeado por Comercio 1"
    })
    print_result("11. Comercio 1 bloqueado de MODIFICAR oferta de Comercio 2", res_hack_edit.status_code == 403, f"Status code: {res_hack_edit.status_code} ({res_hack_edit.text})")

    # 12. TEST CONTROL DE PROPIEDAD: Comercio 1 NO PUEDE pausar/activar la promoción de Comercio 2
    res_hack_toggle = client.patch(f"{API_BASE}/promotions/{p2_id}/toggle-status", headers=m1_headers)
    print_result("12. Comercio 1 bloqueado de PAUSAR oferta de Comercio 2", res_hack_toggle.status_code == 403, f"Status code: {res_hack_toggle.status_code} ({res_hack_toggle.text})")

    # 13. TEST CONTROL DE PROPIEDAD: Comercio 1 NO PUEDE eliminar la promoción de Comercio 2
    res_hack_del = client.delete(f"{API_BASE}/promotions/{p2_id}", headers=m1_headers)
    print_result("13. Comercio 1 bloqueado de ELIMINAR oferta de Comercio 2", res_hack_del.status_code == 403, f"Status code: {res_hack_del.status_code} ({res_hack_del.text})")

    # 14. TEST PERMISOS PROPIOS: Comercio 1 SÍ PUEDE modificar su propia promoción
    res_own_edit = client.put(f"{API_BASE}/promotions/{p1_id}", headers=m1_headers, json={
        "title": "Pizza Especial Bella Napoli (Edición Limitada)",
        "discount_percent": 35.0
    })
    print_result("14. Comercio 1 modifica satisfactoriamente su propia oferta", res_own_edit.status_code == 200, f"Nuevo título: {res_own_edit.json().get('title')}")

    # 15. TEST PERMISOS PROPIOS: Comercio 1 SÍ PUEDE pausar y activar su propia oferta
    res_own_toggle = client.patch(f"{API_BASE}/promotions/{p1_id}/toggle-status", headers=m1_headers)
    print_result("15. Comercio 1 pausa/activa satisfactoriamente su propia oferta", res_own_toggle.status_code == 200, f"is_active: {res_own_toggle.json().get('is_active')}")

    # 16. TEST ADMINISTRADOR ACCESO TOTAL: Admin puede consultar todas las promociones globales
    res_adm_promos = client.get(f"{API_BASE}/admin/promotions", headers=admin_headers)
    print_result("16. Administrador accede al listado global de todas las ofertas", res_adm_promos.status_code == 200, f"Total ofertas obtenidas: {len(res_adm_promos.json())}")

    # 17. TEST ADMINISTRADOR ACCESO TOTAL: Admin puede modificar la oferta de Comercio 2
    res_adm_edit = client.put(f"{API_BASE}/promotions/{p2_id}", headers=admin_headers, json={
        "title": "Combo Viking Burger (Modificado por Administrador)"
    })
    print_result("17. Administrador modifica oferta de Comercio 2", res_adm_edit.status_code == 200, f"Título actualizado: {res_adm_edit.json().get('title')}")

    # 18. TEST ADMINISTRADOR ACCESO TOTAL: Admin puede crear una categoría nueva
    res_adm_cat = client.post(f"{API_BASE}/admin/categories", headers=admin_headers, json={
        "name": "Mascotas y Veterinaria",
        "slug": "mascotas",
        "icon": "🐾"
    })
    print_result("18. Administrador crea nueva categoría en el catálogo", res_adm_cat.status_code in (200, 201), f"Categoría creada: {res_adm_cat.json().get('name')}")

    # 19. TEST ADMINISTRADOR ACCESO TOTAL: Admin puede eliminar la oferta de Comercio 2
    res_adm_del = client.delete(f"{API_BASE}/promotions/{p2_id}", headers=admin_headers)
    print_result("19. Administrador elimina oferta de Comercio 2", res_adm_del.status_code == 200, f"Status code: {res_adm_del.status_code}")

    # 20. TEST PERMISOS PROPIOS: Comercio 1 SÍ PUEDE eliminar su propia oferta
    res_own_del = client.delete(f"{API_BASE}/promotions/{p1_id}", headers=m1_headers)
    print_result("20. Comercio 1 elimina satisfactoriamente su propia oferta", res_own_del.status_code == 200, f"Status code: {res_own_del.status_code}")

    print("\n=======================================================")
    print("🎉 TODAS LAS 20 PRUEBAS DE RBAC Y PROPIEDAD PASARON AL 100%")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
