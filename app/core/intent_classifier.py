"""
Intent Classifier Module
Classifies incoming user messages into structured hackathon intents with confidence scoring.
"""

import re
from typing import Tuple

class IntentClassifier:
    """Core logic classifier mapping natural language queries to hackathon actions."""

    INTENT_PATTERNS = {
        "greeting": [
            r"^(hi|hello|hey|greetings|hola|good morning|good afternoon|sup)\b",
            r"^start\b"
        ],
        "mentor_request": [
            r"\b(mentor|mentor help|call mentor|need help|stuck|call a mentor|request mentor|send mentor)\b",
            r"\b(debug help|need assistance|can someone help)\b"
        ],
        "ticket_status": [
            r"\b(my ticket|ticket status|where is the mentor|mentor arriving|check ticket)\b"
        ],
        "submission": [
            r"\b(submission|submit|devpost|deadline|due date|code freeze|how to submit|submit project)\b"
        ],
        "food": [
            r"\b(food|lunch|dinner|breakfast|snacks|coffee|midnight meal|eat|cafeteria)\b"
        ],
        "schedule": [
            r"\b(schedule|timeline|agenda|when is|what time|program|opening ceremony|pitch time)\b"
        ],
        "rules": [
            r"\b(rules|rule|allowed|pre-existing|can we use|code of conduct|team size|eligibility)\b"
        ],
        "judging": [
            r"\b(judg\w*|rubric|criteria|evaluation|prizes|awards|how to win|scoring)\b"
        ],
        "tracks": [
            r"\b(track|tracks|problem statement|challenges|domain|themes|ai agents|fintech|healthtech)\b"
        ],
        "venue_wifi": [
            r"\b(wifi|wi-fi|internet|password|ssid|venue|hardware lab|room|restroom|location|where is)\b"
        ],
        "profile_update": [
            r"\b(my team is|we are team|sitting at table|our table is|team name:)\b"
        ]
    }

    def classify(self, text: str) -> Tuple[str, float]:
        """Returns the predicted intent and a confidence score between 0.0 and 1.0."""
        text_lower = text.strip().lower()

        if not text_lower:
            return "general_ai", 0.0

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Exact or strong match gets high confidence
                    return intent, 0.92

        # Soft keyword checks
        if any(word in text_lower for word in ["mentor", "stuck", "error", "bug"]):
            return "mentor_request", 0.75
        if any(word in text_lower for word in ["when", "time", "clock", "date"]):
            return "schedule", 0.70
        if any(word in text_lower for word in ["wifi", "network", "net"]):
            return "venue_wifi", 0.80
        if any(word in text_lower for word in ["rules", "allowed", "legal"]):
            return "rules", 0.78
        if any(word in text_lower for word in ["submit", "portal", "link"]):
            return "submission", 0.82

        return "general_ai", 0.50

# Global singleton
intent_classifier = IntentClassifier()
