from abc import ABC, abstractmethod
import random
from typing import List, Dict, Any

class CommentaryProvider(ABC):
    @abstractmethod
    def generate_shot_commentary(self, event_context: dict, style: str, session_history: List[dict]) -> str:
        pass
        
    @abstractmethod
    def generate_match_story(self, final_score: str, session_history: List[dict], dna_profile: dict) -> str:
        pass

class MockProvider(CommentaryProvider):
    def generate_shot_commentary(self, event_context: dict, style: str, session_history: List[dict]) -> str:
        result = event_context.get("result", "Goal")
        power = event_context.get("power_registered", 0.5)
        shot_type = event_context.get("shot_type") or event_context.get("shot_target", "Strike")
        score_state = event_context.get("score_state", "")
        
        # Dynamic Memory Check
        miss_streak = 0
        for past_event in reversed(session_history):
            if past_event.get("result") == "Missed" or past_event.get("result") == "Saved":
                miss_streak += 1
            else:
                break
                
        if miss_streak > 1 and result == "Goal":
            memory_prefix = f"He finally makes up for those {miss_streak} disastrous previous attempts! "
        elif miss_streak > 1 and result != "Goal":
            memory_prefix = f"That's {miss_streak + 1} misses in a row... the pressure is getting to him. "
        else:
            memory_prefix = ""

        if style == "Professional":
            if result == "Goal":
                return memory_prefix + f"{shot_type} finished cleanly. The keeper read late and the scoreboard pressure shifts."
            return memory_prefix + f"{shot_type} denied. The keeper studies the pattern and reacts sharply."
            
        elif style == "Emotional Uncle":
            if result == "Goal":
                if power > 0.8:
                    return memory_prefix + "YES! PURE POWER! THAT'S MY BOY!"
                return memory_prefix + "YES! WHAT A BEAUTIFUL SHOT!"
            return memory_prefix + "What was that?! My grandmother could have kicked it better!"

        elif style in {"Conspiracy Analyst", "Conspiracy Theorist"}:
            if result == "Goal":
                return memory_prefix + f"Look at the spin on that {shot_type}. The data agencies do not want us asking why the keeper froze."
            return memory_prefix + f"Convenient save. Too convenient. The keeper has clearly been studying the user's gesture archive."

        elif style in {"Robot AI", "Robot Learning Football"}:
            if result == "Goal":
                return memory_prefix + f"Goal event confirmed. {shot_type} success probability updated. Celebration protocol: active."
            return memory_prefix + f"Attempt failed. {shot_type} vector intercepted. Recalibrating emotional disappointment module."
            
        if result == "Goal":
            return memory_prefix + f"What a {shot_type}! {score_state} The stadium has lift-off."
        return memory_prefix + f"{shot_type} fails this time. {score_state} Pressure rising."

    def generate_match_story(self, final_score: str, session_history: List[dict], dna_profile: dict) -> str:
        # Generate the End Match Story requested in V3
        primary_match = dna_profile.get("primary_match", "Unknown")
        goals = sum(1 for e in session_history if e.get("result") == "Goal")
        total = len(session_history)
        
        if goals == total:
            return f"A flawless performance! Channeling his inner {primary_match}, the player dominated the session, scoring {goals} out of {total} penalties with absolute precision."
        elif goals > total / 2:
            return f"After a few shaky moments, the {primary_match}-inspired performance led to a solid victory, securing {goals} out of {total} penalties."
        else:
            return f"A tough day at the office. Despite showing flashes of {primary_match}'s brilliance, the player struggled against the keeper, managing only {goals} out of {total} shots."

class OllamaProvider(CommentaryProvider):
    def __init__(self, model: str = "llama3"):
        self.model = model
        # Requires httpx or ollama python client

    def generate_shot_commentary(self, event_context: dict, style: str, session_history: List[dict]) -> str:
        # Stub for the actual HTTP call to Ollama localhost
        return f"[Ollama {style}] A generated contextual commentary based on {event_context['result']} and history of {len(session_history)} shots."
        
    def generate_match_story(self, final_score: str, session_history: List[dict], dna_profile: dict) -> str:
        return f"[Ollama] Epic match story summary generated here for a {final_score} finish."

# Factory
def get_commentary_provider(provider_type: str = "mock") -> CommentaryProvider:
    if provider_type.lower() == "ollama":
        return OllamaProvider()
    return MockProvider()
