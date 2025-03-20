import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from wa.models import UserPreferences
from .models import UserStatistics, ExposureReport
from .forms import SoundProfileForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from wa.models import UserPreferences, ExposureReport, AudioAdjustmentRecord, HearingRiskNotification
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
import json
from wa.models import UserPreferences, ExposureReport, AudioAdjustmentRecord, HearingRiskNotification
from profiles.models import UserStatistics

def profiles_page(request):
    return render(request, 'sound_profiles.html')

@csrf_exempt
@login_required
def apply_profile(request, profile_id):
    user_prefs = get_object_or_404(UserPreferences, user=request.user)
    profiles = user_prefs.get_audio_profiles()

    if profile_id < 0 or profile_id >= len(profiles):
        return JsonResponse({'status': 'error', 'message': 'Profile not found'}, status=404)

    # Guardar el perfil aplicado como el activo
    user_prefs.audio_settings = json.dumps(profiles[profile_id])
    user_prefs.save(update_fields=['audio_settings'])

    return JsonResponse({'status': 'success', 'applied_profile': profiles[profile_id]})

@csrf_exempt
@login_required
def list_profiles(request):
    user_prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
    if not user_prefs.audio_profiles or len(user_prefs.audio_profiles) < 3:
        user_prefs.audio_profiles = [
           {"name": "Music", "bass": 80, "mid": 60, "treble": 50, "environment": "Indoor"},
            {"name": "Podcast", "bass": 40, "mid": 85, "treble": 50, "environment": "Outdoor"},
            {"name": "Movies", "bass": 90, "mid": 50, "treble": 70, "environment": "Home Theater"},
            {"name": "Gaming", "bass": 70, "mid": 65, "treble": 75, "environment": "Gaming Room"},
            {"name": "Calls", "bass": 30, "mid": 95, "treble": 80, "environment": "Office"},
            {"name": "Relax", "bass": 60, "mid": 50, "treble": 40, "environment": "Quiet Space"},
        ]
        user_prefs.save(update_fields=['audio_profiles'])

    return JsonResponse({"profiles": user_prefs.audio_profiles})


@csrf_exempt
@login_required
def delete_profile(request, profile_index):
    if request.method == 'POST':
        try:
            user_prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
            profiles = user_prefs.get_audio_profiles()
            if profile_index < 0 or profile_index >= len(profiles):
                return JsonResponse({'status': 'error', 'message': 'Invalid profile index'}, status=400)
            deleted_profile = profiles.pop(profile_index)
            user_prefs.save_audio_profiles(profiles)
            return JsonResponse({'status': 'success', 'deleted_profile': deleted_profile})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def create_profile(request):
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            user_prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
            profiles = user_prefs.get_audio_profiles()

            if not all(k in data for k in ['name', 'bass', 'mid', 'treble', 'environment']):
                return JsonResponse({'status': 'error', 'message': 'Missing fields'}, status=400)

            profiles.append(data)
            user_prefs.save_audio_profiles(profiles)

            return JsonResponse({'status': 'success', 'profile': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
@login_required
def edit_profile(request, profile_index):
    """
    Actualiza un perfil existente en la posición profile_index
    """
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            user_prefs, _ = UserPreferences.objects.get_or_create(user=request.user)

            profiles = user_prefs.audio_profiles
            if profile_index < 0 or profile_index >= len(profiles):
                return JsonResponse({'status': 'error', 'message': 'Invalid profile index'}, status=400)

            # Actualizamos el perfil existente
            profiles[profile_index] = data
            user_prefs.audio_profiles = profiles
            user_prefs.save(update_fields=['audio_profiles'])

            return JsonResponse({'status': 'success', 'updated_profile': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def user_statistics(request):
    # Obtener las preferencias del usuario
    user_prefs = get_object_or_404(UserPreferences, user=request.user)

    # Calcular el tiempo total de exposición
    exposure_reports = ExposureReport.objects.filter(user=user_prefs)
    total_exposure_time = sum(report.total_exposure_time for report in exposure_reports)

    # Calcular el tiempo promedio diario de exposición
    if exposure_reports:
        average_daily_exposure = total_exposure_time / 7  # Promedio diario en la última semana
    else:
        average_daily_exposure = 0

    # Obtener el número de notificaciones de riesgo
    risk_notifications = HearingRiskNotification.objects.filter(user=user_prefs).count()

    # Obtener datos para el gráfico de volumen
    audio_adjustments = AudioAdjustmentRecord.objects.filter(user=user_prefs).order_by('timestamp')
    volume_data = [adjustment.recommended_volume for adjustment in audio_adjustments]
    volume_labels = [adjustment.timestamp.strftime('%H:%M') for adjustment in audio_adjustments]

    # Convertir los datos a JSON
    volume_data_json = json.dumps(volume_data, cls=DjangoJSONEncoder)
    volume_labels_json = json.dumps(volume_labels, cls=DjangoJSONEncoder)

    # Consejos de salud auditiva
    health_tips = []
    if risk_notifications > 0:
        health_tips.append("You have had high volume peaks. Consider reducing the volume in noisy environments.")
    if total_exposure_time > 120:  # Más de 2 horas
        health_tips.append("Remember to take 5-minute breaks every hour when listening to audio for extended periods.")

    return render(request, 'statistics.html', {
        'total_exposure_time': total_exposure_time,
        'average_daily_exposure': round(average_daily_exposure, 1),
        'risk_notifications': risk_notifications,
        'volume_data_json': volume_data_json,
        'volume_labels_json': volume_labels_json,
        'health_tips': health_tips,
    })

@login_required
def apply_profile_by_name(request, profile_name):
    user_prefs = UserPreferences.objects.get(user=request.user)
    profile = next((p for p in user_prefs.audio_profiles if p['name'].lower() == profile_name.lower()), None)

    if profile:
        return JsonResponse({'status': 'success', 'profile': profile})

    return JsonResponse({'error': 'Profile not found'}, status=404)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserPreferences

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
import json
from wa.models import UserPreferences, AudioAdjustmentRecord, HearingRiskNotification

@csrf_exempt
@login_required
def user_profile(request):
    # Obtener las preferencias del usuario
    user_prefs = get_object_or_404(UserPreferences, user=request.user)

    # Calcular la edad
    if user_prefs.birthday:
        today = date.today()
        age = today.year - user_prefs.birthday.year - ((today.month, today.day) < (user_prefs.birthday.month, user_prefs.birthday.day))
    else:
        age = "N/A"

    # Definir rangos ideales según la edad
    def get_ideal_ranges(age):
        if age == "N/A":
            return None  # No se puede determinar el rango sin la edad
        elif age < 18:
            return {"low": (20.0, 40.0), "mid": (30.0, 50.0), "high": (40.0, 60.0)}  # Rangos para menores de 18
        elif 18 <= age <= 40:
            return {"low": (25.0, 45.0), "mid": (35.0, 55.0), "high": (45.0, 65.0)}  # Rangos para adultos jóvenes
        elif 41 <= age <= 60:
            return {"low": (30.0, 50.0), "mid": (40.0, 60.0), "high": (50.0, 70.0)}  # Rangos para adultos mayores
        else:
            return {"low": (35.0, 55.0), "mid": (45.0, 65.0), "high": (55.0, 75.0)}  # Rangos para mayores de 60

    # Obtener los rangos ideales según la edad
    ideal_ranges = get_ideal_ranges(age)

    # Lógica para determinar el estado del último test de audición
    last_test_status = "No Data"
    if ideal_ranges and (user_prefs.low_freq_threshold != 50.0 or user_prefs.mid_freq_threshold != 50.0 or user_prefs.high_freq_threshold != 50.0):
        low_in_range = ideal_ranges["low"][0] <= user_prefs.low_freq_threshold <= ideal_ranges["low"][1]
        mid_in_range = ideal_ranges["mid"][0] <= user_prefs.mid_freq_threshold <= ideal_ranges["mid"][1]
        high_in_range = ideal_ranges["high"][0] <= user_prefs.high_freq_threshold <= ideal_ranges["high"][1]

        if low_in_range and mid_in_range and high_in_range:
            last_test_status = "Good"
        else:
            last_test_status = "Needs Attention"

    # Obtener las estadísticas del usuario
    user_stats = UserStatistics.objects.filter(user=user_prefs).first()
    total_time = user_stats.get_total_exposure_time() if user_stats else 0
    sessions_this_week = user_stats.get_sessions_last_week() if user_stats else 0

    # Obtener los ajustes de volumen recientes
    audio_adjustments = AudioAdjustmentRecord.objects.filter(user=user_prefs).order_by('-timestamp')[:10]
    volume_data = [adjustment.recommended_volume for adjustment in audio_adjustments]
    volume_labels = [adjustment.timestamp.strftime('%H:%M') for adjustment in audio_adjustments]

    # Obtener las notificaciones de riesgo
    risk_notifications = HearingRiskNotification.objects.filter(user=user_prefs).order_by('-date_and_time')[:5]

    # Pasar los datos a la plantilla
    context = {
        "user_prefs": user_prefs,
        "age": age,
        "preferred_volume": round(user_prefs.ideal_volume, 1),
        "total_time": total_time,
        "sessions_this_week": sessions_this_week,
        "volume_data": json.dumps(volume_data, cls=DjangoJSONEncoder),
        "volume_labels": json.dumps(volume_labels, cls=DjangoJSONEncoder),
        "risk_notifications": risk_notifications,
        "last_test_status": last_test_status,
        "low_freq_threshold": user_prefs.low_freq_threshold,
        "mid_freq_threshold": user_prefs.mid_freq_threshold,
        "high_freq_threshold": user_prefs.high_freq_threshold,
        "ideal_ranges": ideal_ranges,  # Pasar los rangos ideales a la plantilla (opcional)
    }
    
    return render(request, "profile.html", context)