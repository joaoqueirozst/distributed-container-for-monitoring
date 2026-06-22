import psutil, socket, requests, time
from datetime import datetime

VM1_URL = "http://10.10.1.2/api/v1/metrics/host"
ID = int(socket.gethostname()[-1])

def coletar():
    return {
        "agent_id": ID,
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory()._asdict(),
        "disk_percent": psutil.disk_usage("/")._asdict(),
        "connections_tcp": len([c for c in psutil.net_connections() if c.type.name=="SOCK_STREAM"]),
        "uptime_seconds": time.time() - psutil.boot_time(),
    }

while True:
    try:
        dados = coletar()
        requests.post(f"{VM1_URL}", json=dados, timeout=5)
        print(f"Dados: {dados}")
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(30)