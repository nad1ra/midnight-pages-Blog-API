from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.exceptions import ValidationError
from .models import CustomUser



def send_verification_token(email, token):
    message = f'Please verify your email using this token: {token}'
    send_mail(
        subject='Email Verification',
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False
    )

def send_password_reset_email(user):
    token = default_token_generator.make_token(user)
    message = f'Please follow the link below to reset your password:{token}'


    send_mail(
        'Password reset request',
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False
    )


def reset_password_confirm(token, new_password, confirm_password):
    if new_password != confirm_password:
        raise ValidationError("The password and confirmation password do not match.")

    for user in CustomUser.objects.all():
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return {"detail": "The password has been successfully updated."}
    raise ValidationError("The token is invalid or has expired.")