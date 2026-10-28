"""
AI Generation Service
Connects to Google Gemini API (or OpenAI) when keys are available,
and provides intelligent, context-aware local response synthesis when offline.
"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """Hybrid AI Engine: Cloud LLM (Gemini) + Smart Local Fallback."""

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self._init_gemini()

    def _init_gemini(self):
        if self.gemini_api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"[AIService] Notice: Gemini SDK initialization: {e}")

    def set_api_key(self, api_key: str):
        self.gemini_api_key = api_key.strip()
        self._init_gemini()

    def generate_response(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_data: Optional[str] = None
    ) -> str:
        """Generates conversational output using Gemini or the smart local generator."""
        # 1. If Gemini Client is active, use Gemini 2.5 Flash
        if self.client:
            try:
                system_instruction = (
                    "You are 'NovaBot', the official interactive AI assistant for HackNova 2026. "
                    "Help hackathon participants with rules, schedule, tech stack questions, debugging advice, "
                    "and mentor coordination. Keep your tone encouraging, snappy, precise, and well-formatted with markdown.\n"
                )
                if context_data:
                    system_instruction += f"\nRelevant Hackathon Facts:\n{context_data}\n"

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "system_instruction": system_instruction,
                        "temperature": 0.5,
                        "max_output_tokens": 800
                    }
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"[AIService] Cloud LLM error: {e}. Falling back to local synthesizer.")

        # 2. Smart Contextual Local Response Generator (Zero-dependency fallback)
        return self._synthesize_local_response(prompt, context_data)

    def _synthesize_local_response(self, prompt: str, context_data: Optional[str] = None) -> str:
        """Intelligent local synthesis for hackathon queries without needing an external API key."""
        prompt_lower = prompt.lower()

        # If we have structured context data from KnowledgeBase, format and explain it
        if context_data:
            return (
                f"{context_data}\n\n"
                "> 💡 *Have more questions? Ask about rules, schedule, Wi-Fi, or request a mentor at your table!*"
            )

        # Technical / coding query assistance
        if any(w in prompt_lower for w in ["python", "javascript", "react", "fastapi", "bug", "docker", "api"]):
            return (
                f"### 💻 **Technical Advisory**\n\n"
                f"I noticed you are asking about development tools or architecture regarding:\n"
                f"> *\"{prompt}\"*\n\n"
                f"**Quick Recommendations for Hackathon Velocity:**\n"
                f"1. **Fast Prototyping:** Use FastAPI / Streamlit for quick backends and rapid MVP demos.\n"
                f"2. **Mocking Services:** Don't let external rate limits block you — use mock responses for demo resilience.\n"
                f"3. **Need a Mentor?** If you are facing an elusive bug, type **`\"I need a mentor at Table [your table]\"`** and a domain expert will drop by!"
            )

        # General inquiry fallback
        return (
            f"Hello hacker! 🚀 I'm **NovaBot**, your real-time HackNova 2026 copilot.\n\n"
            f"Here is what I can help you automate instantly:\n"
            f"- 📅 **Schedule & Deadlines:** Check code freeze and meal times\n"
            f"- 🧑‍🏫 **On-Demand Mentorship:** Dispatch a mentor directly to your table\n"
            f"- ⚖️ **Rules & Guidelines:** Team limits, APIs, and judging rubrics\n"
            f"- 📶 **Venue Details:** Wi-Fi credentials, labs, and cafeteria info\n\n"
            f"*Try asking: 'When is code freeze?' or 'I need a mentor at Table 4'!*"
        )

# Global singleton
ai_service = AIService()
