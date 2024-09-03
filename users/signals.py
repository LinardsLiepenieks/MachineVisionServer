from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import transaction
from .models import Profile
from api.models import APIKey
import uuid
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Created profile for user: {instance.username}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    logger.debug(f"Saved profile for user: {instance.username}")

@receiver(post_save, sender=Profile)
@transaction.atomic
def create_api_and_redis_keys(sender, instance, created, **kwargs):
    if created:
        try:
            # Create an API key
            api_key = uuid.uuid4()
            APIKey.objects.create(
                profile=instance,
                name=f"API Key for {instance.user.username}",
                key=str(api_key)
            )
            logger.info(f"Created API key for user: {instance.user.username}")

            # Generate a redis_key if not present
            if not instance.redis_key:
                instance.redis_key = f"{instance.user.username}_{uuid.uuid4().hex}"
                instance.save(update_fields=['redis_key'])
                logger.info(f"Generated Redis key for user: {instance.user.username}")
        except Exception as e:
            logger.error(f"Error creating API and Redis keys for user {instance.user.username}: {str(e)}")
            raise