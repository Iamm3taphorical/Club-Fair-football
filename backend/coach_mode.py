import random
from typing import Dict, Any, List

class TacticalGenerator:
    def __init__(self):
        self.formations = [
            "4-3-3", "4-2-3-1", "4-4-2", "3-5-2", "3-4-3", 
            "4-1-4-1", "4-3-2-1", "5-3-2", "5-4-1", "4-2-2-2",
            "4-4-1-1", "3-4-2-1", "3-4-1-2", "4-1-2-1-2", "4-5-1"
        ]
        self.strategies = ["High Press", "Defensive Block", "Counter Attack", "Possession", "Gegenpressing"]
        self.coaches = [
            "Pep Guardiola", "Jurgen Klopp", "Jose Mourinho", "Carlo Ancelotti", 
            "Mikel Arteta", "Diego Simeone", "Erik ten Hag", "Xabi Alonso", 
            "Roberto De Zerbi", "Zinedine Zidane"
        ]

    def generate_segment_scenario(self, segment: str, current_score: str) -> Dict[str, Any]:
        """
        Generates a dynamic scenario for the specific segment.
        Segments: '0-15', '16-30', '31-45', '46-60', '61-75', '76-90'
        """
        opponent_formation = random.choice(self.formations)
        
        # Determine opponent strategy based on segment and score
        h_score, a_score = map(int, current_score.split('-'))
        if segment in {"76-90", "61-75"} and a_score < h_score:
            opponent_strategy = "High Press" # Opponent trailing
        elif segment in {"76-90", "61-75"} and a_score > h_score:
            opponent_strategy = "Defensive Block" # Opponent leading
        else:
            opponent_strategy = random.choice(self.strategies)
            
        pressure = "High" if opponent_strategy in {"High Press", "Gegenpressing"} else "Medium"
        
        return {
            "segment": segment,
            "current_score": current_score,
            "opponent_formation": opponent_formation,
            "opponent_strategy": opponent_strategy,
            "pressure_level": pressure,
            "objective": "Win the segment"
        }

    def generate_scenario(self) -> Dict[str, Any]:
        """Backward-compatible single scenario used by older tests/tools."""
        scenario = self.generate_segment_scenario("0-15", "0-0")
        return {
            **scenario,
            "minute": 0,
            "opponent_shape": scenario["opponent_formation"],
        }

class MatchSimulationEngine:
    def __init__(self):
        pass

    def simulate_segment(self, scenario: Dict[str, Any], user_tactics: Dict[str, Any], coach_dna: Dict[str, int]) -> Dict[str, Any]:
        """
        Simulates 15 minutes of a match based on tactical decisions.
        """
        timeline = []
        segment = scenario.get("segment", "0-15")
        start_min, end_min = map(int, segment.split('-'))
        
        attack_power = user_tactics.get("attack", 50) + (coach_dna.get("vision", 70) * 0.2)
        defense_power = user_tactics.get("defense", 50) + (coach_dna.get("leadership", 70) * 0.2)
        possession_power = user_tactics.get("possession", 55) + (coach_dna.get("creativity", 70) * 0.12)
        pressure_power = user_tactics.get("pressure", 55)
        width_power = user_tactics.get("width", 55)
        
        # Stamina modifier (simulated based on segment)
        stamina_drain = (end_min / 90.0) * 15 
        attack_power -= stamina_drain
        defense_power -= stamina_drain
        
        # Tactical Rock-Paper-Scissors
        if scenario["opponent_strategy"] == "Defensive Block" and attack_power < 75:
            attack_power -= 10
        if scenario["opponent_strategy"] == "Counter Attack" and defense_power < 62:
            defense_power -= 10
        if scenario["opponent_strategy"] == "High Press" and possession_power < 65:
            possession_power -= 10
        if scenario["opponent_strategy"] == "Defensive Block" and width_power > 68:
            attack_power += 5
        if scenario["opponent_strategy"] == "Possession" and pressure_power > 68:
            defense_power += 5
            
        home_score = int(scenario["current_score"].split("-")[0])
        away_score = int(scenario["current_score"].split("-")[1])
        
        segment_goals_for = 0
        segment_goals_against = 0
        passes_completed = random.randint(38, 72) + int(max(0, possession_power) * 0.42)
        shots_attempted = random.randint(0, 2) + int(max(0, attack_power - 45) * 0.035)
        fouls = random.randint(1, 4)
        offsides = random.randint(0, 2)

        user_goal_prob = min(0.30, max(0.035, 0.10 + ((attack_power - 65) / 500.0) + ((possession_power - 60) / 900.0)))
        opponent_goal_prob = min(0.28, max(0.025, 0.09 + ((68 - defense_power) / 520.0)))

        if random.random() < user_goal_prob:
            minute = random.randint(start_min + 2, end_min)
            timeline.append(f"{minute}' GOAL! The {user_tactics.get('formation', 'custom')} shape opens the {scenario['opponent_strategy']}.")
            home_score += 1
            segment_goals_for = 1
            shots_attempted += 1
        if random.random() < opponent_goal_prob:
            minute = random.randint(start_min + 2, end_min)
            timeline.append(f"{minute}' Goal conceded. The opponent exploited a gap against the {user_tactics.get('formation', 'custom')} block.")
            away_score += 1
            segment_goals_against = 1

        if not timeline:
            minute = random.randint(start_min + 3, end_min)
            if possession_power > 70:
                timeline.append(f"{minute}' Strong possession spell controls the tempo at {scenario['current_score']}.")
            elif defense_power > 72:
                timeline.append(f"{minute}' Compact defending shuts down the {scenario['opponent_strategy']}.")
            else:
                timeline.append(f"{minute}' Midfield battle, neither side creating a clear chance.")

        # Segment Tactical Points
        segment_points = (segment_goals_for * 20) - (segment_goals_against * 15)
        if passes_completed > 100: segment_points += 5
        if segment_goals_for == 0 and segment_goals_against == 0 and defense_power > 70: segment_points += 10
        
        return {
            "new_score": f"{home_score}-{away_score}",
            "segment_goals_for": segment_goals_for,
            "segment_goals_against": segment_goals_against,
            "timeline": timeline,
            "stats": {
                "passes": passes_completed,
                "shots": shots_attempted,
                "fouls": fouls,
                "offsides": offsides
            },
            "segment_points": max(0, segment_points),
        }

    def simulate_match(self, scenario: Dict[str, Any], user_tactics: Dict[str, Any], coach_dna: Dict[str, int]) -> Dict[str, Any]:
        """Backward-compatible full-match wrapper for older callers."""
        score = scenario.get("current_score", "0-0")
        timeline: List[str] = []
        total_points = 0
        for segment in ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90"]:
            segment_scenario = {**scenario, "segment": segment, "current_score": score}
            result = self.simulate_segment(segment_scenario, user_tactics, coach_dna)
            score = result["new_score"]
            timeline.extend(result["timeline"])
            total_points += result["segment_points"]
        return {
            "final_score": score,
            "timeline": timeline,
            "total_points": total_points,
            "explanation": "Six balanced 15-minute segments simulated from tactics, score state, and coach DNA.",
        }
