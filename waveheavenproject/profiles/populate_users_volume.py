# waveheavenproject/profiles/populate_users_volume.py

import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from wa.models import UserPreferences, AudioAdjustmentRecord
from django.utils.timezone import make_aware

def populate_fake_users(n=50):
    for i in range(n):
        username = f"testuser{i}"
        email = f"{username}@example.com"
        password = "testpassword123"

        if User.objects.filter(username=username).exists():
            continue  # Evita duplicados

        user = User.objects.create_user(username=username, email=email, password=password)

        years_ago = random.randint(13, 60)  # Edad entre 13 y 60
        birthday = datetime.now() - timedelta(days=years_ago * 365)
        birthday = birthday.date()

        # Volumen ideal más alto para jóvenes
        if 13 <= years_ago <= 22:
            ideal_volume = random.uniform(75.0, 95.0)
        else:
            ideal_volume = random.uniform(40.0, 70.0)

        prefs = UserPreferences.objects.create(
            user=user,
            name=username,
            birthday=birthday,
            email=email,
            ideal_volume=ideal_volume,
        )

        # Generar entre 5 y 12 registros de ajustes
        for _ in range(random.randint(5, 12)):
            # Simular un volumen recomendado en torno al ideal con ligera variación
            if 13 <= years_ago <= 22:
                volume = random.randint(70, 100)
            else:
                volume = random.randint(35, 75)

            detected_noise = random.randint(30, 100)
            timestamp = make_aware(datetime.now() - timedelta(minutes=random.randint(1, 5000)))

            AudioAdjustmentRecord.objects.create(
                user=prefs,
                recommended_volume=volume,
                detected_noise=detected_noise,
                timestamp=timestamp
            )

    print(f"✅ Se han agregado hasta {n} usuarios nuevos de prueba.")