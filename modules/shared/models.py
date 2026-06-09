from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Student:
    student_id: str
    name: str


@dataclass(frozen=True)
class DNAProfile:
    archetype: str
    footballer: str
    strength: str
    weakness: str
    special_ability: str
    suggested_position: str
    ratings: dict[str, int]
    challenges: list[str]


@dataclass(frozen=True)
class PenaltyResult:
    shot: str
    target: str
    success: bool
    keeper_guess: str
    difficulty: float
    reaction_time: float
    points: int
    commentary_event: str


@dataclass(frozen=True)
class CoachScenario:
    minute: int
    current_score: str
    opponent_shape: str
    opponent_style: str
    objective: str
    pressure_level: str


@dataclass(frozen=True)
class TacticalPlan:
    formation: str
    pressing: int
    fullbacks: int
    extra_striker: bool
    tempo: int
    defensive_line: int
    risk_tolerance: int


@dataclass(frozen=True)
class CoachEvaluation:
    attack: int
    defense: int
    possession: int
    creativity: int
    risk: int
    coach_score: int
    rank: str
    summary: str


@dataclass(frozen=True)
class MatchEvent:
    minute: str
    title: str
    detail: str
    tone: str = "neutral"


@dataclass(frozen=True)
class MatchSimulation:
    final_score: str
    result_label: str
    events: list[MatchEvent]
    points: int


@dataclass(frozen=True)
class LeaderboardEntry:
    student_id: str
    name: str
    final_score: int
    best_mode: str
    dna: str
    coach_rank: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

