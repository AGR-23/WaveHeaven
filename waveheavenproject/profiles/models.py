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
        proxy = True  # No new DB table, just additional methods

    def get_recommendations(self):
        """
        Generate personalized recommendations based on exposure data.
        """
        if self.total_exposure_time > 120:  # More than 2 hours
            return "Consider taking breaks between listening sessions to protect your hearing."
        elif self.total_exposure_time > 60:  # More than 1 hour
            return "Try lowering your volume slightly for a safer experience."
        else:
            return "You're listening at a safe level. Keep enjoying your audio!"

    def get_sessions_last_week(self):
        """
        Count the number of exposure sessions in the past 7 days.
        """
        last_week = now().date() - timedelta(days=7)
        return ExposureReport.objects.filter(user=self.user, date__gte=last_week).count()