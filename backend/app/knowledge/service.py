"""Condition knowledge and risk assessment — no external APIs."""

import json
import os
from pathlib import Path

_CONDITIONS: dict | None = None

HIGH_RISK_CLASSES = {"melanoma"}
MEDIUM_RISK_CLASSES = {"eczema", "fungal"}


def _load_conditions() -> dict:
    global _CONDITIONS
    if _CONDITIONS is None:
        path = Path(__file__).parent / "conditions.json"
        with open(path, encoding="utf-8") as f:
            _CONDITIONS = json.load(f)
    return _CONDITIONS


def normalize_class_name(class_name: str) -> str:
    """Map model output to knowledge-base key."""
    key = class_name.strip().lower().replace(" ", "_")
    aliases = {
        "benign_tumors": "benign",
        "benign_tumor": "benign",
        "fungal_infections": "fungal",
        "fungal_infection": "fungal",
    }
    return aliases.get(key, key)


def assess_risk(predicted_class: str, confidence: float) -> dict:
    """Compute urgency from prediction — conservative, not a diagnosis."""
    key = normalize_class_name(predicted_class)
    conditions = _load_conditions()
    info = conditions.get(key, {})

    base = info.get("base_urgency", "medium")
    level = base

    if confidence < 0.55:
        if level == "low":
            level = "medium"
        elif level == "medium":
            level = "high"

    if key in HIGH_RISK_CLASSES and confidence >= 0.35:
        level = "high"

    labels = {
        "low": "Routine awareness",
        "medium": "Schedule a check-up",
        "high": "Seek prompt medical evaluation",
    }

    return {
        "level": level,
        "label": labels.get(level, "Schedule a check-up"),
        "reason": _risk_reason(key, confidence, level),
    }


def _risk_reason(class_key: str, confidence: float, level: str) -> str:
    if class_key == "melanoma":
        return "Melanoma is a serious condition. AI screening is not a diagnosis — a dermatologist should evaluate any suspicious lesion."
    if confidence < 0.55:
        return f"The model is uncertain ({confidence * 100:.0f}% confidence). A professional examination is recommended."
    if level == "low":
        return "Based on the model output, routine self-monitoring and standard skin care may be sufficient, but this is not medical advice."
    return "Consider consulting a healthcare provider for an accurate assessment."


def get_insights(predicted_class: str, confidence: float, all_probabilities: dict) -> dict:
    """Build educational insights from the knowledge base."""
    key = normalize_class_name(predicted_class)
    conditions = _load_conditions()
    info = conditions.get(key)

    if not info:
        return {
            "condition_key": key,
            "display_name": predicted_class.replace("_", " ").title(),
            "description": "No detailed information available for this classification.",
            "symptoms": [],
            "care_tips": ["Consult a dermatologist for personalized advice."],
            "when_to_see_doctor": "When in doubt, always consult a qualified healthcare professional.",
            "risk": assess_risk(predicted_class, confidence),
            "disclaimer": _disclaimer(),
        }

    sorted_probs = sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
    alternatives = [
        {"class": k.replace("_", " ").title(), "probability": round(v, 4)}
        for k, v in sorted_probs[1:3]
        if v > 0.05
    ]

    return {
        "condition_key": key,
        "display_name": info["display_name"],
        "description": info["description"],
        "symptoms": info["symptoms"],
        "care_tips": info["care_tips"],
        "when_to_see_doctor": info["when_to_see_doctor"],
        "risk": assess_risk(predicted_class, confidence),
        "alternatives": alternatives,
        "disclaimer": _disclaimer(),
    }


def _disclaimer() -> str:
    return (
        "DermAI provides educational information only. It is not a medical device "
        "and cannot replace professional diagnosis or treatment."
    )
