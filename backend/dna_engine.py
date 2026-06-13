from typing import Dict, Any, Tuple

class FootballDNAEvolutionEngine:
    def __init__(self):
        self.profiles = {
            # ── Forwards ──────────────────────────────────────────────
            "Messi":        {"creativity": 95, "finishing": 92, "vision": 94, "speed": 85, "leadership": 75, "flair": 90},
            "Ronaldo":      {"creativity": 80, "finishing": 98, "vision": 82, "speed": 89, "leadership": 88, "flair": 85},
            "Mbappe":       {"creativity": 78, "finishing": 90, "vision": 76, "speed": 98, "leadership": 70, "flair": 84},
            "Haaland":      {"creativity": 62, "finishing": 96, "vision": 65, "speed": 88, "leadership": 72, "flair": 58},
            "Neymar":       {"creativity": 92, "finishing": 86, "vision": 88, "speed": 91, "leadership": 70, "flair": 98},
            "Lewandowski":  {"creativity": 72, "finishing": 96, "vision": 78, "speed": 76, "leadership": 84, "flair": 68},
            "Suarez":       {"creativity": 78, "finishing": 94, "vision": 80, "speed": 80, "leadership": 80, "flair": 76},
            "Benzema":      {"creativity": 84, "finishing": 92, "vision": 86, "speed": 78, "leadership": 82, "flair": 82},
            "Salah":        {"creativity": 82, "finishing": 90, "vision": 80, "speed": 92, "leadership": 76, "flair": 80},
            "Son":          {"creativity": 80, "finishing": 88, "vision": 78, "speed": 90, "leadership": 74, "flair": 78},
            "Griezmann":    {"creativity": 82, "finishing": 86, "vision": 84, "speed": 82, "leadership": 78, "flair": 80},
            "Vinicius":     {"creativity": 84, "finishing": 82, "vision": 76, "speed": 96, "leadership": 66, "flair": 94},
            "Lautaro":      {"creativity": 74, "finishing": 88, "vision": 74, "speed": 82, "leadership": 76, "flair": 72},
            "Rashford":     {"creativity": 76, "finishing": 82, "vision": 72, "speed": 92, "leadership": 68, "flair": 78},
            "Saka":         {"creativity": 82, "finishing": 80, "vision": 80, "speed": 86, "leadership": 72, "flair": 82},
            # ── Legends (Forwards) ────────────────────────────────────
            "Pele":         {"creativity": 94, "finishing": 96, "vision": 90, "speed": 88, "leadership": 92, "flair": 94},
            "Maradona":     {"creativity": 98, "finishing": 88, "vision": 92, "speed": 82, "leadership": 86, "flair": 98},
            "R9":           {"creativity": 86, "finishing": 98, "vision": 82, "speed": 96, "leadership": 74, "flair": 92},
            "Ronaldinho":   {"creativity": 96, "finishing": 82, "vision": 92, "speed": 84, "leadership": 70, "flair": 99},
            "Henry":        {"creativity": 86, "finishing": 94, "vision": 86, "speed": 92, "leadership": 82, "flair": 86},
            "Cruyff":       {"creativity": 96, "finishing": 84, "vision": 96, "speed": 82, "leadership": 90, "flair": 92},
            "Eusebio":      {"creativity": 82, "finishing": 94, "vision": 80, "speed": 90, "leadership": 80, "flair": 84},
            "Romario":      {"creativity": 82, "finishing": 96, "vision": 78, "speed": 86, "leadership": 68, "flair": 88},
            # ── Midfielders ───────────────────────────────────────────
            "De Bruyne":    {"creativity": 96, "finishing": 84, "vision": 98, "speed": 75, "leadership": 85, "flair": 80},
            "Modric":       {"creativity": 92, "finishing": 72, "vision": 94, "speed": 78, "leadership": 86, "flair": 88},
            "Kroos":        {"creativity": 88, "finishing": 76, "vision": 96, "speed": 68, "leadership": 84, "flair": 78},
            "Iniesta":      {"creativity": 94, "finishing": 74, "vision": 96, "speed": 76, "leadership": 82, "flair": 92},
            "Xavi":         {"creativity": 92, "finishing": 68, "vision": 98, "speed": 70, "leadership": 88, "flair": 84},
            "Zidane":       {"creativity": 96, "finishing": 86, "vision": 94, "speed": 80, "leadership": 90, "flair": 96},
            "Pirlo":        {"creativity": 92, "finishing": 78, "vision": 96, "speed": 62, "leadership": 82, "flair": 90},
            "Pogba":        {"creativity": 86, "finishing": 78, "vision": 82, "speed": 78, "leadership": 72, "flair": 88},
            "Bruno":        {"creativity": 88, "finishing": 84, "vision": 90, "speed": 76, "leadership": 80, "flair": 82},
            "Pedri":        {"creativity": 88, "finishing": 70, "vision": 90, "speed": 78, "leadership": 72, "flair": 86},
            "Bellingham":   {"creativity": 84, "finishing": 82, "vision": 84, "speed": 84, "leadership": 82, "flair": 80},
            "Beckham":      {"creativity": 86, "finishing": 80, "vision": 92, "speed": 76, "leadership": 86, "flair": 88},
            "Kaka":         {"creativity": 90, "finishing": 86, "vision": 88, "speed": 90, "leadership": 78, "flair": 90},
            # ── Defensive Midfielders ─────────────────────────────────
            "Kante":        {"creativity": 60, "finishing": 50, "vision": 75, "speed": 85, "leadership": 80, "flair": 50},
            "Busquets":     {"creativity": 78, "finishing": 50, "vision": 92, "speed": 58, "leadership": 86, "flair": 66},
            "Casemiro":     {"creativity": 62, "finishing": 62, "vision": 76, "speed": 72, "leadership": 88, "flair": 54},
            "Vieira":       {"creativity": 72, "finishing": 68, "vision": 78, "speed": 80, "leadership": 92, "flair": 64},
            "Makelele":     {"creativity": 58, "finishing": 42, "vision": 76, "speed": 74, "leadership": 84, "flair": 48},
            "Rice":         {"creativity": 72, "finishing": 66, "vision": 78, "speed": 76, "leadership": 80, "flair": 60},
            # ── Defenders ─────────────────────────────────────────────
            "Ramos":        {"creativity": 60, "finishing": 72, "vision": 68, "speed": 76, "leadership": 96, "flair": 66},
            "Van Dijk":     {"creativity": 56, "finishing": 60, "vision": 74, "speed": 78, "leadership": 92, "flair": 52},
            "Maldini":      {"creativity": 64, "finishing": 52, "vision": 80, "speed": 76, "leadership": 94, "flair": 72},
            "Beckenbauer":  {"creativity": 80, "finishing": 68, "vision": 86, "speed": 76, "leadership": 96, "flair": 78},
            "Thiago Silva": {"creativity": 62, "finishing": 54, "vision": 78, "speed": 72, "leadership": 90, "flair": 58},
            "Cannavaro":    {"creativity": 56, "finishing": 46, "vision": 74, "speed": 78, "leadership": 92, "flair": 54},
            "TAA":          {"creativity": 86, "finishing": 68, "vision": 88, "speed": 80, "leadership": 72, "flair": 78},
            "Marcelo":      {"creativity": 84, "finishing": 66, "vision": 82, "speed": 84, "leadership": 72, "flair": 90},
            "Cafu":         {"creativity": 76, "finishing": 64, "vision": 78, "speed": 88, "leadership": 84, "flair": 80},
            "Roberto Carlos":{"creativity": 78, "finishing": 76, "vision": 74, "speed": 90, "leadership": 78, "flair": 92},
            # ── Goalkeepers ───────────────────────────────────────────
            "Buffon":       {"creativity": 42, "finishing": 30, "vision": 78, "speed": 62, "leadership": 96, "flair": 56},
            "Neuer":        {"creativity": 58, "finishing": 34, "vision": 82, "speed": 72, "leadership": 90, "flair": 62},
            "Courtois":     {"creativity": 44, "finishing": 28, "vision": 76, "speed": 66, "leadership": 82, "flair": 48},
            "Alisson":      {"creativity": 52, "finishing": 30, "vision": 78, "speed": 68, "leadership": 84, "flair": 54},
            "Ter Stegen":   {"creativity": 60, "finishing": 32, "vision": 80, "speed": 64, "leadership": 80, "flair": 58},
        }
        self.identity_meta = {
            # ── Forwards ──────────────────────────────────────────────
            "Messi":       {"display_name": "Lionel Messi",       "style": "Playmaker",              "special_ability": "Curve Shot",        "suggested_role": "CAM"},
            "Ronaldo":     {"display_name": "Cristiano Ronaldo",  "style": "Explosive Finisher",     "special_ability": "Power Shot",        "suggested_role": "ST"},
            "Mbappe":      {"display_name": "Kylian Mbappé",      "style": "Lightning Striker",      "special_ability": "Speed Burst",       "suggested_role": "ST"},
            "Haaland":     {"display_name": "Erling Haaland",     "style": "Goal Machine",           "special_ability": "Clinical Finish",   "suggested_role": "ST"},
            "Neymar":      {"display_name": "Neymar Jr",          "style": "Flair Winger",           "special_ability": "Panenka Touch",     "suggested_role": "LW"},
            "Lewandowski": {"display_name": "Robert Lewandowski", "style": "Box Predator",           "special_ability": "Positioning",       "suggested_role": "ST"},
            "Suarez":      {"display_name": "Luis Suárez",        "style": "Street Fighter",         "special_ability": "Instinct Finish",   "suggested_role": "ST"},
            "Benzema":     {"display_name": "Karim Benzema",      "style": "Complete Forward",       "special_ability": "Link-Up Play",      "suggested_role": "CF"},
            "Salah":       {"display_name": "Mohamed Salah",      "style": "Inverted Winger",        "special_ability": "Cut-Inside Curl",   "suggested_role": "RW"},
            "Son":         {"display_name": "Son Heung-min",      "style": "Two-Footed Assassin",    "special_ability": "Both-Foot Finish",  "suggested_role": "LW"},
            "Griezmann":   {"display_name": "Antoine Griezmann",  "style": "Shadow Striker",         "special_ability": "Smart Run",         "suggested_role": "SS"},
            "Vinicius":    {"display_name": "Vinícius Jr",        "style": "Electric Dribbler",      "special_ability": "Stepovers",         "suggested_role": "LW"},
            "Lautaro":     {"display_name": "Lautaro Martínez",   "style": "Bull Striker",           "special_ability": "Pressing Trigger",  "suggested_role": "ST"},
            "Rashford":    {"display_name": "Marcus Rashford",    "style": "Pace Demon",             "special_ability": "Counter Attack",    "suggested_role": "LW"},
            "Saka":        {"display_name": "Bukayo Saka",        "style": "Starboy Winger",         "special_ability": "1v1 Dribble",       "suggested_role": "RW"},
            # ── Legends (Forwards) ────────────────────────────────────
            "Pele":        {"display_name": "Pelé",               "style": "The King",               "special_ability": "Total Football",    "suggested_role": "CF"},
            "Maradona":    {"display_name": "Diego Maradona",     "style": "El Diez",                "special_ability": "Solo Run",          "suggested_role": "CAM"},
            "R9":          {"display_name": "Ronaldo Nazário",    "style": "Il Fenomeno",            "special_ability": "Elastico Finish",   "suggested_role": "ST"},
            "Ronaldinho":  {"display_name": "Ronaldinho Gaúcho",  "style": "Joga Bonito",            "special_ability": "No-Look Pass",      "suggested_role": "CAM"},
            "Henry":       {"display_name": "Thierry Henry",      "style": "The Professor",          "special_ability": "Glide Finish",      "suggested_role": "ST"},
            "Cruyff":      {"display_name": "Johan Cruyff",       "style": "Total Footballer",       "special_ability": "Cruyff Turn",       "suggested_role": "CF"},
            "Eusebio":     {"display_name": "Eusébio",            "style": "Black Panther",          "special_ability": "Thunderbolt",       "suggested_role": "ST"},
            "Romario":     {"display_name": "Romário",            "style": "Baixinho",               "special_ability": "Fox in the Box",    "suggested_role": "ST"},
            # ── Midfielders ───────────────────────────────────────────
            "De Bruyne":   {"display_name": "Kevin De Bruyne",    "style": "Tactical Creator",       "special_ability": "Vision Pass",       "suggested_role": "CM"},
            "Modric":      {"display_name": "Luka Modrić",        "style": "Midfield Maestro",       "special_ability": "Body Feint",        "suggested_role": "CM"},
            "Kroos":       {"display_name": "Toni Kroos",         "style": "Metronome",              "special_ability": "Laser Pass",        "suggested_role": "CM"},
            "Iniesta":     {"display_name": "Andrés Iniesta",     "style": "The Illusionist",        "special_ability": "La Croqueta",       "suggested_role": "CM"},
            "Xavi":        {"display_name": "Xavi Hernández",     "style": "The Architect",          "special_ability": "Tiki-Taka",         "suggested_role": "CM"},
            "Zidane":      {"display_name": "Zinedine Zidane",    "style": "Le Maestro",             "special_ability": "Roulette",          "suggested_role": "CAM"},
            "Pirlo":       {"display_name": "Andrea Pirlo",       "style": "The Conductor",          "special_ability": "Free Kick Bend",    "suggested_role": "DM"},
            "Pogba":       {"display_name": "Paul Pogba",         "style": "Box-to-Box Flair",       "special_ability": "Long Range Drive",  "suggested_role": "CM"},
            "Bruno":       {"display_name": "Bruno Fernandes",    "style": "Chance Creator",         "special_ability": "Through Ball",      "suggested_role": "CAM"},
            "Pedri":       {"display_name": "Pedri González",     "style": "Pocket Passer",          "special_ability": "Press Escape",      "suggested_role": "CM"},
            "Bellingham":  {"display_name": "Jude Bellingham",    "style": "Box Crasher",            "special_ability": "Late Run",          "suggested_role": "CM"},
            "Beckham":     {"display_name": "David Beckham",      "style": "The Crosser",            "special_ability": "Precision Cross",   "suggested_role": "RM"},
            "Kaka":        {"display_name": "Kaká",               "style": "Galloping Genius",       "special_ability": "Acceleration Burst","suggested_role": "CAM"},
            # ── Defensive Midfielders ─────────────────────────────────
            "Kante":       {"display_name": "N'Golo Kanté",       "style": "Ball-Winning Engine",    "special_ability": "Pressure Trap",     "suggested_role": "CDM"},
            "Busquets":    {"display_name": "Sergio Busquets",    "style": "Invisible Wall",         "special_ability": "Interception Read",  "suggested_role": "CDM"},
            "Casemiro":    {"display_name": "Casemiro",           "style": "The Tank",               "special_ability": "Tactical Foul",     "suggested_role": "CDM"},
            "Vieira":      {"display_name": "Patrick Vieira",     "style": "The General",            "special_ability": "Midfield Dominance","suggested_role": "CDM"},
            "Makelele":    {"display_name": "Claude Makélélé",    "style": "The Shield",             "special_ability": "Position Lock",     "suggested_role": "CDM"},
            "Rice":        {"display_name": "Declan Rice",        "style": "Modern Anchor",          "special_ability": "Ball Recovery",     "suggested_role": "CDM"},
            # ── Defenders ─────────────────────────────────────────────
            "Ramos":       {"display_name": "Sergio Ramos",       "style": "Warrior Captain",        "special_ability": "Clutch Header",     "suggested_role": "CB"},
            "Van Dijk":    {"display_name": "Virgil van Dijk",    "style": "The Colossus",           "special_ability": "Aerial Command",    "suggested_role": "CB"},
            "Maldini":     {"display_name": "Paolo Maldini",      "style": "The Elegant Wall",       "special_ability": "Perfect Tackle",    "suggested_role": "CB"},
            "Beckenbauer": {"display_name": "Franz Beckenbauer",  "style": "Der Kaiser",             "special_ability": "Libero Surge",      "suggested_role": "CB"},
            "Thiago Silva":{"display_name": "Thiago Silva",       "style": "The Veteran Shield",     "special_ability": "Reading the Game",  "suggested_role": "CB"},
            "Cannavaro":   {"display_name": "Fabio Cannavaro",    "style": "The Gladiator",          "special_ability": "Last-Ditch Block",  "suggested_role": "CB"},
            "TAA":         {"display_name": "Trent Alexander-Arnold","style": "Playmaking Fullback", "special_ability": "Cross-Field Switch", "suggested_role": "RB"},
            "Marcelo":     {"display_name": "Marcelo Vieira",     "style": "Samba Fullback",         "special_ability": "Overlap Run",       "suggested_role": "LB"},
            "Cafu":        {"display_name": "Cafu",               "style": "Il Pendolino",           "special_ability": "Engine Run",        "suggested_role": "RB"},
            "Roberto Carlos":{"display_name": "Roberto Carlos",   "style": "Thunderbolt Left-Back", "special_ability": "Banana Free Kick",  "suggested_role": "LB"},
            # ── Goalkeepers ───────────────────────────────────────────
            "Buffon":      {"display_name": "Gianluigi Buffon",   "style": "The Legend Keeper",      "special_ability": "Reflex Save",       "suggested_role": "GK"},
            "Neuer":       {"display_name": "Manuel Neuer",       "style": "Sweeper Keeper",         "special_ability": "Rush Out",          "suggested_role": "GK"},
            "Courtois":    {"display_name": "Thibaut Courtois",   "style": "The Wall",               "special_ability": "Shot Stopping",     "suggested_role": "GK"},
            "Alisson":     {"display_name": "Alisson Becker",     "style": "The Complete Keeper",    "special_ability": "Distribution",      "suggested_role": "GK"},
            "Ter Stegen":  {"display_name": "Marc-André ter Stegen","style": "Ball-Playing Keeper",  "special_ability": "Sweeper Pass",      "suggested_role": "GK"},
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
        if shot_frequency.get("Power Shot", 0) >= 2 and previous_match in {"Messi", "Neymar", "Ronaldinho", "Iniesta"}:
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
            dist = sum((stats.get(k, 70) - p_stats[k]) ** 2 for k in p_stats.keys()) ** 0.5
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
