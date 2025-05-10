from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user):
    message = f'Please verify your email by sending the following token: {user.verification_token}'
    send_mail('Email Verification', message, settings.EMAIL_HOST_USER, [user.email])
