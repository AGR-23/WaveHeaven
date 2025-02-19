chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "adjustVolume") {
        chrome.scripting.executeScript({
            target: { tabId: message.tabId },
            func: (volume) => {
                const audioElement = document.querySelector("audio, video");
                if (audioElement) {
                    audioElement.volume = volume;
                }
            },
            args: [message.volume]
        });
        sendResponse({ status: "success" });
    }
    return true; // Mantener el canal de comunicación abierto
});