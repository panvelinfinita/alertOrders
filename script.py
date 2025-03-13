import smtplib
import requests
import datetime
import os
import pytz
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuração do servidor SMTP do Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = "alertamkpin@gmail.com"
EMAIL_SENHA = "cxxfypbbpropyeua"  # Substituir pela senha de app
EMAIL_DESTINATARIO = "jvcosta@grupopanvel.com.br"

# Configuração da API VTEX
API_URL = os.getenv("API_URL", "https://panvelprd.vtexcommercestable.com.br/api/oms/pvt/orders")
HEADERS = {"X-VTEX-API-AppKey": "vtexappkey-panvelprd-OLDAFN","X-VTEX-API-AppToken": "UOFVLDXSQIKCFYVTKNGANQCHIWJLHGWBOPXWGORMXUPEYLSHJPNTPXSIHZNDCTTYOLNFWTALWYJEKBMDYEYXZEUSCHZWEAYQUILSCTOOCWIONMKBRUVESGZOFMQRYZUD","Content-Type": "application/json","Accept": "application/json"}

# Definição dos fusos horários
UTC = pytz.utc
SAO_PAULO = pytz.timezone("America/Sao_Paulo")

def obter_ultimo_pedido():
    """Consulta a API e retorna o último pedido como um objeto datetime no fuso de São Paulo."""
    print("🔹 Consultando a API VTEX...")

    hoje = datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")

    params = {
        "f_creationDate": f"creationDate:[{hoje} TO {agora}]",
        "f_status": "payment-approved,invoiced"
    }

    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        pedidos = data.get("list", [])
        if not pedidos:
            print("❌ Nenhum pedido encontrado para o filtro.")
            return None

        ultimo_pedido = max(pedidos, key=lambda x: x["creationDate"])
        creation_date = ultimo_pedido["creationDate"]

        if "+" in creation_date:
            creation_date = creation_date.split("+")[0]
        if "." in creation_date:
            creation_date = creation_date.split(".")[0] + "." + creation_date.split(".")[1][:6]

        dt_utc = datetime.datetime.fromisoformat(creation_date).replace(tzinfo=UTC)
        dt_sao_paulo = dt_utc.astimezone(SAO_PAULO)

        print(f"✅ Último pedido encontrado em: {dt_sao_paulo.strftime('%d/%m/%Y %H:%M:%S')}")
        return dt_sao_paulo
    except Exception as e:
        print(f"❌ Erro ao consultar API: {e}")
        return None

def enviar_email(ultimo_pedido):
    """Envia um e-mail de alerta se passaram mais de 30 minutos sem pedidos."""
    agora = datetime.datetime.now(SAO_PAULO)
    tempo_sem_pedido = (agora - ultimo_pedido).total_seconds()

    if tempo_sem_pedido > 3600:  # 60 minutos sem pedido
        print("🚨 Mais de 60 minutos sem pedidos. Preparando envio de e-mail...")
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = EMAIL_DESTINATARIO
        msg["Subject"] = "🚨 Alerta: Tempo sem pedidos!"

        mensagem = f"""
        <html>
        <body>
            <h2>🚨 Alerta de Pedidos</h2>
            <p>Estamos desde <strong>{ultimo_pedido.strftime('%H:%M:%S')}</strong> sem efetivar pedidos.</p>
            <p>Por favor, verifique o sistema!</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(mensagem, "html"))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
            server.quit()
            print("✅ E-mail de alerta enviado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail: {e}")
    else:
        print(f"✅ Último pedido foi há {tempo_sem_pedido/60:.1f} minutos. Nenhum alerta necessário.")

# Loop para rodar a cada 15 minutos
print("🔄 Iniciando monitoramento de pedidos...")

for i in range(48):  # Executa 48 vezes
    print(f"\n🔄 Verificação {i+1}/48:")
    ultimo_pedido = obter_ultimo_pedido()

    if ultimo_pedido:
        enviar_email(ultimo_pedido)
    else:
        print("⚠️ Nenhum pedido encontrado para alerta.")

    print("⏳ Aguardando 30 minutos para a próxima verificação...")
    time.sleep(1800)  # 600 segundos = 10 minutos

print("⏹ Monitoramento finalizado. Execute novamente para continuar.")
