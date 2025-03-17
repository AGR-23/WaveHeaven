from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, DeviceForm
from .models import Device
from wa.models import UserPreferences, Device
from django.contrib.auth.models import User  # Importar modelo de usuario

def home(request):
    return render(request, 'index.html')  # Asegúrate de que el archivo index.html esté en la carpeta templates

@csrf_exempt
def toggle_microphone(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])  # Solo permitir POST

    try:
        data = json.loads(request.body)
        is_active = data.get('active', False)

        # Si el usuario no está autenticado, usa un usuario por defecto (cambiar según necesidad)
        if request.user.is_authenticated:
            user_prefs, created = UserPreferences.objects.get_or_create(user=request.user)
        else:
            user_prefs, created = UserPreferences.objects.get_or_create(user=User.objects.first())  # Usa el primer usuario de la BD

        user_prefs.microphone_active = is_active
        user_prefs.save()

        return JsonResponse({'status': 'success', 'microphone_active': user_prefs.microphone_active})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def adjust_volume(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])  # Solo permitir POST

    try:
        data = json.loads(request.body)
        detected_volume = float(data.get('volume', 50.0))  # Volumen detectado desde el frontend

        # Si el usuario no está autenticado, usa un usuario por defecto
        if request.user.is_authenticated:
            user_prefs, created = UserPreferences.objects.get_or_create(user=request.user)
        else:
            user_prefs, created = UserPreferences.objects.get_or_create(user=User.objects.first())  # Usa el primer usuario

        # Ajustar el volumen en un rango de ±10 unidades
        ideal_volume = user_prefs.ideal_volume
        adjusted_volume = min(max(detected_volume, ideal_volume - 10), ideal_volume + 10)

        # Guardar el volumen ajustado en la base de datos
        user_prefs.last_adjusted_volume = adjusted_volume
        user_prefs.save()

        return JsonResponse({'adjusted_volume': adjusted_volume})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def set_sound_category(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        data = json.loads(request.body)
        category = data.get('category', 'music')

        # Obtener preferencias del usuario (como en tus otras vistas)
        if request.user.is_authenticated:
            user_prefs = UserPreferences.objects.get(user=request.user)
        else:
            user_prefs = UserPreferences.objects.get(user=User.objects.first())

        user_prefs.sound_category = category
        user_prefs.save()

        return JsonResponse({'status': 'success', 'category': user_prefs.sound_category})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def user_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        device_form = DeviceForm(request.POST)
        
        if user_form.is_valid() and device_form.is_valid():
            # Guardar el usuario
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            # Obtener la fecha de nacimiento desde el formulario
            birthday = user_form.cleaned_data.get("birthday")

            # Calcular la edad
            today = date.today()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

            # Crear UserPreferences para el usuario con perfiles por defecto
            user_prefs = UserPreferences.objects.create(
                user=user,
                name=user_form.cleaned_data.get("username"),
                email=user_form.cleaned_data.get("email"),
                birthday=birthday,  # Guardar la fecha de nacimiento
            )

            # Agregar perfiles de audio por defecto
            user_prefs.audio_profiles = [
                {
                    "name": "Music",
                    "bass": 80,
                    "mid": 60,
                    "treble": 50,
                    "environment": "Indoor"
                },
                {
                    "name": "Podcast",
                    "bass": 40,
                    "mid": 85,
                    "treble": 60,
                    "environment": "Outdoor"
                }
            ]
            user_prefs.save()

            # Guardar el dispositivo asociado al UserPreferences
            device = device_form.save(commit=False)
            device.user = user_prefs  # Asignar UserPreferences en lugar de User
            device.save()

            # Iniciar sesión automáticamente después del registro
            login(request, user)

            return redirect("hearing_test")

    else:
        user_form = UserRegisterForm()
        device_form = DeviceForm()

    return render(request, "register.html", {"user_form": user_form, "device_form": device_form})

def hearing_test(request):
    if request.method == "POST":
        low_volume = request.POST.get("low_volume", 50)
        mid_volume = request.POST.get("mid_volume", 50)
        high_volume = request.POST.get("high_volume", 50)

        if request.user.is_authenticated:
            user_prefs, created = UserPreferences.objects.get_or_create(user=request.user)
            # Guardamos el volumen promedio de las pruebas como el ideal
            user_prefs.ideal_volume = (int(low_volume) + int(mid_volume) + int(high_volume)) / 3
            user_prefs.save()

            return redirect("dashboard")  # Redirigir al dashboard

    return render(request, "hearing_test.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirects to profiles after login
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def user_dashboard(request):
    user_prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
    profiles = user_prefs.get_audio_profiles()
    return render(request, "dashboard.html", {"profiles": profiles})

# implementar la vista para mostrar el ecualizador FR:O7
@login_required
def equalizer_view(request):
    user_prefs = UserPreferences.objects.get(user=request.user)
    return render(request, 'equalizer.html', {'profiles': user_prefs.get_audio_profiles()})

# implementar la vista para guardar la configuración del ecualizador FR:O7
@csrf_exempt
@login_required
def save_equalizer_settings(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile_name = data.get('profile_name', 'Custom')

            # Obtener las preferencias del usuario
            user_prefs = UserPreferences.objects.get(user=request.user)

            # Crear un nuevo perfil de sonido con todas las frecuencias
            new_profile = {
                'name': profile_name,
                'bass': data.get('bass', 50),
                'mid': data.get('mid', 50),
                'treble': data.get('treble', 50),
                'environment': 'Custom'
            }

            # Añadir el nuevo perfil a la lista de perfiles de audio
            profiles = user_prefs.get_audio_profiles()
            profiles.append(new_profile)

            # Guardar los perfiles actualizados
            user_prefs.save_audio_profiles(profiles)

            return JsonResponse({'status': 'success', 'profile': new_profile})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)