from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from typing import Any

from modules.shared.models import DNAProfile


ARCHETYPES: dict[str, dict[str, Any]] = {
    "Messi": {
        "archetype": "Playmaker",
        "strength": "Vision",
        "weakness": "Physicality",
        "special_ability": "Curve Shot",
        "suggested_position": "CAM",
        "ratings": {"Creativity": 92, "Vision": 95, "Finishing": 81, "Leadership": 84, "Flair": 93},
        "challenges": ["Left Corner", "Right Corner", "Curve Shot"],
    },
    "Ronaldo": {
        "archetype": "Finisher",
        "strength": "Finishing",
        "weakness": "Low-Risk Build-Up",
        "special_ability": "Power Shot",
        "suggested_position": "ST",
        "ratings": {"Creativity": 80, "Vision": 84, "Finishing": 96, "Leadership": 91, "Power": 94},
        "challenges": ["Top Corner", "Power Shot", "Precision Shot"],
    },
    "Neymar": {
        "archetype": "Showman",
        "strength": "Risk and Dribbling",
        "weakness": "Defensive Discipline",
        "special_ability": "Panenka",
        "suggested_position": "LW",
        "ratings": {"Creativity": 93, "Vision": 88, "Finishing": 84, "Leadership": 79, "Flair": 96},
        "challenges": ["Panenka", "Trick Shot", "Flair Challenge"],
    },
    "Haaland": {
        "archetype": "Warrior",
        "strength": "Power",
        "weakness": "Creative Build-Up",
        "special_ability": "Rapid Finish",
        "suggested_position": "ST",
        "ratings": {"Creativity": 72, "Vision": 75, "Finishing": 95, "Leadership": 80, "Power": 97},
        "challenges": ["Rapid Fire", "Power Challenge", "Low Shot"],
    },
    "Mbappe": {
        "archetype": "Speedster",
        "strength": "Speed",
        "weakness": "Deep Defensive Shape",
        "special_ability": "Explosive Top Corner",
        "suggested_position": "RW",
        "ratings": {"Creativity": 85, "Vision": 84, "Finishing": 91, "Leadership": 83, "Speed": 98},
        "challenges": ["Top Corner", "Counter Attack", "Precision Shot"],
    },
    "Vinicius Jr": {
        "archetype": "Allrounder",
        "strength": "Dribbling",
        "weakness": "Consistency",
        "special_ability": "Left Corner",
        "suggested_position": "LW",
        "ratings": {"Creativity": 88, "Vision": 84, "Finishing": 86, "Leadership": 79, "Flair": 91},
        "challenges": ["Left Corner", "Curve Shot", "Dribble and Shoot"],
    },
    "Van Dijk": {
        "archetype": "Defender",
        "strength": "Physicality",
        "weakness": "Creative Attacks",
        "special_ability": "Low Shot",
        "suggested_position": "CB",
        "ratings": {"Creativity": 75, "Vision": 78, "Finishing": 72, "Leadership": 94, "Power": 94},
        "challenges": ["Low Shot", "Header", "Set Piece"],
    },
    "De Bruyne": {
        "archetype": "Tactician",
        "strength": "Passing Range",
        "weakness": "Recovery Speed",
        "special_ability": "Vision Pass",
        "suggested_position": "CM",
        "ratings": {"Creativity": 96, "Vision": 98, "Finishing": 84, "Leadership": 88, "Power": 82},
        "challenges": ["Curve Shot", "Precision Shot", "Perfect Assist"],
    },
    "Salah": {
        "archetype": "Finisher",
        "strength": "Positioning",
        "weakness": "Creative Risk",
        "special_ability": "Right Corner",
        "suggested_position": "RW",
        "ratings": {"Creativity": 84, "Vision": 82, "Finishing": 93, "Leadership": 86, "Speed": 91},
        "challenges": ["Right Corner", "Quick Turn and Shoot", "Penalty"],
    },
}

DNA_POOL: dict[str, dict[str, list[dict[str, str]]]] = {}
for _footballer, _data in ARCHETYPES.items():
    _archetype = str(_data["archetype"])
    DNA_POOL.setdefault(_archetype, {"players": []})["players"].append(
        {
            "footballer": _footballer,
            "special_ability": str(_data["special_ability"]),
            "suggested_position": str(_data["suggested_position"]),
        }
    )


ANSWER_WEIGHTS: dict[str, dict[str, dict[str, int]]] = {
    "style": {
        "Passing": {"Messi": 4, "De Bruyne": 4, "Neymar": 2, "Mbappe": 1, "Vinicius Jr": 2, "Salah": 1},
        "Shooting": {"Ronaldo": 4, "Haaland": 4, "Mbappe": 2, "Salah": 3, "Van Dijk": 1},
        "Balanced": {"Messi": 2, "Ronaldo": 2, "Mbappe": 2, "Vinicius Jr": 2, "Salah": 2, "De Bruyne": 2},
    },
    "risk": {
        "Safe control": {"Messi": 3, "Van Dijk": 3, "De Bruyne": 2, "Ronaldo": 1},
        "Calculated risks": {"Messi": 2, "Mbappe": 2, "Salah": 2, "Ronaldo": 1, "De Bruyne": 2},
        "High risk": {"Neymar": 4, "Mbappe": 2, "Vinicius Jr": 3, "Haaland": 1},
    },
    "role": {
        "Attack": {"Ronaldo": 3, "Haaland": 3, "Mbappe": 2, "Salah": 3},
        "Defense": {"Van Dijk": 4, "Haaland": 1, "Ronaldo": 1},
        "Both": {"Messi": 2, "Neymar": 2, "Mbappe": 2, "Vinicius Jr": 1, "De Bruyne": 2},
    },
    "teamwork": {
        "Teamwork": {"Messi": 3, "Mbappe": 1, "Van Dijk": 2, "De Bruyne": 3},
        "Individual brilliance": {"Neymar": 4, "Ronaldo": 3, "Mbappe": 2, "Vinicius Jr": 3},
        "Depends on the match": {"Messi": 2, "Ronaldo": 2, "Salah": 2, "Haaland": 1, "De Bruyne": 2},
    },
    "moment": {
        "Perfect assist": {"Messi": 4, "De Bruyne": 4, "Vinicius Jr": 2},
        "Last-minute winner": {"Ronaldo": 3, "Haaland": 3, "Mbappe": 2, "Salah": 2},
        "Skill move": {"Neymar": 4, "Vinicius Jr": 3},
        "Counter attack": {"Mbappe": 4, "Salah": 3, "Haaland": 2},
        "Dominant press": {"Haaland": 2, "Van Dijk": 3, "Ronaldo": 1, "De Bruyne": 1},
    },
}

# Optional variation factor for caller-supplied RNGs. The default path is
# deterministic because identity matching must be explainable and repeatable.
RANDOMNESS_FACTOR = 0.08


def generate_dna(answers: dict[str, str], expression_signal: str = "focused", rng: random.Random | None = None) -> DNAProfile:
    """
    Generate a DNA profile based on questionnaire answers.
    
    Args:
        answers: Mapping of question keys to answer strings
        expression_signal: Facial expression signal (focused, confident, creative, intense)
        rng: Random number generator for reproducible results (uses global if None)
    
    Returns:
        DNAProfile matching the player's style and characteristics
    """
    scores: defaultdict[str, float] = defaultdict(float)
    
    # Accumulate scores from questionnaire answers
    for question, answer in answers.items():
        for footballer, points in ANSWER_WEIGHTS.get(question, {}).get(answer, {}).items():
            scores[footballer] += float(points)

    # Apply expression bonus (personality signal)
    expression_bonus = {
        "focused": {"Messi": 1, "Ronaldo": 1, "Van Dijk": 1},
        "confident": {"Ronaldo": 2, "Mbappe": 1, "Salah": 1},
        "creative": {"Neymar": 2, "Messi": 1, "Vinicius Jr": 2},
        "intense": {"Haaland": 2, "Ronaldo": 1, "Van Dijk": 1},
    }
    for footballer, points in expression_bonus.get(expression_signal, {}).items():
        scores[footballer] += float(points)

    for footballer, points in _combination_bonuses(answers).items():
        scores[footballer] += float(points)

    # Add bounded variation only when a caller explicitly supplies an RNG.
    max_score = max(scores.values()) if scores else 10
    for footballer in ARCHETYPES:
        if rng is None:
            scores[footballer] += _stable_tiebreaker(answers, expression_signal, footballer)
        else:
            scores[footballer] += rng.uniform(-RANDOMNESS_FACTOR * max_score, RANDOMNESS_FACTOR * max_score)

    # Select footballer with highest score (secondary sort by name for determinism)
    selected = max(ARCHETYPES, key=lambda name: (scores[name], name))
    data = ARCHETYPES[selected]
    
    return DNAProfile(
        archetype=str(data["archetype"]),
        footballer=selected,
        strength=str(data["strength"]),
        weakness=str(data["weakness"]),
        special_ability=str(data["special_ability"]),
        suggested_position=str(data["suggested_position"]),
        ratings=dict(data["ratings"]),
        challenges=list(data["challenges"]),
    )


def _stable_tiebreaker(answers: dict[str, str], expression_signal: str, footballer: str) -> float:
    source = "|".join(
        [expression_signal, footballer]
        + [f"{key}:{answers[key]}" for key in sorted(answers)]
    )
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF / 100


def _combination_bonuses(answers: dict[str, str]) -> dict[str, int]:
    bonuses: defaultdict[str, int] = defaultdict(int)

    if answers.get("role") == "Defense":
        bonuses["Van Dijk"] += 5
    if answers.get("style") == "Passing" and answers.get("moment") == "Perfect assist":
        bonuses["De Bruyne"] += 4
    if answers.get("style") == "Shooting" and answers.get("moment") == "Last-minute winner":
        bonuses["Ronaldo"] += 4
        bonuses["Haaland"] += 2
    if answers.get("style") == "Shooting" and answers.get("risk") == "Calculated risks":
        bonuses["Salah"] += 3
    if answers.get("risk") == "High risk" and answers.get("teamwork") == "Individual brilliance":
        bonuses["Neymar"] += 4
    if answers.get("style") == "Passing" and answers.get("risk") == "High risk":
        bonuses["Vinicius Jr"] += 4
    if answers.get("role") == "Attack" and answers.get("moment") == "Counter attack":
        bonuses["Mbappe"] += 4

    return dict(bonuses)
