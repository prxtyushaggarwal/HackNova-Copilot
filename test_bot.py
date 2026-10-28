"""
Unit Test Suite for Hackathon Chatbot
Validates core logic, response parsing, entity extraction, and multi-turn state management.
"""

import pytest
from app.core.engine import bot_engine
from app.core.intent_classifier import intent_classifier
from app.parser.response_parser import response_parser
from app.state.state_manager import state_manager
from app.state.models import DialogueState, TicketStatus

def test_intent_classification():
    """Verifies intent routing for common hackathon queries."""
    intents = [
        ("When is the submission deadline?", "submission"),
        ("What is the Wi-Fi password?", "venue_wifi"),
        ("Can we use pre-existing code?", "rules"),
        ("How are projects judged?", "judging"),
        ("What time is lunch today?", "food"),
        ("I need a mentor to help us debug", "mentor_request"),
        ("Hello there!", "greeting"),
    ]
    for text, expected_intent in intents:
        intent, conf = intent_classifier.classify(text)
        assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
        assert conf > 0.6

def test_entity_extraction():
    """Verifies regex extraction of table numbers, team names, and tracks."""
    # Test table extraction
    e1 = response_parser.extract_entities("We are sitting at table 14, please send help")
    assert e1.get("table_number") == "14"

    e2 = response_parser.extract_entities("Desk T-25 has network issues")
    assert e2.get("table_number") == "25"

    # Test team name extraction
    e3 = response_parser.extract_entities("Team NovaHackers working on autonomous agents")
    assert e3.get("team_name") == "NovaHackers"
    assert e3.get("track") == "ai_agents"

    # Test github URL extraction
    e4 = response_parser.extract_entities("Here is our repo https://github.com/hacker/my-project")
    assert e4.get("github_url") == "https://github.com/hacker/my-project"

def test_multi_turn_state_management():
    """Verifies dialogue state machine transitions and slot filling."""
    session_id = "test_turn_user_99"

    # Turn 1: User asks for mentor without specifying table
    res1 = bot_engine.process_query(session_id, "I need a mentor")
    session = state_manager.get_session(session_id)
    assert session.dialogue_state == DialogueState.AWAITING_TABLE_FOR_MENTOR
    assert "Which table" in res1.reply_text

    # Turn 2: User provides table number
    res2 = bot_engine.process_query(session_id, "We are at Table 8")
    session = state_manager.get_session(session_id)
    assert session.dialogue_state == DialogueState.IDLE
    assert len(session.tickets) == 1
    assert session.tickets[0].table_number == "8"
    assert session.tickets[0].status == TicketStatus.PENDING
    assert res2.action is not None
    assert res2.action.action_type == "TICKET_CREATED"

def test_profile_persistence():
    """Verifies user profile updates survive across queries."""
    session_id = "test_profile_user_1"
    bot_engine.process_query(session_id, "Our team is ByteBuilders sitting at table 12")
    session = state_manager.get_session(session_id)
    assert session.user_profile.team_name == "ByteBuilders"
    assert session.user_profile.table_number == "12"

    # Next turn: mentor request immediately uses table 12 without re-asking
    res = bot_engine.process_query(session_id, "Need help with database connection")
    assert "Table 12" in res.reply_text
    assert session.dialogue_state == DialogueState.IDLE

def test_response_structure_and_schema():
    """Validates structured response payload format."""
    res = bot_engine.process_query("test_schema", "What is the Wi-Fi password?")
    assert res.intent == "venue_wifi"
    assert res.confidence >= 0.7
    assert len(res.quick_replies) > 0
    assert "SSID" in res.reply_text
    assert res.execution_time_ms >= 0.0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
