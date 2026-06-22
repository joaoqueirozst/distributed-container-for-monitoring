import psutil, socket, requests, time
from datetime import datetime

VM1_URL = "http://10.10.1.2:9000"
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

while True:
    try:
        dados = coletar()
        requests.post(f"{VM1_URL}/metricas/host", json=dados, timeout=5)
        print(f"Enviado: {dados['timestamp']}")
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(30)