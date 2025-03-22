       // Initialize Lucide icons
       lucide.createIcons();
    
       // Variables for audio processing
       let audioContext;
       let analyser;
       let microphone;
       let dataArray;
       let isListening = false;
       let ambientVolumeDisplay = document.getElementById("ambientVolumeDisplay");
       let activeTabId = null;
       let globalAudioContext = new (window.AudioContext || window.webkitAudioContext)();
       let gainNode = globalAudioContext.createGain(); // Volume controller
       let sourceNode = globalAudioContext.createGain(); // Volume controller
       let exposureStartTime = null;
       let exposureTime = 0; // Tiempo de exposición acumulado en milisegundos
       let exposureThreshold = 5 * 1000; // 5 seconds in milliseconds (just to test later it should be 10 minutes)
       let warningTriggered = false;
       let eqFilters = [];
   
       const frequencies = [60, 250, 1000, 4000, 16000];
   
       const selectSoundProfile = document.querySelector("#soundProfile");
   
       selectSoundProfile.addEventListener("change", function (e) {
           e.preventDefault();
           e.stopImmediatePropagation();
           // updateEqualizer();
       });
   
       // Initialize equalizer
       setupEqualizer();
       filledSoundProfile();
   
       // Function to get filled sound profile
       async function filledSoundProfile() {
           try {
               const response = await fetch('/list_profiles/');
               const data = await response.json();
               const selectElement = document.getElementById("soundProfile");
   
               // Limpiar opciones previas
               selectElement.innerHTML = "";
   
               if (data.profiles.length === 0) {
                   selectElement.innerHTML = `<option disabled>No sound profiles available</option>`;
                   return;
               }
   
               data.profiles.forEach(profile => {
                   let option = document.createElement("option");
                   option.value = profile.name;
                   option.textContent = profile.name;
                   selectElement.appendChild(option);
               });
   
               // Aplicar automáticamente el primer perfil si está disponible
               if (data.profiles.length > 0) {
                   applySoundProfile(data.profiles[0].name);
               }
   
           } catch (error) {
               console.error("Error loading sound profiles:", error);
           }
       }
   
       // Function to get CSRF token
       function getCookie(name) {
           let cookieValue = null;
           if (document.cookie && document.cookie !== '') {
               const cookies = document.cookie.split(';');
               for (let i = 0; i < cookies.length; i++) {
                   const cookie = cookies[i].trim();
                   if (cookie.startsWith(name + '=')) {
                       cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                       break;
                   }
               }
           }
           return cookieValue;
       }
   
       // Capture audio from tabs
       async function captureAudioFromTabs() {
           try {
               const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
               const audioTrack = stream.getAudioTracks()[0];
   
               if (!audioTrack) {
                   throw new Error("No audio detected in the selected tab.");
               }
   
               const audioSource = globalAudioContext.createMediaStreamSource(new MediaStream([audioTrack]));
   
               audioSource.connect(gainNode).connect(globalAudioContext.destination);
               eqFilters.forEach(filter => gainNode.connect(filter));
               eqFilters[eqFilters.length - 1].connect(globalAudioContext.destination);
   
               console.log("Capturing audio from active tab...");
               showNotification("Audio capture started", "success");
           } catch (error) {
               console.error("Could not capture tab audio:", error);
               showNotification("Make sure to share a tab with audio when prompted", "error");
           }
       }
   
       // Start listening to ambient sound
       async function startListening() {
           if (isListening) return;
           isListening = true;
   
           // Iniciar el contador de tiempo de exposición
           exposureStartTime = Date.now();
           console.log('time:', exposureStartTime);
           exposureTime = exposureStartTime;
   
           try {
               const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
               audioContext = new AudioContext();
               analyser = audioContext.createAnalyser();
               microphone = audioContext.createMediaStreamSource(stream);
               microphone.connect(analyser);
               analyser.fftSize = 256;
               dataArray = new Uint8Array(analyser.frequencyBinCount);
               analyzeAudio();
   
               // Also capture tab audio
               await captureAudioFromTabs();
   
               // Update UI
               document.querySelector('button[onclick="startListening()"]').classList.add('bg-green-600');
               document.querySelector('button[onclick="startListening()"]').classList.remove('bg-blue-600');
           } catch (error) {
               console.error("Error accessing microphone:", error);
               showNotification("Could not access microphone. Check permissions.", "error");
               isListening = false;
           }
       }
   
       // Stop listening
       function stopListening() {
           if (!isListening) return;
           isListening = false;
   
           exposureStartTime = exposureTime;
           exposureTime = 0;
           exposureTimee = Date.now();
   
           console.log('start time:', exposureStartTime);
           console.log('finish time:', exposureTimee);
           console.log('final time:', exposureTimee-exposureStartTime);
   
           // Calcular el tiempo de exposición acumulado
           if (exposureStartTime != null) {
               exposureTime = exposureTimee-exposureStartTime;
               exposureStartTime = null;
           }

           console.log('exposureTime: ', exposureTime)
       
   
           // Actualizar la visualización del tiempo de exposición
           updateExposureTimeDisplay();
   
           // Enviar el tiempo de exposición al servidor
           sendExposureTimeToServer();
   
           if (audioContext) {
               audioContext.close();
           }
           ambientVolumeDisplay.textContent = "Ambient Volume: --";
           document.getElementById('volumeIndicator').style.width = "0%";
   
           // Update UI
           document.querySelector('button[onclick="startListening()"]').classList.remove('bg-green-600');
           document.querySelector('button[onclick="startListening()"]').classList.add('bg-blue-600');
   
           showNotification("Microphone deactivated", "info");
       }
   
       // Analyze audio
       function analyzeAudio() {
           if (!isListening) return;
           analyser.getByteFrequencyData(dataArray);
   
           let volume = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;
   
           ambientVolumeDisplay.textContent = `Ambient Volume: ${volume.toFixed(0)}`;
   
           // Update volume indicator
           const volumePercentage = Math.min(100, (volume / 255) * 100);
           document.getElementById('volumeIndicator').style.width = `${volumePercentage}%`;
   
           // Change color based on volume
           if (volumePercentage > 80) {
               document.getElementById('volumeIndicator').className = 'bg-red-600 h-4 rounded-full transition-all duration-300';
           } else if (volumePercentage > 60) {
               document.getElementById('volumeIndicator').className = 'bg-yellow-500 h-4 rounded-full transition-all duration-300';
           } else {
               document.getElementById('volumeIndicator').className = 'bg-blue-600 h-4 rounded-full transition-all duration-300';
           }
   
           adjustVolumeBasedOnAmbient(volume);
           checkNoiseExposure(volume);
   
           requestAnimationFrame(analyzeAudio);
       }
   
       function showNotification(message, type = 'info') {
           const notification = document.createElement('div');
           notification.className = `notification ${type}`;
           notification.textContent = message;
   
           // Agregar la notificación al cuerpo del documento
           document.body.appendChild(notification);
   
           // Eliminar la notificación después de unos segundos
           setTimeout(() => {
               notification.remove();
           }, 3000);  // La notificación desaparece después de 3 segundos
       }
   
       // Adjust volume based on ambient noise
       async function adjustVolumeBasedOnAmbient(ambientVolume) {
           await ensureAudioContextIsRunning();
   
           const soundProfile = document.getElementById('soundProfile');
           const category = soundProfile ? soundProfile.value : 'music';
   
           let newVolume;
   
           switch (category) {
               case 'Music':
                   newVolume = ambientVolume > 50
                       ? Math.max(0.3, 1.0 - (ambientVolume - 50) / 80)
                       : 1.0;
                   break;
               case 'Podcast':
                   newVolume = ambientVolume > 50
                       ? Math.max(0.4, 0.8 - (ambientVolume - 50) / 120)
                       : 0.8;
                   break;
               case 'Call':
                   newVolume = ambientVolume > 50
                       ? Math.max(0.5, 1.2 - (ambientVolume - 50) / 90)
                       : 1.0;
                   break;
               default:
                   newVolume = 1.0;
           }
   
           newVolume = Math.max(0.1, Math.min(1, newVolume));
   
           gainNode.gain.cancelScheduledValues(globalAudioContext.currentTime);
           gainNode.gain.setTargetAtTime(newVolume, globalAudioContext.currentTime, 0.5);
   
           const volumeDisplay = document.getElementById("tabVolumeDisplay");
           if (volumeDisplay) {
               volumeDisplay.textContent = `${Math.round(newVolume * 100)}%`;
   
               // Change color based on volume
               if (newVolume < 0.3) {
                   volumeDisplay.className = 'font-semibold text-red-500';
               } else if (newVolume < 0.6) {
                   volumeDisplay.className = 'font-semibold text-yellow-500';
               } else {
                   volumeDisplay.className = 'font-semibold text-green-500';
               }
           }
       }
   
       // Ensure audio context is running
       async function ensureAudioContextIsRunning() {
           if (globalAudioContext.state === 'suspended') {
               await globalAudioContext.resume();
               console.log('AudioContext resumed');
           }
       }
   
       // Check for prolonged noise exposure
       function checkNoiseExposure(ambientVolume) {
           const dBThreshold = 85; // 85 dB warning limit
   
           if (ambientVolume >= dBThreshold) {
               if (!exposureStartTime) {
                   exposureStartTime = Date.now(); // Start tracking
               }
   
               let elapsedTime = Date.now() - exposureStartTime;
               if (elapsedTime >= exposureThreshold && !warningTriggered) {
                   console.log('Warning: High noise exposure detected');
                   triggerWarning();
                   warningTriggered = true; // Prevent multiple warnings
               }
           } else {
               exposureStartTime = null; // Reset if volume drops
               warningTriggered = false;
           }
       }
   
       // Trigger warning notification
       function triggerWarning() {
           if (Notification.permission === "granted") {
               new Notification("⚠ High Noise Exposure", {
                   body: "You've been exposed to high noise levels (>85 dB) for too long. Consider lowering the volume or taking a break.",
                   icon: "/static/images/warning-icon.png"
               });
           } else if (Notification.permission !== "denied") {
               Notification.requestPermission().then(permission => {
                   if (permission === "granted") {
                       triggerWarning();
                   }
               });
           } else {
               showNotification("High Noise Exposure Warning: You've been listening to loud sounds for too long!", "warning");
           }
           
           sendRiskNotification();
       }

       async function sendRiskNotification() { //just trying to save to db
           const csrfToken = getCookie("csrftoken");
       
           try {
               const response = await fetch("/record_hearing_risk/", {
                   method: "POST",
                   headers: {
                       "Content-Type": "application/json",
                       "X-CSRFToken": csrfToken,
                   },
                   body: JSON.stringify({
                       warning_type: "High Noise Exposure",
                       exposure_threshold: 10, // Example threshold
                   }),
               });
       
               const data = await response.json();
               if (data.status === "success") {
                   console.log("Hearing risk notification recorded successfully:", data);
               } else {
                   console.error("Failed to record hearing risk:", data.message);
               }
           } catch (error) {
               console.error("Error sending risk notification:", error);
           }
       }
   
       // Setup equalizer
       async function setupEqualizer() {
           eqFilters = frequencies.map((freq, index) => {
               const filter = globalAudioContext.createBiquadFilter();
               filter.type = "peaking";
               filter.frequency.value = freq;
               filter.Q.value = 1.414;
               filter.gain.value = 0;
               return filter;
           });
   
           // Chain filters
           for (let i = 0; i < eqFilters.length - 1; i++) {
               eqFilters[i].connect(eqFilters[i + 1]);
           }
   
           // Connect gain node to first filter
           gainNode.connect(eqFilters[0]);
   
           // Connect last filter to destination
           eqFilters[eqFilters.length - 1].connect(globalAudioContext.destination);
       }
   
       // Update equalizer when slider changes
       function updateEqualizer(frequency, value) {
           const index = frequencies.indexOf(frequency);
           if (index !== -1) {
               eqFilters[index].gain.setTargetAtTime(parseFloat(value), globalAudioContext.currentTime, 0.1);
   
               // Actualizar visualización
               document.getElementById(`eq-value-${frequency}`).textContent = `${value} dB`;
   
               // Mapear de -30 a 30 dB en porcentaje de 0% a 100%
               const heightPercentage = ((parseFloat(value) + 30) / 60) * 100;
               document.getElementById(`eq-level-${frequency}`).style.height = `${heightPercentage}%`;
           }
       }
   
       // Update master volume
       function updateMasterVolume(value) {
           const volumeValue = parseFloat(value) / 100;
           gainNode.gain.setTargetAtTime(volumeValue, globalAudioContext.currentTime, 0.1);
           document.getElementById('masterVolumeValue').textContent = `${value}%`;
       }
   
       // Apply equalizer presets
       function applyPreset(preset) {
           let values = [];
   
           switch (preset) {
               case 'flat':
                   values = [0, 0, 0, 0, 0];
                   break;
               case 'bass':
                   values = [15, 8, 0, -2, -5];
                   break;
               case 'vocal':
                   values = [-5, 0, 10, 5, -5];
                   break;
               case 'treble':
                   values = [-10, -5, 0, 10, 15];
                   break;
           }
   
           // Apply values to sliders and update equalizer
           frequencies.forEach((freq, index) => {
               const slider = document.getElementById(`eq${freq}`);
               slider.value = values[index];
               updateEqualizer(freq, values[index]);
           });
   
           showNotification(`Applied ${preset} preset`, "success");
       }
   
       // Apply sound profile
       async function applySoundProfile(profileName = null) {
   
           try {
               if (!profileName) {
                   profileName = document.getElementById("soundProfile").value;
               }
   
               const response = await fetch(`/apply_profile_by_name/${profileName}/`);
               const data = await response.json();
   
               if (data.status === "success") {
                   console.log(`Applying profile: ${profileName}`, data.profile);
   
                   // Aplicar ajustes del perfil al ecualizador
                   if (data.profile.bass !== undefined) {
                       updateEqualizer(60, data.profile.bass / 2 - 25);
                       document.getElementById('eq60').value = data.profile.bass / 2 - 25;
                   }
                   if (data.profile.mid !== undefined) {
                       updateEqualizer(1000, data.profile.mid / 2 - 25);
                       document.getElementById('eq1000').value = data.profile.mid / 2 - 25;
                   }
                   if (data.profile.treble !== undefined) {
                       updateEqualizer(16000, data.profile.treble / 2 - 25);
                       document.getElementById('eq16000').value = data.profile.treble / 2 - 25;
                   }
               }
   
           } catch (error) {
               console.error("Error applying profile:", error)
           }
       }
   
       // Update exposure time display
       function updateExposureTimeDisplay() {
           const exposureTimeDisplay = document.getElementById("exposureTimeDisplay");
           if (exposureTimeDisplay) {
               const seconds = Math.floor(exposureTime / 1000);  // Convertir milisegundos a segundos
               exposureTimeDisplay.textContent = `Exposure Time: ${seconds} seconds`;
           } else {
               console.error('Element with ID "exposureTimeDisplay" not found');
           }
       }
   
       async function sendExposureTimeToServer() {
           const csrfToken = getCookie('csrftoken');
           console.log('exposureTime to send: ', exposureTime);
           const exposureTimeInMinutes = Math.floor(exposureTime / 60000);
           console.log('exposureTime minutos conversion: ', exposureTimeInMinutes);
   
           try {
               const response = await fetch('/save_exposure_time/', {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                       'X-CSRFToken': csrfToken,
                   },
                   body: JSON.stringify({
                       exposure_time: exposureTimeInMinutes,  // Asegúrate de que este valor sea correcto
                   }),
               });
   
               if (response.ok) {
                   console.log('Exposure time saved successfully');
                   console.log('Exposure time to send:', exposureTimeInMinutes);
               } else {
                   console.error('Failed to save exposure time');
               }
           } catch (error) {
               console.error('Error saving exposure time:', error);
           }
       }
   
       // Dark mode toggle
       document.getElementById('darkModeToggle').addEventListener('click', () => {
           const isDark = document.documentElement.classList.toggle('dark');
           localStorage.setItem('theme', isDark ? 'dark' : 'light');
       });
   
       // Check for saved theme preference
       const savedTheme = localStorage.getItem('theme');
       if (savedTheme === 'dark') {
           document.documentElement.classList.add('dark');
       }
   
       // Initialize equalizer display
       frequencies.forEach(freq => {
           updateEqualizer(freq, 0);
       });