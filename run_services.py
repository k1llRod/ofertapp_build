import sys
import os
import time
import subprocess

# Asegurar codificación utf-8 para salida en terminal Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SERVICES = [
    {
        "name": "Auth Service",
        "cwd": os.path.join("services", "auth-service"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"],
        "port": 8001,
        "env": {"DATABASE_URL": "sqlite:///./auth.db", "PORT": "8001"}
    },
    {
        "name": "Transactions Service",
        "cwd": os.path.join("services", "transactions-service"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002"],
        "port": 8002,
        "env": {"DATABASE_URL": "sqlite:///./transactions.db", "PORT": "8002", "AUTH_SERVICE_URL": "http://127.0.0.1:8001", "NOTIFICATIONS_SERVICE_URL": "http://127.0.0.1:8003"}
    },
    {
        "name": "Notifications Service",
        "cwd": os.path.join("services", "notifications-services"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8003"],
        "port": 8003,
        "env": {"DATABASE_URL": "sqlite:///./notifications.db", "PORT": "8003", "AUTH_SERVICE_URL": "http://127.0.0.1:8001"}
    },
    {
        "name": "Reports Service",
        "cwd": os.path.join("services", "reports-service"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8004"],
        "port": 8004,
        "env": {"PORT": "8004", "TRANSACTIONS_SERVICE_URL": "http://127.0.0.1:8002"}
    },
    {
        "name": "API Gateway",
        "cwd": "api-gateway",
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        "port": 8000,
        "env": {
            "PORT": "8000",
            "AUTH_SERVICE_URL": "http://127.0.0.1:8001",
            "TRANSACTIONS_SERVICE_URL": "http://127.0.0.1:8002",
            "NOTIFICATIONS_SERVICE_URL": "http://127.0.0.1:8003",
            "REPORTS_SERVICE_URL": "http://127.0.0.1:8004"
        }
    }
]

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processes = []

    print("==================================================")
    print(">> INICIANDO MICROSERVICIOS DE OFERTAPP (LOCAL)...")
    print("==================================================")

    for s in SERVICES:
        full_cwd = os.path.join(base_dir, s["cwd"])
        env = os.environ.copy()
        env.update(s.get("env", {}))

        p = subprocess.Popen(
            s["cmd"],
            cwd=full_cwd,
            env=env
        )
        processes.append((s["name"], p, s["port"]))
        print(f"  [+] {s['name']} iniciado en http://127.0.0.1:{s['port']}")
        time.sleep(1.0)

    print("\n==================================================")
    print("[OK] TODOS LOS SERVICIOS ESTAN CORRIENDO:")
    print("  * API Gateway: http://127.0.0.1:8000")
    print("  * Swagger Docs Gateway: http://127.0.0.1:8000/docs")
    print("  * Healthcheck: http://127.0.0.1:8000/health")
    print("Presiona Ctrl + C para detener todos los servicios.")
    print("==================================================\n")

    try:
        while True:
            time.sleep(1)
            for name, p, port in processes:
                if p.poll() is not None:
                    print(f"[!] Alerta: {name} se detuvo inesperadamente con codigo {p.returncode}")
    except KeyboardInterrupt:
        print("\n[!] Deteniendo microservicios de Ofertapp...")
        for name, p, _ in processes:
            p.terminate()
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
        print("[OK] Todos los microservicios fueron detenidos limpiamente.")

if __name__ == "__main__":
    main()
