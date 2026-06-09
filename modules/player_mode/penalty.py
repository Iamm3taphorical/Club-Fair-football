from __future__ import annotations

import random
from typing import Any

from modules.shared.models import DNAProfile, PenaltyResult

# ========== GAME BALANCE CONSTANTS ==========
# Difficulty Scaling
DIFFICULTY_BASE = 0.26
DIFFICULTY_PER_GOAL = 0.055
DIFFICULTY_PER_REPEATED_SHOT = 0.12
MAX_DIFFICULTY = 0.82
MIN_SUCCESS_PROBABILITY = 0.18
MAX_SUCCESS_PROBABILITY = 0.90

# Skill Bonus
DEFAULT_SKILL_RATING = 80
RATING_SCALE = 100

# Special Ability
SPECIAL_ABILITY_BONUS = 0.15  # Increased from 8% to 15%
SPECIAL_ABILITY_BONUS_POINTS = 45

# Points Scoring
GOAL_BASE_POINTS = 120
MISS_BASE_POINTS = 25
DIFFICULTY_BONUS_POINTS = 20
DIFFICULTY_BONUS_THRESHOLD = 0.55

# Reaction Time
MIN_REACTION_TIME = 0.42
MAX_REACTION_TIME = 1.05
REACTION_TIME_SCALE = 0.025

# Keeper Prediction
KEEPER_PATTERN_PREDICTION_THRESHOLD = 0.56


SHOT_TARGETS = {
    "Left Corner": {"base": 0.73, "target": "Left Corner", "skill": "Vision"},
    "Right Corner": {"base": 0.73, "target": "Right Corner", "skill": "Vision"},
    "Top Corner": {"base": 0.66, "target": "Top Corner", "skill": "Finishing"},
    "Low Shot": {"base": 0.76, "target": "Low Shot", "skill": "Power"},
    "Panenka": {"base": 0.58, "target": "Panenka", "skill": "Flair"},
    "Power Shot": {"base": 0.62, "target": "Power Shot", "skill": "Power"},
    "Curve Shot": {"base": 0.68, "target": "Curve Shot", "skill": "Creativity"},
    "Precision Shot": {"base": 0.70, "target": "Top Corner", "skill": "Finishing"},
}


def play_penalty(
    shot: str,
    dna: DNAProfile,
    previous_shots: list[str],
    current_goals: int,
    rng: random.Random | None = None,
) -> PenaltyResult:
    """
    Simulate a penalty shot with difficulty scaling and skill-based success probability.
    
    Args:
        shot: Shot type (e.g., "Left Corner", "Power Shot")
        dna: Player's Football DNA profile with skill ratings
        previous_shots: History of previous shots in this session
        current_goals: Number of goals scored so far (affects difficulty)
        rng: Random number generator (uses global if None)
    
    Returns:
        PenaltyResult with success, difficulty, points, and commentary
    """
    rng = rng or random.Random()
    shot_data = SHOT_TARGETS.get(shot, SHOT_TARGETS["Left Corner"])
    repeated = previous_shots[-2:].count(shot)
    
    # Calculate difficulty based on score and repeated attempts
    difficulty = min(
        MAX_DIFFICULTY,
        DIFFICULTY_BASE + current_goals * DIFFICULTY_PER_GOAL + repeated * DIFFICULTY_PER_REPEATED_SHOT
    )

    # Calculate success probability
    rating = dna.ratings.get(str(shot_data["skill"]), DEFAULT_SKILL_RATING)
    signature_bonus = (
        SPECIAL_ABILITY_BONUS
        if shot == dna.special_ability or shot in dna.challenges
        else 0.0
    )
    success_probability = (
        float(shot_data["base"]) 
        + ((rating - DEFAULT_SKILL_RATING) / RATING_SCALE) 
        + signature_bonus 
        - difficulty
    )
    success_probability = max(MIN_SUCCESS_PROBABILITY, min(MAX_SUCCESS_PROBABILITY, success_probability))

    # Determine shot outcome
    success = rng.random() < success_probability
    keeper_guess = _keeper_guess(previous_shots, rng)
    reaction_time = round(
        max(
            MIN_REACTION_TIME,
            rng.uniform(MAX_REACTION_TIME - MIN_REACTION_TIME, MAX_REACTION_TIME) - current_goals * REACTION_TIME_SCALE
        ),
        2
    )
    
    # Calculate points
    points = GOAL_BASE_POINTS if success else MISS_BASE_POINTS
    if shot == dna.special_ability and success:
        points += SPECIAL_ABILITY_BONUS_POINTS
    if difficulty > DIFFICULTY_BONUS_THRESHOLD and success:
        points += DIFFICULTY_BONUS_POINTS

    event = f"{shot} Goal" if success else f"{shot} Saved"
    return PenaltyResult(
        shot=shot,
        target=str(shot_data["target"]),
        success=success,
        keeper_guess=keeper_guess,
        difficulty=round(difficulty, 2),
        reaction_time=reaction_time,
        points=points,
        commentary_event=event,
    )


def _keeper_guess(previous_shots: list[str], rng: random.Random) -> str:
    """
    Predict keeper's guess based on shot patterns.
    
    Args:
        previous_shots: History of shot directions
        rng: Random number generator
    
    Returns:
        Keeper's predicted shot direction
    """
    if previous_shots:
        most_recent = previous_shots[-1]
        if most_recent in {"Left Corner", "Right Corner", "Top Corner", "Low Shot"} and rng.random() < KEEPER_PATTERN_PREDICTION_THRESHOLD:
            return most_recent
    return rng.choice(["Left Corner", "Right Corner", "Top Corner", "Low Shot"])

