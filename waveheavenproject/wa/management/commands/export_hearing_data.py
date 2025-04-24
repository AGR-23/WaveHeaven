# management/commands/export_hearing_data.py
from django.core.management.base import BaseCommand
from wa.models import UserPreferences, ExposureReport
import pandas as pd

class Command(BaseCommand):
    help = 'Export hearing data for model training' #this is it

    def handle(self, *args, **kwargs):
        data = []
        for user in UserPreferences.objects.all():
            report = ExposureReport.objects.filter(user=user).last()
            if report:
                risk_level = (
                    "High" if report.total_exposure_time > 120 else
                    "Medium" if report.total_exposure_time > 60 else
                    "Low"
                )
                data.append({
                    "ideal_volume": user.ideal_volume,
                    "last_adjusted_volume": user.last_adjusted_volume,
                    "microphone_active": int(user.microphone_active),
                    "low_freq": user.low_freq_threshold,
                    "mid_freq": user.mid_freq_threshold,
                    "high_freq": user.high_freq_threshold,
                    "exposure_time": report.total_exposure_time,
                    "risk_level": risk_level
                })
        
        df = pd.DataFrame(data)
        df.to_csv("hearing_risk_data.csv", index=False)
        self.stdout.write(self.style.SUCCESS("Data exported successfully"))
