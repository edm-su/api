from sendgrid import Mail, SendGridAPIClient

from app.settings import settings


def send_recovery_email(email: str, code: str) -> None:
    url = f'{settings.frontend_url}/user/recovery/{code}'
    message = Mail(
        settings.email_from,
        email,
        'Восстановление пароля на edm.su',
        f'Для смены пароля перейдите по ссылке: {url}',
    )
    send_email(message)


def send_activate_email(email: str, code: str) -> None:
    message = Mail(
        settings.email_from,
        email,
        'Регистрация на edm.su',
        f'Вы успешно зарегистрированы для активации аккаунта перейдите по '
        f'ссылке: {settings.frontend_url}/user/activate/{code}')
    send_email(message)


def send_email(message: Mail) -> None:
    sg = SendGridAPIClient(settings.sendgrid_api_key)
    sg.send(message)
