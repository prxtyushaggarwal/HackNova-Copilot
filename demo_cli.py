"""
Interactive CLI Demo
Enables testing the Hackathon Chatbot directly in the terminal,
demonstrating intent classification, multi-turn state transitions, and mentor ticket generation.
"""

import sys
import os

# Enable UTF-8 console output for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.engine import bot_engine
from app.state.state_manager import state_manager
from app.config import settings

def run_cli_demo():
    session_id = "cli_demo_user"
    print("\n" + "="*65)
    print(f"🤖  Welcome to {settings.EVENT_NAME} AI Chatbot (CLI Interactive Mode)")
    print("="*65)
    print("💡 Try commands or queries like:")
    print("   • 'What is the schedule?'")
    print("   • 'Wi-Fi password'")
    print("   • 'I need a mentor for debugging our API'  (triggers state flow)")
    print("   • 'What are the rules and judging criteria?'")
    print("   • 'Type 'quit' or 'exit' to stop.")
    print("="*65 + "\n")

    while True:
        try:
            user_input = input("\n🧑‍💻 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Happy Hacking! Good luck with your project.\n")
                break

            response = bot_engine.process_query(session_id, user_input)

            # Display response
            print(f"\n⚡ NovaBot [Intent: {response.intent.upper()} | Conf: {int(response.confidence*100)}% | Latency: {response.execution_time_ms:.1f}ms]:")
            print("-" * 55)
            print(response.reply_text)
            print("-" * 55)

            if response.quick_replies:
                print("💡 Suggested Quick Replies: " + " | ".join([f"[{r}]" for r in response.quick_replies]))

            # Show session state updates if tickets were affected
            session = state_manager.get_session(session_id)
            if session and session.tickets:
                print(f"🎟️  Active Tickets for this Session: {len(session.tickets)} (Latest: {session.tickets[-1].ticket_id} at Table {session.tickets[-1].table_number})")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    run_cli_demo()
