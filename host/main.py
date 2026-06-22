import psutil, socket, requests, time
from datetime import datetime

VM1_URL = "http://10.10.1.2/api/v1/metrics/host"
HOSTNAME = socket.gethostname()

def coletar():
    return {
        "host": HOSTNAME,
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory()._asdict(),
        "disk_percent": psutil.disk_usage("/")._asdict(),
        "uptime": time.time() - psutil.boot_time(),
        "conexoes_tcp": len([c for c in psutil.net_connections() if c.type.name=="SOCK_STREAM"]),
    }

while True:
    try:
        dados = coletar()
        requests.post(f"{VM1_URL}", json=dados, timeout=5)
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(30)