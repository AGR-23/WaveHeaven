from django.db import models
from django.contrib.auth.models import User

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ideal_volume = models.FloatField(default=50.0)
    microphone_active = models.BooleanField(default=False)
    last_adjusted_volume = models.FloatField(default=50.0)  # Guarda el último volumen ajustado