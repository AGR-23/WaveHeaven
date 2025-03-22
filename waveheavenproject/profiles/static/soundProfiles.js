let profiles = []; // Variable global para almacenar los perfiles

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadProfiles(); // ✅ Carga los perfiles al inicio
    lucide.createIcons();
});


function loadProfiles() {
    fetch('/list_profiles/')
        .then(response => response.json())
        .then(data => {
            profiles = data.profiles;
            const container = document.getElementById('profilesContainer');
            container.innerHTML = '';

            if (profiles && profiles.length > 0) {
                profiles.forEach((profile, index) => {
                    // Generamos la tarjeta
                    const profileCard = `
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-4">
<div class="flex justify-between items-start">
<div>
  <h3 class="text-xl font-semibold">${profile.name}</h3>
  <p class="text-gray-500 dark:text-gray-400">${profile.environment}</p>
</div>
<div class="flex space-x-2">
  <button onclick="openCreateProfileModal(${index})" 
    class="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition">
    <i data-lucide="edit" class="h-4 w-4"></i>
  </button>
  <button onclick="deleteProfile(${index})" 
    class="px-3 py-1 text-sm bg-red-100 dark:bg-red-700 text-red-800 dark:text-red-200 rounded-md hover:bg-red-200 dark:hover:bg-red-600 transition">
    <i data-lucide="trash-2" class="h-4 w-4"></i>
  </button>
</div>
</div>
<div class="mt-4 grid grid-cols-3 gap-4">
${renderBar('Bass', profile.bass)}
${renderBar('Mid', profile.mid)}
${renderBar('Treble', profile.treble)}
</div>
</div>
`;
                    container.innerHTML += profileCard;
                });
            } else {
                container.innerHTML = '<p class="text-gray-500 dark:text-gray-400">No hay perfiles disponibles.</p>';
            }

            lucide.createIcons();
        })
        .catch(error => {
            console.error('Error al cargar perfiles:', error);
            document.getElementById('profilesContainer').innerHTML = '<p class="text-red-500">Error al cargar perfiles.</p>';
        });
}

// Función para renderizar barras de colores según label
function renderBar(label, value) {
    let barColor = 'bg-blue-500'; // default

    if (label.toLowerCase() === 'mid') {
        barColor = 'bg-green-500';
    } else if (label.toLowerCase() === 'treble') {
        barColor = 'bg-red-500';
    }

    return `
<div>
<div class="flex justify-between items-center mb-1">
<p class="text-sm text-gray-500 dark:text-gray-400">${label}</p>
<span class="text-xs font-medium text-gray-600 dark:text-gray-300">${value}%</span>
</div>
<div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
<div class="h-2 ${barColor} rounded-full transition-all duration-500" style="width: ${value}%"></div>
</div>
</div>
`;
}
// Función para abrir el modal de creación/edición
function openCreateProfileModal(profileIndex = null) {
    const modal = document.getElementById("profileModal");
    const modalTitle = document.getElementById("modalTitle");
    const form = document.getElementById("profileForm");

    if (profileIndex !== null) {
        modalTitle.textContent = "Edit Profile";
        const profile = profiles[profileIndex];
        document.getElementById("profileName").value = profile.name;
        document.getElementById("profileBass").value = profile.bass;
        document.getElementById("profileMid").value = profile.mid;
        document.getElementById("profileTreble").value = profile.treble;
        document.getElementById("profileEnvironment").value = profile.environment;
        form.setAttribute("data-index", profileIndex);
    } else {
        modalTitle.textContent = "New Profile";
        form.reset();
        form.removeAttribute("data-index");
    }

    modal.classList.remove("hidden");
}

// Función para cerrar el modal
function closeProfileModal() {
    document.getElementById("profileModal").classList.add("hidden");
}

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para guardar (crear o editar) un perfil
function saveProfile(event) {
    event.preventDefault();
    const form = event.target;

    const profileData = {
        name: document.getElementById("profileName").value,
        bass: parseInt(document.getElementById("profileBass").value),
        mid: parseInt(document.getElementById("profileMid").value),
        treble: parseInt(document.getElementById("profileTreble").value),
        environment: document.getElementById("profileEnvironment").value,
    };

    console.log("Enviando datos al backend:", profileData);

    let url = "/create_profile/";
    let method = "POST";

    if (form.hasAttribute("data-index")) {
        const index = form.getAttribute("data-index");
        url = `/edit_profile/${index}/`;
    }

    fetch(url, {
        method: method,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify(profileData),
    })
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend:", data);
            if (data.status === "success") {
                closeProfileModal();
                loadProfiles();
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => console.error("Error en fetch:", error));
}

// Función para eliminar un perfil
function deleteProfile(index) {
    if (confirm("Are you sure you want to delete this profile?")) {
        fetch(`/delete_profile/${index}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
            .then(response => response.json())
            .then(data => {
                console.log("Respuesta al eliminar:", data);
                if (data.status === "success") {
                    showNotification("Profile deleted successfully!", "success");
                    loadProfiles();
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(error => console.error("Error al eliminar perfil:", error));
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className =
        "fixed bottom-4 right-4 px-6 py-3 rounded-md shadow-lg flex items-center space-x-2 transition-opacity duration-300 z-50";
    if (type === "success") {
        notification.classList.add("bg-green-500", "text-white");
        notification.innerHTML = `<i data-lucide="check-circle" class="h-5 w-5 mr-2"></i><span>${message}</span>`;
    } else if (type === "error") {
        notification.classList.add("bg-red-500", "text-white");
        notification.innerHTML = `<i data-lucide="alert-circle" class="h-5 w-5 mr-2"></i><span>${message}</span>`;
    } else {
        notification.classList.add("bg-blue-500", "text-white");
        notification.innerHTML = `<i data-lucide="info" class="h-5 w-5 mr-2"></i><span>${message}</span>`;
    }
    document.body.appendChild(notification);
    lucide.createIcons();
    setTimeout(() => {
        notification.classList.add("opacity-0");
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}