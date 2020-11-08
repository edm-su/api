from sendgrid import Mail, SendGridAPIClient

from app import settings


def send_recovery_email(email: str, code: str) -> None:
    url = f'{settings.FRONTEND_URL}/user/recovery/{code}'
    message = Mail(
        settings.EMAIL_FROM,
        email,
        'Восстановление пароля на edm.su',
        f'Для смены пароля перейдите по ссылке: {url}',
    )
    send_email(message)


def send_activate_email(email: str, code: str) -> None:
    message = Mail(
        settings.EMAIL_FROM,
        email,
        'Регистрация на edm.su',
        f'Вы успешно зарегистрированы для активации аккаунта перейдите по '
        f'ссылке: {settings.FRONTEND_URL}/user/activate/{code}')
    send_email(message)


def send_email(message: Mail) -> None:
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)
