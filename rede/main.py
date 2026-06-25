import requests, time, os
import psutil

VM1_URL = "http://10.0.20.10/api/v1/metrics/network"

# Mapeamento fixo de interfaces por switch
INTERFACES_SW1 = [
    {"interface_name": "ens3", "vlan_id": 10},
    {"interface_name": "ens4", "vlan_id": 40},
    {"interface_name": "ens5", "vlan_id": 40},
    {"interface_name": "ens6", "vlan_id": 50},
    {"interface_name": "ens7", "vlan_id": 60},
    {"interface_name": "ens8", "vlan_id": None}, # não tem VLAN definida (FIREWAL_1)
    {"interface_name": "ens9", "vlan_id": None}, # não tem VLAN definida (labredes1)
    {"interface_name": "ens13", "vlan_id": None}, # não tem VLAN definida (TRUNK_INTER_SW)
]

INTERFACES_SW2 = [
    {"interface_name": "ens3", "vlan_id": 10},
    {"interface_name": "ens4", "vlan_id": 20},
    {"interface_name": "ens5", "vlan_id": 20},
    {"interface_name": "ens6", "vlan_id": 30},
    {"interface_name": "ens7", "vlan_id": 40},
    {"interface_name": "ens8", "vlan_id": 40},
    {"interface_name": "ens9", "vlan_id": 60},
    {"interface_name": "ens10", "vlan_id": None}, # não tem VLAN definida (FIREWAL_2)
    {"interface_name": "ens11", "vlan_id": None}, # não tem VLAN definida (labredes1)
    {"interface_name": "ens15", "vlan_id": None}, # não tem VLAN definida (TRUNK_INTER_SW)
]

SWITCH = os.getenv("SWITCH", "sw1")

if SWITCH == "sw1":
    AGENT_ID = 1
    INTERFACES = INTERFACES_SW1
else:
    AGENT_ID = 2
    INTERFACES = INTERFACES_SW2

def get_interface_stats(iface):
    stats = psutil.net_io_counters(pernic=True)
    if iface in stats:
        s = stats[iface]
        return s.bytes_recv, s.bytes_sent, s.packets_recv, s.packets_sent
    return 0, 0, 0, 0

def coletar_e_enviar():
    for iface in INTERFACES:
        nome = iface["interface_name"]
        bytes_in, bytes_out, packets_in, packets_out = get_interface_stats(nome)
        dados = {
            "agent_id": AGENT_ID,
            "interface_name": nome,
            "vlan_id": iface["vlan_id"],
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "packets_in": packets_in,
            "packets_out": packets_out,
        }
        try:
            r = requests.post(VM1_URL, json=dados, timeout=5)
            print(f"Enviado {nome}: {r.status_code}")
        except Exception as e:
            print(f"Erro {nome}: {e}")

while True:
    coletar_e_enviar()
    time.sleep(30)