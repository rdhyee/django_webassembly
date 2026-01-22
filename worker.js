// Django WebAssembly - Service Worker
// Runs Django in the browser via Pyodide (Python WebAssembly)

const PYODIDE_VERSION = "0.29.2";
const WHEEL_VERSION = "0.2.0";

importScripts(`https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.js`);
importScripts("https://cdn.jsdelivr.net/npm/xhr-shim@0.1.3/src/index.min.js");

// XMLHttpRequest not normally available in service worker (needed by pyodide)
self.XMLHttpRequest = self.XMLHttpRequestShim;

let pyodide = null;
let loaded = false;
let loadError = null;
const cookies = {};

// Notify clients of loading progress
const notifyClients = async (message) => {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage(message);
  });
};

const setupPython = async () => {
  try {
    await notifyClients({ type: "loading", stage: "pyodide", message: "Loading Python runtime..." });

    pyodide = await loadPyodide();

    await notifyClients({ type: "loading", stage: "packages", message: "Installing packages..." });

    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("tzdata");
    await micropip.install(`./wheel/django_webassembly-${WHEEL_VERSION}-py3-none-any.whl`);

    await notifyClients({ type: "loading", stage: "django", message: "Initializing Django..." });

    const initScript = await (await fetch("./init.py")).text();
    pyodide.runPython(initScript);

    loaded = true;
    loadError = null;

    await notifyClients({ type: "loaded", message: "Ready!" });
  } catch (error) {
    loadError = error;
    console.error("Failed to setup Python:", error);
    await notifyClients({ type: "error", message: `Failed to load: ${error.message}` });
    throw error;
  }
};

self.addEventListener("install", (event) => {
  console.log("Service Worker: Installing...");
  event.waitUntil(setupPython());
});

// Build cookie string from stored cookies
const buildCookieString = () => {
  return Object.entries(cookies)
    .map(([key, value]) => `${key}=${value}`)
    .join("; ");
};

// Parse and store all Set-Cookie headers (improved to handle multiple cookies)
const parseSetCookieHeaders = (setCookieHeader) => {
  if (!setCookieHeader) return;

  // Handle both single string and array of cookies
  const cookieStrings = Array.isArray(setCookieHeader) ? setCookieHeader : [setCookieHeader];

  for (const cookieStr of cookieStrings) {
    // Parse "name=value; path=/; ..." format
    const parts = cookieStr.split(";");
    if (parts.length > 0) {
      const [name, ...valueParts] = parts[0].split("=");
      if (name && valueParts.length > 0) {
        cookies[name.trim()] = valueParts.join("=").trim();
      }
    }
  }
};

// Map file extensions to MIME types for proper content-type handling
const MIME_TYPES = {
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".eot": "application/vnd.ms-fontobject",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".css": "text/css",
  ".js": "application/javascript",
  ".json": "application/json",
};

// Fix content-type for static files if needed
const fixContentType = (headers, url) => {
  if (headers["Content-Type"] === "application/octet-stream") {
    for (const [ext, mimeType] of Object.entries(MIME_TYPES)) {
      if (url.endsWith(ext)) {
        headers["Content-Type"] = mimeType;
        break;
      }
    }
  }
  return headers;
};

const djangoRequest = async (request) => {
  // Ensure Python is loaded
  if (!loaded) {
    if (loadError) {
      return new Response(`Python failed to load: ${loadError.message}`, {
        status: 503,
        headers: { "Content-Type": "text/plain" }
      });
    }
    await setupPython();
  }

  const method = request.method.toLowerCase();
  const url = request.url;

  // Build headers with cookies
  const reqHeaders = {};
  request.headers.forEach((value, key) => {
    reqHeaders[key] = value;
  });
  reqHeaders["Cookie"] = buildCookieString();
  if (request.referrer) {
    reqHeaders["Referer"] = request.referrer;
  }

  // Get request body for methods that support it
  let params = "";
  if (["post", "put", "patch", "delete"].includes(method)) {
    try {
      params = await request.text();
    } catch (e) {
      // No body or already consumed
    }
  }

  try {
    // Use pyodide.globals to safely pass data without string interpolation
    // This prevents code injection vulnerabilities
    pyodide.globals.set("_request_url", url);
    pyodide.globals.set("_request_params", params);
    pyodide.globals.set("_request_headers", pyodide.toPy(reqHeaders));
    pyodide.globals.set("_request_method", method);

    let response = pyodide.runPython(`
import json

_response = getattr(app, _request_method)(
    _request_url,
    params=_request_params,
    headers=dict(_request_headers),
    expect_errors=True,
)

try:
    _body = _response.text
except UnicodeDecodeError:
    _body = bytes(_response.body)

_body
`);

    // Handle binary responses
    if (response instanceof pyodide.ffi.PyBuffer) {
      response = response.toJs();
    } else if (typeof response === "object" && !(response instanceof Uint8Array) && !(typeof response === "string")) {
      response = new Uint8Array(response);
    }

    // Get response headers
    const headersPy = pyodide.runPython(`json.dumps(dict(_response.headers))`);
    let respHeaders = JSON.parse(headersPy);

    // Get status code
    const status = pyodide.runPython("_response.status_code");

    // Clean up globals
    pyodide.runPython(`
del _request_url, _request_params, _request_headers, _request_method, _response, _body
`);

    // Parse and store cookies
    parseSetCookieHeaders(respHeaders["Set-Cookie"]);

    // Fix content types for static files
    respHeaders = fixContentType(respHeaders, url);

    // Handle redirects
    if (status === 301 || status === 302) {
      return Response.redirect(respHeaders["Location"], status);
    }

    return new Response(response, { headers: respHeaders, status: status });

  } catch (error) {
    console.error("Django request error:", error);
    return new Response(`Error processing request: ${error.message}`, {
      status: 500,
      headers: { "Content-Type": "text/plain" }
    });
  }
};

self.addEventListener("fetch", (event) => {
  event.respondWith(djangoRequest(event.request));
});

self.addEventListener("activate", (event) => {
  console.log("Service Worker: Activated");
  event.waitUntil(self.clients.claim());
});

// Handle messages from the main page
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "GET_STATUS") {
    event.source.postMessage({
      type: "status",
      loaded: loaded,
      error: loadError ? loadError.message : null,
      pyodideVersion: PYODIDE_VERSION,
    });
  }
});
