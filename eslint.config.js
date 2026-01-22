import js from "@eslint/js";

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        // Browser globals
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        console: "readonly",
        location: "readonly",
        setTimeout: "readonly",
        fetch: "readonly",
        Response: "readonly",
        Request: "readonly",
        Headers: "readonly",
        Uint8Array: "readonly",
        // Service Worker globals
        self: "readonly",
        importScripts: "readonly",
        // Pyodide globals
        loadPyodide: "readonly",
        XMLHttpRequestShim: "readonly",
      },
    },
    rules: {
      "indent": ["error", 2],
      "linebreak-style": ["error", "unix"],
      "quotes": ["error", "double"],
      "semi": ["error", "always"],
      "object-curly-spacing": ["error", "always"],
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    },
  },
  {
    ignores: ["node_modules/**", "wheel/**", "*.min.js"],
  },
];
