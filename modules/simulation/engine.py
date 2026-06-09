from __future__ import annotations

import random

from modules.shared.models import CoachEvaluation, CoachScenario, MatchEvent, MatchSimulation


def simulate_match(
    scenario: CoachScenario,
    evaluation: CoachEvaluation,
    rng: random.Random | None = None,
) -> MatchSimulation:
    rng = rng or random.Random()
    base_home, base_away = [int(part) for part in scenario.current_score.split("-")]
    chance_power = evaluation.attack * 0.35 + evaluation.creativity * 0.24 + evaluation.possession * 0.16
    exposure = evaluation.risk * 0.22 + max(0, 70 - evaluation.defense) * 0.28

    goals_for = 0
    goals_against = 0
    events: list[MatchEvent] = []

    for offset in [2, 5, 8, 11, 14]:
        minute = scenario.minute + offset
        roll = rng.uniform(0, 100)
        if roll < chance_power * 0.22:
            goals_for += 1
            events.append(
                MatchEvent(
                    minute=f"{minute}'",
                    title="GOAL",
                    detail="Your tactical adjustment creates the overload and the finish is clinical.",
                    tone="positive",
                )
            )
        elif roll < chance_power * 0.40:
            events.append(
                MatchEvent(
                    minute=f"{minute}'",
                    title="Chance Created",
                    detail="The new shape opens a passing lane between the defensive and midfield lines.",
                    tone="positive",
                )
            )
        elif roll > 100 - exposure * 0.16:
            goals_against += 1 if rng.random() < 0.35 else 0
            title = "Conceded" if goals_against else "Dangerous Counter"
            detail = "The aggressive setup leaves space behind the fullback channel."
            events.append(MatchEvent(minute=f"{minute}'", title=title, detail=detail, tone="warning"))
        else:
            events.append(
                MatchEvent(
                    minute=f"{minute}'",
                    title="Control Phase",
                    detail="Your team circulates possession and waits for the next pressing trigger.",
                )
            )

    final_home = base_home + goals_for
    final_away = base_away + goals_against
    if final_home > final_away:
        result = "Victory"
        points = 220 + evaluation.coach_score
    elif final_home == final_away:
        result = "Draw"
        points = 130 + evaluation.coach_score
    else:
        result = "Defeat"
        points = 70 + evaluation.coach_score

    events.append(MatchEvent(minute="FT", title=result, detail=f"Final score: {final_home}-{final_away}."))
    return MatchSimulation(
        final_score=f"{final_home}-{final_away}",
        result_label=result,
        events=events,
        points=points,
    )

