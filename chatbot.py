import json
import os
import sys
import time
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

# Load environment variables
load_dotenv()

# Setup structured JSON logging
logger = logging.getLogger("chatbot_service")
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Initialize FastAPI app
app = FastAPI(title="Oghenetega EV Chatbot Service", version="1.0.0")

# Instrument Prometheus metrics
Instrumentator().instrument(app).expose(app)

class ChatbotManager:
    def __init__(self, history_dir="history"):
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)
        
        self.system_prompt = """
        You are Oghenetega, an enthusiastic, high-energy expert on all things electric vehicles (EVs).
        You love talking about battery technology, charging networks, motors, and EV models.
        You occasionally use car-related puns (like 'let's accelerate' or 'you're fully charged').
        Keep your answers relatively concise but very knowledgeable.
        """
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment")
            # We don't exit immediately here to allow FastAPI to start and fail healthchecks or show startup errors properly
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=self.system_prompt
            )

    def get_history_file(self, session_id: str) -> str:
        return os.path.join(self.history_dir, f"{session_id}_history.json")

    def load_history(self, session_id: str) -> list:
        history_file = self.get_history_file(session_id)
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Error loading history", extra={"session_id": session_id, "error": str(e)})
        return []

    def save_history(self, session_id: str, history: list):
        history_file = self.get_history_file(session_id)
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            logger.error("Error saving history", extra={"session_id": session_id, "error": str(e)})

    def reset_history(self, session_id: str):
        history_file = self.get_history_file(session_id)
        if os.path.exists(history_file):
            try:
                os.remove(history_file)
            except Exception as e:
                logger.error("Error deleting history file", extra={"session_id": session_id, "error": str(e)})

    def generate_response(self, session_id: str, user_input: str) -> tuple[str, int]:
        if not self.model:
            raise ValueError("Gemini API not configured. Missing GEMINI_API_KEY.")
            
        history = self.load_history(session_id)
        
        # Build Gemini session history
        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
            
        chat_session = self.model.start_chat(history=gemini_history)
        
        # Call API (non-streaming for standard REST API response, or we could stream, but keeping it standard JSON for service requests)
        response = chat_session.send_message(user_input)
        
        tokens_used = 0
        if response.usage_metadata:
            tokens_used = response.usage_metadata.total_token_count
            
        # Update history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "model", "content": response.text})
        self.save_history(session_id, history)
        
        return response.text, tokens_used

bot_manager = ChatbotManager()

# Request Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

# Middleware to log requests and responses in JSON
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request processed",
            extra={
                "method": request.method,
                "url": str(request.url.path),
                "status_code": response.status_code,
                "duration_seconds": process_time
            }
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed",
            extra={
                "method": request.method,
                "url": str(request.url.path),
                "error": str(e),
                "duration_seconds": process_time
            }
        )
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/health")
def health_check():
    # If model configuration failed, report unhealthy
    if not bot_manager.model:
        raise HTTPException(status_code=503, detail="Gemini API not configured")
    return {"status": "healthy"}

@app.post("/chat")
def chat(payload: ChatRequest):
    try:
        start_time = time.time()
        reply, tokens = bot_manager.generate_response(payload.session_id, payload.message)
        duration = time.time() - start_time
        
        logger.info(
            "Chat interaction successful",
            extra={
                "session_id": payload.session_id,
                "tokens_used": tokens,
                "duration_seconds": duration
            }
        )
        return {"response": reply, "tokens_used": tokens}
    except Exception as e:
        logger.error(
            "Error during chat interaction",
            extra={
                "session_id": payload.session_id,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def reset_chat(payload: ChatRequest):
    bot_manager.reset_history(payload.session_id)
    logger.info("Chat history cleared", extra={"session_id": payload.session_id})
    return {"message": f"History cleared for session: {payload.session_id}"}
