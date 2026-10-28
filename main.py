"""
FastAPI Server & Real-Time Interaction Gateway
Integrates WebSocket endpoints, REST API, state synchronization, and UI serving.
"""

import os
import sys
import json
from pathlib import Path

# Enable UTF-8 for console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.engine import bot_engine
from app.state.state_manager import state_manager
from app.parser.action_schemas import ParsedBotResponse
from app.config import settings

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "web" / "static"
TEMPLATE_DIR = BASE_DIR / "app" / "web" / "templates"

app = FastAPI(
    title="HackNova Real-Time AI Chatbot",
    description="Automated Query Handling, Response Parsing, and State Management for Hackathons",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and template mounts
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Request Models
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ProfileUpdateRequest(BaseModel):
    session_id: str
    team_name: Optional[str] = None
    table_number: Optional[str] = None
    track: Optional[str] = None

# --- Web UI Routes ---
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"event": settings.EVENT_NAME})

# --- REST API Endpoints ---
@app.post("/api/chat", response_model=ParsedBotResponse)
async def handle_chat_rest(req: ChatRequest):
    """Processes user queries via standard HTTP POST request."""
    response = bot_engine.process_query(session_id=req.session_id, user_message=req.message)
    return response

@app.get("/api/state/{session_id}")
async def get_session_state(session_id: str):
    """Returns the full conversational state, profile, and tickets for a session."""
    session = state_manager.get_or_create_session(session_id)
    return session.model_dump()

@app.post("/api/profile")
async def update_profile(req: ProfileUpdateRequest):
    """Updates participant metadata (team, table, track)."""
    updated = state_manager.update_profile(
        req.session_id,
        team_name=req.team_name,
        table_number=req.table_number,
        track=req.track
    )
    return {"status": "ok", "profile": updated.model_dump()}

@app.get("/api/tickets")
async def list_all_tickets():
    """Organizer view: lists all active mentor tickets across tables."""
    tickets = state_manager.get_all_tickets()
    return {"count": len(tickets), "tickets": [t.model_dump() for t in tickets]}

@app.post("/api/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str):
    """Marks a mentor ticket as resolved."""
    success = state_manager.resolve_ticket(ticket_id)
    return {"ticket_id": ticket_id, "resolved": success}

# --- Real-Time WebSocket Endpoint ---
@app.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """Bi-directional WebSocket for sub-second real-time interaction."""
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            user_msg = payload.get("text", "")
            
            if not user_msg.strip():
                continue

            # Core processing: intent -> state machine -> knowledge -> parsing
            bot_response = bot_engine.process_query(session_id=session_id, user_message=user_msg)
            
            # Send structured response back in real-time
            await websocket.send_text(bot_response.model_dump_json())

    except WebSocketDisconnect:
        # Client gracefully closed or refreshed
        pass
    except Exception as e:
        print(f"[WebSocket] Error in session {session_id}: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(">> HackNova Interactive AI Chatbot Server starting...")
    print(">> Open your browser at: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, app_dir=str(BASE_DIR))
