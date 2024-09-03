from django.contrib.auth.models import User
from machines.models import Machine
from django.db import models
import uuid

class BaseAPIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.owner_name})"

    @property
    def owner_name(self):
        raise NotImplementedError("Subclasses must implement this property")

class APIKey(BaseAPIKey):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='api_keys')

    @property
    def owner_name(self):
        return self.profile.user.username

class MachineApiKey(BaseAPIKey):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='api_keys')

    @property
    def owner_name(self):
        return self.machine.name
    

class AudioRecording(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recording = models.FileField(upload_to='recordings/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording by {self.user.username} at {self.created_at}"

class Objective(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Objective for {self.user.username} at {self.timestamp}"





    


