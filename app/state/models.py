"""
State Models for Multi-Turn Hackathon Interaction
Handles session context, dialogue state machine, user profile, and mentor requests.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class DialogueState(str, Enum):
    IDLE = "IDLE"
    AWAITING_TABLE_FOR_MENTOR = "AWAITING_TABLE_FOR_MENTOR"
    AWAITING_ISSUE_FOR_MENTOR = "AWAITING_ISSUE_FOR_MENTOR"
    AWAITING_TEAM_REGISTRATION = "AWAITING_TEAM_REGISTRATION"
    CONFIRMING_SUBMISSION = "CONFIRMING_SUBMISSION"

class TicketStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    RESOLVED = "RESOLVED"

class MentorTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: f"TICK-{uuid.uuid4().hex[:6].upper()}")
    team_name: str
    table_number: str
    track: Optional[str] = "General"
    topic: str
    status: TicketStatus = TicketStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

class UserProfile(BaseModel):
    participant_name: Optional[str] = "Hacker"
    team_name: Optional[str] = None
    table_number: Optional[str] = None
    track: Optional[str] = None
    github_url: Optional[str] = None

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    intent: Optional[str] = None
    quick_replies: List[str] = Field(default_factory=list)
    action: Optional[Dict[str, Any]] = None

class SessionState(BaseModel):
    session_id: str
    user_profile: UserProfile = Field(default_factory=UserProfile)
    dialogue_state: DialogueState = DialogueState.IDLE
    dialogue_context: Dict[str, Any] = Field(default_factory=dict)
    messages: List[ChatMessage] = Field(default_factory=list)
    tickets: List[MentorTicket] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_active: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
