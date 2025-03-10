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
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = EMAIL_DESTINATARIO
        msg["Subject"] = ASSUNTO

        msg.attach(MIMEText(MENSAGEM, "plain"))

        print("🔹 Conectando ao servidor SMTP...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Ativa logs detalhados da conexão SMTP
        server.starttls()
        
        print("🔹 Logando no e-mail...")
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)

        print("🔹 Enviando e-mail...")
        server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())

        server.quit()
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

# Testar o envio do e-mail
enviar_email()