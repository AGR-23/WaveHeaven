from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, DeviceForm
from .models import Device
from wa.models import UserPreferences
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
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            # Guardar la información del dispositivo
            device = device_form.save(commit=False)
            device.user = user
            device.save()

            login(request, user)  # Autenticamos automáticamente después del registro
            return redirect("dashboard")
    else:
        user_form = UserRegisterForm()
        device_form = DeviceForm()
    return render(request, "register.html", {"user_form": user_form, "device_form": device_form})

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

def user_dashboard(request):
    return render(request, "dashboard.html")