
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, WHATSAPP_NUMBER
from plyer import notification

logger = logging.getLogger(__name__)

# Importación opcional de pywhatkit
try:
    import pywhatkit as pwk
    PWK_AVAILABLE = True
except ImportError:
    logger.warning("PyWhatKit no disponible. Funcionalidad de WhatsApp desactivada.")
    pwk = None
    PWK_AVAILABLE = False


class CommunicationManager:
    """Gestor de comunicaciones (email, WhatsApp, notificaciones)"""

    @staticmethod
    def send_email(to_email, subject, body, html_body=None):
        """Enviar email con manejo de errores robusto"""
        if not all([EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS]):
            logger.error("Configuración de email incompleta. No se puede enviar el correo.")
            return False, "Configuración de email incompleta"

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_USER
            msg['To'] = to_email

            msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True, "Email enviado exitosamente"
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Error de autenticación SMTP: {e}. Revisa tus credenciales.")
            return False, "Error de autenticación SMTP"
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False, f"Error enviando email: {e}"

    @staticmethod
    def send_whatsapp(phone_number, message):
        """Enviar mensaje de WhatsApp con verificación de disponibilidad"""
        if not PWK_AVAILABLE:
            logger.warning("Intento de enviar WhatsApp, pero PyWhatKit no está disponible.")
            return False, "Funcionalidad de WhatsApp no disponible"
        
        target_number = phone_number or WHATSAPP_NUMBER
        if not target_number:
            logger.error("No se ha definido un número de WhatsApp para enviar el mensaje.")
            return False, "Número de WhatsApp no especificado"

        try:
            # pywhatkit puede ser bloqueante y lanzar excepciones no documentadas
            pwk.sendwhatmsg_instantly(target_number, message, wait_time=15, tab_close=True)
            logger.info(f"Mensaje de WhatsApp enviado a {target_number}")
            return True, "Mensaje de WhatsApp enviado"
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return False, f"Error al enviar WhatsApp: {e}"

    @staticmethod
    def send_notification(title, message, timeout=10):
        """Enviar notificación local con manejo de errores"""
        try:
            notification.notify(title=title, message=message, timeout=timeout)
            logger.info(f"Notificación local enviada: '{title}'")
            return True, "Notificación enviada"
        except Exception as e:
            # Plyer puede fallar en sistemas sin un backend de notificaciones
            logger.error(f"Error enviando notificación local: {e}")
            return False, f"Error al enviar notificación: {e}"

