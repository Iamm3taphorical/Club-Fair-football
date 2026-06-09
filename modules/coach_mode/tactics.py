from __future__ import annotations

import random
from typing import Any

from modules.shared.models import CoachEvaluation, CoachScenario, TacticalPlan


# ========== COACH MODE GAME BALANCE ==========
# Formation Bonuses: (attack_bonus, defense_bonus, possession_bonus)
FORMATION_BONUSES: dict[str, tuple[int, int, int]] = {
    "4-3-3": (9, 6, 8),      # Balanced attacking formation
    "4-2-3-1": (7, 9, 9),    # Defensive but controlled possession
    "3-4-3": (13, -4, 7),    # High attacking risk
    "3-5-2": (10, 2, 8),     # Wing-based attacking
    "5-3-2": (-1, 14, 4),    # Ultra-defensive low block
    "4-1-4-1": (8, 8, 7),    # Midfield control
    "5-4-1": (-2, 12, 6),    # Counter-attacking setup
    "2-3-5": (14, -8, 6),    # Extreme attacking (risky)
}

# Scoring weights for overall coach evaluation
EVALUATION_WEIGHTS = {
    "attack": 0.28,
    "defense": 0.22,
    "possession": 0.18,
    "creativity": 0.22,
    "risk_balance": 0.10,
}

# Coach rank thresholds
COACH_RANK_THRESHOLDS = {
    90: "Football Genius",
    80: "Elite Manager",
    70: "Tactical Analyst",
    58: "Assistant Coach",
    0: "Sunday League Coach",
}

SCENARIOS = [
    CoachScenario(
        minute=83,
        current_score="1-2",
        opponent_shape="4-4-2 Low Block",
        opponent_style="Ultra Defensive",
        objective="Win the match before full time",
        pressure_level="Extreme",
    ),
    CoachScenario(
        minute=71,
        current_score="0-0",
        opponent_shape="5-3-2 Compact Mid Block",
        opponent_style="Time-wasting and countering",
        objective="Break the block without conceding transition chances",
        pressure_level="High",
    ),
    CoachScenario(
        minute=64,
        current_score="2-1",
        opponent_shape="4-2-3-1 High Press",
        opponent_style="Aggressive pressing",
        objective="Protect the lead while creating one more chance",
        pressure_level="Medium",
    ),
    CoachScenario(
        minute=45,
        current_score="1-1",
        opponent_shape="3-5-2 Attacking",
        opponent_style="Direct wing play",
        objective="Establish midfield control at halftime",
        pressure_level="High",
    ),
    CoachScenario(
        minute=90,
        current_score="2-2",
        opponent_shape="4-3-3 Balanced",
        opponent_style="Possession-based",
        objective="Score within 3 minutes or face extra time",
        pressure_level="Extreme",
    ),
    CoachScenario(
        minute=55,
        current_score="0-1",
        opponent_shape="5-4-1 Counter",
        opponent_style="Sitting deep and hitting on transition",
        objective="Penetrate the block without being caught on transition",
        pressure_level="Medium",
    ),
    CoachScenario(
        minute=72,
        current_score="3-1",
        opponent_shape="4-2-3-1 Pressing",
        opponent_style="Pressing after losing possession",
        objective="Control the game and avoid defensive vulnerabilities",
        pressure_level="Low",
    ),
    CoachScenario(
        minute=15,
        current_score="0-0",
        opponent_shape="4-1-4-1 Setup",
        opponent_style="Building possession from the back",
        objective="Set tactical tone without early mistakes",
        pressure_level="Low",
    ),
]


def generate_scenario(rng: random.Random | None = None) -> CoachScenario:
    """
    Generate a random tactical scenario.
    
    Args:
        rng: Random number generator (uses global if None)
    
    Returns:
        CoachScenario with match state and objective
    """
    rng = rng or random.Random()
    return rng.choice(SCENARIOS)


def evaluate_plan(scenario: CoachScenario, plan: TacticalPlan) -> CoachEvaluation:
    """
    Evaluate a tactical plan against a scenario.
    
    Args:
        scenario: Match scenario (score, time, opponent setup)
        plan: Tactical plan with formation, tempo, and other parameters
    
    Returns:
        CoachEvaluation with scores across 5 dimensions and overall rank
    """
    formation_bonus = FORMATION_BONUSES.get(plan.formation, (5, 5, 5))

    # Calculate dimension scores
    attack = 50 + formation_bonus[0] + plan.tempo * 0.22 + plan.fullbacks * 0.15
    defense = 55 + formation_bonus[1] - plan.defensive_line * 0.12 - plan.fullbacks * 0.10
    possession = 48 + formation_bonus[2] + (100 - abs(plan.tempo - 58)) * 0.18
    creativity = 46 + plan.fullbacks * 0.12 + plan.tempo * 0.16 + (12 if plan.extra_striker else 0)
    risk = 28 + plan.pressing * 0.24 + plan.defensive_line * 0.18 + plan.risk_tolerance * 0.32

    # Scenario-specific adjustments
    if "Low Block" in scenario.opponent_shape:
        attack += 8 if plan.extra_striker else 0
        creativity += 8
        defense -= 4
    if "High Press" in scenario.opponent_shape:
        possession -= 7 if plan.tempo > 72 else 0
        defense += 5 if plan.formation in {"4-2-3-1", "5-3-2"} else 0

    values = {
        "attack": _clamp(attack),
        "defense": _clamp(defense),
        "possession": _clamp(possession),
        "creativity": _clamp(creativity),
        "risk": _clamp(risk),
    }
    
    # Calculate overall coach score
    coach_score = _clamp(
        values["attack"] * EVALUATION_WEIGHTS["attack"]
        + values["defense"] * EVALUATION_WEIGHTS["defense"]
        + values["possession"] * EVALUATION_WEIGHTS["possession"]
        + values["creativity"] * EVALUATION_WEIGHTS["creativity"]
        + (100 - abs(values["risk"] - 64)) * EVALUATION_WEIGHTS["risk_balance"]
    )
    
    rank = rank_coach(coach_score)
    summary = _summary(values, coach_score)
    
    return CoachEvaluation(
        attack=values["attack"],
        defense=values["defense"],
        possession=values["possession"],
        creativity=values["creativity"],
        risk=values["risk"],
        coach_score=coach_score,
        rank=rank,
        summary=summary,
    )


def rank_coach(score: int) -> str:
    """
    Rank coach based on evaluation score.
    
    Args:
        score: Overall tactical evaluation score (0-100)
    
    Returns:
        Coach rank/title
    """
    for threshold, rank in sorted(COACH_RANK_THRESHOLDS.items(), reverse=True):
        if score >= threshold:
            return rank
    return "Sunday League Coach"


def _summary(values: dict[str, int], coach_score: int) -> str:
    """Generate descriptive summary of the tactical evaluation."""
    if coach_score >= 82:
        return "Your plan balances pressure, control, and chance creation like a professional match model."
    if values["risk"] > 82:
        return "The attacking idea is bold, but the defensive transition risk is serious."
    if values["attack"] < 62:
        return "The structure is stable, but it may not create enough late chances."
    return "The plan is workable, with one or two tradeoffs that shape the simulated result."


def _clamp(value: float) -> int:
    """Clamp value to valid range [0, 99]."""
    return max(0, min(99, round(value)))

