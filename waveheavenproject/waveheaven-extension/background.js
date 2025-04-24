// Background service worker for the extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "fetch_profiles") {
    fetch(`${request.baseUrl}/list_profiles/`, {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          sendResponse(data.profiles);
        } else {
          sendResponse({ error: data.message });
        }
      })
      .catch(err => sendResponse({ error: err.message }));
    return true; // async
  }
});

// Function to inject into web pages
function applyAudioProfile(profile) {
  // This will be executed in the context of the web page
  const audioElements = document.querySelectorAll('audio, video');

  audioElements.forEach(audio => {
    // Create audio context if not exists
    if (!audio.audioContext) {
      audio.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audio.source = audio.audioContext.createMediaElementSource(audio);

      // Create equalizer nodes
      audio.bass = audio.audioContext.createBiquadFilter();
      audio.mid = audio.audioContext.createBiquadFilter();
      audio.treble = audio.audioContext.createBiquadFilter();

      // Configure filters
      audio.bass.type = "lowshelf";
      audio.bass.frequency.value = 250;

      audio.mid.type = "peaking";
      audio.mid.frequency.value = 1500;
      audio.mid.Q.value = 1;

      audio.treble.type = "highshelf";
      audio.treble.frequency.value = 4000;

      // Connect nodes
      audio.source.connect(audio.bass);
      audio.bass.connect(audio.mid);
      audio.mid.connect(audio.treble);
      audio.treble.connect(audio.audioContext.destination);
    }

    // Apply profile settings
    audio.bass.gain.value = (profile.bass - 50) / 10;
    audio.mid.gain.value = (profile.mid - 50) / 10;
    audio.treble.gain.value = (profile.treble - 50) / 10;

    // Adjust volume
    audio.volume = profile.volume / 100;
  });
}