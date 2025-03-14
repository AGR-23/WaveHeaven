from django.db import models
from wa.models import UserPreferences  # Importar UserPreferences desde wa

# Herencia de UserPreferences en SoundProfile
class SoundProfile(UserPreferences):
    class Meta:
        proxy = True  # Esto hace que SoundProfile sea un modelo proxy

    def custom_method(self):
        return f"Perfil de sonido para {self.user.username}"