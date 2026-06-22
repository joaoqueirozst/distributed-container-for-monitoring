import psutil, socket, requests, time, threading
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()
VM1_URL = "http://10.0.120.185:8000" # IP VM1
HOSTNAME = socket.gethostname()

def coletar():
    return {
        "host": HOSTNAME,
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory()._asdict(),
        "disco": psutil.disk_usage("/")._asdict(),
        "uptime": time.time() - psutil.boot_time(),
        "interfaces": {k: [a._asdict() for a in v] for k,v in psutil.net_if_addrs().items()},
        "conexoes_tcp": len([c for c in psutil.net_connections() if c.type.name=="SOCK_STREAM"]),
        "processos": len(psutil.pids()),
    }

def enviar_periodico():
    while True:
        try:
            dados = coletar()
            requests.post(f"{VM1_URL}/metricas/host", json=dados, timeout=5)
        except Exception as e:
            print(f"Erro ao enviar: {e}")
        time.sleep(30)

@app.on_event("startup")
def startup():
    t = threading.Thread(target=enviar_periodico, daemon=True)
    t.start()

@app.get("/metricas")
def metricas():
    return coletar()

@app.get("/health")
def health():
    return {"status": "ok", "host": HOSTNAME}