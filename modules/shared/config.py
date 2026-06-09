from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "database"
DEFAULT_DATABASE_PATH = DATABASE_DIR / "footballverse.sqlite3"
DATABASE_PATH = Path(os.getenv("FOOTBALLVERSE_DB_PATH", DEFAULT_DATABASE_PATH))

APP_TITLE = "FootballVerse AI"
APP_TAGLINE = "Discover. Play. Coach."

# ========== GAME TUNING PARAMETERS ==========
# Adjust these constants to balance game difficulty and progression

# Penalty Game Difficulty (see modules/player_mode/penalty.py for details)
PENALTY_DIFFICULTY_BASE = 0.26
PENALTY_DIFFICULTY_PER_GOAL = 0.055
PENALTY_DIFFICULTY_PER_REPEAT = 0.12
PENALTY_MAX_DIFFICULTY = 0.82

# Penalty Game Scoring
PENALTY_GOAL_POINTS = 120
PENALTY_MISS_POINTS = 25
PENALTY_DIFFICULTY_BONUS = 20
PENALTY_SPECIAL_ABILITY_BONUS = 45
PENALTY_SPECIAL_ABILITY_MULTIPLIER = 0.15  # 15% success rate increase

# Football DNA
DNA_RANDOMNESS_FACTOR = 0.15  # Adds variety to archetype selection

# Input Validation
MAX_STUDENT_ID_LENGTH = 20
MIN_STUDENT_ID_LENGTH = 3
MAX_NAME_LENGTH = 100

