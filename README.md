# Oghenetega: Production-Ready EV Chatbot Service

Oghenetega is an enthusiastic, high-energy chatbot who knows all about electric vehicles (EVs). This project exposes a FastAPI endpoint with structured logging, Prometheus monitoring, and containerization via Docker.

## Features
- **FastAPI Endpoint:** Exposes `/chat` (to chat) and `/reset` (to wipe session memory).
- **Dockerized:** Packaged with a Dockerfile running as a non-root user and automated `/health` checks.
- **Docker Compose Orchestration:** Runs the app alongside a Prometheus metrics database.
- **Monitoring:** Exposes Prometheus-compatible metrics on `/metrics` to track API request success rates and latencies.
- **Structured JSON Logging:** Outputs standardized logs in JSON format for easy ingestion by log managers (like ELK/Splunk).

---

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed.
- A Gemini API Key from Google AI Studio.

### Configuration
Create a `.env` file in the root directory (never commit this file) with your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Service

Build and start the application and monitoring stack using Docker Compose:
```bash
docker-compose up --build -d
```

Verify that the containers are running and healthy:
```bash
docker-compose ps
```

---

## Interacting with the API

You can test the API by sending POST requests.

### 1. Chat with Oghenetega
**Endpoint:** `POST /chat`

**Example Request (using cURL):**
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Why are EVs better than gas cars?", "session_id": "user_session_1"}'
```

**Example Response:**
```json
{
  "response": "Oghenetega here! Accelerating into this answer... EVs have instant torque, fewer moving parts to break, and zero tailpipe emissions! Plus, charging is way cheaper than gas. You're fully charged!",
  "tokens_used": 154
}
```

### 2. Reset Chat Session
**Endpoint:** `POST /reset`

**Example Request:**
```bash
curl -X POST http://localhost:8000/reset \
     -H "Content-Type: application/json" \
     -d '{"session_id": "user_session_1"}'
```

---

## Monitoring and Metrics

- **API Health Status:** Check `http://localhost:8000/health`
- **Raw Metrics Endpoint:** Access `http://localhost:8000/metrics`
- **Prometheus Dashboard:** Open `http://localhost:9090` in your web browser. 
  - To view latency, search for `http_request_duration_seconds_bucket`.
  - To track request counts/success rate, search for `http_requests_total`.
