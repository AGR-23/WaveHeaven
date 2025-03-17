import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from wa.models import UserPreferences
from .models import UserStatistics, ExposureReport
from .forms import SoundProfileForm

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
    user_prefs, created = UserPreferences.objects.get_or_create(user=request.user)
    if created or not user_prefs.audio_profiles:
        user_prefs.audio_profiles = [
            {"name": "Music", "bass": 80, "mid": 60, "treble": 50, "environment": "Inside"},
            {"name": "Podcast", "bass": 40, "mid": 85, "treble": 65, "environment": "Outside"}
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
    # Ensure we get the UserPreferences instance
    user_prefs = get_object_or_404(UserPreferences, user=request.user)

    # Retrieve the user's exposure report (if it exists)
    exposure_report = ExposureReport.objects.filter(user=user_prefs).first()

    # Pass data to the template
    return render(request, 'statistics.html', {
        'user_prefs': user_prefs,
        'exposure_report': exposure_report,
    })
    
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def apply_profile_by_name(request, profile_name):
    user_prefs = UserPreferences.objects.get(user=request.user)
    profile = next((p for p in user_prefs.audio_profiles if p['name'] == profile_name), None)
    
    if profile:
        # Aquí aplicarías los ajustes al audio (ej: guardar en sesión o modelo)
        return JsonResponse({'status': 'success', 'profile': profile})
    return JsonResponse({'error': 'Profile not found'}, status=404)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserPreferences

@csrf_exempt
@login_required
def user_profile(request):
    user_prefs = get_object_or_404(UserPreferences, user=request.user)

    # Calculate age
    if user_prefs.birthday:
        today = date.today()
        age = today.year - user_prefs.birthday.year - ((today.month, today.day) < (user_prefs.birthday.month, user_prefs.birthday.day))
    else:
        age = "N/A"

    # Retrieve user statistics
    user_stats = UserStatistics.objects.filter(user=user_prefs).first()
    total_time = user_stats.total_exposure_time if user_stats else 0
    sessions_this_week = user_stats.get_sessions_last_week() if user_stats else 0

    # Retrieve hearing test results
    hearing_report = ExposureReport.objects.filter(user=user_prefs).order_by('-date').first()
    hearing_data = hearing_report.frequency_data if hearing_report else []

    # Debugging
    print(f"Total Time: {total_time}, Sessions: {sessions_this_week}, Hearing Data: {hearing_data}")

    context = {
        "user_prefs": user_prefs,
        "age": age,
        "preferred_volume": round(user_prefs.ideal_volume, 1),
        "total_time": total_time,
        "sessions_this_week": sessions_this_week,
        "hearing_report": hearing_report,
        "hearing_data": hearing_data,
    }
    
    return render(request, "profile.html", context)