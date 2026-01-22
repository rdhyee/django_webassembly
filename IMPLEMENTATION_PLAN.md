# Implementation Plan: Django WebAssembly Modernization

## Phase 1: Critical Updates (Foundation)

### 1.1 Update Pyodide (v0.21.3 → v0.29.2)
- [ ] Update CDN URL in `worker.js`
- [ ] Test Pyodide initialization
- [ ] Verify micropip still works
- [ ] Test Django wheel installation
- [ ] Handle any API changes

### 1.2 Update Django (4.1 → 5.2 LTS)
- [ ] Update `pyproject.toml` Django version
- [ ] Review Django 4.2, 5.0, 5.1, 5.2 release notes for breaking changes
- [ ] Update `settings.py` for any deprecated settings
- [ ] Update any deprecated imports/APIs
- [ ] Rebuild wheel

### 1.3 Update Python Dependencies
- [ ] Update `pyproject.toml` Python version requirement
- [ ] Update black, ipdb versions
- [ ] Update WebTest if needed
- [ ] Run `poetry update`

### 1.4 Update JavaScript Dependencies
- [ ] Update eslint to v9.x (with flat config migration)
- [ ] Check if xhr-shim is still needed with modern Pyodide
- [ ] Update `package.json`

### 1.5 Security Improvements
- [ ] Document intentional hardcoded SECRET_KEY for browser-only use
- [ ] Add configurable DEBUG setting
- [ ] Improve cookie handling (multiple cookies)
- [ ] Fix potential code injection in Python execution
- [ ] Add basic input sanitization

### 1.6 Basic Error Handling
- [ ] Add try-catch around Pyodide operations
- [ ] User-friendly error messages
- [ ] Graceful degradation for unsupported browsers

---

## Phase 2: Quality & Testing

### 2.1 Python Unit Tests
- [ ] Create `tests/` directory structure
- [ ] Add pytest and pytest-django to dependencies
- [ ] Write model tests for Question/Choice
- [ ] Write view tests for all endpoints
- [ ] Write admin tests

### 2.2 JavaScript Tests
- [ ] Add Jest for JavaScript testing
- [ ] Write tests for cookie handling
- [ ] Write tests for request building
- [ ] Mock Pyodide for unit tests

### 2.3 Integration/E2E Tests
- [ ] Add Playwright for E2E testing
- [ ] Test full page load
- [ ] Test form submissions
- [ ] Test admin login flow
- [ ] Test across browsers

### 2.4 CI/CD Pipeline
- [ ] Create GitHub Actions workflow
- [ ] Run Python tests on PR
- [ ] Run JavaScript tests on PR
- [ ] Run linting on PR
- [ ] Automated wheel building
- [ ] Automated deployment to GitHub Pages

### 2.5 Documentation Updates
- [ ] Update README with current requirements
- [ ] Add architecture diagram
- [ ] Add contributing guide
- [ ] Add troubleshooting section

---

## Phase 3: Performance & UX

### 3.1 Loading Experience
- [ ] Add progress indicator during Pyodide load
- [ ] Show download progress (Pyodide is ~20MB)
- [ ] Add loading stages feedback
- [ ] Skeleton/placeholder UI

### 3.2 Caching Strategy
- [ ] Cache Pyodide files in service worker
- [ ] Cache Python packages
- [ ] Implement cache versioning
- [ ] Add cache invalidation logic

### 3.3 Code Modernization
- [ ] Convert worker.js to ES modules
- [ ] Split into separate modules
- [ ] Add TypeScript (optional)
- [ ] Modern build tooling (Vite)

### 3.4 Bundle Optimization
- [ ] Minify JavaScript
- [ ] Optimize wheel size
- [ ] Lazy load non-critical components

### 3.5 Browser Compatibility
- [ ] Add feature detection
- [ ] Graceful fallback messages
- [ ] Test Safari/iOS fixes from Pyodide 0.29

---

## Phase 4: Enhanced Features

### 4.1 Offline Support
- [ ] Full offline caching
- [ ] Detect online/offline state
- [ ] Queue operations when offline
- [ ] Sync when back online

### 4.2 Data Persistence
- [ ] IndexedDB backend for SQLite
- [ ] Persist database across sessions
- [ ] Data export (JSON/CSV)
- [ ] Data import/restore
- [ ] Handle storage quota

### 4.3 Developer Experience
- [ ] Hot reload for development
- [ ] Better error messages with stack traces
- [ ] Django Debug Toolbar integration (if possible)
- [ ] SQL query logging

### 4.4 Advanced Features
- [ ] Multiple database support
- [ ] File upload handling
- [ ] WebSocket simulation (if feasible)
- [ ] Custom management commands

---

## Success Criteria Per Phase

### Phase 1 Success
- Application loads and runs with updated dependencies
- All existing functionality works
- No security warnings in browser console
- Wheel builds successfully

### Phase 2 Success
- >80% code coverage
- All tests pass in CI
- Automated deployment works
- Documentation is comprehensive

### Phase 3 Success
- Initial load time improved by >30%
- Repeat visits load instantly from cache
- Modern build tooling in place
- Works across all major browsers

### Phase 4 Success
- Application works fully offline
- Data persists across browser sessions
- Export/import functionality works
- Developer workflow is smooth
