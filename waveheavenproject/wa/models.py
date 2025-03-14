from django.db import models
from django.contrib.auth.models import User
import json

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # Campo user
    name = models.CharField(max_length=151)
    email = models.EmailField(max_length=254, unique=True)
    audio_settings = models.TextField(blank=True, null=True)
    usage_history = models.TextField(blank=True, null=True)
    ideal_volume = models.FloatField(default=50.0)
    microphone_active = models.BooleanField(default=False)
    last_adjusted_volume = models.FloatField(default=50.0)
    low_freq_threshold = models.FloatField(default=50.0)
    mid_freq_threshold = models.FloatField(default=50.0)
    high_freq_threshold = models.FloatField(default=50.0)
    sound_category = models.CharField(
        choices=[('music', 'Música'), ('podcast', 'Podcasts'), ('call', 'Llamadas')],
        default='music',
        max_length=10,
    )
    audio_profiles = models.JSONField(default=list)  # Campo para almacenar perfiles de audio

    def __str__(self):
        return f"Preferencias de {self.user.username}"
    
    def get_audio_profiles(self):
        return self.audio_profiles  # Devuelve la lista de perfiles de audio

    def save_audio_profiles(self, profiles):
        self.audio_profiles = profiles
        self.save()

class SoundProfile(UserPreferences):
    class Meta:
        proxy = True  # Esto hace que SoundProfile sea un modelo proxy

    def custom_method(self):
        return f"Perfil de sonido para {self.user.username}"

class Device(models.Model):
    user = models.ForeignKey(UserPreferences, on_delete=models.CASCADE)  # Relación con UserPreferences
    type = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    headphone_compatibility = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} - {self.version} ({'Compatible' if self.headphone_compatibility else 'Not Compatible'})"

class AudioAdjustmentRecord(models.Model):
    user = models.ForeignKey(UserPreferences, on_delete=models.CASCADE)
    recommended_volume = models.IntegerField()
    detected_noise = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record {self.id} - User {self.user.name}"

class ExposureReport(models.Model):
    user = models.ForeignKey(UserPreferences, on_delete=models.CASCADE)
    total_exposure_time = models.IntegerField()  # En segundos o minutos
    trends = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Exposure Report {self.id} - User {self.user.name}"

class HearingRiskNotification(models.Model):
    user = models.ForeignKey(UserPreferences, on_delete=models.CASCADE)
    report = models.ForeignKey(ExposureReport, on_delete=models.CASCADE)
    warning_type = models.CharField(max_length=100)  # Ej: "High Noise Exposure"
    date_and_time = models.DateTimeField(auto_now_add=True)
    exposure_threshold = models.IntegerField()  # Tiempo de exposición antes de la alerta

    def __str__(self):
        return f"Notification {self.id} - {self.warning_type} - User {self.user.name}"