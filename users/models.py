from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User
from machines.models import Machine

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redis_key = models.CharField(max_length=256, unique=True, blank=True, null=True)
    machines = models.ManyToManyField(Machine, through='ProfileMachine', related_name='profiles')
    

    def __str__(self):
        return f"{self.user.username}'s Profile"


class ProfileMachine(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    # Additional fields can be added here if needed
    class Meta:
        constraints = [
            UniqueConstraint(fields=['profile', 'machine'], name='unique_profile_machine')
        ]

    def __str__(self):
        return f"ProfileMachine(profile={self.profile}, machine={self.machine})"
