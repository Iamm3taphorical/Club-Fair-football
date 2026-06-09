import random
from typing import Dict, Any, List

class TacticalGenerator:
    def __init__(self):
        self.formations = ["4-3-3", "4-2-3-1", "4-4-2", "3-5-2", "3-4-3"]
        self.strategies = ["High Press", "Defensive Block", "Counter Attack", "Possession", "Gegenpressing"]
        self.scores = ["0-1", "1-1", "1-2", "2-2"]
        self.objectives = ["Equalize", "Protect the lead", "Find the winner", "Survive the press"]

    def generate_scenario(self) -> Dict[str, Any]:
        minute = random.randint(73, 86)
        score = random.choice(self.scores)
        opponent_formation = random.choice(self.formations)
        opponent_strategy = random.choice(self.strategies)
        objective = "Equalize" if score in {"0-1", "1-2"} else random.choice(self.objectives)
        
        return {
            "minute": minute,
            "current_score": score,
            "score": score,
            "opponent_formation": opponent_formation,
            "formation": opponent_formation,
            "opponent_strategy": opponent_strategy,
            "opponent": opponent_strategy,
            "objective": objective,
            "pressure_level": "High" if minute > 78 else "Medium"
        }

class MatchSimulationEngine:
    def __init__(self):
        pass

    def simulate_match(self, scenario: Dict[str, Any], user_tactics: Dict[str, Any], coach_dna: Dict[str, int]) -> Dict[str, Any]:
        """
        Simulates the remainder of a match based on tactical decisions.
        """
        timeline = []
        current_minute = scenario["minute"]
        
        # Calculate base probabilities
        attack_power = user_tactics.get("attack", 50) + (coach_dna.get("vision", 70) * 0.2)
        defense_power = user_tactics.get("defense", 50) + (coach_dna.get("leadership", 70) * 0.2)
        possession_power = user_tactics.get("possession", 55) + (coach_dna.get("creativity", 70) * 0.12)
        pressure = user_tactics.get("pressure", user_tactics.get("attack", 50))
        width = user_tactics.get("width", 58)
        
        # Modifier based on opponent strategy
        if scenario["opponent_strategy"] == "Defensive Block" and attack_power < 75:
            attack_power -= 10 # Hard to break down
        if scenario["opponent_strategy"] == "Counter Attack" and defense_power < 62:
            defense_power -= 8
        if user_tactics.get("formation") == "3-4-3":
            attack_power += 8
            defense_power -= 6
        elif user_tactics.get("formation") == "4-2-3-1":
            possession_power += 8
            defense_power += 3
            
        home_score = int(scenario["current_score"].split("-")[0])
        away_score = int(scenario["current_score"].split("-")[1])
        chance_creation = 0
        possession_changes = []
        
        while current_minute <= 90:
            current_minute += random.randint(2, 6)
            if current_minute > 90:
                break
                
            # Event generation
            event_roll = random.random()
            if event_roll < (attack_power / 200.0):
                chance_creation += 1
                timeline.append(f"{current_minute}' GOAL! Brilliant tactical setup leads to a score.")
                home_score += 1
            elif event_roll > (1.0 - (defense_power / 200.0)):
                possession_changes.append(f"{current_minute}' regained")
                timeline.append(f"{current_minute}' Strong defensive block prevents an opponent counter-attack.")
            elif event_roll < 0.2:
                chance_creation += 1
                timeline.append(f"{current_minute}' Opponent creates a chance, but it goes wide.")

        if not timeline:
            timeline.append(f"{min(90, scenario['minute'] + 4)}' Tactical reshuffle stabilizes possession and pins the opponent back.")
                
        final_score = f"{home_score}-{away_score}"
        tactical_rating = self._rating(attack_power, defense_power, possession_power, pressure, width, home_score, away_score, scenario)
        ranking = self._rank(tactical_rating)
        key_event = next((event for event in timeline if "GOAL" in event), timeline[-1])
        
        # AI Explanation
        explanation = self._generate_tactical_explanation(user_tactics, scenario, home_score, away_score)
        
        return {
            "final_score": final_score,
            "timeline": timeline,
            "explanation": explanation,
            "key_event": key_event,
            "tactical_rating": tactical_rating,
            "ranking": ranking,
            "coach_rank": ranking,
            "chance_creation": chance_creation,
            "possession_changes": possession_changes,
            "scores": {
                "attack": round(min(100, attack_power)),
                "defense": round(min(100, defense_power)),
                "possession": round(min(100, possession_power)),
                "creativity": round(min(100, (attack_power + possession_power) / 2)),
            }
        }

    def _generate_tactical_explanation(self, tactics: Dict[str, Any], scenario: Dict[str, Any], h_score: int, a_score: int) -> str:
        if tactics.get("formation") == "3-4-3" and scenario["opponent_strategy"] == "Counter Attack":
            return "Your high wingbacks left the defense exposed to counter-attacks, making it a highly volatile game."
        if tactics.get("possession") > 80:
            return "Your heavy possession strategy successfully starved the opponent of the ball, limiting their chances."
        if scenario["opponent_strategy"] == "Defensive Block" and tactics.get("width", 50) > 65:
            return "Your wide overloads stretched the defensive block and created better crossing lanes late in the match."
        return "Your tactical setup provided a balanced approach, though specific width adjustments could have optimized chance creation."

    def _rating(self, attack_power: float, defense_power: float, possession_power: float, pressure: int, width: int, h_score: int, a_score: int, scenario: Dict[str, Any]) -> int:
        game_state_bonus = 10 if h_score >= a_score and scenario.get("objective") == "Equalize" else 0
        balance_penalty = abs(attack_power - defense_power) * 0.08
        pressure_bonus = min(8, max(0, pressure - 60) * 0.15)
        width_bonus = 5 if scenario.get("opponent_strategy") == "Defensive Block" and width >= 65 else 0
        raw = ((attack_power * 0.34) + (defense_power * 0.28) + (possession_power * 0.28)) - balance_penalty + pressure_bonus + width_bonus + game_state_bonus
        return round(max(35, min(99, raw)))

    def _rank(self, rating: int) -> str:
        if rating >= 90:
            return "Football Genius"
        if rating >= 78:
            return "Elite Manager"
        if rating >= 62:
            return "Tactical Analyst"
        return "Sunday League Coach"
