import random
from datetime import datetime, timedelta
from wa.models import UserPreferences, AudioAdjustmentRecord

def populate_audio_adjustments(user_id):
    user_prefs = UserPreferences.objects.get(user__id=user_id)
    base_time = datetime.now() - timedelta(days=1)

    for i in range(50):
        timestamp = base_time + timedelta(minutes=i * 15)
        detected_noise = random.randint(30, 100)
        recommended_volume = max(0, min(100, 100 - int(detected_noise * 0.7) + random.randint(-5, 5)))

        AudioAdjustmentRecord.objects.create(
            user=user_prefs,
            detected_noise=detected_noise,
            recommended_volume=recommended_volume,
            timestamp=timestamp
        )

    print("Datos de audio agregados exitosamente.")