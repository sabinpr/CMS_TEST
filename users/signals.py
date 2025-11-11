from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def send_password_reset_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{instance.pk}/{token}/"
        subject = "Set your password"
        message = f"Hi {instance.full_name},\n\nPlease set your password by clicking the link below:\n{reset_url}\n\nThis link will expire shortly."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])


@receiver(user_logged_in)
def update_last_active(sender, user, request, **kwargs):
    user.last_active = timezone.now()
    user.save(update_fields=["last_active"])
