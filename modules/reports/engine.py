from __future__ import annotations

import os

from modules.shared.config import BASE_DIR

MPLCONFIGDIR = BASE_DIR / ".cache" / "matplotlib"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib.pyplot as plt
import numpy as np

from modules.shared.models import CoachEvaluation, DNAProfile, PenaltyResult


def player_score(results: list[PenaltyResult]) -> int:
    return sum(result.points for result in results)


def accuracy(results: list[PenaltyResult]) -> int:
    if not results:
        return 0
    return round(100 * sum(1 for result in results if result.success) / len(results))


def average_reaction(results: list[PenaltyResult]) -> float:
    if not results:
        return 0.0
    return round(sum(result.reaction_time for result in results) / len(results), 2)


def best_skill(results: list[PenaltyResult], fallback: str) -> str:
    scored = [result.shot for result in results if result.success]
    if not scored:
        return fallback
    return max(set(scored), key=scored.count)


def radar_chart(profile: DNAProfile, results: list[PenaltyResult] | None = None, coach: CoachEvaluation | None = None):
    labels = ["Accuracy", "Creativity", "Reaction", "Vision", "Power"]
    if coach:
        values = [coach.attack, coach.creativity, coach.defense, coach.possession, 100 - abs(coach.risk - 64)]
    else:
        results = results or []
        values = [
            accuracy(results),
            profile.ratings.get("Creativity", 80),
            max(45, 100 - round(average_reaction(results) * 52)) if results else 72,
            profile.ratings.get("Vision", 80),
            profile.ratings.get("Power", profile.ratings.get("Finishing", 80)),
        ]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    chart_values = values + values[:1]
    chart_angles = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(5.8, 5.8), subplot_kw={"polar": True})
    fig.patch.set_facecolor("#05080f")
    ax.set_facecolor("#09121f")
    ax.plot(chart_angles, chart_values, color="#39d7ff", linewidth=2.5)
    ax.fill(chart_angles, chart_values, color="#2374ff", alpha=0.24)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color="#f5f8ff", fontsize=10)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], color="#9ba8ba", fontsize=8)
    ax.set_ylim(0, 100)
    ax.grid(color="white", alpha=0.13)
    ax.spines["polar"].set_color("#39d7ff")
    return fig
