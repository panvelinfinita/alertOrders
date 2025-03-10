import requests
import datetime
import time
import os
import pytz

# Configurações
API_URL = os.getenv("API_URL", "https://panvelprd.vtexcommercestable.com.br/api/oms/pvt/orders")
WEBHOOK_TEAMS = os.getenv("WEBHOOK_TEAMS", "https://prod-11.westus.logic.azure.com:443/workflows/34cc52deab894b879601fade914a267c/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=W2aiZMfB2kseAhtZxPuEPcyDN3Au_Bl7nBON1uAVDk8")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 10))  # Tempo entre execuções
HEADERS = {
    "X-VTEX-API-AppKey": "vtexappkey-panvelprd-OLDAFN",
    "X-VTEX-API-AppToken": "UOFVLDXSQIKCFYVTKNGANQCHIWJLHGWBOPXWGORMXUPEYLSHJPNTPXSIHZNDCTTYOLNFWTALWYJEKBMDYEYXZEUSCHZWEAYQUILSCTOOCWIONMKBRUVESGZOFMQRYZUD", 
    "Content-Type": "application/json", 
    "Accept": "application/json",
    }

# Definição dos fusos horários
UTC = pytz.utc
SAO_PAULO = pytz.timezone("America/Sao_Paulo")

def obter_ultimo_pedido():
    """Consulta a API e retorna o último pedido como um objeto datetime no fuso de São Paulo."""
    
    # Definir o intervalo de datas para a consulta (apenas pedidos do dia atual)
    hoje = datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")

    params = {
        "f_creationDate": f"creationDate:[{hoje} TO {agora}]",
        "f_status": "payment-approved,invoiced"
    }

    # Chamada da API com os parâmetros
    response = requests.get(API_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    pedidos = data["list"]
    if not pedidos:
        print("❌ Nenhum pedido encontrado para o filtro.")
        return None

    # Pegando o último pedido com base no campo "creationDate"
    ultimo_pedido = max(pedidos, key=lambda x: x["creationDate"])

    # Ajuste para remover fuso horário e converter corretamente
    creation_date = ultimo_pedido["creationDate"]

    # Removendo fuso horário (+00:00) se existir
    if "+" in creation_date:
        creation_date = creation_date.split("+")[0]

    # Removendo casas decimais extras (apenas deixar 6 dígitos)
    if "." in creation_date:
        creation_date = creation_date.split(".")[0] + "." + creation_date.split(".")[1][:6]

    # Converter para datetime UTC
    dt_utc = datetime.datetime.fromisoformat(creation_date).replace(tzinfo=UTC)

    # Converter para horário de São Paulo
    dt_sao_paulo = dt_utc.astimezone(SAO_PAULO)

    return dt_sao_paulo


def enviar_alerta(ultimo_pedido):
    """Envia um alerta para o Microsoft Teams se passar do tempo limite."""
    mensagem = {
        "title": "🚨 Alerta: Tempo sem pedidos!",
        "text": f"Estamos desde às {ultimo_pedido} sem efetivar pedido."
    }
    requests.post(WEBHOOK_TEAMS, json=mensagem)

while True:
    try:
        ultimo = obter_ultimo_pedido()
        agora = datetime.datetime.now(SAO_PAULO)
        
        if ultimo and (agora - ultimo).total_seconds() > 1800:  # 30 minutos
            enviar_alerta(ultimo)
        
        print(f"Verificação feita às {agora}. Último pedido às {ultimo}.")
        
    except Exception as e:
        print(f"Erro: {e}")
    
    # Espera X minutos antes de rodar de novo
    time.sleep(INTERVALO_MINUTOS * 60)