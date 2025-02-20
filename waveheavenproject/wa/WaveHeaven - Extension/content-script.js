window.addEventListener("message", (event) => {
    // Opcional: Verifica el origen del mensaje para mayor seguridad
    if (event.source !== window) return;
  
    if (event.data && event.data.type === "CONNECT_TO_TAB") {
      console.log("Mensaje de conexión recibido en el content script.");
      // Aquí puedes realizar la lógica de conexión o comunicarte con el background script
      chrome.runtime.sendMessage({ type: "connectToTab" }, (response) => {
        console.log("Respuesta del background:", response);
      });
    }
  });
  