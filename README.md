# 🚀 HackNova Copilot — Hackathon AI Query Automation Chatbot

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-success.svg)](https://websockets.readthedocs.io/)
[![Tests](https://img.shields.io/badge/Tests-5%20Passing-brightgreen.svg)](test_bot.py)

An interactive, AI-powered conversational system built in Python to automate query handling, mentor dispatches, and participant assistance during live hackathons.

> **Resume Alignment:**
> - *"Developed an interactive AI-powered chatbot using Python to automate query handling during the hackathon."*
> - *"Implemented core logic, response parsing, and state management for real-time user interaction."*

---

## 🌟 Key Features

1. **⚡ Core Orchestration Logic (`app/core/`)**
   - **Intent Classifier:** Detects participant intents (`schedule`, `rules`, `judging`, `mentor_request`, `submission`, `venue_wifi`, `food`, `general_ai`) with confidence scoring.
   - **Knowledge Base:** Curated hackathon repository with fuzzy token search for instantaneous, reliable answers.
   - **Hybrid AI Engine:** Seamlessly connects to **Google Gemini** when an API key is available, or operates completely offline using the deterministic **Smart Hackathon Synthesizer**.

2. **🔍 Response Parsing & Entity Extraction (`app/parser/`)**
   - **Entity Recognition:** Automatically extracts table numbers (`Table 14`, `T-25`), team names (`Team ByteForge`), tracks, and GitHub repositories from arbitrary user messages.
   - **Dynamic Quick-Reply Chips:** Context-aware action buttons attached to bot responses for instant one-tap interactions.
   - **Action Trigger Payload:** Structures payloads for UI actions (`TICKET_CREATED`, `PROFILE_UPDATED`, `SHOW_SCHEDULE`).

3. **🧠 State Management (`app/state/`)**
   - **Multi-Turn Dialogue State Machine:** Manages complex conversational workflows like slot-filling for mentor requests (`AWAITING_TABLE_FOR_MENTOR` $\to$ `IDLE`).
   - **Session & Profile Tracking:** Maintains team name, table location, chosen track, and conversation history per participant across turns.
   - **Live Ticket Lifecycle:** Thread-safe mentor ticket issuance and status management (`PENDING` $\to$ `RESOLVED`).

4. **🌐 Real-Time User Interaction (`app/web/`)**
   - **Full-Duplex WebSockets:** Sub-second bi-directional message streaming (`/ws/{session_id}`).
   - **Interactive Dark Glassmorphism UI:** Modern responsive dashboard featuring a live submission countdown timer, active ticket cards, and Markdown rendering.
   - **Interactive CLI Mode (`demo_cli.py`):** Test the full chatbot experience straight from the terminal.

---

## 🏗️ Project Architecture

```
hackathon-query-bot/
├── app/
│   ├── config.py                 # Hackathon schedule, tracks, Wi-Fi, rules
│   ├── core/
│   │   ├── engine.py             # Central controller (coordinates Intent -> State -> Parser)
│   │   ├── intent_classifier.py  # Regex & keyword intent classification with confidence scores
│   │   └── knowledge_base.py     # Offline-capable query retrieval & scoring
│   ├── parser/
│   │   ├── action_schemas.py     # Pydantic schemas for structured client responses
│   │   └── response_parser.py    # Entity extraction (table #, team) & markdown structuring
│   ├── state/
│   │   ├── models.py             # Pydantic models for Session, Profile, and Mentor Tickets
│   │   └── state_manager.py      # Thread-safe (RLock) multi-turn session state repository
│   ├── services/
│   │   └── ai_service.py         # Google Gemini integration + intelligent local synthesizer
│   └── web/
│       ├── static/
│       │   ├── css/style.css     # Glassmorphism dark theme styling
│       │   └── js/chat.js        # WebSocket client, markdown rendering & countdown clock
│       └── templates/
│           └── index.html        # Interactive chat interface & dashboard
├── main.py                       # FastAPI application entrypoint (WebSocket + REST endpoints)
├── demo_cli.py                   # Terminal CLI for interactive testing
├── test_bot.py                   # Automated unit test suite (pytest)
├── requirements.txt              # Project dependencies
├── .env.example                  # Environment configuration template
└── README.md                     # Documentation
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the project directory
cd hackathon-query-bot

# Install requirements
pip install -r requirements.txt
```

### 2. (Optional) Configure Gemini API Key

If you want the chatbot to use Google Gemini for dynamic technical answers:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"

# Linux / macOS
export GEMINI_API_KEY="your-gemini-api-key"
```
*(If no key is provided, the chatbot runs in **Smart Local Synthesizer Mode** with zero external dependencies!)*

### 3. Launch the Web Application

```bash
python main.py
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 💻 Interactive Terminal CLI Mode

You can also run and demo the chatbot directly inside your terminal:

```bash
python demo_cli.py
```

---

## 🧪 Running Unit Tests

Run the test suite verifying intent classification, entity extraction, and multi-turn state management:

```bash
python -m pytest test_bot.py -v
```

All 5 core test cases pass:
- ✅ `test_intent_classification` (Schedule, Wi-Fi, Rules, Judging, Mentor)
- ✅ `test_entity_extraction` (Table numbers, Team names, GitHub URLs)
- ✅ `test_multi_turn_state_management` (Slot-filling & state transitions)
- ✅ `test_profile_persistence` (Context preservation across turns)
- ✅ `test_response_structure_and_schema` (Pydantic contract validation)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `WS` | `/ws/{session_id}` | Real-time bi-directional chat socket |
| `POST` | `/api/chat` | Send a query and receive a structured JSON response |
| `GET` | `/api/state/{session_id}` | Retrieve profile, conversation history, and tickets |
| `POST` | `/api/profile` | Update participant metadata (team, table, track) |
| `GET` | `/api/tickets` | Retrieve all active mentor tickets across the hackathon |
| `POST` | `/api/tickets/{id}/resolve`| Mark a mentor ticket as resolved |

---

## 💡 Example Multi-Turn Interaction

```text
User: "I need a mentor to help us debug"
NovaBot: "I can dispatch a mentor right away! Which table is your team seated at?"
State: AWAITING_TABLE_FOR_MENTOR

User: "Table 14"
NovaBot: "🎟️ Mentor Ticket Dispatched! [TICK-A8B42]
          A mentor has been alerted via Discord and will visit Table 14 shortly!"
State: IDLE
Action: TICKET_CREATED (Table: 14)
```
