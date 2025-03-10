import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuração do servidor SMTP do Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = "alertamkpin@gmail.com"
EMAIL_SENHA = "cxxfypbbpropyeua"

EMAIL_DESTINATARIO = "jvcosta@grupopanvel.com.br"
ASSUNTO = "🚨 Alerta: Tempo sem pedidos!"
MENSAGEM = "Estamos desde às 14:48 sem efetivar pedidos. Por favor, verifique o sistema."

def enviar_email():
    """Envia um e-mail de alerta."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg["Subject"] = ASSUNTO

    msg.attach(MIMEText(MENSAGEM, "plain"))