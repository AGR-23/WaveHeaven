// Asegurar contexto de audio global
if (!window.globalAudioContext) {
    window.globalAudioContext = new (window.AudioContext || window.webkitAudioContext)();
}

// Crear nodos de audio para un mediaElement
function createAudioNodes(mediaElement) {
    try {
        if (!mediaElement.sourceNode) {
            console.log("🎧 Creando nodos de audio...");

            mediaElement.sourceNode = window.globalAudioContext.createMediaElementSource(mediaElement);

            mediaElement.bassFilter = window.globalAudioContext.createBiquadFilter();
            mediaElement.midFilter = window.globalAudioContext.createBiquadFilter();
            mediaElement.trebleFilter = window.globalAudioContext.createBiquadFilter();

            mediaElement.bassFilter.type = "lowshelf";
            mediaElement.bassFilter.frequency.value = 250;

            mediaElement.midFilter.type = "peaking";
            mediaElement.midFilter.frequency.value = 1500;
            mediaElement.midFilter.Q.value = 1;

            mediaElement.trebleFilter.type = "highshelf";
            mediaElement.trebleFilter.frequency.value = 4000;

            mediaElement.sourceNode
                .connect(mediaElement.bassFilter)
                .connect(mediaElement.midFilter)
                .connect(mediaElement.trebleFilter)
                .connect(window.globalAudioContext.destination);
        }

        return true;
    } catch (error) {
        console.error("❌ Error en createAudioNodes:", error);
        return false;
    }
}

// Función para aplicar el perfil de sonido
function applySoundProfile(profile) {
    console.log("Applying profile:", profile);

    // Actualizar controles deslizantes del ecualizador
    if (profile.filters) {
        profile.filters.forEach(filter => {
            const sliderId = `eq${filter.frequency}`;
            const slider = document.getElementById(sliderId);
            if (slider) {
                slider.value = filter.gain;
                // Disparar evento para actualizar la UI
                const event = new Event('input', { bubbles: true });
                slider.dispatchEvent(event);
            }
        });
    }

    // Aplicar a elementos de audio/video
    const mediaElements = Array.from(document.querySelectorAll("audio, video"));

    mediaElements.forEach(mediaEl => {
        try {
            if (!mediaEl._audioNodesCreated) {
                createAudioNodes(mediaEl);
                mediaEl._audioNodesCreated = true;
            }

            if (mediaEl.bassFilter && profile.bass !== undefined) {
                mediaEl.bassFilter.gain.value = (profile.bass - 50) / 10;
            }
            if (mediaEl.midFilter && profile.mid !== undefined) {
                mediaEl.midFilter.gain.value = (profile.mid - 50) / 10;
            }
            if (mediaEl.trebleFilter && profile.treble !== undefined) {
                mediaEl.trebleFilter.gain.value = (profile.treble - 50) / 10;
            }
        } catch (err) {
            console.error("Error applying profile to media element:", err);
        }
    });
}

// Escuchar mensajes de la extensión
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "APPLY_AUDIO_PROFILE") {
        applySoundProfile(message.profile);
        sendResponse({ success: true });
    }
    return true; // Mantener el puerto abierto para sendResponse
});

async function applySoundProfile(profileName = null) {
    try {
        if (!profileName) {
            const profileSelect = document.getElementById('profiles');
            profileName = profileSelect.value;
        }

        // Enviar solicitud al servidor para obtener el perfil
        const response = await fetch(`/apply_profile_by_name/${profileName}/`);
        const data = await response.json();

        if (data.status === "success") {
            console.log(`Applying profile: ${profileName}`, data.profile);
            // Actualizar controles deslizantes del ecualizador
            document.querySelectorAll('.eq-slider').forEach(slider => {
                const freq = slider.id.replace('eq', '');
                const gain = profile.filters.find(f => f.frequency == freq)?.gain || 0;
                slider.value = gain;
                slider.dispatchEvent(new Event('input')); // Forzar actualización visual
            });

            console.log("✅ Perfil aplicado correctamente");

            // Aplicar ajustes al ecualizador en el navegador
            if (data.applied_profile.bass !== undefined) {
                updateEqualizer(64, data.applied_profile.bass / 2 - 25);
                document.getElementById('eq6').value = data.applied_profile.bass / 2 - 25;
            }
            if (data.applied_profile.mid !== undefined) {
                updateEqualizer(1000, data.applied_profile.mid / 2 - 25);
                document.getElementById('eq1000').value = data.applied_profile.mid / 2 - 25;
            }
            if (data.applied_profile.treble !== undefined) {
                updateEqualizer(16000, data.applied_profile.treble / 2 - 25);
                document.getElementById('eq16000').value = data.applied_profile.treble / 2 - 25;
            }


            // Enviar el perfil a los elementos de audio en la página web
            chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                chrome.scripting.executeScript({
                    target: { tabId: tabs[0].id },
                    func: applyAudioProfile,
                    args: [data.applied_profile]
                });
            });
        }

    } catch (error) {
        console.error("Error applying profile:", error);
    }
}

// Agregar el evento al botón de aplicar perfil
document.getElementById('apply-btn').addEventListener('click', () => {
    const profileSelect = document.getElementById('profiles');
    const profileName = profileSelect.value;
    applySoundProfile(profileName);
})



chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "applyProfile") {
        const mediaElement = document.querySelector('audio, video');  // Encuentra el audio o video en la página

        if (mediaElement) {
            const context = new (window.AudioContext || window.webkitAudioContext)();
            const source = context.createMediaElementSource(mediaElement);
            const gainNode = context.createGain();
            const profile = request.profile;  // El perfil seleccionado

            // Aplicamos el perfil de sonido (ejemplo simple)
            switch (profile) {
                case "Relax":
                    gainNode.gain.value = 0.5;  // Bajo volumen para el perfil Relax
                    break;
                case "Focus":
                    gainNode.gain.value = 1.5;  // Volumen más alto para Focus
                    break;
                // Puedes agregar más perfiles y ajustarlos aquí
                default:
                    gainNode.gain.value = 1;  // Perfil por defecto (normal)
            }

            // Conectar y aplicar
            source.connect(gainNode).connect(context.destination);
            sendResponse({ status: "Perfil aplicado: " + profile });
        }
    }
});