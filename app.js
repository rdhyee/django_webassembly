// Django WebAssembly - Application Entry Point
// Registers service worker and handles loading progress

const updateLoadingStatus = (message, isError = false) => {
  const statusEl = document.getElementById("loading-status");
  if (statusEl) {
    statusEl.textContent = message;
    if (isError) {
      statusEl.classList.add("error");
    }
  }
};

const checkBrowserSupport = () => {
  const missing = [];

  if (!("serviceWorker" in navigator)) {
    missing.push("Service Workers");
  }

  if (typeof WebAssembly === "undefined") {
    missing.push("WebAssembly");
  }

  if (missing.length > 0) {
    return {
      supported: false,
      message: `Your browser doesn't support: ${missing.join(", ")}. Please use a modern browser like Chrome, Firefox, Safari, or Edge.`
    };
  }

  return { supported: true };
};

const initServiceWorker = async () => {
  const support = checkBrowserSupport();
  if (!support.supported) {
    updateLoadingStatus(support.message, true);
    return;
  }

  try {
    // Listen for messages from service worker
    navigator.serviceWorker.addEventListener("message", (event) => {
      const data = event.data;
      if (data.type === "loading") {
        updateLoadingStatus(data.message);
      } else if (data.type === "loaded") {
        updateLoadingStatus(data.message);
      } else if (data.type === "error") {
        updateLoadingStatus(data.message, true);
      }
    });

    const registration = await navigator.serviceWorker.register("./worker.js");
    console.log("Service worker registration succeeded:", registration);

    // If already active, check if Python is loaded
    if (registration.active) {
      registration.active.postMessage({ type: "GET_STATUS" });
    }

    // Listen for state changes during installation
    if (registration.installing) {
      updateLoadingStatus("Installing service worker...");
      registration.installing.addEventListener("statechange", (event) => {
        if (event.target.state === "activated") {
          // Give a moment for Python to finish setup, then reload
          setTimeout(() => location.reload(), 100);
        }
      });
    }

    // Handle updates to existing service worker
    registration.addEventListener("updatefound", () => {
      const newWorker = registration.installing;
      if (newWorker) {
        newWorker.addEventListener("statechange", () => {
          if (newWorker.state === "activated") {
            // New service worker activated, reload to use it
            location.reload();
          }
        });
      }
    });

  } catch (error) {
    console.error("Service worker registration failed:", error);
    updateLoadingStatus(`Failed to register service worker: ${error.message}`, true);
  }
};

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initServiceWorker);
} else {
  initServiceWorker();
}
