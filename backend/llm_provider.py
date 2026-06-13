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
        keeper_guess = event_context.get("keeper_guess", "")
        
        # Dynamic Memory Check
        miss_streak = 0
        for past_event in reversed(session_history):
            if past_event.get("result") == "Missed" or past_event.get("result") == "Saved":
                miss_streak += 1
            else:
                break
                
        if miss_streak > 1 and result == "Goal":
            memory_prefix = random.choice([
                f"He finally makes up for those {miss_streak} disastrous previous attempts! ",
                f"After {miss_streak} frustrating misses, redemption at last! ",
                f"The monkey is off the back! {miss_streak} missed, but this one counts! ",
            ])
        elif miss_streak > 1 and result != "Goal":
            memory_prefix = random.choice([
                f"That's {miss_streak + 1} misses in a row... the pressure is getting to him. ",
                f"Oh no, {miss_streak + 1} consecutive failures! The crowd is restless. ",
                f"Another one goes begging. {miss_streak + 1} in a row now. Nerves of jelly. ",
            ])
        else:
            memory_prefix = ""

        shot_number = len(session_history) + 1
        shot_context = f"Penalty {shot_number}. " if shot_number <= 5 else ""

        if style == "Professional":
            if result == "Goal":
                line = random.choice([
                    f"{shot_type} finished cleanly. The keeper read late and the scoreboard pressure shifts.",
                    f"Clinical {shot_type}. Perfect placement, perfect execution. {score_state}",
                    f"What composure! The {shot_type} flies in. The keeper was left rooted.",
                    f"Textbook penalty. {shot_type} into the net, the keeper went {keeper_guess} but couldn't reach it.",
                    f"Cool as you like. {shot_type} dispatched with authority.",
                ])
            elif result == "Saved":
                line = random.choice([
                    f"{shot_type} denied. The keeper studies the pattern and reacts sharply.",
                    f"Saved! The goalkeeper guessed {keeper_guess} and got a strong hand to the {shot_type}.",
                    f"The keeper was equal to that {shot_type}. Read it perfectly.",
                    f"Denied! A fine save from the keeper who anticipated the {shot_type}.",
                ])
            else:
                line = random.choice([
                    f"{shot_type} goes wide. That will haunt him.",
                    f"Over the bar! The {shot_type} was struck with too much venom.",
                    f"Missed! The {shot_type} sails into the stands. The crowd gasps.",
                    f"Off target. {shot_type} fails to trouble the keeper this time.",
                ])
            return memory_prefix + shot_context + line
            
        elif style == "Emotional Uncle":
            if result == "Goal":
                if power > 0.8:
                    line = random.choice([
                        "YES! PURE POWER! THAT'S MY BOY!",
                        "WHAT A ROCKET! Did you see that power? INCREDIBLE!",
                        "BOOOOM! The net is still shaking! That's raw power!",
                    ])
                else:
                    line = random.choice([
                        "YES! WHAT A BEAUTIFUL SHOT!",
                        "GOOOAL! I told everyone he could do it! GENIUS!",
                        "Look at that! Smooth as butter! My heart is RACING!",
                        "I'm crying tears of joy right now! WHAT A PENALTY!",
                    ])
            elif result == "Saved":
                line = random.choice([
                    "What was that?! My grandmother could have kicked it better!",
                    "NO NO NO! Why did you go THERE?! The keeper was WAITING!",
                    "I can't watch! He's killing me! That was so predictable!",
                    "Oh come ON! Put some thought into it! The keeper read you like a book!",
                ])
            else:
                line = random.choice([
                    "WHERE IS THAT GOING?! To the moon?! Focus, son!",
                    "MISSED?! I can't believe my eyes! Even I could have scored that!",
                    "Oh no, oh no, oh no! That's gone into orbit!",
                ])
            return memory_prefix + line

        elif style in {"Conspiracy Analyst", "Conspiracy Theorist"}:
            if result == "Goal":
                line = random.choice([
                    f"Look at the spin on that {shot_type}. The data agencies do not want us asking why the keeper froze.",
                    f"Goal. But notice how the keeper moved {keeper_guess} a full 0.3 seconds early. Almost as if the script said so.",
                    f"Convenient that the {shot_type} went in. The algorithm clearly favors this outcome. Follow the data.",
                    f"They scored. The keeper's diving angle? Exactly 17 degrees off. Coincidence? I think not.",
                ])
            elif result == "Saved":
                line = random.choice([
                    f"Convenient save. Too convenient. The keeper has clearly been studying the user's gesture archive.",
                    f"Saved? Or was it... predetermined? The keeper knew. They always know. Check the data feeds.",
                    f"Another save. The algorithms are laughing at us. This keeper has insider information.",
                ])
            else:
                line = random.choice([
                    f"Missed? Or was the trajectory altered mid-flight? Big Football doesn't want you to know.",
                    f"The ball curved away. Wind? Or electromagnetic interference? You decide.",
                ])
            return memory_prefix + line

        elif style in {"Robot AI", "Robot Learning Football"}:
            if result == "Goal":
                line = random.choice([
                    f"Goal event confirmed. {shot_type} success probability updated. Celebration protocol: active.",
                    f"GOAL.exe executed successfully. {shot_type} vector: optimal. Dopamine simulation: running.",
                    f"Target acquired. {shot_type} delivered to net coordinates. Human joy emotion: processing.",
                    f"Objective complete. The {shot_type} has registered on my happiness module. Beep boop. Goal.",
                ])
            elif result == "Saved":
                line = random.choice([
                    f"Attempt failed. {shot_type} vector intercepted. Recalibrating emotional disappointment module.",
                    f"SAVE detected. Goalkeeper prediction accuracy: concerning. Updating threat assessment.",
                    f"Error: ball.position != net.interior. {shot_type} blocked. Sadness subroutine activated.",
                ])
            else:
                line = random.choice([
                    f"MISS. {shot_type} trajectory deviated from optimal path by significant margin. Confusion: high.",
                    f"Target missed. Ball exited valid scoring zone. Embarrassment module: initializing.",
                ])
            return memory_prefix + line
            
        # Default / fallback style
        if result == "Goal":
            line = random.choice([
                f"What a {shot_type}! {score_state} The stadium has lift-off.",
                f"GOAL! The {shot_type} beats the keeper! {score_state} Magnificent!",
                f"It's in! Beautiful {shot_type}! The crowd goes absolutely wild!",
                f"The net bulges! {shot_type} past the despairing dive of the goalkeeper!",
            ])
        elif result == "Saved":
            line = random.choice([
                f"{shot_type} fails this time. {score_state} Pressure rising.",
                f"Denied! The keeper pulls off a brilliant save from the {shot_type}.",
                f"No goal! The {shot_type} is palmed away. What a save!",
            ])
        else:
            line = random.choice([
                f"{shot_type} goes begging! Off target and into the crowd.",
                f"Missed! The {shot_type} flies wide. A terrible miss!",
            ])
        return memory_prefix + line

    def generate_match_story(self, final_score: str, session_history: List[dict], dna_profile: dict) -> str:
        # Generate the End Match Story requested in V3
        primary_match = dna_profile.get("primary_match", "Unknown")
        display_name = dna_profile.get("display_name") or dna_profile.get("name_match") or primary_match
        style = dna_profile.get("style", "")
        goals = sum(1 for e in session_history if e.get("result") == "Goal")
        total = len(session_history)
        
        if goals == total:
            return random.choice([
                f"A flawless performance! Channeling his inner {display_name}, the player dominated the session, scoring {goals} out of {total} penalties with absolute precision.",
                f"Perfection. Every single penalty found the back of the net. The {style} energy of {display_name} was on full display today. {goals}/{total} — immaculate.",
                f"Five from five! A masterclass in penalty taking. {display_name} would be proud of this clinical display.",
            ])
        elif goals > total / 2:
            return random.choice([
                f"After a few shaky moments, the {display_name}-inspired performance led to a solid victory, securing {goals} out of {total} penalties.",
                f"A gritty display worthy of {display_name}'s {style} identity. {goals} goals from {total} attempts — not perfect, but effective.",
                f"The player showed real character to finish with {goals}/{total}. The {display_name} DNA shone through when it mattered most.",
            ])
        else:
            return random.choice([
                f"A tough day at the office. Despite showing flashes of {display_name}'s brilliance, the player struggled against the keeper, managing only {goals} out of {total} shots.",
                f"The keeper won this battle. Only {goals} from {total} penalties converted. But even {display_name} has bad days — the DNA will evolve.",
                f"A humbling session. {goals}/{total} — the keeper had the upper hand today. Time to regroup and channel that {style} energy differently.",
            ])

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
