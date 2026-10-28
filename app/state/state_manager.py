"""
Session and Dialogue State Management
Maintains real-time conversational context, state machine transitions,
and user-specific hackathon data across multi-turn interactions.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
import threading
from app.state.models import SessionState, DialogueState, UserProfile, MentorTicket, TicketStatus, ChatMessage

class StateManager:
    """Thread-safe state manager for conversational sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}
        self._lock = threading.RLock()

    def get_or_create_session(self, session_id: str) -> SessionState:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionState(session_id=session_id)
            session = self._sessions[session_id]
            session.last_active = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        with self._lock:
            return self._sessions.get(session_id)

    def update_profile(self, session_id: str, **kwargs) -> UserProfile:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                session = SessionState(session_id=session_id)
                self._sessions[session_id] = session

            profile_data = session.user_profile.model_dump()
            for key, val in kwargs.items():
                if val is not None and key in profile_data:
                    profile_data[key] = val
            session.user_profile = UserProfile(**profile_data)
            return session.user_profile

    def set_dialogue_state(self, session_id: str, state: DialogueState, context: Optional[Dict[str, Any]] = None):
        with self._lock:
            session = self.get_or_create_session(session_id)
            session.dialogue_state = state
            if context is not None:
                session.dialogue_context.update(context)

    def clear_dialogue_context(self, session_id: str):
        with self._lock:
            session = self.get_or_create_session(session_id)
            session.dialogue_state = DialogueState.IDLE
            session.dialogue_context.clear()

    def add_message(self, session_id: str, message: ChatMessage):
        with self._lock:
            session = self.get_or_create_session(session_id)
            session.messages.append(message)
            # Limit history to latest 50 messages per session
            if len(session.messages) > 50:
                session.messages = session.messages[-50:]

    def create_mentor_ticket(self, session_id: str, topic: str, table_number: Optional[str] = None) -> MentorTicket:
        with self._lock:
            session = self.get_or_create_session(session_id)
            table = table_number or session.user_profile.table_number or "Unassigned"
            team = session.user_profile.team_name or f"Team-{session_id[:5]}"
            track = session.user_profile.track or "General"

            ticket = MentorTicket(
                team_name=team,
                table_number=str(table),
                track=track,
                topic=topic,
                status=TicketStatus.PENDING
            )
            session.tickets.append(ticket)
            # Also update session profile table if provided
            if table_number and table_number != "Unassigned":
                session.user_profile.table_number = str(table_number)
            return ticket

    def get_all_tickets(self) -> List[MentorTicket]:
        with self._lock:
            all_tickets = []
            for session in self._sessions.values():
                all_tickets.extend(session.tickets)
            return all_tickets

    def resolve_ticket(self, ticket_id: str) -> bool:
        with self._lock:
            for session in self._sessions.values():
                for ticket in session.tickets:
                    if ticket.ticket_id == ticket_id:
                        ticket.status = TicketStatus.RESOLVED
                        return True
            return False

# Global singleton
state_manager = StateManager()
