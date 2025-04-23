const BASE_URL = 'http://localhost:8000';
const profileSelect = document.getElementById('profiles');
const applyBtn = document.getElementById('apply-btn');
const refreshBtn = document.getElementById('refresh-btn');
const statusText = document.querySelector('.status p');
const currentProfileText = document.getElementById('current-profile');
const exposureTimeElement = document.getElementById('exposure-time');
const stopBtn = document.getElementById('stop-btn');
const refreshTimeBtn = document.getElementById('refresh-time-btn');

let currentProfileName = "None";
let exposureTime = 0;
let exposureTimer = null;

stopBtn.addEventListener('click', () => {
  stopExposureTimer();
  chrome.storage.sync.set({ exposurePaused: true });
  showNotification('Exposure timer paused');
});

refreshTimeBtn.addEventListener('click', () => {
  exposureTime = 0;
  updateExposureTime();
  saveExposureTime();
  showNotification('Exposure time reset to 0');
});

function showStatus(msg, isError = false) {
  statusText.textContent = msg;
  statusText.style.color = isError ? 'red' : 'black';
}

function showNotification(message, isError = false) {
  const notification = document.createElement('div');
  notification.className = `notification ${isError ? 'error' : 'success'}`;
  notification.textContent = message;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}

async function loadProfiles() {
  profileSelect.innerHTML = `<option value="">Loading profiles...</option>`;
  try {
    const profiles = await new Promise((res, rej) => {
      chrome.runtime.sendMessage({ type: 'fetch_profiles', baseUrl: BASE_URL }, resp => {
        if (resp.error) rej(resp.error);
        else res(resp);
      });
    });

    profileSelect.innerHTML = `<option value="">-- Select a profile --</option>`;
    profiles.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = p.name;
      opt.dataset.profile = JSON.stringify(p);
      profileSelect.appendChild(opt);
    });
    showStatus('Profiles loaded');
  } catch (err) {
    console.error("Error loading profiles:", err);
    profileSelect.innerHTML = `<option value="">Error loading</option>`;
    showStatus(`Error: ${err}`, true);
  }
}

function updateExposureTime() {
  exposureTime++;
  const minutes = Math.floor(exposureTime / 60);
  const seconds = exposureTime % 60;
  exposureTimeElement.textContent = `Exposure Time: ${minutes}m ${seconds}s`;
  chrome.storage.sync.set({ exposureTime });
}

function startExposureTimer() {
  chrome.storage.sync.get('exposurePaused', result => {
    if (result.exposurePaused) return;
    if (!exposureTimer) exposureTimer = setInterval(updateExposureTime, 1000);
  });
}

function stopExposureTimer() {
  if (exposureTimer) {
    clearInterval(exposureTimer);
    exposureTimer = null;
  }
}

function loadExposureTime() {
  chrome.storage.sync.get('exposureTime', result => {
    if (result.exposureTime) {
      exposureTime = result.exposureTime;
      updateExposureTime();
    }
  });
}

function saveExposureTime() {
  chrome.storage.sync.set({ exposureTime }, () => {
    console.log('Exposure time saved:', exposureTime);
  });
}

function applyAudioProfile(profile) {
  const audioElements = document.querySelectorAll('audio, video');
  audioElements.forEach(mediaElement => {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    const source = context.createMediaElementSource(mediaElement);

    const bass = context.createBiquadFilter();
    bass.type = 'lowshelf';
    bass.frequency.value = 250;
    bass.gain.value = (profile.bass - 50) / 10;

    const mid = context.createBiquadFilter();
    mid.type = 'peaking';
    mid.frequency.value = 1500;
    mid.Q.value = 1;
    mid.gain.value = (profile.mid - 50) / 10;

    const treble = context.createBiquadFilter();
    treble.type = 'highshelf';
    treble.frequency.value = 4000;
    treble.gain.value = (profile.treble - 50) / 10;

    source.connect(bass).connect(mid).connect(treble).connect(context.destination);
    console.log(`🎚️ Applied EQ profile to media element`, profile);
  });
}

applyBtn.addEventListener('click', async () => {
  const selectedOption = profileSelect.selectedOptions[0];
  if (!selectedOption || !selectedOption.dataset.profile) {
    showStatus('Select a profile first', true);
    return;
  }
  const profile = JSON.parse(selectedOption.dataset.profile);
  currentProfileName = profile.name;

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url?.startsWith('http')) {
      showStatus('Invalid tab to apply profile', true);
      return;
    }

    const encodedName = encodeURIComponent(profile.name.trim());
    const response = await fetch(`${BASE_URL}/apply_profile_by_name/${encodedName}/`, {
      method: 'GET',
      credentials: 'include'
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.message || 'Server error');
    }

    const data = await response.json();
    showStatus(`Profile applied: ${data.applied_profile.name}`);
    showNotification(`Profile applied: ${data.applied_profile.name}`);
    currentProfileText.textContent = `Current profile: ${currentProfileName}`;
    chrome.storage.local.set({ currentProfile: currentProfileName });
    startExposureTimer();

    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: applyAudioProfile,
      args: [data.applied_profile]
    });
  } catch (err) {
    console.error('Error applying profile:', err);
    showStatus(`Error: ${err.message}`, true);
    showNotification(`Error: ${err.message}`, true);
  }
});

refreshBtn.addEventListener('click', loadProfiles);

document.addEventListener('DOMContentLoaded', () => {
  loadProfiles();
  loadExposureTime();
  chrome.storage.local.get('currentProfile', data => {
    if (data.currentProfile) {
      currentProfileName = data.currentProfile;
      currentProfileText.textContent = `Current profile: ${currentProfileName}`;
    }
  });
});

window.addEventListener('beforeunload', saveExposureTime);
