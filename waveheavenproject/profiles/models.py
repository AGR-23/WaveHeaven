from django.db import models
from wa.models import ExposureReport, UserPreferences  # Import models from wa
from django.utils.timezone import now
from datetime import timedelta

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

    def get_total_exposure_time(self):
        """
        Calculate the total exposure time in minutes based on all ExposureReport records.
        """
        total_time = ExposureReport.objects.filter(user=self.user).aggregate(
            total_time=models.Sum('total_exposure_time')
        )['total_time']
        return total_time if total_time else 0  # Return 0 if no records exist

    def get_average_daily_exposure_last_week(self):
        """
        Calculate the average daily exposure time in the last 7 days.
        """
        last_week = now().date() - timedelta(days=7)
        reports_last_week = ExposureReport.objects.filter(user=self.user, date__gte=last_week)
        total_time_last_week = reports_last_week.aggregate(
            total_time=models.Sum('total_exposure_time')
        )['total_time']

        if total_time_last_week:
            return total_time_last_week / 7  # Promedio diario
        return 0