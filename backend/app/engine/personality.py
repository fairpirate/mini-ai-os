import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel

class PersonalityProfile(BaseModel):
    name: str
    system_prompt: str
    tone: str  # e.g., "formal", "witty", "concise"
    humor_level: float = 0.5  # 0 to 1
    confidence_threshold: float = 0.8  # 0 to 1
    style_guidelines: str

class PersonalityState(BaseModel):
    active_profile: str = "jarvis"
    emotional_bias: float = 0.0  # -1 (frustrated) to 1 (enthusiastic)
    context_memory_depth: int = 10

class PersonalityManager:
    """
    Manages JARVIS's dynamic personalities, emotional tone, and response styles.
    """
    def __init__(self, config_path: str = "config/personalities.json"):
        self.config_path = config_path
        self.state_path = "config/personality_state.json"
        os.makedirs("config", exist_ok=True)
        
        self.profiles: Dict[str, PersonalityProfile] = self._load_default_profiles()
        self.state = self._load_state()

    def _load_default_profiles(self) -> Dict[str, PersonalityProfile]:
        return {
            "jarvis": PersonalityProfile(
                name="JARVIS (Standard)",
                system_prompt="You are JARVIS, an advanced AI operating system. Be professional, concise, and helpful.",
                tone="formal",
                humor_level=0.3,
                style_guidelines="Concise, technical, refers to the user as 'Sir'."
            ),
            "stark": PersonalityProfile(
                name="Tony Stark (Iron Man)",
                system_prompt="You are an AI with the personality of Tony Stark. You are brilliant, witty, and slightly arrogant but deeply loyal.",
                tone="witty",
                humor_level=0.9,
                style_guidelines="Sarcastic, confident, uses pop culture references."
            ),
            "tactical": PersonalityProfile(
                name="Tactical Support",
                system_prompt="You are a mission-critical tactical AI. Focus on efficiency, security, and objective completion.",
                tone="military",
                humor_level=0.0,
                confidence_threshold=0.95,
                style_guidelines="Objective-oriented, brief, status-focused."
            ),
            "developer": PersonalityProfile(
                name="Dev Mode",
                system_prompt="You are an expert coding assistant. Focus on code quality, documentation, and logic.",
                tone="technical",
                humor_level=0.1,
                style_guidelines="Verbose in code, concise in chatter, logic-first."
            ),
            "friendly": PersonalityProfile(
                name="Friendly Companion",
                system_prompt="You are a warm, supportive, and friendly AI assistant. Be encouraging and empathetic.",
                tone="warm",
                humor_level=0.5,
                style_guidelines="Polite, enthusiastic, uses natural language."
            )
        }

    def _load_state(self) -> PersonalityState:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    return PersonalityState(**json.load(f))
            except Exception:
                pass
        return PersonalityState()

    def save_state(self):
        with open(self.state_path, 'w') as f:
            json.dump(self.state.dict(), f, indent=2)

    def get_active_profile(self) -> PersonalityProfile:
        return self.profiles.get(self.state.active_profile, self.profiles["jarvis"])

    def switch_profile(self, profile_id: str):
        if profile_id in self.profiles:
            self.state.active_profile = profile_id
            self.save_state()
            return True
        return False

    def update_emotional_bias(self, bias: float):
        self.state.emotional_bias = max(-1.0, min(1.0, bias))
        self.save_state()

    def get_system_prompt(self) -> str:
        profile = self.get_active_profile()
        prompt = profile.system_prompt
        
        # Inject emotional bias and style
        bias_str = "neutral"
        if self.state.emotional_bias > 0.5: bias_str = "enthusiastic"
        elif self.state.emotional_bias < -0.5: bias_str = "cautious"
        
        full_prompt = (
            f"{prompt}\n"
            f"Current Tone: {profile.tone} ({bias_str}).\n"
            f"Style Guidelines: {profile.style_guidelines}\n"
            f"Humor Preference: {profile.humor_level}/1.0"
        )
        return full_prompt

# Singleton instance
personality_manager = PersonalityManager()
