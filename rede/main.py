import subprocess, requests, threading, time, socket
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()
VM1_URL = "http://10.0.120.185:8000" # IP VM1
HOSTNAME = socket.gethostname()

def ovs_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except:
        return ""

def coletar():
    return {
        "host": HOSTNAME,
        "timestamp": datetime.utcnow().isoformat(),
        "bridges": ovs_cmd("ovs-vsctl list-br"),
        "ports": ovs_cmd("ovs-vsctl show"),
        "vlans": ovs_cmd("ovs-vsctl list port"),
        "interfaces": ovs_cmd("ovs-ofctl dump-ports-desc br0"),
        "mac_table": ovs_cmd("ovs-appctl fdb/show br0"),
        "estatisticas": ovs_cmd("ovs-ofctl dump-ports br0"),
    }

def enviar_periodico():
    while True:
        try:
            dados = coletar()
            requests.post(f"{VM1_URL}/metricas/rede", json=dados, timeout=5)
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