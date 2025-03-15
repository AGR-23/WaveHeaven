from django.db import models
from wa.models import ExposureReport, UserPreferences  # Import models from wa

class SoundProfile(UserPreferences):
    class Meta:
        proxy = True  # Proxy model, no changes to DB schema

    def custom_method(self):
        return f"Perfil de sonido para {self.user.username}"

class UserStatistics(ExposureReport):
    """
    Proxy model to extend ExposureReport without modifying the wa app.
    """
    class Meta:
        proxy = True  # This prevents Django from creating a new table

    def get_recommendations(self):
        """
        Generate personalized recommendations based on exposure data.
        """
        if self.total_exposure_time > 120:  # Example: more than 2 hours
            return "Consider taking breaks between listening sessions to protect your hearing."
        elif self.total_exposure_time > 60:  # Example: more than 1 hour
            return "Try lowering your volume slightly for a safer experience."
        else:
            return "You're listening at a safe level. Keep enjoying your audio!"