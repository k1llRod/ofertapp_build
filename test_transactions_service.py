import sys
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Asegurar codificación utf-8 para salida en terminal Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, 'services/transactions-service')
import models
import schemas
import seed_data
from database import Base, get_db
import main

from sqlalchemy.pool import StaticPool

# Base de datos de prueba aislada en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

main.app.dependency_overrides[get_db] = override_get_db

class TestTransactionsServiceScaffold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        seed_data.seed_initial_data(db)
        db.close()
        cls.client = TestClient(main.app)

    def test_01_health_check(self):
        """Verifica que el endpoint /health responda correctamente"""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "transactions-service")

    def test_02_initial_transactions_seeded(self):
        """Verifica que las transacciones iniciales hayan sido cargadas por seed_data"""
        res = self.client.get("/transactions")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 3)
        codes = [t["transaction_code"] for t in data]
        self.assertIn("TXN-DEMO-0001", codes)

    def test_03_create_transaction_success(self):
        """Verifica la creación de una transacción con Servicio, Producto y Usuario"""
        payload = {
            "service": "Gastronomía / Cafetería",
            "product": "Combo Desayuno Flat White + Croissant",
            "user_id": 42,
            "user_name": "Ana Rodriguez",
            "user_email": "ana@ofertapp.com",
            "amount": 3850.0,
            "quantity": 2,
            "payment_method": "credit_card",
            "status": "completed",
            "description": "Desayuno para dos personas en sucursal"
        }
        res = self.client.post("/transactions", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        
        # Validar campos requeridos y estructura
        self.assertIn("id", data)
        self.assertIn("transaction_code", data)
        self.assertEqual(data["service"], "Gastronomía / Cafetería")
        self.assertEqual(data["product"], "Combo Desayuno Flat White + Croissant")
        self.assertEqual(data["user_id"], 42)
        self.assertEqual(data["user_name"], "Ana Rodriguez")
        self.assertEqual(data["user_email"], "ana@ofertapp.com")
        self.assertEqual(data["amount"], 3850.0)
        self.assertEqual(data["quantity"], 2)
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["payment_method"], "credit_card")
        self.assertTrue(data["transaction_code"].startswith("TXN-"))

    def test_04_create_transaction_with_aliases(self):
        """Verifica la flexibilidad en nombres de atributos (service_name, product_name, user)"""
        payload = {
            "service_name": "Fitness & Salud",
            "product_name": "Pase Libre Mensual",
            "user": "Carlos Giménez",
            "user_id": 88,
            "monto": 21000.0
        }
        res = self.client.post("/transactions", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["service"], "Fitness & Salud")
        self.assertEqual(data["product"], "Pase Libre Mensual")
        self.assertEqual(data["amount"], 21000.0)
        self.assertEqual(data["user_id"], 88)

    def test_05_create_transaction_missing_service_fails(self):
        """Verifica que falle con 400 si falta el servicio"""
        payload = {
            "product": "Zapatillas Urbanas",
            "user_id": 5
        }
        res = self.client.post("/transactions", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("servicio", res.json()["detail"].lower())

    def test_06_create_transaction_missing_product_fails(self):
        """Verifica que falle con 400 si falta el producto"""
        payload = {
            "service": "Moda y Calzado",
            "user_id": 5
        }
        res = self.client.post("/transactions", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("producto", res.json()["detail"].lower())

    def test_07_list_transactions_with_filters(self):
        """Verifica el listado con filtros por usuario, servicio y producto"""
        # Filtrar por usuario 42
        res_u = self.client.get("/transactions?user_id=42")
        self.assertEqual(res_u.status_code, 200)
        for t in res_u.json():
            self.assertEqual(t["user_id"], 42)

        # Filtrar por servicio
        res_s = self.client.get("/transactions?service=Fitness")
        self.assertEqual(res_s.status_code, 200)
        self.assertGreaterEqual(len(res_s.json()), 1)
        self.assertIn("Fitness", res_s.json()[0]["service"])

        # Filtrar por producto
        res_p = self.client.get("/transactions?product=Croissant")
        self.assertEqual(res_p.status_code, 200)
        self.assertGreaterEqual(len(res_p.json()), 1)

    def test_08_get_transaction_by_id(self):
        """Verifica la obtención de una transacción individual por ID"""
        # Crear transacción
        payload = {
            "service": "Entretenimiento",
            "product": "2 Entradas de Cine IMAX",
            "user_id": 99,
            "amount": 8000.0
        }
        res_create = self.client.post("/transactions", json=payload)
        tx_id = res_create.json()["id"]

        # Consultar por ID
        res_get = self.client.get(f"/transactions/{tx_id}")
        self.assertEqual(res_get.status_code, 200)
        data = res_get.json()
        self.assertEqual(data["id"], tx_id)
        self.assertEqual(data["product"], "2 Entradas de Cine IMAX")

    def test_09_get_transaction_by_id_not_found(self):
        """Verifica el retorno de 404 para ID inexistente"""
        res = self.client.get("/transactions/999999")
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
