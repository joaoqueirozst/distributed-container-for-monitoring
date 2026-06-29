# Plataforma Distribuída de Gerenciamento, Monitoramento, Observabilidade e Segurança de Redes

> Este trabalho foi desenvolvido por alunos da disciplina de *Laboratório de Redes* do IFES, campus Guarapari, e consiste na construção colaborativa de uma *Plataforma Distribuída de Gerenciamento, Monitoramento, Observabilidade e Segurança de Redes*. Cada aluno foi responsável por um módulo específico da plataforma, que juntos formam a infraestrutura completa.

# Container Distribuído de Monitoramento (Aluno 8)

O repositório conta com o desenvolvimento de *agentes* distribuídos de monitoramento implementados como containers Docker dentro das *VMs* e *Switches* do sistema, responsáveis pela coleta e envio de métricas para o **Servidor Central (VM1)**. Para isso, foi implementado dois tipos de agentes: **HOST** e **REDE**. O local de execução de cada agente será conforme a tabela abaixo.

| Agente | Atuação |
|--------|---------|
| Host   | VM1, VM2, VM3, VM4, VM6, VM7, VM9, VM10 |
| Rede   | VM-SW1, VM-SW2 |

# Agente HOST

O Agente de Host é um container Docker desenvolvido em Python, responsável por coletar métricas do sistema operacional da máquina local onde está sendo executado. Ele foi configurado para que, a cada 30s (em *loop*), *coleta* e *envia* automaticamente para a *API* do **Servidor Central (VM1)** as informações de:

- `agent_id`: identificador da *VM* onde o agente está em execução
- `cpu_percent`: percentual de uso do processador
- `ram_percent`: percentual de uso da memória RAM
- `disk_percent`: percentual de uso do disco
- `connections_tcp`: número de conexões TCP ativas
- `uptime_seconds`: tempo de funcionamento da máquina em segundos

Além de informar a *VM* ou *Switche* em que estão sendo lidos os dados.

Para realizar a coleta das informações, foi-se implementada a biblioteca `psutil`, responsável para obter informações do sistema operacional local. Neste trabalho, as métricas lidas foram selecionadas conforme as configuraçãos do *Aluno 1*.

Adicionalmente, para envio desses dados, foi-se utilizada a biblioteca `requests`, que realiza as requisições `HTTP` e os envia para *VM1* via `requests.post`. Com isso, os dados são serializados em formato `.JSON` (formato padrão de troca de dados) e enviados via `HTTP POST` para o endpoint `/api/v1/metrics/host` da *VM1*.

> Sobre o método `HTTP POST`, ele é utilizado na comunicação web para envio de dados para um servidor, sem isso, *VM1* não tem os dados das máquinas da infraestrutura.

A seguir, apresenta-se a linha de código com a lógica acima, indicando: envio via `requests.post`; destino *VM1* (10.0.20.10/api/v1/metrics/host); serialização dos dados.

```bash
requests.post(f"{VM1_URL}", json=dados, timeout=5)
```

Além disso, para melhor supervisão do envio, foi-se adicionado `print(f"Enviado: {r.status_code}")`, para verificar *status* da resposta HTTP.

Com essas configurações, após o envio, a *VM1* fica responsável por armazenar e disponibilizar consultas pelos demais módulos da plataforma. O fluxo completo desse processo pode ser observado na figura abaixo.

<p align="center">
  <img src="fluxo.png" width="600"/>
</p>

## Dockerfile

Após essa etapa, o *agente host* foi empacotado em um *container Docker*. O `Dockerfile` define a imagem base com `Python 3.11`, instala as dependências necessárias (em `requirements.txt`) e executa o agente automaticamente ao iniciar o container.

A utilização do Docker garante que o agente rode igualmente em qualquer *VM*, independente das configurações locais, sendo necessário apenas clonar o repositório, construir a imagem e executar o container com um único comando. A tabela a seguir ilustra como esse processo foi feito dentro de cada *VM*.

## Execução

| Comando | Descrição |
|---------|-----------|
| `git clone https://github.com/joaoqueirozst/distributed-container-for-monitoring` | Clona o repositório com o código do agente |
| `cd distributed-container-for-monitoring` | Entra na pasta do repositório |
| `docker build -t host ./host` | Constrói a imagem Docker do agente host |
| `docker run -d --network host --name host host` | Sobe o container em background usando a rede da *VM* |
| `docker logs -f host` | Acompanha os logs em tempo real |

E caso seja necessário parar o container, remover o repositório ou apagar a imagem Docker (atualizar o código ou reconfigurar o agente, por exemplo), os seguintes comandos podem ser utilizados:

| Comando | Descrição |
|---------|-----------|
| `docker kill host && docker rm host` | Para e remove o container em execução |
| `rm -rf distributed-container-for-monitoring` | Remove a pasta do repositório clonado |
| `docker rmi host` | Apaga a imagem Docker do agente |

## Testes

Os testes foram realizados em duas máquinas distintas para validar o funcionamento e a robustez do agente. O primeiro teste foi feito na própria *VM1* (Servidor Central), e o outro, em uma VM aleatória.

Para *VM1*, acesso à máquina via `ssh root@10.10.1.2` e, rodando os comandos da seção **Execução**, tem-se, após rodar o comando de `docker logs -f host`, a saída obtida:

```
Enviado: 201
Dados: {'agent_id': 1, 'cpu_percent': 11.3, 'ram_percent': 61.4, 'disk_percent': 76.9, 'connections_tcp': 15, 'uptime_seconds': 244447}
Enviado: 201
Dados: {'agent_id': 1, 'cpu_percent': 1.0, 'ram_percent': 39.0, 'disk_percent': 17.3, 'connections_tcp': 7, 'uptime_seconds': 1127915}
```

Com o agente sendo executado diretamente na *VM1*, que possui uma rota configurada a partir da máquina **local** *labredes*, o container subiu corretamente e os *logs* confirmaram o envio das métricas com status `201`, indicando que a requisição teve sucesso e os dados foram armazenados na API.

Um segundo teste foi realizado para validar, oficialmente, o funcionamento do agente com uma máquina **externa** (*VM Ubuntu*), ao envio de dados para o *Servidor Central*. Para isso, acesso à *VM Ubuntu* foi realizado em dois passos:
1. Conectando à máquina *labredes* via `ssh root@10.10.1.22` (máquina criada por outro aluno), que possui rota para a rede **interna**;
2. A partir dela, acessa a *VM Ubuntu* em `ssh root@10.0.60.20`, que não é acessível diretamente da máquina **local**.

Como essa máquina, no momento em que foi feito o teste, não resolvia o DNS do GitHub, não era possível fazer `git clone` diretamente. A solução foi copiar a pasta já clonada da *VM1* para *Vm Ubuntu* via rede **interna**, que funcionava normalmente, com o comando:

```bash
scp -r ~/distributed-container-for-monitoring root@10.0.60.20:~
```

> O comando `SCP` (Secure Copy Protocol) é responsável por copiar arquivos entre máquinas utilizando `ssh`.

Efetuando isso, após `docker logs -f host`, a resposta foi:

```
Enviado: 201
Dados: {'agent_id': 2, 'cpu_percent': 1.0, 'ram_percent': 39.0, 'disk_percent': 17.3, 'connections_tcp': 7, 'uptime_seconds': 1127915}
Enviado: 201
Dados: {'agent_id': 2, 'cpu_percent': 1.0, 'ram_percent': 39.0, 'disk_percent': 17.3, 'connections_tcp': 7, 'uptime_seconds': 1127946}
```

> `agente_id: 2` indica que eram informações de outra máquina, e não mais *VM1*!

Novamente, o status `201` confirma que o agente está funcionando e enviando corretamente, indicando que a requisição foi bem-sucedida. Como o agente operou corretamente tanto no *Servidor Central (VM1)* quanto em uma *VM* **externa**, conclui-se que o mesmo comportamento se aplica a todas as demais *VMs* da infraestrutura.

Ao final, a imagem do *agente host* foi criada no Docker Hub, permitindo que qualquer *VM* possa baixar e executar o agente diretamente, sem necessidade de clonar o repositório e buildar localmente. Os comandos da próxima tabela ilustruam esse processo.

| Comando | Descrição |
|---------|-----------|
| `docker build -t joaoqueirozz/host:v2 .` | Constrói a imagem com a tag do Docker Hub |
| `docker push joaoqueirozz/host:v2` | Publica a imagem no Docker Hub |

E para o usuário usar a imagem criada:

```bash
docker pull joaoqueirozz/host:v2
docker run joaoqueirozz/host:v2
```


# Agente REDE

O *agente rede* é responsável por coletar estatísticas de tráfego das *interfaces* dos switches virtuais (*VM_SW1* e *VM_SW2*) e enviá-las para o *Servidor Central (VM1)*. Para isso, utiliza um *mapeamento fixo* que define manualmente quais interfaces existem em cada switch e a qual *VLAN* pertencem. Essas informações de cada interface são baseadas na topologia configurada pelo *Aluno 5*, no OpenStack, e contém dados de:

- `agent_id`: identificador do switch (1 para *VM_SW1*, 2 para *VM_SW2*)
- `interface_name`: nome da interface (ex: `ens3`, `ens4`)
- `vlan_id`: *VLAN* à qual a interface pertence (`None` para interfaces sem *VLAN* definida)
- `bytes_in`: total de bytes recebidos pela interface
- `bytes_out`: total de bytes enviados pela interface
- `packets_in`: total de pacotes recebidos pela interface
- `packets_out`: total de pacotes enviados pela interface

O mapeamento foi definido de forma *individual* para *cada interface* pois o *schema* da API da *VM1* espera receber apenas uma requisição por interface, ou seja, cada envio representa uma única interface específica com sua respectiva *VLAN*. Mesmo que duas interfaces pertençam à mesma VLAN, como `ens4` e `ens5` no *SW1* (ambas na *VLAN 40*, por exemplo), cada uma possui estatísticas de tráfego independentes e deve ser reportada separadamente.

> Interfaces sem *VLAN* definida (Firewall, Trunk) recebem `None`.

As configurações realizadas nesta etapa foram parecidas com as feitas anteriormente, mas com algumas modificações. Primeiramente, foi necessária a instalação do Docker, pois *VM_SW1* e *VM_SW2*, por se tratar de *switches virtuais*, não possuiam o Docker instalado. Diferente das demais *VMs* da infraestrutura, em que o Docker já estava disponível.

```bash
apt install docker.io -y
```

A coleta das estatísticas é realizada pela função `get_interface_stats()`, que utiliza `psutil.net_io_counters(pernic=True)` para retornar as estatísticas de cada interface individualmente. Para cada interface são coletados bytes e pacotes recebidos e enviados. Caso a interface não seja encontrada no sistema, a função retorna zeros para todos os campos.

Também foi implementada a função `coletar_e_enviar()`, que percorre cada interface do mapeamento fixo, monta o `.JSON` com os dados coletados e envia uma requisição `POST` separada para a *VM1* via `requests.post`. Todo esse processo fica em estrutura de *loop*.

## Dockerfile

Da forma semelhante ao que foi feito no *agente host*, este agente também foi empacotado em um *container Docker*.

## Execução

| Comando | Descrição |
|---------|-----------|
| `cd distributed-container-for-monitoring` | Entra na pasta do repositório |
| `docker build -t host ./rede` | Constrói a imagem Docker do agente rede |
| `docker run -d --network host --privileged --name rede -e SWITCH=sw2 rede` | Sobe o container em background, com condição para saber qual *SW* |
| `docker logs -f rede` | Acompanha os logs em tempo real |

## Testes

Os testes foram feitos no *SW2*, seguindo a mesma lógica do agente anterior, sendo que se funcionasse para *SW2*, certamente funcionaria para *SW1*, de forma redundante.

Na fase de validação do *agente rede*, até o momento em que foram realizados os testes, o *SW2* também não resolvia o DNS do GitHub, não sendo possível fazer `git clone`. A solução foi copiar a pasta já clonada da *VM1* para o *SW2* via rede interna, com o comando `SCP`, com o IP destino *SW2* (nesse caso, `192.168.10.105`):

```bash
scp -r ~/distributed-container-for-monitoring root@192.168.10.105:~
```

Para acessar *SW2*: `ssh root@10.10.1.38`

Ao rodar o agente com o comando `docker logs -f rede`, a seguinte saída foi observada:

```bash
Erro ens3: [Errno 104] Connection aborted., ConnectionResetError(104, 'Connection reset by peer')
Erro ens4: [Errno 104] Connection aborted., ConnectionResetError(104, 'Connection reset by peer')
Erro ens5: [Errno 104] Connection aborted., ConnectionResetError(104, 'Connection reset by peer')
[...]
```

Analisando a saída, o erro `Connection reset by peer` indica que o *SW2* conseguiu chegar até o destino (*VM1*), mas a conexão foi fechada imediatamente pelo servidor. Isso significa que a requisição saiu corretamente do agente, porém foi bloqueada ou rejeitada antes de ser processada pela API. O provável motivo é que, no momento que foi realizado o teste, o roteamento entre *VLANS* ainda não havia sido completamente configurado pelo *Aluno 11*, impedindo que a requisição fosse aceita pela *VM1*.

Para fins comparativos, pela API do *Aluno 1*, esperava-se uma saída semelhante à indicada:

```bash
{
    "interface_name": "ens15",
    "vlan_id": null,
    "id": 739,
    "agent_id": 2,
    "bytes_out": 37065743,
    "packets_out": 359343,
    "bytes_in": 414681296,
    "packets_in": 465085,
    "collected_at": "2026-06-25T18:09:18.275668"
  }

```

Vale ressaltar que este erro visto anteriormente não invalida a implementação do *agente rede*. O possível problema está na camada de rede da infraestrutura, dependendo da configuração do *Aluno 11* para liberar o tráfego entre o SW2 e a VM1.

Após isso, o mesmo processo realizado para construção da imagem no Docker Hub foi feita para o *agente rede*, com os comandos indicados na tabela abaixo.

| Comando | Descrição |
|---------|-----------|
| `docker build -t joaoqueirozz/rede:v1 .` | Constrói a imagem com a tag do Docker Hub |
| `docker push joaoqueirozz/host:v1` | Publica a imagem no Docker Hub |

E para o usuário usar a imagem criada:

```bash
docker pull joaoqueirozz/rede:v1
docker run joaoqueirozz/rede:v1
```
