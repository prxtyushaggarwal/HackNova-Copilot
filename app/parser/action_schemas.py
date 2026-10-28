"""
Schemas for Parsed Responses and Action Triggers
Used by the response parser to deliver structured payloads to frontend/clients.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ParsedAction(BaseModel):
    action_type: str # e.g. "NONE", "TICKET_CREATED", "PROFILE_UPDATED", "OPEN_LINK", "SHOW_SCHEDULE"
    payload: Dict[str, Any] = Field(default_factory=dict)

class ParsedBotResponse(BaseModel):
    reply_text: str
    intent: str
    confidence: float
    quick_replies: List[str] = Field(default_factory=list)
    action: Optional[ParsedAction] = None
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
