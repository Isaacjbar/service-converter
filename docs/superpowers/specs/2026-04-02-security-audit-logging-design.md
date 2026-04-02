# Security & Observability Design
**Date:** 2026-04-02  
**Project:** service-converter + converter-web-app  
**Status:** Approved by user

---

## Overview

Add three cross-cutting security/observability layers to the Django backend and React frontend:

1. **AuditLog** — database table that records every significant action (CRUD, login, errors)
2. **Django Logger** — file-based logging for all incoming HTTP requests and caught exceptions
3. **SHA-256 + AES-256** — data integrity checksums on audit entries and payload encryption between frontend and backend

---

## 1. AuditLog — New `apps/audit` App

### Model: `AuditLog`

| Field | Type | Notes |
|-------|------|-------|
| `id` | BigAutoField | PK |
| `user` | FK → User, null=True, SET_NULL | Who performed the action |
| `action` | CharField(10) | CREATE, UPDATE, DELETE, LOGIN, ACCESS, ERROR |
| `resource` | CharField(100) | Model name: "DiagramHistory", "User", etc. |
| `resource_id` | CharField(50), null | ID of affected object |
| `description` | TextField | Human-readable detail |
| `ip_address` | GenericIPAddressField, null | Extracted from request |
| `checksum` | CharField(64) | SHA-256 of entry content (tamper detection) |
| `created_at` | DateTimeField(auto_now_add=True) | Immutable timestamp |

> No `updated_at` — audit entries are write-once and never updated.

### Checksum Computation

```
sha256(str(user_id) + action + resource + str(resource_id) + description)
```

Computed in `AuditLog.save()` before writing to DB (`created_at` is excluded because `auto_now_add` is not available pre-save). Allows offline verification that content fields have not been tampered with.

### Population Strategy — Django Signals

Signals (not middleware) write to AuditLog because they have direct access to the model instance and the request context is passed via `kwargs`:

| Signal | Source | Action logged |
|--------|--------|---------------|
| `post_save` on `DiagramHistory` (created=True) | converter | CREATE DiagramHistory |
| `post_delete` on `DiagramHistory` | converter | DELETE DiagramHistory |
| `post_save` on `User` (created=True) | accounts | CREATE User |
| `post_save` on `User` (created=False) | accounts | UPDATE User |
| Login success (JWT `token_obtain_pair`) | accounts | LOGIN User |
| Exception caught in views | any view | ERROR |

IP address is injected into signals via a thread-local helper (`utils/request_context.py`) set by the RequestLoggingMiddleware.

---

## 2. Django Logger

### Configuration (in `config/settings.py`)

Two rotating file handlers:

| Logger name | File | Level | Content |
|-------------|------|-------|---------|
| `converter.requests` | `logs/requests.log` | INFO | Every HTTP request: method, path, user, IP, response status |
| `converter.errors` | `logs/errors.log` | ERROR | Caught exceptions with full traceback |

Both also write to console (stdout) for Docker/container visibility.

**Rotation:** 10 MB per file, 5 backups kept.

**Format:**
```
[2026-04-02 14:32:01] INFO converter.requests POST /convert/ user=3 ip=192.168.1.1 → 200
[2026-04-02 14:32:05] ERROR converter.errors ConvertView: ZipFile extraction failed ...traceback...
```

### RequestLoggingMiddleware (`config/middleware.py`)

- Runs before the view; logs method, path, user ID (or "anon"), IP
- After the view returns; logs response status code
- Also stores IP in thread-local for signals to access
- Skips `/admin/` and static/media paths to reduce noise

### View-level Error Logging

Add `logger.error(exc_info=True)` to all existing bare `except` blocks:
- `apps/converter/views.py` — ZIP extraction, conversion errors
- `apps/accounts/views.py` — no explicit try/catch today; add a top-level handler around user update/delete

---

## 3. SHA-256 & AES-256

### SHA-256 — Two Uses

**A) AuditLog integrity checksum** (described above)

**B) `source_hash` field on `DiagramHistory`**
- New `CharField(64)` field: SHA-256 of `source_code`
- Computed automatically in `DiagramHistory.save()`
- Enables fast deduplication queries without comparing full source text
- The conversion service already computes SHA-256 for its LRU cache; this reuses the same utility

### AES-256-GCM — Payload Encryption

#### Key Management
- **Algorithm:** AES-256-GCM (authenticated encryption — integrity + confidentiality)
- **Key:** 32-byte shared secret stored in:
  - Django: `settings.AES_SECRET_KEY` (from `AES_SECRET_KEY` env var, hex-encoded 64 chars)
  - React: `import.meta.env.VITE_AES_KEY` (same value)
- **IV/Nonce:** 12 random bytes generated per request, prepended to ciphertext
- **Wire format:** `base64(nonce[12] + ciphertext + tag[16])`

#### Scope
- **Encrypted:** JSON request bodies (POST/PATCH/PUT) and JSON responses
- **Not encrypted:** Multipart form data (file uploads) — binary payloads are impractical to encrypt at this layer; HTTPS covers transport security for those
- **Signal header:** `X-Encrypted: true` on requests; backend echoes same header on responses

#### Middleware Order in `settings.MIDDLEWARE`

`RequestLoggingMiddleware` must be placed **before** `AESEncryptionMiddleware`:
- Logging middleware sets the thread-local IP (needed by signals) and logs the raw request before decryption alters the body.
- AES middleware then decrypts the body so DRF parsers see plain JSON.

Both go after `CorsMiddleware` and before `AuthenticationMiddleware`.

#### Backend — `AESEncryptionMiddleware` (`config/middleware.py`)

```
Request arrives with X-Encrypted: true
  → Middleware reads raw body, decrypts, replaces request._body
  → Content-Type forced to application/json
  → View processes normally
Response leaves
  → Middleware encrypts response.content
  → Returns JSON: {"data": "<base64-ciphertext>"}
```

Middleware short-circuits with HTTP 400 if decryption fails (bad key or tampered payload).

#### Frontend — Axios Interceptors (`src/utils/crypto.js` + `src/api/client.js`)

```
Request interceptor:
  if config.data and method !== GET:
    encrypt config.data → set as string body
    add header X-Encrypted: true

Response interceptor:
  if response.headers['x-encrypted'] === 'true':
    decrypt response.data.data → parse JSON → replace response.data
```

Uses the **Web Crypto API** (native browser API, no extra dependency) with AES-GCM 256.

---

## Files to Create / Modify

### New files

| Path | Purpose |
|------|---------|
| `apps/audit/__init__.py` | App package |
| `apps/audit/apps.py` | AppConfig, registers signals |
| `apps/audit/models.py` | AuditLog model |
| `apps/audit/signals.py` | Signal handlers |
| `apps/audit/admin.py` | Admin list view (read-only) |
| `apps/audit/migrations/0001_initial.py` | Initial migration |
| `utils/__init__.py` | Utils package |
| `utils/crypto.py` | sha256(), encrypt_aes256(), decrypt_aes256() |
| `utils/request_context.py` | Thread-local current request IP |
| `config/middleware.py` | RequestLoggingMiddleware, AESEncryptionMiddleware |
| `logs/.gitkeep` | Ensure logs/ directory is tracked |
| `src/utils/crypto.js` | Frontend AES-256-GCM helpers (Web Crypto API) |

### Modified files

| Path | Change |
|------|--------|
| `config/settings.py` | Add LOGGING, AES_SECRET_KEY, register audit app, add middlewares |
| `apps/history/models.py` | Add `source_hash` field, compute in save() |
| `apps/converter/views.py` | Add logger.error() in exception handlers |
| `apps/accounts/views.py` | Add logger.error() in exception handlers |
| `requirements.txt` | Add `cryptography>=42.0` |
| `src/api/client.js` (or equivalent axios instance) | Add encrypt/decrypt interceptors |
| `.env.example` (both projects) | Document AES_SECRET_KEY / VITE_AES_KEY |

---

## Non-Goals

- AES encryption of multipart file uploads
- Per-session key exchange (ECDH) — shared static key is sufficient for this project
- Soft deletes on DiagramHistory
- Rate limiting
- JWT token blacklist for logout
