"""Modulo de envio de emails."""
import os
import smtplib
import logging
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.utils import formataddr

from app.config.settings import settings

logger = logging.getLogger(__name__)
ATTACH_FILE_TYPE = ['pdf']
SENDER_EMAIL = settings.FROM_EMAIL
SENDER_NAME = settings.FROM_EMAIL_NAME
SUBJECT = "Permiso de ingreso aprobado"
BODY = "<p>Estimado usuario, su permiso de ingreso ha sido aprobado.</p>"


def allowed_file(filename: str, extensions=ATTACH_FILE_TYPE) -> bool:
    """Validate file extension

    :param filename: file name to validate
    :type filename: str
    :param extensions: list of allowed extensions, defaults to ['xlsx']
    :type extensions: list, optional
    :return: validation result
    :rtype: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


def send_email_with_attachments(
    file_name: str,
    recipients: list | str,
) -> bool:
    """
    Send an email with HTML body and attached files

    Args:
        recipients (list): List of recipients.
        dir_files (str): attached files path.

    Returns:
        dict: Email service response.
    """
    try:
        if isinstance(recipients, list):
            recipients = ', '.join(recipients)
        msg = EmailMessage()
        msg['From'] = formataddr((SENDER_NAME, SENDER_EMAIL))
        msg['To'] = recipients
        msg['Subject'] = SUBJECT

        # Format the email body to be sent as HTML
        msg.add_alternative(BODY, subtype="html")
        # Attach files from the specified directory
        if os.path.isfile(file_name) and allowed_file(file_name):
            with open(file_name, 'rb') as f:
                content = f.read()
                part = MIMEApplication(content, _subtype=ATTACH_FILE_TYPE[-1])
                part.add_header('Content-Disposition', 'attachment', filename=file_name)
                msg.attach(part)

        # Send the email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as s:
            s.send_message(msg)
        logger.info('Correo electrónico enviado correctamente')
        return True

    except TimeoutError as e:
        logger.error(f"Error al enviar correo: {e}")
        return False
