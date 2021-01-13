import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app import settings


def send_recovery_email(email: str, code: str) -> None:
    message = MIMEMultipart()
    message['From'] = settings.EMAIL_FROM
    message['To'] = email
    message['Subject'] = 'Восстановление пароля на edm.su'

    url = f'{settings.FRONTEND_URL}/user/recovery/{code}'
    text = f'Для смены пароля перейдите по ссылке: {url}'
    message.attach(MIMEText(text, 'plain'))
    send_email(message)


def send_activate_email(email: str, code: str) -> None:
    message = MIMEMultipart()
    message['From'] = settings.EMAIL_FROM
    message['To'] = email
    message['Subject'] = 'Регистрация на edm.su'
    text = f'Вы успешно зарегистрированы для активации аккаунта перейдите ' \
           f'по ссылке: {settings.FRONTEND_URL}/user/activate/{code}'
    message.attach(MIMEText(text, 'plain'))
    send_email(message)


def send_email(message: MIMEMultipart) -> None:
    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.sendmail(message['From'], message['To'], message.as_string())
    server.quit()
