"""
Core Orchestration Engine
Coordinates intent classification, dialogue state transitions,
knowledge retrieval, entity extraction, and response parsing.
"""

import time
from typing import Dict, Any, Optional
from app.state.models import DialogueState, ChatMessage, TicketStatus
from app.state.state_manager import state_manager
from app.core.intent_classifier import intent_classifier
from app.core.knowledge_base import knowledge_base
from app.parser.response_parser import response_parser
from app.parser.action_schemas import ParsedBotResponse, ParsedAction
from app.services.ai_service import ai_service
from app.config import settings

class ChatbotEngine:
    """Core logic engine handling real-time hackathon queries."""

    def process_query(self, session_id: str, user_message: str) -> ParsedBotResponse:
        start_time = time.perf_counter()
        session = state_manager.get_or_create_session(session_id)
        text_clean = user_message.strip()

        # Log user message
        state_manager.add_message(session_id, ChatMessage(role="user", content=text_clean))

        # Step 1: Entity Extraction
        entities = response_parser.extract_entities(text_clean)
        if entities:
            state_manager.update_profile(session_id, **entities)

        # Step 2: Handle Active State Machine (Slot-filling / Multi-turn flows)
        if session.dialogue_state == DialogueState.AWAITING_TABLE_FOR_MENTOR:
            if "cancel" in text_clean.lower():
                state_manager.clear_dialogue_context(session_id)
                return self._finalize(
                    session_id,
                    "Mentor request cancelled. Let me know if you need anything else!",
                    intent="mentor_request",
                    confidence=1.0,
                    start_time=start_time
                )

            table_extracted = entities.get("table_number")
            if not table_extracted:
                # Check if user just typed a number like "4" or "Table 4"
                words = text_clean.split()
                for w in words:
                    if w.isdigit():
                        table_extracted = w
                        break

            if table_extracted:
                topic = session.dialogue_context.get("topic", "General Technical Help")
                ticket = state_manager.create_mentor_ticket(session_id, topic=topic, table_number=str(table_extracted))
                state_manager.clear_dialogue_context(session_id)

                reply = (
                    f"### 🎟️ **Mentor Ticket Dispatched!**\n\n"
                    f"- **Ticket ID:** `{ticket.ticket_id}`\n"
                    f"- **Table:** `{ticket.table_number}`\n"
                    f"- **Topic:** {ticket.topic}\n"
                    f"- **Status:** ⏳ *{ticket.status.value}*\n\n"
                    f"A roving mentor has been alerted via Discord and will visit **Table {ticket.table_number}** shortly!"
                )
                action = ParsedAction(action_type="TICKET_CREATED", payload=ticket.model_dump())
                return self._finalize(session_id, reply, intent="mentor_request", confidence=1.0, action=action, start_time=start_time)
            else:
                reply = "Please specify your **Table Number** (e.g. *\"Table 12\"* or *\"5\"*) so the mentor can locate your team:"
                return self._finalize(session_id, reply, intent="mentor_request", confidence=0.9, start_time=start_time)

        # Step 3: Intent Classification
        intent, confidence = intent_classifier.classify(text_clean)

        # Step 4: Dispatch based on Intent & Context
        action: Optional[ParsedAction] = None

        if intent == "mentor_request":
            topic = text_clean
            table = entities.get("table_number") or session.user_profile.table_number
            if table:
                ticket = state_manager.create_mentor_ticket(session_id, topic=topic, table_number=str(table))
                reply = (
                    f"### 🎟️ **Mentor Request Created!**\n\n"
                    f"- **Ticket ID:** `{ticket.ticket_id}`\n"
                    f"- **Table:** `{ticket.table_number}`\n"
                    f"- **Topic:** {topic}\n"
                    f"- **Status:** ⏳ *{ticket.status.value}*\n\n"
                    f"A mentor has been dispatched to **Table {ticket.table_number}**. Hang tight!"
                )
                action = ParsedAction(action_type="TICKET_CREATED", payload=ticket.model_dump())
            else:
                state_manager.set_dialogue_state(
                    session_id,
                    DialogueState.AWAITING_TABLE_FOR_MENTOR,
                    context={"topic": topic}
                )
                reply = (
                    "### 🧑‍🏫 **Requesting a Mentor**\n\n"
                    "I can dispatch a mentor right away! **Which table is your team seated at?**\n"
                    "*(e.g., \"Table 7\" or simply \"7\")*"
                )

        elif intent == "ticket_status":
            if not session.tickets:
                reply = "You currently have no active mentor tickets. Need help with a bug or pitch? Type **`\"I need a mentor\"`**!"
            else:
                ticket_lines = [
                    f"- **{t.ticket_id}** | Table {t.table_number} | *{t.topic}* | Status: **{t.status.value}** ({t.created_at})"
                    for t in session.tickets
                ]
                reply = (
                    f"### 📋 **Your Active Mentor Tickets ({len(session.tickets)})**\n\n"
                    + "\n".join(ticket_lines)
                )

        elif intent == "greeting":
            team_text = f" for **{session.user_profile.team_name}**" if session.user_profile.team_name else ""
            table_text = f" at **Table {session.user_profile.table_number}**" if session.user_profile.table_number else ""
            reply = (
                f"### 👋 Welcome to **{settings.EVENT_NAME}**! 🚀\n\n"
                f"I am your automated Hackathon Copilot{team_text}{table_text}.\n\n"
                f"**How can I assist you right now?**\n"
                f"- 📅 Check the event schedule & code freeze countdown\n"
                f"- 🧑‍🏫 Call a mentor to your table with live status tracking\n"
                f"- 📶 Wi-Fi password & venue facilities map\n"
                f"- ⚖️ Review official rules and judging rubrics\n\n"
                f"*Choose a quick action below or type any question!*"
            )
            action = ParsedAction(action_type="SHOW_OVERVIEW", payload={"event": settings.EVENT_NAME})

        elif intent == "profile_update":
            reply = (
                f"### ✅ **Team Profile Updated**\n\n"
                f"- **Team Name:** `{session.user_profile.team_name or 'Not set'}`\n"
                f"- **Table:** `{session.user_profile.table_number or 'Not set'}`\n"
                f"- **Track:** `{session.user_profile.track or 'General'}`\n\n"
                f"Whenever you request a mentor, they will automatically head to **Table {session.user_profile.table_number or 'your table'}**."
            )
            action = ParsedAction(action_type="PROFILE_UPDATED", payload=session.user_profile.model_dump())

        else:
            # Try knowledge base match first
            kb_result = knowledge_base.search(text_clean)
            if kb_result:
                article, kb_score = kb_result
                confidence = max(confidence, kb_score)
                reply = article["answer"]
            else:
                # Fallback to AI generation with contextual awareness
                reply = ai_service.generate_response(text_clean)

        return self._finalize(
            session_id,
            reply,
            intent=intent,
            confidence=confidence,
            action=action,
            entities=entities,
            start_time=start_time
        )

    def _finalize(
        self,
        session_id: str,
        reply_text: str,
        intent: str,
        confidence: float,
        action: Optional[ParsedAction] = None,
        entities: Optional[Dict[str, Any]] = None,
        start_time: float = 0.0
    ) -> ParsedBotResponse:
        session = state_manager.get_or_create_session(session_id)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        structured_response = response_parser.structure_response(
            raw_text=reply_text,
            intent=intent,
            confidence=confidence,
            dialogue_state=session.dialogue_state.value,
            action=action,
            extracted_entities=entities,
            latency_ms=latency_ms
        )

        # Log assistant message
        state_manager.add_message(
            session_id,
            ChatMessage(
                role="assistant",
                content=structured_response.reply_text,
                intent=intent,
                quick_replies=structured_response.quick_replies,
                action=action.model_dump() if action else None
            )
        )

        return structured_response

# Global singleton
bot_engine = ChatbotEngine()
