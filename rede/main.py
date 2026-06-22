import subprocess, requests, time, socket
from datetime import datetime

VM1_URL = "http://10.10.1.2:9000"
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

while True:
    try:
        dados = coletar()
        requests.post(f"{VM1_URL}/metricas/rede", json=dados, timeout=5)
        print(f"Enviado: {dados['timestamp']}")
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(30)