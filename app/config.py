"""
Hackathon Configuration & Knowledge Constants
Defines event details, rules, tracks, and runtime settings.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import List, Dict, Any

class HackathonSettings:
    EVENT_NAME: str = "HackNova 2026"
    EVENT_THEME: str = "Building with Agentic AI & Next-Gen Systems"
    START_TIME: str = "2026-10-28 09:00:00"
    SUBMISSION_DEADLINE: str = "2026-10-29 12:00:00"
    WIFI_SSID: str = "HackNova-Guest"
    WIFI_PASSWORD: str = "hackthefuture2026"
    VENUE: str = "Tech Innovation Center, Hall A & B"
    DISCORD_URL: str = "https://discord.gg/hacknova"
    SUBMISSION_PORTAL: str = "https://hacknova.devpost.com"

    TRACKS: List[Dict[str, Any]] = [
        {"id": "ai_agents", "name": "Autonomous AI Agents", "lead_mentor": "Dr. Sarah Lin"},
        {"id": "fintech", "name": "Decentralized & Intelligent FinTech", "lead_mentor": "Alex Rivera"},
        {"id": "health", "name": "HealthTech & Bio-Informatics", "lead_mentor": "Priya Sharma"},
        {"id": "open_source", "name": "Open Innovation & Developer Tools", "lead_mentor": "Marcus Chen"},
    ]

    JUDGING_CRITERIA: List[Dict[str, Any]] = [
        {"criterion": "Innovation & Originality", "weight": "25%"},
        {"criterion": "Technical Complexity & Execution", "weight": "30%"},
        {"criterion": "User Experience & Design", "weight": "20%"},
        {"criterion": "Practical Impact & Feasibility", "weight": "15%"},
        {"criterion": "Pitch & Presentation", "weight": "10%"},
    ]

    SCHEDULE: List[Dict[str, Any]] = [
        {"time": "Day 1 - 09:00 AM", "event": "Check-in & Breakfast"},
        {"time": "Day 1 - 10:30 AM", "event": "Opening Ceremony & Problem Release"},
        {"time": "Day 1 - 11:30 AM", "event": "Hacking Begins 🚀"},
        {"time": "Day 1 - 01:30 PM", "event": "Lunch & Sponsor Networking"},
        {"time": "Day 1 - 04:00 PM", "event": "Mentor Round 1 (Architecture Review)"},
        {"time": "Day 1 - 08:30 PM", "event": "Dinner & Mini Fun Event"},
        {"time": "Day 2 - 12:00 AM", "event": "Midnight Snacks & Coding Marathon"},
        {"time": "Day 2 - 08:00 AM", "event": "Breakfast & Submission Warmup"},
        {"time": "Day 2 - 11:00 AM", "event": "Mentor Round 2 (Demo Polishing)"},
        {"time": "Day 2 - 12:00 PM", "event": "Final Code Freeze & Devpost Submission Deadline ⏰"},
        {"time": "Day 2 - 01:30 PM", "event": "Judging Rounds & Live Demos"},
        {"time": "Day 2 - 04:30 PM", "event": "Closing Ceremony & Prize Distribution 🏆"},
    ]

settings = HackathonSettings()
