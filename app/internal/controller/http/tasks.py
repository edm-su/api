import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.internal.entity.settings import settings


def send_recovery_email(email: str, code: str) -> None:
    message = MIMEMultipart()
    message["From"] = settings.email_from
    message["To"] = email
    message["Subject"] = "Восстановление пароля на edm.su"

    url = f"{settings.frontend_url}/user/recovery/{code}"
    text = f"Для смены пароля перейдите по ссылке: {url}"
    message.attach(MIMEText(text, "plain"))
    send_email(message)


def send_activate_email(email: str, code: str) -> None:
    message = MIMEMultipart()
    message["From"] = settings.email_from
    message["To"] = email
    message["Subject"] = "Регистрация на edm.su"
    text = (
        f"Вы успешно зарегистрированы для активации аккаунта перейдите "
        f"по ссылке: {settings.frontend_url}/user/activate/{code}"
    )
    message.attach(MIMEText(text, "plain"))
    send_email(message)


def send_email(message: MIMEMultipart) -> None:
    server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
    server.login(settings.smtp_user, settings.smtp_password)
    server.sendmail(message["From"], message["To"], message.as_string())
    server.quit()
