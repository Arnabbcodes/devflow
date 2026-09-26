"""AI package for DevFlow using Groq API."""
from app.ai.groq_client import ask_groq
from app.ai.prompts import (
    ANALYSIS_SYSTEM,
    ANALYSIS_USER,
    FIX_SYSTEM,
    FIX_USER,
    TESTS_SYSTEM,
    TESTS_USER,
    REPORT_SYSTEM,
    REPORT_USER,
)

__all__ = [
    "ask_groq",
    "ANALYSIS_SYSTEM",
    "ANALYSIS_USER",
    "FIX_SYSTEM",
    "FIX_USER",
    "TESTS_SYSTEM",
    "TESTS_USER",
    "REPORT_SYSTEM",
    "REPORT_USER",
]
