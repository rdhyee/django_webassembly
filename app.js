// Django WebAssembly - Application Entry Point
// Registers service worker and handles loading progress

const STAGES = ["init", "pyodide", "packages", "django"];
let currentStage = 0;

const updateProgress = (progress) => {
  const progressBar = document.getElementById("progress-bar");
  if (progressBar) {
    progressBar.style.width = `${progress}%`;
  }
};

const setStage = (stage) => {
  const stageIndex = STAGES.indexOf(stage);
  if (stageIndex === -1) return;

  // Mark previous stages as complete
  for (let i = 0; i < stageIndex; i++) {
    const el = document.getElementById(`stage-${STAGES[i]}`);
    if (el) {
      el.classList.remove("active");
      el.classList.add("complete");
    }
  }

  // Mark current stage as active
  const currentEl = document.getElementById(`stage-${stage}`);
  if (currentEl) {
    currentEl.classList.remove("complete");
    currentEl.classList.add("active");
  }

  // Mark future stages as inactive
  for (let i = stageIndex + 1; i < STAGES.length; i++) {
    const el = document.getElementById(`stage-${STAGES[i]}`);
    if (el) {
      el.classList.remove("active", "complete");
    }
  }

  currentStage = stageIndex;
};

const updateLoadingStatus = (message, isError = false) => {
  const statusEl = document.getElementById("loading-status");
  if (statusEl) {
    statusEl.textContent = message;
    if (isError) {
      statusEl.classList.add("error");
    } else {
      statusEl.classList.remove("error");
    }
  }
};

const showBrowserWarning = (message) => {
  const warningEl = document.getElementById("browser-warning");
  const messageEl = document.getElementById("warning-message");
  if (warningEl && messageEl) {
    messageEl.textContent = message;
    warningEl.classList.add("show");
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

  if (!window.caches) {
    missing.push("Cache API");
  }

  if (missing.length > 0) {
    return {
      supported: false,
      message: `Missing: ${missing.join(", ")}. Please use Chrome, Firefox, Safari, or Edge.`
    };
  }

  return { supported: true };
};

const handleServiceWorkerMessage = (event) => {
  const data = event.data;

  switch (data.type) {
  case "loading":
    updateLoadingStatus(data.message);
    if (data.progress !== undefined) {
      updateProgress(data.progress);
    }
    if (data.stage) {
      setStage(data.stage);
    }
    break;

  case "loaded":
    updateLoadingStatus(data.message);
    updateProgress(100);
    // Mark all stages complete
    STAGES.forEach(stage => {
      const el = document.getElementById(`stage-${stage}`);
      if (el) {
        el.classList.remove("active");
        el.classList.add("complete");
      }
    });
    break;

  case "error":
    updateLoadingStatus(data.message, true);
    break;

  case "status":
    if (data.loaded) {
      // Already loaded, we can reload to show the app
      location.reload();
    } else if (data.error) {
      updateLoadingStatus(data.error, true);
    }
    break;
  }
};

const initServiceWorker = async () => {
  setStage("init");
  updateProgress(5);

  const support = checkBrowserSupport();
  if (!support.supported) {
    showBrowserWarning(support.message);
    updateLoadingStatus("Browser not supported", true);
    return;
  }

  try {
    // Listen for messages from service worker
    navigator.serviceWorker.addEventListener("message", handleServiceWorkerMessage);

    updateLoadingStatus("Registering service worker...");
    const registration = await navigator.serviceWorker.register("./worker.js");
    console.log("Service worker registration succeeded:", registration);

    // If already active and loaded, get status
    if (registration.active) {
      registration.active.postMessage({ type: "GET_STATUS" });
    }

    // Listen for state changes during installation
    if (registration.installing) {
      updateLoadingStatus("Installing service worker...");
      setStage("pyodide");
      updateProgress(10);

      registration.installing.addEventListener("statechange", (event) => {
        if (event.target.state === "activated") {
          // Give a moment for Django to finish initialization
          updateLoadingStatus("Finalizing...");
          updateProgress(95);
          setTimeout(() => location.reload(), 500);
        }
      });
    } else if (registration.waiting) {
      // New version waiting, skip waiting
      registration.waiting.postMessage({ type: "SKIP_WAITING" });
    }

    // Handle updates to existing service worker
    registration.addEventListener("updatefound", () => {
      const newWorker = registration.installing;
      if (newWorker) {
        updateLoadingStatus("Updating...");
        newWorker.addEventListener("statechange", () => {
          if (newWorker.state === "activated") {
            location.reload();
          }
        });
      }
    });

  } catch (error) {
    console.error("Service worker registration failed:", error);
    updateLoadingStatus(`Registration failed: ${error.message}`, true);
    showBrowserWarning(error.message);
  }
};

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initServiceWorker);
} else {
  initServiceWorker();
}
