# Django WebAssembly: Modernization Assessment

**Assessment Date:** January 2026
**Last Project Update:** ~2022 (4 years ago)
**Current State:** Proof of Concept
**Target State:** Production-Ready Software

---

## Executive Summary

This Django WebAssembly project is an innovative proof of concept demonstrating that Django applications can run entirely in the browser using Pyodide (Python compiled to WebAssembly) and Service Workers. The last commit was approximately 4 years ago, and significant updates are needed across dependencies, security, architecture, and tooling to bring this to production quality.

**Effort Estimate:** Medium-to-Large (depending on scope of production features)

---

## 1. Critical Dependency Updates

### 1.1 Pyodide (Highest Priority)

| Component | Current | Latest | Breaking Changes |
|-----------|---------|--------|------------------|
| Pyodide | v0.21.3 | v0.29.2 | Yes - significant |

**Required Changes:**

- **Python version upgrade**: Pyodide 0.29.2 uses Python 3.13.2 (up from 3.10)
- **API changes**: The `loadPyodide()` API has evolved; review [migration guide](https://pyodide.org/en/stable/project/changelog.html)
- **WebAssembly exceptions**: Projects must now use `-fwasm-exceptions` instead of `-fexceptions`
- **JSPI support**: JavaScript Promise Integration is now enabled by default (since 0.27.7), enabling `asyncio.run()` and `loop.run_until_complete()` - this could simplify async Django operations
- **Package availability**: More Python packages are now available via micropip

**Update in `worker.js`:**
```javascript
// FROM:
importScripts("https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js");
// TO:
importScripts("https://cdn.jsdelivr.net/pyodide/v0.29.2/full/pyodide.js");
```

### 1.2 Django (High Priority)

| Component | Current | Latest Stable | Latest LTS |
|-----------|---------|---------------|------------|
| Django | ^4.1.1 (EOL) | 6.0.1 | 5.2.x |

**Django 4.1 reached end-of-life.** Recommended upgrade path:
1. 4.1 → 4.2 (LTS, EOL April 2026)
2. 4.2 → 5.0
3. 5.0 → 5.1
4. 5.1 → 5.2 (LTS) OR 6.0

**Key Django Changes Since 4.1:**

- **Django 5.0+**: Dropped Python 3.8/3.9 support; new `Field.db_default` for database-computed defaults
- **Django 5.2**: New `shell --imports` auto-imports models; utf8mb4 default for MySQL
- **Django 6.0**: Template partials, background tasks framework, CSP middleware, modernized email API

**Recommendation:** Target Django 5.2 LTS for stability, or Django 6.0 if background tasks feature is desired.

### 1.3 Python Dependencies

| Package | Current | Latest | Notes |
|---------|---------|--------|-------|
| Python | ^3.10 | 3.13+ | Pyodide 0.29 requires 3.13 |
| WebTest | ^3.0.0 | ~3.0.1 | Minor updates only |
| black | ^22.8.0 | 24.x | Major version bump |
| ipdb | ^0.13.9 | 0.13.13 | Minor updates |

### 1.4 JavaScript Dependencies

| Package | Current | Latest | Notes |
|---------|---------|--------|-------|
| eslint | ^8.24.0 | 9.x | Major version with flat config |
| xhr-shim | ^0.1.3 | 0.1.3 | No updates (may need alternative) |

**Concern:** `xhr-shim` hasn't been updated; verify compatibility with modern Pyodide. Pyodide may have improved its fetch/XHR handling.

---

## 2. Security Improvements

### 2.1 Critical Security Issues

1. **Hardcoded SECRET_KEY** (`settings.py:23`)
   ```python
   SECRET_KEY = "django-insecure-7)6m67&xwfifm-a$4q9nr9ygh3=b8t0due-5=*$n*p+&^t-ac&"
   ```
   - For browser-only operation, this is less critical since there's no server
   - Document this as intentional for the use case or generate per-session

2. **DEBUG = True** (`settings.py:26`)
   - Should be configurable; exposing debug info in browser could leak implementation details

3. **Hardcoded Credentials** (`init.py:34-36`)
   ```python
   user = User(username="matt", is_staff=True, is_superuser=True)
   user.set_password("password")
   ```
   - Document this is demo-only or allow configuration

### 2.2 Content Security Policy

- Add CSP headers (Django 6.0 has built-in CSP middleware)
- Restrict script sources to trusted CDNs
- Consider Subresource Integrity (SRI) for CDN scripts

### 2.3 Service Worker Security

- Implement proper scope restrictions
- Add version checking for cache invalidation
- Consider signed scripts for integrity

---

## 3. Architecture Improvements

### 3.1 Current Limitations

1. **Single Cookie Handling** (`worker.js:82-83`)
   ```javascript
   // only saving first one right now
   const nameValue = setCookie.split(";")[0].split("=");
   ```
   - Needs to handle multiple cookies properly

2. **No Request Body for DELETE** (`worker.js:51`)
   - Only POST, PUT, PATCH handle request bodies

3. **URL Injection Risk** (`worker.js:56-57`)
   ```javascript
   response = app.${method}(
       "${request.url}",
   ```
   - URL and params inserted directly into Python code string

4. **Font MIME Type Workaround** (`worker.js:85-87`)
   - Hardcoded fix for `.woff` files; needs generalization

### 3.2 Recommended Architectural Changes

1. **Separate Configuration from Code**
   - Environment variables or configuration file for settings
   - Allow customization of demo data

2. **Modular Service Worker**
   - Split `worker.js` into modules (request handling, Python bridge, cookie management)
   - Use ES modules (now widely supported)

3. **Error Handling**
   - Add try-catch around Python execution
   - Implement user-friendly error messages
   - Add error reporting/logging

4. **State Management**
   - Consider IndexedDB for persistent storage
   - Add data export/import functionality
   - Handle database corruption gracefully

5. **Loading Experience**
   - Progress indicator during Pyodide load (~20MB download)
   - Estimated time remaining
   - Graceful fallback if WebAssembly unsupported

---

## 4. Testing Requirements

### 4.1 Current State

- `django_webassembly/polls/tests.py` exists but is empty
- No JavaScript tests
- No integration tests
- No CI/CD pipeline

### 4.2 Recommended Test Suite

1. **Python Unit Tests**
   - Model tests for Question/Choice
   - View tests for all endpoints
   - Admin registration tests

2. **JavaScript Tests**
   - Service worker registration
   - Request interception
   - Cookie handling
   - Error conditions

3. **Integration Tests**
   - Full page load in headless browser
   - Form submission through service worker
   - Admin login flow
   - Database persistence across reloads

4. **Browser Compatibility Tests**
   - Chrome, Firefox, Safari, Edge
   - Mobile browsers
   - WebAssembly feature detection

5. **Testing Tools**
   - pytest + pytest-django for Python
   - Playwright or Puppeteer for E2E
   - Jest for JavaScript unit tests

---

## 5. Production Readiness Checklist

### 5.1 Build System

- [ ] Modern build tooling (Vite, esbuild, or webpack)
- [ ] JavaScript bundling and minification
- [ ] Source maps for debugging
- [ ] Asset versioning/cache busting
- [ ] Automated wheel building in CI

### 5.2 Development Experience

- [ ] Hot reload for development
- [ ] TypeScript for worker.js (optional but recommended)
- [ ] Proper local development setup instructions
- [ ] Docker development environment

### 5.3 Deployment

- [ ] GitHub Actions CI/CD pipeline
- [ ] Automated testing on PR
- [ ] Automated deployment to GitHub Pages
- [ ] Version tagging and releases
- [ ] CDN configuration for production

### 5.4 Documentation

- [ ] Comprehensive README with:
  - Browser requirements
  - Known limitations
  - Use cases
  - Architecture diagram
- [ ] API documentation
- [ ] Contributing guide
- [ ] Changelog
- [ ] Troubleshooting guide

### 5.5 Monitoring & Observability

- [ ] Client-side error tracking (Sentry, etc.)
- [ ] Performance monitoring
- [ ] Usage analytics (privacy-respecting)

---

## 6. Browser Compatibility

### 6.1 Current Requirements

- Service Worker support
- WebAssembly support
- Modern JavaScript (ES2021)

### 6.2 Browser Support Matrix

| Browser | Service Workers | WebAssembly | Status |
|---------|----------------|-------------|--------|
| Chrome 80+ | ✅ | ✅ | Supported |
| Firefox 78+ | ✅ | ✅ | Supported |
| Safari 14+ | ✅ | ✅ | Needs testing |
| Edge 80+ | ✅ | ✅ | Supported |
| iOS Safari 14+ | ✅ | ✅ | Needs testing |

### 6.3 Known Issues

- Pyodide 0.27.1 had Safari/iPad crash (fixed in 0.29.2)
- Service workers may behave differently across browsers
- Memory constraints on mobile devices

---

## 7. Performance Considerations

### 7.1 Current Pain Points

1. **Initial Load Time**
   - Pyodide is ~20MB compressed
   - Full Django initialization takes several seconds
   - No caching strategy for repeated visits

2. **Memory Usage**
   - Full Python runtime in browser
   - SQLite database in memory
   - No memory management strategy

### 7.2 Recommended Optimizations

1. **Caching Strategy**
   - Cache Pyodide files in service worker
   - Cache Python packages
   - Implement smart cache invalidation

2. **Progressive Loading**
   - Show meaningful content while loading
   - Lazy-load non-critical packages
   - Skeleton screens

3. **Bundle Size**
   - Analyze and minimize Python package dependencies
   - Tree-shake unused Django features if possible
   - Compress wheel file

4. **Web Workers**
   - Consider running Pyodide in dedicated worker
   - Keep main thread responsive
   - Use SharedArrayBuffer if available

---

## 8. New Features to Consider

### 8.1 Offline Support

- Service worker caching for true offline use
- Sync capabilities when back online
- Conflict resolution for data changes

### 8.2 Data Persistence

- IndexedDB backend for SQLite
- Data export (JSON, CSV)
- Data import/restore
- Multi-user local storage

### 8.3 Developer Tools

- Browser DevTools extension
- Django Debug Toolbar integration
- SQL query visualization

### 8.4 Multi-Framework Support

- Flask support
- FastAPI support (with limitations)
- Generic WSGI/ASGI adapter

---

## 9. Implementation Roadmap

### Phase 1: Critical Updates (Foundation)
- Update Pyodide to latest version
- Update Django to 5.2 LTS or 6.0
- Fix security issues
- Update all dependencies
- Basic error handling

### Phase 2: Quality & Testing
- Add comprehensive test suite
- Set up CI/CD pipeline
- Improve documentation
- Browser compatibility testing

### Phase 3: Production Features
- Performance optimizations
- Caching strategy
- Better loading experience
- Monitoring integration

### Phase 4: Enhanced Features
- Offline support
- Data persistence
- Developer tools
- Additional framework support

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pyodide API breaking changes | High | High | Thorough testing, pin versions |
| Browser compatibility issues | Medium | Medium | Comprehensive browser testing |
| Performance regression | Medium | Medium | Benchmarking before/after |
| Django async compatibility | Low | Medium | Test async features carefully |
| Memory leaks in browser | Medium | High | Memory profiling, limits |

---

## 11. Resources

### Documentation
- [Pyodide Documentation](https://pyodide.org/en/stable/)
- [Pyodide Changelog](https://pyodide.org/en/stable/project/changelog.html)
- [Django 6.0 Release Notes](https://docs.djangoproject.com/en/6.0/releases/)
- [Django Upgrade Guide](https://upgradedjango.com/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

### Tools
- [Pyodide GitHub](https://github.com/pyodide/pyodide)
- [Django GitHub](https://github.com/django/django)
- [WebTest](https://docs.pylonsproject.org/projects/webtest/)

---

## Conclusion

This proof of concept demonstrates an innovative approach to running Django in the browser. With the updates outlined above, it could become a valuable tool for:

- **Educational purposes**: Teaching Django without server setup
- **Portfolio projects**: Hosting interactive demos on GitHub Pages
- **Prototyping**: Rapid iteration without deployment infrastructure
- **Offline applications**: Apps that work without connectivity

The core architecture is sound, but 4 years of ecosystem evolution require significant updates to dependencies, security practices, and tooling. The recommended approach is an incremental modernization following the phased roadmap above.
