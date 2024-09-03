from django.db import models
import uuid

class Machine(models.Model):
    name = models.CharField(max_length=255)
    machine_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    redis_key = models.CharField(max_length=400, blank=True, editable=False)


    def __str__(self):
        return f"Machine(name={self.name}, id={self.machine_id})"


