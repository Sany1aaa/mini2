import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

logger = logging.getLogger('users')

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Новый пользователь зарегистрирован: {instance.email}")
        print(f"Signal fired for user creation: {instance.email}")


@receiver(user_logged_in, sender=User)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"Пользователь вошел в систему: {user.email}")


@receiver(user_logged_out, sender=User)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"Пользователь вышел из системы: {user.email}")