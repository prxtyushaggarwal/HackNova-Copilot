"""
Knowledge Base & Semantic Query Matcher
Provides rapid, offline-capable query retrieval for hackathon-specific questions,
with scoring, synonym expansion, and structured data lookups.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from app.config import settings

class KnowledgeBase:
    """In-memory Knowledge Base with fuzzy matching and category indexing."""

    def __init__(self):
        self.articles = self._load_articles()

    def _load_articles(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "schedule_overview",
                "category": "schedule",
                "keywords": ["schedule", "agenda", "timeline", "events", "when", "time", "hours", "program"],
                "title": "Hackathon Schedule Overview",
                "answer": (
                    f"### 📅 **{settings.EVENT_NAME} Official Schedule**\n\n"
                    + "\n".join([f"- **{item['time']}**: {item['event']}" for item in settings.SCHEDULE])
                    + f"\n\n> ⏰ **Critical Notice:** Devpost submissions freeze strictly at **{settings.SUBMISSION_DEADLINE}**!"
                )
            },
            {
                "id": "submission_deadline",
                "category": "schedule",
                "keywords": ["deadline", "due date", "submission time", "code freeze", "submit project", "last time"],
                "title": "Project Submission Deadline",
                "answer": (
                    f"### ⏰ **Submission Deadline & Code Freeze**\n\n"
                    f"- **Hard Deadline:** `{settings.SUBMISSION_DEADLINE}`\n"
                    f"- **Submission Portal:** [{settings.SUBMISSION_PORTAL}]({settings.SUBMISSION_PORTAL})\n\n"
                    "**Deliverables Checklist:**\n"
                    "1. Public GitHub repository link with a comprehensive `README.md`.\n"
                    "2. 2-3 minute unlisted demo video (YouTube / Loom).\n"
                    "3. Working live demo URL or APK / executable (if applicable).\n"
                    "4. Track selection and team member taggings.\n\n"
                    "> 💡 *Tip: Do not wait until the last 15 minutes to submit!*"
                )
            },
            {
                "id": "wifi_venue",
                "category": "venue_wifi",
                "keywords": ["wifi", "wi-fi", "internet", "password", "network", "ssid", "connect"],
                "title": "Venue Wi-Fi Details",
                "answer": (
                    f"### 📶 **High-Speed Venue Wi-Fi**\n\n"
                    f"- **SSID:** `{settings.WIFI_SSID}`\n"
                    f"- **Password:** `{settings.WIFI_PASSWORD}`\n"
                    f"- **Bandwidth:** Dual-band 2.4GHz & 5GHz (prefer 5GHz for lower latency).\n\n"
                    "If you encounter connection drops, check with the Helpdesk at Hall A entrance."
                )
            },
            {
                "id": "venue_facilities",
                "category": "venue_wifi",
                "keywords": ["venue", "room", "hall", "restroom", "food", "cafeteria", "sleeping", "lab", "hardware"],
                "title": "Venue & Facilities",
                "answer": (
                    f"### 📍 **Venue & Facility Map**\n\n"
                    f"- **Location:** {settings.VENUE}\n"
                    "- **Main Hacking Arena:** Halls A & B (Tables 1 - 60)\n"
                    "- **Hardware & IoT Lab:** Hall B, Room 104 (Sensors, ESP32, RaspPi kits available upon student ID)\n"
                    "- **Rest & Quiet Zone:** 2nd Floor Lounge (Silent zone for power naps)\n"
                    "- **Cafeteria / Refreshments:** Ground Floor Annex (Water, coffee, energy drinks available 24/7)"
                )
            },
            {
                "id": "rules_and_eligibility",
                "category": "rules",
                "keywords": ["rules", "allowed", "pre-existing", "code", "library", "framework", "eligibility", "cheat"],
                "title": "Rules & Code Originality",
                "answer": (
                    f"### ⚖️ **{settings.EVENT_NAME} Hackathon Rules**\n\n"
                    "1. **Fresh Code Requirement:** All core application code must be written during the hackathon. Using pre-existing personal projects is prohibited.\n"
                    "2. **Open Source & APIs:** You are encouraged to use open-source libraries, public packages, and APIs (Gemini, Hugging Face, OpenAI, Firebase, etc.).\n"
                    "3. **Team Size:** Teams must consist of **2 to 4 members**.\n"
                    "4. **Originality & AI Ethics:** AI code-assist tools (GitHub Copilot, Antigravity, Cursor) are allowed, but your team must understand and explain every piece of code during judging.\n"
                    "5. **Code of Conduct:** Harassment or disruptive behavior will lead to immediate disqualification."
                )
            },
            {
                "id": "judging_criteria",
                "category": "rules",
                "keywords": ["judging", "rubric", "criteria", "evaluation", "score", "points", "win", "prizes"],
                "title": "Judging Criteria & Rubric",
                "answer": (
                    f"### 🏆 **Judging Rubric (Total: 100%)**\n\n"
                    + "\n".join([f"- **{c['criterion']}**: `{c['weight']}`" for c in settings.JUDGING_CRITERIA])
                    + "\n\n**Pitch Format:** 3 minutes live presentation + 2 minutes judge Q&A."
                )
            },
            {
                "id": "tracks_info",
                "category": "tracks",
                "keywords": ["tracks", "domains", "themes", "categories", "problem statements", "track"],
                "title": "Hackathon Tracks & Challenges",
                "answer": (
                    f"### 🚀 **{settings.EVENT_NAME} Tracks**\n\n"
                    + "\n".join([f"**{i+1}. {t['name']}**\n   - Lead Mentor: *{t['lead_mentor']}*\n   - ID: `{t['id']}`" for i, t in enumerate(settings.TRACKS)])
                    + "\n\n*Teams can compete in any one primary track.*"
                )
            },
            {
                "id": "mentor_support",
                "category": "mentor_request",
                "keywords": ["mentor", "help", "stuck", "assistance", "debug", "guidance", "advisor", "support"],
                "title": "Requesting Mentor Support",
                "answer": (
                    "### 🧑‍🏫 **On-Demand Mentorship Support**\n\n"
                    "Stuck on a bug, architecture bottleneck, or need pitch coaching? You can request a mentor straight through this chatbot!\n\n"
                    "Simply send: **`\"I need a mentor for [your issue] at Table [number]\"`**.\n"
                    "Or tap the **Request a Mentor** quick action button below."
                )
            },
            {
                "id": "food_meals",
                "category": "schedule",
                "keywords": ["food", "lunch", "dinner", "breakfast", "meal", "coffee", "snacks", "midnight"],
                "title": "Food & Refreshment Schedule",
                "answer": (
                    "### 🍕 **Food & Refreshment Timing**\n\n"
                    "- **Day 1 Lunch:** 01:30 PM – 02:45 PM (Cafeteria)\n"
                    "- **Day 1 Evening Snacks:** 05:30 PM (Hall Annex)\n"
                    "- **Day 1 Dinner:** 08:30 PM – 10:00 PM (Cafeteria)\n"
                    "- **Midnight Pizza & Red Bull:** 12:00 AM (Main Arena)\n"
                    "- **Day 2 Breakfast:** 08:00 AM – 09:15 AM (Cafeteria)\n"
                    "\n*Vegetarian, vegan, and non-veg options clearly marked.*"
                )
            }
        ]

    def search(self, query: str) -> Optional[Tuple[Dict[str, Any], float]]:
        """Finds the best matching article using token overlap and keyword weights."""
        q_clean = query.lower()
        words = set(q_clean.split())
        best_article = None
        best_score = 0.0

        for article in self.articles:
            score = 0.0
            # Direct keyword hits
            for kw in article["keywords"]:
                if kw in q_clean:
                    score += 2.5
                elif any(w == kw for w in words):
                    score += 1.5

            # Category hit
            if article["category"] in q_clean:
                score += 1.0

            # Title match
            for t_word in article["title"].lower().split():
                if t_word in words:
                    score += 0.8

            if score > best_score:
                best_score = score
                best_article = article

        # Normalize score between 0.0 and 1.0
        normalized_score = min(best_score / 4.0, 1.0)
        if best_article and normalized_score >= 0.35:
            return best_article, normalized_score

        return None

# Global singleton
knowledge_base = KnowledgeBase()
