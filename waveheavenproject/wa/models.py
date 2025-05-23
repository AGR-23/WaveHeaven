from django.db import models
from django.contrib.auth.models import User
import json
from datetime import date

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # Campo user
    name = models.CharField(max_length=151)
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=254)
    audio_settings = models.TextField(blank=True, null=True)
    usage_history = models.TextField(blank=True, null=True)
    ideal_volume = models.FloatField(default=50.0)
    microphone_active = models.BooleanField(default=False)
    last_adjusted_volume = models.FloatField(default=50.0)
    low_freq_threshold = models.FloatField(default=50.0)
    mid_freq_threshold = models.FloatField(default=50.0)
    high_freq_threshold = models.FloatField(default=50.0)
    in_party_mode = models.BooleanField(default=False)
    current_party = models.ForeignKey('PartySession', on_delete=models.SET_NULL, null=True, blank=True)
    sound_category = models.CharField(
        choices=[('music', 'Música'), ('podcast', 'Podcasts'), ('call', 'Llamadas')],
        default='music',
        max_length=10,
    )
    audio_profiles = models.JSONField(default=list)  # Campo para almacenar perfiles de audio
    active_profile = models.CharField(max_length=100, blank=True) # Campo para almacenar el perfil activo

    def __str__(self):
        return f"Preferencias de {self.user.username}"
    
    def get_audio_profiles(self):
        return self.audio_profiles  # Devuelve la lista de perfiles de audio

    def save_audio_profiles(self, profiles):
        self.audio_profiles = profiles
        self.save(update_fields=['audio_profiles'])

class SoundProfile(UserPreferences):
    class Meta:
        proxy = True  # Esto hace que SoundProfile sea un modelo proxy

    def custom_method(self):
        return f"Perfil de sonido para {self.user.username}"
    
    def save_audio_profiles(self, profiles):
        self.audio_profiles = profiles
        self.save()

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
    total_exposure_time = models.IntegerField()  # Tiempo de exposición en minutos
    date = models.DateField(auto_now_add=True)   # Fecha de creación del informe

    def __str__(self):
        return f"Exposure Report for {self.user.user.username} on {self.date}"

class HearingRiskNotification(models.Model):
    user = models.ForeignKey(UserPreferences, on_delete=models.CASCADE)
    report = models.ForeignKey(ExposureReport, on_delete=models.CASCADE)
    warning_type = models.CharField(max_length=100)  # Ej: "High Noise Exposure"
    date_and_time = models.DateTimeField(auto_now_add=True)
    exposure_threshold = models.IntegerField()  # Tiempo de exposición antes de la alerta

    def __str__(self):
        return f"Notification {self.id} - {self.warning_type} - User {self.user.name}"
    
class PartySession(models.Model):
    host = models.ForeignKey(UserPreferences, on_delete=models.CASCADE, related_name='hosted_parties')
    participants = models.ManyToManyField(UserPreferences, related_name='joined_parties')
    session_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # Campos para configuración de audio grupal
    group_bass = models.IntegerField(default=80)
    group_mid = models.IntegerField(default=60)
    group_treble = models.IntegerField(default=70)

    def __str__(self):
        return f"Party Session {self.session_code}"

class ChatMessage(models.Model):
     party_session = models.ForeignKey('PartySession', on_delete=models.CASCADE, related_name='chat_messages')
     user = models.ForeignKey(UserPreferences, on_delete=models.CASCADE)  # Link to UserPreferences
     content = models.TextField()
     timestamp = models.DateTimeField(auto_now_add=True)

     def __str__(self):
         return f'Message by {self.user.user.username} in {self.party_session.session_code} at {self.timestamp}'