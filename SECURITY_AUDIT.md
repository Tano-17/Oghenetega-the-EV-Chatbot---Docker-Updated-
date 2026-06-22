# 🔐 Security Audit Report
**Project:** Oghenetega EV Chatbot Service  
**Auditor:** Tano   
**Date:** 20 June 2026  
**Codebase:** `C:\Users\Tano\.gemini\antigravity\scratch\chatbot_project`

---

## 1. Executive Summary

The Oghenetega EV Chatbot is a FastAPI-based AI chat service powered by Google Gemini, containerized with Docker and monitored with Prometheus. The application demonstrates strong architectural practices — including a non-root Docker user, structured JSON logging, and session-based conversation memory — but contains **one critical and several medium-severity vulnerabilities** that must be resolved before any production launch. The most urgent issue is a hardcoded, live API key committed in the `.env` file, which could immediately compromise the project's Google Cloud account if the repository is ever made public.

---

## 2. Vulnerabilities Found (OWASP Checklist)

| # | Vulnerability | OWASP Category | Severity | File(s) |
|---|---|---|---|---|
| V-01 | Live API key stored in `.env` file (not excluded from git) | A02: Cryptographic Failures | 🔴 **Critical** |`.env`, `.gitignore` |
| V-02 | No input validation / length limits on user messages | A03: Injection | 🟠 **High** | `chatbot.py` L118–120 |
| V-03 | Session IDs are user-controlled strings (no auth/validation) | A01: Broken Access Control | 🟠 **High** | `chatbot.py` L58–59 |
| V-04 | `/metrics` Prometheus endpoint is publicly exposed | A01: Broken Access Control | 🟡 **Medium** | `chatbot.py` L32 |
| V-05 | History files stored locally with no access controls | A04: Insecure Design | 🟡 **Medium** | `chatbot.py` L35–37 |
| V-06 | No rate limiting on `/chat` endpoint | A04: Insecure Design | 🟡 **Medium** | `chatbot.py` L162 |
| V-07 | Error messages returned verbatim to client | A05: Security Misconfiguration | 🟡 **Medium** | `chatbot.py` L186 |
| V-08 | Dependency versions are not pinned to exact versions | A06: Vulnerable Components | 🔵 **Low** | `requirements.txt` |
| V-09 | No HTTPS/TLS — service runs on plain HTTP | A02: Cryptographic Failures | 🔵 **Low** | `docker-compose.yml` |
| V-10 | CORS policy not configured (FastAPI default: deny all, but undocumented) | A05: Security Misconfiguration | 🔵 **Low** | `chatbot.py` |

---

## 3. Vulnerability Details

### 🔴 V-01 — Hardcoded Live API Key (Critical)
**What it is:** The `.env` file contains a real, active `GEMINI_API_KEY`. The `.gitignore` does list `.env`, but because the file was likely created before `.gitignore` was set up, there is a risk it was committed at some point. Any git history leak, accidental `git add`, or repository made public would immediately expose the key.

**Why it matters:** An attacker could use this key to make unlimited Gemini API calls billed to your account, or access any other Google Cloud services the key is permitted for.

---

### 🟠 V-02 — No Input Validation on User Messages (High)
**What it is:** The `ChatRequest` model accepts any `message` string with no length cap, no content filtering, and no sanitisation.
```python
class ChatRequest(BaseModel):
    message: str          # ← no max_length, no validation
    session_id: str = "default_session"
```
**Why it matters:** A user could send an enormous prompt (prompt injection / jailbreak), crash the API with a multi-MB payload, or craft a message designed to manipulate the AI's system prompt.

---

### 🟠 V-03 — Unauthenticated Session ID Access (High)
**What it is:** Any caller who knows (or guesses) another user's `session_id` can read their full conversation history and impersonate them in future turns. There is no authentication, token validation, or session ownership check.

**Why it matters:** This is a broken access control vulnerability — user A can trivially spy on or manipulate user B's session.

---

### 🟡 V-04 — Public Prometheus Metrics Endpoint (Medium)
**What it is:** `Instrumentator().instrument(app).expose(app)` mounts `/metrics` with no authentication. This endpoint reveals internal runtime data: endpoint names, request durations, error rates, and server performance.

**Why it matters:** This is information disclosure — an attacker can map your API surface and time attacks using real performance data.

---

### 🟡 V-05 — Unprotected Local History Files (Medium)
**What it is:** Conversation history is saved as plain `.json` files on disk in the `history/` directory, named predictably (`{session_id}_history.json`). There is no encryption at rest.

**Why it matters:** Anyone with filesystem access (or a path traversal bug introduced later) can read any user's full conversation history in plaintext.

---

### 🟡 V-06 — No Rate Limiting (Medium)
**What it is:** The `/chat` endpoint accepts unlimited requests per second from any IP with no throttling or quota.

**Why it matters:** A single bad actor could spam the endpoint causing API quota exhaustion (costing you money) or a denial-of-service for other users.

---

### 🟡 V-07 — Raw Exception Messages Exposed to Client (Medium)
**What it is:**
```python
raise HTTPException(status_code=500, detail=str(e))  # line 186
```
Internal Python exception messages (which may contain file paths, variable names, or API error details) are returned directly in the HTTP response.

**Why it matters:** Information disclosure — attackers can harvest internal system details from error responses.

---

### 🔵 V-08 — Unpinned Dependency Versions (Low)
**What it is:** `requirements.txt` uses `>=` version specifiers (e.g. `fastapi>=0.100.0`). A future `pip install` could pull in a vulnerable newer version automatically.

---

### 🔵 V-09 — No HTTPS/TLS (Low)
**What it is:** The app runs on plain HTTP (`port 8000`). All messages, including API responses, are transmitted unencrypted.

---

### 🔵 V-10 — CORS Not Explicitly Configured (Low)
**What it is:** FastAPI's CORS middleware is not added. While the default is restrictive for browsers, it is undocumented behaviour and should be explicitly set for any web-facing deployment.

---

## 4. Fixes Implemented

| # | Fix | What Changed |
|---|---|---|
| F-01 | `.env` key rotation reminder added | (manual step required — see below) |
| F-02 | `.gitignore` verified to exclude `.env` | Confirmed `.env` is listed |
| F-03 | Error responses sanitised | Replace `str(e)` with a generic message in HTTP 500 responses |

> [!IMPORTANT]
> **F-01 requires manual action.** The API key in `.env` (`AIzaSyA7GajQO9-Le7DTpXSYW_vWQ9y8asAbm8o`) should be **revoked immediately** in the Google Cloud Console and replaced with a new one. Never commit a real key — use environment variable injection via your deployment platform instead.

---

## 5. Remaining Risks (Not Yet Fixed)

| # | Risk | Why Not Fixed |
|---|---|---|
| V-02 | No input validation | Requires adding Pydantic `max_length` constraints and a moderation layer |
| V-03 | Unauthenticated sessions | Requires implementing an authentication system (e.g. JWT tokens) — beyond scope of this audit |
| V-04 | Public `/metrics` endpoint | Requires adding middleware or network-level restriction |
| V-06 | No rate limiting | Requires adding `slowapi` or a reverse proxy like NGINX |
| V-09 | No HTTPS | Requires a reverse proxy (NGINX + Let's Encrypt) or cloud load balancer with TLS termination |

---

## 6. Recommendations Before Production Launch

1. **🔴 Rotate the API key immediately.** Go to [Google Cloud Console → APIs & Credentials](https://console.cloud.google.com/apis/credentials) and delete the current key. Set the new key via environment injection (Docker secret or cloud platform env var), never in a committed file.

2. **🟠 Add input validation.** Add `max_length=2000` to the `message` field in `ChatRequest` and consider a profanity/injection filter.

3. **🟠 Add authentication.** Implement JWT-based session tokens so users can only access their own conversation history.

4. **🟡 Restrict `/metrics`.** Either remove the public exposure or protect it with Basic Auth or network-level firewall rules.

5. **🟡 Add rate limiting.** Install `slowapi` and limit `/chat` to e.g. 10 requests/minute per IP.

6. **🟡 Add HTTPS.** Put the service behind an NGINX reverse proxy with Let's Encrypt, or deploy to a cloud platform (e.g. Cloud Run, Railway) that handles TLS automatically.

7. **🔵 Pin all dependency versions** using `pip freeze > requirements.txt` and check them with `pip audit` regularly.

8. **🔵 Add CORS policy** explicitly via FastAPI's `CORSMiddleware`, even if just to whitelist `null` for local development.

---

*Report generated — for educational purposes as part of Project assignment.*
