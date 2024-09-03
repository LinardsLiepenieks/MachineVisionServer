from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Machine
from api.models import MachineApiKey
import uuid

@receiver(post_save, sender=Machine)
def create_machine_api_key(sender, instance, created, **kwargs):
    if created:
        # Generate a new API key
        api_key = str(uuid.uuid4())
        
        # Create a MachineAPIKey instance
        MachineApiKey.objects.create(
            machine=instance,
            name=f"API Key for {instance.name}",
            key=api_key
        )


@receiver(pre_save, sender=Machine)
def set_redis_key(sender, instance, **kwargs):
    if not instance.redis_key:
        instance.redis_key = f"{instance.name}_{instance.machine_id}"
