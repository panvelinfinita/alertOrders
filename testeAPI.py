import requests
import datetime
import os
import pytz  # Biblioteca para trabalhar com fusos horários

# Configurações
API_URL = os.getenv("API_URL", "https://panvelprd.vtexcommercestable.com.br/api/oms/pvt/orders")
HEADERS = {"X-VTEX-API-AppKey": "vtexappkey-panvelprd-OLDAFN","X-VTEX-API-AppToken": "UOFVLDXSQIKCFYVTKNGANQCHIWJLHGWBOPXWGORMXUPEYLSHJPNTPXSIHZNDCTTYOLNFWTALWYJEKBMDYEYXZEUSCHZWEAYQUILSCTOOCWIONMKBRUVESGZOFMQRYZUD", "Content-Type": "application/json", "Accept": "application/json"}

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

# Testar a função
ultimo = obter_ultimo_pedido()
if ultimo:
    print(f"✅ Último pedido encontrado (Horário de Brasília): {ultimo}")
else:
    print("⚠️ Nenhum pedido encontrado.")