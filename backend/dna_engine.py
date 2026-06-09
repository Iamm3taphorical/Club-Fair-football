from typing import Dict, Any, Tuple

class FootballDNAEvolutionEngine:
    def __init__(self):
        self.profiles = {
            "Messi": {"creativity": 95, "finishing": 92, "vision": 94, "speed": 85, "leadership": 75, "flair": 90},
            "Ronaldo": {"creativity": 80, "finishing": 98, "vision": 82, "speed": 89, "leadership": 88, "flair": 85},
            "De Bruyne": {"creativity": 96, "finishing": 84, "vision": 98, "speed": 75, "leadership": 85, "flair": 80},
            "Neymar": {"creativity": 92, "finishing": 86, "vision": 88, "speed": 91, "leadership": 70, "flair": 98},
            "Kante": {"creativity": 60, "finishing": 50, "vision": 75, "speed": 85, "leadership": 80, "flair": 50}
        }
        self.identity_meta = {
            "Messi": {
                "display_name": "Lionel Messi",
                "style": "Playmaker",
                "special_ability": "Curve Shot",
                "suggested_role": "CAM",
            },
            "Ronaldo": {
                "display_name": "Cristiano Ronaldo",
                "style": "Explosive Finisher",
                "special_ability": "Power Shot",
                "suggested_role": "ST",
            },
            "De Bruyne": {
                "display_name": "Kevin De Bruyne",
                "style": "Tactical Creator",
                "special_ability": "Vision Pass",
                "suggested_role": "CM",
            },
            "Neymar": {
                "display_name": "Neymar Jr",
                "style": "Flair Winger",
                "special_ability": "Panenka Touch",
                "suggested_role": "LW",
            },
            "Kante": {
                "display_name": "N'Golo Kante",
                "style": "Ball-Winning Engine",
                "special_ability": "Pressure Trap",
                "suggested_role": "CDM",
            },
        }

    def generate_initial_score(self, quiz_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate base DNA scores from an initial interaction/quiz.
        """
        # Baseline average player
        base_stats = {"creativity": 70, "finishing": 70, "vision": 70, "speed": 70, "leadership": 70, "flair": 70}
        
        # Modify based on answers (mock logic for now)
        if quiz_answers.get("playstyle") == "Attacking":
            base_stats["finishing"] += 10
            base_stats["flair"] += 5
        elif quiz_answers.get("playstyle") == "Playmaker":
            base_stats["creativity"] += 15
            base_stats["vision"] += 15
        elif quiz_answers.get("playstyle") == "Power":
            base_stats["finishing"] += 14
            base_stats["leadership"] += 8
        elif quiz_answers.get("playstyle") == "Tactical":
            base_stats["vision"] += 12
            base_stats["leadership"] += 10
        elif quiz_answers.get("playstyle") == "Flair":
            base_stats["flair"] += 16
            base_stats["speed"] += 8
            
        match, percentages = self._find_closest_match(base_stats)
        profile = self._compose_profile(base_stats, match, percentages)
        
        return profile

    def evolve_dna(self, current_stats: Dict[str, int], match_events: list) -> Dict[str, Any]:
        """
        Evolve DNA based on recent gameplay/coaching decisions.
        """
        new_stats = current_stats.copy()
        
        for event in match_events:
            if event["type"] == "POWER_SHOT_GOAL":
                new_stats["finishing"] = min(99, new_stats["finishing"] + 2)
            elif event["type"] == "PANENKA_GOAL":
                new_stats["flair"] = min(99, new_stats["flair"] + 3)
                new_stats["creativity"] = min(99, new_stats["creativity"] + 1)
            elif event["type"] == "COACH_POSSESSION_WIN":
                new_stats["vision"] = min(99, new_stats["vision"] + 2)
                new_stats["leadership"] = min(99, new_stats["leadership"] + 1)
            elif event["type"] == "CURVE_SHOT_GOAL":
                new_stats["creativity"] = min(99, new_stats["creativity"] + 2)
                new_stats["vision"] = min(99, new_stats["vision"] + 1)
            elif event["type"] == "LOW_SHOT_GOAL":
                new_stats["finishing"] = min(99, new_stats["finishing"] + 1)
                new_stats["speed"] = min(99, new_stats["speed"] + 1)
            elif event["type"] == "SAVED_POWER_SHOT":
                new_stats["finishing"] = max(1, new_stats["finishing"] - 1)
                
        match, percentages = self._find_closest_match(new_stats)
        profile = self._compose_profile(new_stats, match, percentages)
        
        return profile

    def build_evolution_label(self, previous_match: str, evolved_match: str, shot_frequency: Dict[str, int]) -> str:
        """
        Convert raw evolution data into a shareable football identity label.
        """
        if shot_frequency.get("Power Shot", 0) >= 2 and previous_match in {"Messi", "Neymar"}:
            return f"Hybrid {previous_match}-Ronaldo"
        if shot_frequency.get("Panenka", 0) >= 2:
            return f"{evolved_match} with Neymar Influence"
        if shot_frequency.get("Top Corner", 0) + shot_frequency.get("Left Shot", 0) >= 3:
            return f"{evolved_match} with De Bruyne Influence"
        if previous_match != evolved_match:
            return f"{previous_match} to {evolved_match}"
        return f"{evolved_match} Archetype"

    def profile_for_match(
        self,
        stats: Dict[str, int],
        match: str,
        confidence_score: int,
        percentages: Dict[str, int] | None = None,
    ) -> Dict[str, Any]:
        """
        Compose a DNA profile when an external identity matcher has a confirmed result.
        """
        next_percentages = percentages.copy() if percentages else {}
        next_percentages[match] = max(confidence_score, next_percentages.get(match, 0))
        return self._compose_profile(stats, match, next_percentages)

    def _find_closest_match(self, stats: Dict[str, int]) -> Tuple[str, Dict[str, int]]:
        """
        Calculates similarity percentage to known legends.
        """
        distances = {}
        for player, p_stats in self.profiles.items():
            # Calculate Euclidean distance
            dist = sum((stats[k] - p_stats[k]) ** 2 for k in stats.keys()) ** 0.5
            distances[player] = dist
            
        # Convert distances to similarity percentages
        max_dist = 150 # approximate max possible distance
        similarities = {}
        for player, dist in distances.items():
            sim = max(0, 100 - (dist / max_dist * 100))
            similarities[player] = round(sim)
            
        # Sort by highest similarity
        sorted_sims = dict(sorted(similarities.items(), key=lambda item: item[1], reverse=True))
        primary_match = list(sorted_sims.keys())[0]
        
        return primary_match, sorted_sims

    def _compose_profile(self, stats: Dict[str, int], match: str, percentages: Dict[str, int]) -> Dict[str, Any]:
        meta = self.identity_meta.get(match, self.identity_meta["Messi"])
        sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
        confidence_score = max(percentages.values()) if percentages else 0

        return {
            "stats": stats,
            "traits": {
                "Vision": stats.get("vision", 70),
                "Creativity": stats.get("creativity", 70),
                "Power": round((stats.get("finishing", 70) + stats.get("leadership", 70)) / 2),
                "Speed": stats.get("speed", 70),
            },
            "primary_match": match,
            "name_match": meta["display_name"],
            "display_name": meta["display_name"],
            "style": meta["style"],
            "archetype": meta["style"],
            "special_ability": meta["special_ability"],
            "suggested_role": meta["suggested_role"],
            "strength": sorted_stats[0][0].replace("_", " ").title(),
            "weakness": sorted_stats[-1][0].replace("_", " ").title(),
            "confidence_score": confidence_score,
            "confidence_threshold": 60,
            "confidence_status": "confirmed" if confidence_score >= 60 else "provisional",
            "percentages": percentages,
            "dataset_source": "Kaggle football players and staff faces dataset adapter",
            "identity_basis": "face embedding adapter plus personality signal",
        }
