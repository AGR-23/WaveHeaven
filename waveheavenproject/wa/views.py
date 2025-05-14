from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import joblib
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, DeviceForm
from .models import Device
from wa.models import UserPreferences, Device, ExposureReport, AudioAdjustmentRecord, HearingRiskNotification, PartySession, ChatMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Importar modelo de usuario
import random
import string
from profiles.views import apply_profile_by_name

model = joblib.load('hearing_risk_model.pkl') # llamar el modelo de riesgo auditivo

def predict_user_risk(user): # funcion para predecir el riesgo auditivo con el modelo
    report = ExposureReport.objects.filter(user=user).last() #agarra el último informe de exposición
    if report:
        data = [[
            user.ideal_volume,
            user.last_adjusted_volume,
            int(user.microphone_active),
            user.low_freq_threshold,
            user.mid_freq_threshold,
            user.high_freq_threshold,
            report.total_exposure_time
        ]]
        risk = model.predict(data)[0] # Predecir el riesgo auditivo
        return ['Low', 'Medium', 'High'][risk]
    return 'Unknown'

from .spotify_api import (
    get_auth_url,
    get_token_from_code,
    get_current_playback,
)

def home(request):
    return render(request, 'index.html') 

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
            
        if user_prefs.in_party_mode and user_prefs.current_party:
            # Aumentar límite de volumen en modo fiesta
            ideal_volume = user_prefs.ideal_volume
            max_volume = ideal_volume + 20  # Permite +20% sobre el volumen ideal
            adjusted_volume = min(max(detected_volume, ideal_volume - 10), max_volume)
        else:
            # Ajustar el volumen en un rango de ±10 unidades
            ideal_volume = user_prefs.ideal_volume
            adjusted_volume = min(max(detected_volume, ideal_volume - 10), ideal_volume + 10)

        # Guardar el volumen ajustado en la base de datos
        user_prefs.last_adjusted_volume = adjusted_volume
        user_prefs.save()

        # Crear un registro en AudioAdjustmentRecord
        AudioAdjustmentRecord.objects.create(
            user=user_prefs,
            recommended_volume=int(adjusted_volume),  # Asegúrate de que sea un entero
            detected_noise=0,  # Puedes ajustar este valor según sea necesario
        )

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

@csrf_exempt
def user_register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        device_form = DeviceForm(request.POST)

        if user_form.is_valid() and device_form.is_valid():
            # Crear usuario
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            birthday = user_form.cleaned_data.get("birthday")

            # Crear UserPreferences
            user_prefs = UserPreferences.objects.create(
                user=user,
                name=user_form.cleaned_data.get("username"),
                email=user_form.cleaned_data.get("email"),
                birthday=birthday,
            )

            # Asignar microphone_active según lo recibido en el formulario
            microphone_access = request.POST.get("microphone_access")
            user_prefs.microphone_active = (microphone_access == "Sí")

            # Perfiles de audio por defecto
            user_prefs.audio_profiles = [
                {"name": "Music", "bass": 80, "mid": 60, "treble": 50, "environment": "Indoor"},
                {"name": "Podcast", "bass": 40, "mid": 85, "treble": 50, "environment": "Outdoor"},
                {"name": "Call", "bass": 50, "mid": 50, "treble": 50, "environment": "Indoor"},
                {"name": "Gaming", "bass": 70, "mid": 65, "treble": 75, "environment": "Gaming Room"},
                {"name": "Calls", "bass": 30, "mid": 95, "treble": 80, "environment": "Office"},
                {"name": "Relax", "bass": 60, "mid": 50, "treble": 40, "environment": "Quiet Space"},
                {"name": "Party!", "bass": 90, "mid": 70, "treble": 85, "environment": "Party"},
            ]
            user_prefs.save()

            # Guardar dispositivo (sin type ni headphone_compatibility)
            device = device_form.save(commit=False)
            device.user = user_prefs
            device.save()

            login(request, user)
            return redirect("hearing_test")

    else:
        user_form = UserRegisterForm()
        device_form = DeviceForm()

    return render(request, "register.html", {"user_form": user_form, "device_form": device_form})

@login_required
def create_party_session(request):
    if request.method == 'POST':
        user_prefs = UserPreferences.objects.get(user=request.user)
        session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        party = PartySession.objects.create(host=user_prefs, session_code=session_code)
        
        party.participants.add(user_prefs)

        # Apply "Party!" profile after creating the session
        apply_profile_by_name(request, "Party!")  # Assuming request is needed by the function

        return JsonResponse({'status': 'success', 'session_code': session_code})
    return JsonResponse({'status': 'error'}, status=400)

def hearing_test(request):
    user_prefs = UserPreferences.objects.get(user=request.user)
    
    if request.method == 'POST':
        low_volume = float(request.POST.get('low_volume', 50))
        mid_volume = float(request.POST.get('mid_volume', 50))
        high_volume = float(request.POST.get('high_volume', 50))

        # Actualizar los campos en UserPreferences
        user_prefs.low_freq_threshold = low_volume
        user_prefs.mid_freq_threshold = mid_volume
        user_prefs.high_freq_threshold = high_volume
        user_prefs.save()  # Guardar los cambios en la base de datos

        # Crear un registro en AudioAdjustmentRecord
        AudioAdjustmentRecord.objects.create(
            user=user_prefs,
            recommended_volume=(low_volume + mid_volume + high_volume) / 3,  # Volumen promedio
            detected_noise=0,  # Puedes ajustar este valor según sea necesario
        )

        return redirect('dashboard')  # Redirigir al dashboard después de la prueba

    return render(request, 'hearing_test.html')

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

    hearing_risk = predict_user_risk(user_prefs) # Predecir el riesgo auditivo del usuario

    return render(request, "dashboard.html", {
        "profiles": profiles,
        "hearing_risk": hearing_risk,
        "user_prefs": user_prefs,
        })

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
            user_prefs = UserPreferences.objects.get(user=request.user)
            if user_prefs.in_party_mode and user_prefs.current_party:
                # Actualizar configuración grupal
                party = user_prefs.current_party
                data = json.loads(request.body)
                
                party.group_bass = data.get('bass', party.group_bass)
                party.group_mid = data.get('mid', party.group_mid)
                party.group_treble = data.get('treble', party.group_treble)
                party.save()
                
                # Forzar actualización en todos los participantes
                for participant in party.participants.all():
                    participant.active_profile = "Party!"
                    participant.save(update_fields=['active_profile'])
                
                return JsonResponse({'status': 'success'})
            else:
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

                return JsonResponse({'status': 'success', 'applied_profile': new_profile})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def save_exposure_time(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exposure_time = data.get('exposure_time', 0)

            # Asegúrate de que exposure_time sea un entero
            try:
                exposure_time = int(exposure_time)
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid exposure_time'}, status=400)

            # Obtener las preferencias del usuario actual
            user_prefs = UserPreferences.objects.get(user=request.user)

            # Crear un nuevo informe de exposición
            exposure_report = ExposureReport.objects.create(
                user=user_prefs,
                total_exposure_time=exposure_time,
            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def record_hearing_risk(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        warning_type = data.get("warning_type", "Unknown Risk")
        exposure_threshold = data.get("exposure_threshold", 10)  # Default to 10 min

        if user.is_authenticated:
            user_prefs, _ = UserPreferences.objects.get_or_create(user=user)

            # Save the notification in the database
            notification = HearingRiskNotification.objects.create(
                user=user,
                warning_type=warning_type,
                exposure_threshold=exposure_threshold
            )

            return JsonResponse({"status": "success", "notification_id": notification.id}, status=201)
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

# -------------------- SPOTIFY --------------------

def spotify_login(request):
    return redirect(get_auth_url())

def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("❌ Código no proporcionado por Spotify.", status=400)

    try:
        token_data = get_token_from_code(code)
        token = token_data["access_token"]
        request.session["spotify_token"] = token
        return redirect("spotify_playback")  # Redirige a tu vista con Web SDK
    except Exception as e:
        # Muestra el error directamente en texto plano
        return HttpResponse(f"❌ Ocurrió un error durante la autenticación con Spotify:<br><pre>{str(e)}</pre>", status=500)

def spotify_playback(request):
    token = request.session.get("spotify_token")
    if not token:
        return redirect(get_auth_url())
    return render(request, "spotify_playback.html", {"token": token})

def spotify_player(request):
    token = request.session.get("spotify_token")
    if not token:
        return redirect(get_auth_url())
    return render(request, "spotify_player.html", {"token": token})

@login_required
def spotify_search_playback(request):
    token = request.session.get("spotify_token")
    if not token:
        return redirect("spotify_login")
    
    # Obtener perfiles personalizados del usuario
    user_prefs = UserPreferences.objects.get(user=request.user)
    profiles = user_prefs.get_audio_profiles()

    return render(request, "spotify_search_playback.html", {
        "token": token,
        "profiles": profiles
    })
    
    # Función interna para aplicar el perfil Party! directamente al modelo
def apply_profile_by_name_internal(user_prefs, profile_name):
    profiles = user_prefs.get_audio_profiles()
    profile = next(
        (p for p in profiles if str(p.get('name', '')).strip().lower() == profile_name.strip().lower()),
        None
    )
    if profile:
        user_prefs.active_profile = profile_name
        user_prefs.audio_settings = json.dumps(profile)
        user_prefs.save(update_fields=['active_profile', 'audio_settings'])
        
@login_required
@csrf_exempt
def create_party_session(request):
    if request.method == 'POST':
        user_prefs = UserPreferences.objects.get(user=request.user)
        session_code = str(random.randint(100000, 999999))
        party = PartySession.objects.create(
            host=user_prefs,  # Set the host here
            session_code=session_code,
            group_bass=90,
            group_mid=70,
            group_treble=85
        )
        party.participants.add(user_prefs) #make sure the host is added to the participants list
        #  Get the list of participants
        participants = list(party.participants.values_list('user__username', flat=True))

        user_prefs.in_party_mode = True
        user_prefs.current_party = party
        user_prefs.save()

        # apply_profile_by_name_internal(user_prefs, "Party!")  # You can keep this if it's needed

        return JsonResponse({'status': 'success', 'session_code': session_code, 'participants': participants, 'host': user_prefs.user.username}) #send the host username in the response
    return JsonResponse({'status': 'error'}, status=400)

# views.py (en join_party_session)
@login_required
@csrf_exempt
def join_party_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_code = data.get('session_code')
        try:
            party = PartySession.objects.get(session_code=session_code, is_active=True)
            user_prefs = UserPreferences.objects.get(user=request.user)
            user_prefs.in_party_mode = True
            user_prefs.current_party = party
            user_prefs.save()
            party.participants.add(user_prefs)
            
             #  Get the list of participants
            participants = list(party.participants.values_list('user__username', flat=True))

            # Aplicar el perfil "Party" al usuario que se une
            from profiles.views import apply_profile_by_name
            # Simular una request para apply_profile_by_name para el usuario actual
           

            return JsonResponse({'status': 'success', 'session_code': session_code, 'participants': participants})
        except PartySession.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Código inválido'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def update_party_settings(request):
    if request.method == 'POST':
        user_prefs = UserPreferences.objects.get(user=request.user)
        if user_prefs.current_party and user_prefs.current_party.host == user_prefs:
            data = json.loads(request.body)
            party = user_prefs.current_party
            party.group_bass = data.get('bass', party.group_bass)
            party.group_mid = data.get('mid', party.group_mid)
            party.group_treble = data.get('treble', party.group_treble)
            party.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@csrf_exempt
def leave_party(request):
    if request.method == 'POST':
        user_prefs = UserPreferences.objects.get(user=request.user)
        user_prefs.in_party_mode = False
        user_prefs.current_party = None
        user_prefs.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def send_chat_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content')
            user_prefs = UserPreferences.objects.get(user=request.user)
            party_session = user_prefs.current_party

            if not party_session:
                return JsonResponse({'status': 'error', 'message': 'User is not in a party.'}, status=400)

            message = ChatMessage.objects.create(
                user=user_prefs,
                party_session=party_session,
                content=content
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_chat_messages(request, party_id):
    try:
        party_session = PartySession.objects.get(id=party_id)
        messages = ChatMessage.objects.filter(party_session=party_session).order_by('timestamp')[:100]  # Get last 100 messages
        messages_list = [{
            'user': msg.user.user.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
        } for msg in messages]
        return JsonResponse({'status': 'success', 'messages': messages_list})
    except PartySession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Party session not found.'}, status=404)