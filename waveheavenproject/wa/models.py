from django.db import models

class UserPreferences(models.Model):
    id_user = models.AutoField(primary_key=True)  # ID del usuario (ahora es la PK)
    name = models.CharField(max_length=150)  # Nombre del usuario
    email = models.EmailField(unique=True)  # Email del usuario, debe ser único
    audio_settings = models.TextField(blank=True, null=True)  # Preferencias de audio
    usage_history = models.TextField(blank=True, null=True)  # Historial de uso

    ideal_volume = models.FloatField(default=50.0)  
    microphone_active = models.BooleanField(default=False)
    last_adjusted_volume = models.FloatField(default=50.0)

    low_freq_threshold = models.FloatField(default=50.0)  # 250Hz
    mid_freq_threshold = models.FloatField(default=50.0)  # 1000Hz
    high_freq_threshold = models.FloatField(default=50.0)  # 4000Hz

    SOUND_CATEGORIES = [
        ('music', 'Música'),
        ('podcast', 'Podcasts'),
        ('call', 'Llamadas'),
    ]
    sound_category = models.CharField(
        max_length=10,
        choices=SOUND_CATEGORIES,
        default='music'
    )

    def __str__(self):
        return f"{self.name} ({self.email})"

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