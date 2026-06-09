import hashlib
from typing import Dict, Any, List

class PenaltyGameEngine:
    def __init__(self):
        # AI Goalkeeper difficulty modes
        self.difficulties = {
            "Easy": 0.2,
            "Medium": 0.5,
            "Hard": 0.75,
            "Legendary": 0.95
        }

    def play_shot(self, player_id: str, gesture: str, shot_target: str, previous_shots: List[str], difficulty_level: str, power: float, curve: float) -> dict:
        """
        Calculates the result of a penalty shot with V3 mechanics.
        """
        base_diff = self.difficulties.get(difficulty_level, 0.5)
        previous_targets = [shot for shot in previous_shots if shot in self._targets()]
        attempt_index = len(previous_targets) + 1
        
        # 1. Analyze player patterns. The keeper is deterministic/adaptive rather
        # than a plain random picker, but still has imperfect human-like reads.
        keeper_guess = self._ai_keeper_guess(previous_targets, difficulty_level, player_id, shot_target)
        
        # 2. Shot Execution Score based on Power and Curve
        # High power increases chance of goal, but reduces accuracy
        accuracy_penalty = max(0, (power - 0.78) * 0.38)
        
        # Curve can deceive the keeper
        deception_bonus = abs(curve) * 0.22
        target_bonus = {
            "Left Corner": 0.07,
            "Right Corner": 0.07,
            "Top Corner": -0.04,
            "Low Shot": 0.03,
            "Panenka": -0.08,
            "Power Shot": 0.02,
        }.get(shot_target, 0.0)
        
        execution_roll = self._stable_roll(player_id, gesture, shot_target, attempt_index, power, curve)
        shot_accuracy = execution_roll - accuracy_penalty + deception_bonus + target_bonus
        repeated_count = previous_targets.count(shot_target)
        adaptive_pressure = min(0.18, repeated_count * 0.06)
        effective_difficulty = min(0.98, base_diff + adaptive_pressure)
        reaction_delay = self._reaction_delay(effective_difficulty, repeated_count, keeper_guess == shot_target)
        
        # 3. Determine result
        if keeper_guess == shot_target:
            # Keeper dived the right way, harder to score
            if shot_accuracy > (effective_difficulty + 0.22) and power > 0.8:
                result = "Goal" # Overpowered the keeper
            else:
                result = "Saved"
        else:
            # Keeper went the wrong way
            if shot_accuracy > (effective_difficulty * 0.46):
                result = "Goal"
            else:
                result = "Missed" # Wide or over the bar
                
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
            "shot_accuracy": round(max(0.0, min(1.0, shot_accuracy)), 3)
        }

    def _ai_keeper_guess(self, previous_shots: List[str], difficulty: str, player_id: str, intended_target: str) -> str:
        targets = self._targets()
        if not previous_shots:
            index = int(self._stable_roll(player_id, difficulty, intended_target) * len(targets))
            return targets[min(index, len(targets) - 1)]
            
        counts = {}
        for shot in previous_shots:
            counts[shot] = counts.get(shot, 0) + 1
            
        most_frequent = max(counts, key=counts.get)
        last_shot = previous_shots[-1]
        predictability = {
            "Easy": 0.18,
            "Medium": 0.38,
            "Hard": 0.58,
            "Legendary": 0.82,
        }.get(difficulty, 0.38)
        repeat_bias = min(0.18, counts.get(intended_target, 0) * 0.06)
        read_score = self._stable_roll(player_id, difficulty, intended_target, len(previous_shots), most_frequent)
        
        if read_score < predictability + repeat_bias:
            return most_frequent
        if read_score < predictability + repeat_bias + 0.12:
            return last_shot

        index = int(read_score * len(targets))
        return targets[min(index, len(targets) - 1)]

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
