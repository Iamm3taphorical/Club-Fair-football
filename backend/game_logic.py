import hashlib
import random
from typing import Dict, Any, List

class PenaltyGameEngine:
    def __init__(self):
        # AI Goalkeeper difficulty modes
        self.difficulties = {
            "Easy": 0.4,
            "Medium": 0.65,
            "Hard": 0.85,
            "Legendary": 0.95
        }

    def play_shot(self, player_id: str, gesture: str, shot_target: str, previous_shots: List[str], difficulty_level: str, power: float, curve: float) -> dict:
        """
        Calculates the result of a penalty shot with V3 mechanics.
        """
        base_diff = self.difficulties.get(difficulty_level, 0.5)
        previous_targets = [shot for shot in previous_shots if shot in self._targets()]
        attempt_index = len(previous_targets) + 1
        
        # 1. AI Keeper decides where to dive
        keeper_guess = self._ai_keeper_guess(previous_targets, difficulty_level, player_id, shot_target)
        
        # 2. Determine result based on keeper guess vs shot target
        repeated_count = previous_targets.count(shot_target)
        adaptive_pressure = min(0.18, repeated_count * 0.06)
        effective_difficulty = min(0.98, base_diff + adaptive_pressure)
        reaction_delay = self._reaction_delay(effective_difficulty, repeated_count, keeper_guess == shot_target)
        
        # Use real randomness for the execution quality
        execution_roll = random.random()
        
        if keeper_guess == shot_target:
            # Keeper dived the right way — very hard to score
            if power > 0.85 and execution_roll > 0.75:
                result = "Goal"  # Overpowered the keeper
            else:
                result = "Saved"
        else:
            # Keeper went the wrong way — should almost always be a goal
            if execution_roll < 0.12:
                result = "Missed"  # Skied it or hit the post
            else:
                result = "Goal"
                
        return {
            "result": result,
            "keeper_guess": keeper_guess,
            "shot_target": shot_target,
            "shot_type": self._shot_type_for_target(gesture, shot_target),
            "gesture": gesture,
            "power_registered": power,
            "curve_registered": curve,
            "difficulty_applied": base_diff,
            "adaptive_difficulty": round(effective_difficulty, 3),
            "reaction_delay": reaction_delay,
            "reaction_time": reaction_delay,
            "prediction_basis": self._prediction_basis(previous_targets, keeper_guess),
            "shot_accuracy": round(max(0.0, min(1.0, execution_roll)), 3)
        }

    def _ai_keeper_guess(self, previous_shots: List[str], difficulty: str, player_id: str, intended_target: str) -> str:
        targets = self._targets()
        if not previous_shots:
            return random.choices(
                ["Left Corner", "Right Corner", "Top Corner", "Low Shot"],
                weights=[0.4, 0.4, 0.15, 0.05],
                k=1
            )[0]
            
        counts = {}
        for shot in previous_shots:
            counts[shot] = counts.get(shot, 0) + 1
            
        most_frequent = max(counts, key=counts.get)
        last_shot = previous_shots[-1]
        predictability = {
            "Easy": 0.15,
            "Medium": 0.30,
            "Hard": 0.50,
            "Legendary": 0.70,
        }.get(difficulty, 0.30)
        repeat_bias = min(0.25, counts.get(intended_target, 0) * 0.08)
        
        # Use actual randomness for a realistic keeper
        read_roll = random.random()
        
        if read_roll < predictability + repeat_bias:
            return intended_target
        if read_roll < predictability + repeat_bias + 0.15:
            return most_frequent
        if read_roll < predictability + repeat_bias + 0.25:
            return last_shot

        # Random dive, heavily favoring corners since keepers rarely stay middle
        return random.choices(
            ["Left Corner", "Right Corner", "Top Corner", "Low Shot"],
            weights=[0.4, 0.4, 0.15, 0.05],
            k=1
        )[0]

    def _reaction_delay(self, difficulty: float, repeated_count: int, correct_read: bool) -> float:
        base_delay = 0.92 - (difficulty * 0.38) - (repeated_count * 0.035)
        if correct_read:
            base_delay -= 0.08
        return round(max(0.34, min(0.96, base_delay)), 2)

    def _prediction_basis(self, previous_shots: List[str], keeper_guess: str) -> str:
        if not previous_shots:
            return "opening stance read"
        if keeper_guess == max(set(previous_shots), key=previous_shots.count):
            return "shot history pattern"
        if keeper_guess == previous_shots[-1]:
            return "last-shot tendency"
        return "body-shape read"

    def _stable_roll(self, *parts: Any) -> float:
        source = "|".join(str(part) for part in parts)
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)

    def _targets(self) -> List[str]:
        return ["Left Corner", "Right Corner", "Top Corner", "Low Shot", "Panenka", "Power Shot"]

    def _shot_type_for_target(self, gesture: str, shot_target: str) -> str:
        if gesture == "Point Left":
            return "Left Shot"
        if gesture == "Point Right":
            return "Right Shot"
        if gesture == "Point Up":
            return "Top Corner"
        if gesture == "Point Down":
            return "Low Shot"
        if gesture == "Pinch":
            return "Panenka"
        if gesture in {"Power Shot", "Fist"}:
            return "Power Shot"
        return shot_target
