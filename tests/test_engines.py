import unittest

from modules.coach_mode.tactics import evaluate_plan, generate_scenario
from modules.football_dna.engine import generate_dna
from modules.player_mode.penalty import play_penalty
from modules.shared.models import TacticalPlan
from modules.simulation.engine import simulate_match


class EngineTests(unittest.TestCase):
    def test_dna_generation_returns_profile(self):
        profile = generate_dna(
            {
                "style": "Passing",
                "risk": "Calculated risks",
                "role": "Attack",
                "teamwork": "Teamwork",
                "moment": "Perfect assist",
            }
        )
        self.assertTrue(profile.footballer)
        self.assertTrue(profile.ratings)
        self.assertTrue(profile.challenges)

    def test_penalty_returns_result(self):
        profile = generate_dna(
            {
                "style": "Shooting",
                "risk": "High risk",
                "role": "Attack",
                "teamwork": "Individual brilliance",
                "moment": "Last-minute winner",
            }
        )
        result = play_penalty("Power Shot", profile, [], 0)
        self.assertEqual(result.shot, "Power Shot")
        self.assertGreater(result.points, 0)

    def test_coach_simulation_returns_final_score(self):
        scenario = generate_scenario()
        plan = TacticalPlan(
            formation="4-2-3-1",
            pressing=65,
            fullbacks=55,
            extra_striker=True,
            tempo=70,
            defensive_line=58,
            risk_tolerance=64,
        )
        evaluation = evaluate_plan(scenario, plan)
        simulation = simulate_match(scenario, evaluation)
        self.assertIn("-", simulation.final_score)
        self.assertTrue(simulation.events)


if __name__ == "__main__":
    unittest.main()
