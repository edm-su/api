from sendgrid import Mail, SendGridAPIClient

from app import settings


def send_recovery_email(email, code) -> None:
    url = f'{settings.FRONTEND_URL}/user/recovery/{code}'
    message = Mail(settings.EMAIL_FROM,
                   email,
                   'Восстановление пароля на edm.su',
                   f'Для смены пароля перейдите по ссылке: {url}',
                   )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)


def send_activate_email(email, code):
    message = Mail(
        settings.EMAIL_FROM,
        email,
        'Регистрация на edm.su',
        f'Вы успешно зарегистрированы для активации аккаунта перейдите по '
        f'ссылке: {settings.FRONTEND_URL}/user/activate/{code}')
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)
    return f'{email} отправлено письмо с активацией аккаунта'
