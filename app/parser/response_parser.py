"""
Response Parser & Entity Extraction Module
Implements robust entity recognition, structured response generation,
and actionable payload formatting for real-time user interaction.
"""

import re
from typing import Dict, Any, List, Optional
from app.parser.action_schemas import ParsedBotResponse, ParsedAction

class ResponseParser:
    """Parses user input for entities and structures bot responses with quick-actions."""

    # Regex patterns for hackathon entity extraction
    TABLE_PATTERNS = [
        re.compile(r'\b(?:table|tbl|desk|t)[-:\s#]*([a-zA-Z]?\d{1,3})\b', re.IGNORECASE),
        re.compile(r'\b(?:at|sitting at|seated at)\s+(?:table\s*)?([a-zA-Z]?\d{1,3})\b', re.IGNORECASE)
    ]
    
    TEAM_PATTERNS = [
        re.compile(r'\b(?:our team is|team name is|we are team|team:?)\s+([a-zA-Z0-9_\-]+(?:\s+[a-zA-Z0-9_\-]+)?)', re.IGNORECASE),
        re.compile(r'\bteam\s+([a-zA-Z0-9_\-]+)', re.IGNORECASE)
    ]

    GITHUB_PATTERN = re.compile(r'https?://github\.com/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+', re.IGNORECASE)
    
    TRACK_KEYWORDS = {
        "ai_agents": ["ai", "agents", "llm", "agentic", "gemini", "autonomous"],
        "fintech": ["fintech", "defi", "crypto", "payment", "finance", "banking"],
        "health": ["health", "medical", "doctor", "hospital", "bio", "healthcare"],
        "open_source": ["open source", "devtools", "infrastructure", "tooling", "library"]
    }

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extracts hackathon-specific entities from arbitrary user text."""
        entities = {}

        # 1. Extract Table Number
        for pat in self.TABLE_PATTERNS:
            match = pat.search(text)
            if match:
                entities["table_number"] = match.group(1).upper()
                break

        # 2. Extract Team Name
        for pat in self.TEAM_PATTERNS:
            match = pat.search(text)
            if match:
                extracted = match.group(1).strip()
                # strip trailing stop words
                extracted = re.sub(r'\s+(sitting|working|at|from|with)$', '', extracted, flags=re.IGNORECASE)
                # filter out false positives
                if extracted.lower() not in ["schedule", "rules", "mentor", "wifi", "help", "is"]:
                    entities["team_name"] = extracted
                    break

        # 3. Extract GitHub Repository
        github_match = self.GITHUB_PATTERN.search(text)
        if github_match:
            entities["github_url"] = github_match.group(0)

        # 4. Extract Track
        text_lower = text.lower()
        for track_id, keywords in self.TRACK_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                entities["track"] = track_id
                break

        return entities

    def build_quick_replies(self, intent: str, dialogue_state: str = "IDLE") -> List[str]:
        """Generates dynamic quick-reply chips based on intent and state."""
        if dialogue_state == "AWAITING_TABLE_FOR_MENTOR":
            return ["Table 1", "Table 5", "Table 10", "Table 15", "Cancel Request"]
        
        if dialogue_state == "AWAITING_ISSUE_FOR_MENTOR":
            return ["API Integration Bug", "Model Latency issue", "Pitch Review", "Cancel Request"]

        replies_map = {
            "schedule": ["What's the submission deadline?", "When is lunch?", "When do mentors arrive?"],
            "rules": ["Can we use pre-built APIs?", "What is the team size limit?", "Judging criteria"],
            "mentor_request": ["I need a mentor at Table 4", "Who are the mentors?", "Cancel request"],
            "submission": ["Submission portal link", "Required deliverables", "Code freeze time"],
            "venue_wifi": ["Wi-Fi password", "Where is the Hardware Lab?", "Restrooms & snacks"],
            "tracks": ["AI Agents Track", "FinTech Track", "HealthTech Track", "Open Source Track"],
            "greeting": ["View Schedule", "Hackathon Rules", "Request a Mentor", "Wi-Fi Details"],
        }
        return replies_map.get(intent, ["View Schedule", "Ask Rules", "Request Mentor", "Wi-Fi Info"])

    def structure_response(
        self,
        raw_text: str,
        intent: str,
        confidence: float,
        dialogue_state: str = "IDLE",
        action: Optional[ParsedAction] = None,
        extracted_entities: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0
    ) -> ParsedBotResponse:
        """Constructs a validated ParsedBotResponse model with quick replies and actions."""
        quick_replies = self.build_quick_replies(intent, dialogue_state)
        
        return ParsedBotResponse(
            reply_text=raw_text.strip(),
            intent=intent,
            confidence=round(confidence, 2),
            quick_replies=quick_replies,
            action=action,
            extracted_entities=extracted_entities or {},
            execution_time_ms=round(latency_ms, 2)
        )

# Global singleton
response_parser = ResponseParser()
