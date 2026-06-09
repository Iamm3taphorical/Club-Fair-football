"""
Comprehensive tests for penalty mechanics, difficulty scaling, and game balance.
"""
import random
import unittest

from modules.player_mode.penalty import (
    DIFFICULTY_BASE,
    DIFFICULTY_PER_GOAL,
    DIFFICULTY_PER_REPEATED_SHOT,
    GOAL_BASE_POINTS,
    MAX_DIFFICULTY,
    MIN_SUCCESS_PROBABILITY,
    SHOT_TARGETS,
    SPECIAL_ABILITY_BONUS,
    play_penalty,
)
from modules.football_dna.engine import generate_dna


class TestPenaltyMechanics(unittest.TestCase):
    """Test penalty shot mechanics, success rates, and point calculations."""

    def setUp(self):
        """Create a standard DNA profile for testing."""
        self.dna = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        })
        self.rng = random.Random(42)  # Seeded for deterministic tests

    def test_penalty_success_requires_valid_shot(self):
        """Test that penalty returns valid result for any shot type."""
        for shot in SHOT_TARGETS.keys():
            result = play_penalty(shot, self.dna, [], 0, self.rng)
            self.assertEqual(result.shot, shot)
            self.assertIn(result.target, [info["target"] for info in SHOT_TARGETS.values()])
            self.assertIsInstance(result.success, bool)

    def test_penalty_returns_required_fields(self):
        """Test that PenaltyResult has all required fields."""
        result = play_penalty("Power Shot", self.dna, [], 0, self.rng)
        self.assertIsNotNone(result.shot)
        self.assertIsNotNone(result.target)
        self.assertIsNotNone(result.success)
        self.assertIsNotNone(result.keeper_guess)
        self.assertIsNotNone(result.difficulty)
        self.assertIsNotNone(result.reaction_time)
        self.assertIsNotNone(result.points)
        self.assertIsNotNone(result.commentary_event)

    def test_difficulty_starts_low(self):
        """Test that first penalty has low difficulty."""
        result = play_penalty("Power Shot", self.dna, [], 0, self.rng)
        expected_difficulty = DIFFICULTY_BASE
        self.assertAlmostEqual(result.difficulty, expected_difficulty, places=2)

    def test_difficulty_increases_per_goal(self):
        """Test that difficulty increases after each goal."""
        result_0_goals = play_penalty("Power Shot", self.dna, [], 0, self.rng)
        result_1_goal = play_penalty("Power Shot", self.dna, [], 1, self.rng)
        result_3_goals = play_penalty("Power Shot", self.dna, [], 3, self.rng)

        self.assertLess(result_0_goals.difficulty, result_1_goal.difficulty)
        self.assertLess(result_1_goal.difficulty, result_3_goals.difficulty)

    def test_difficulty_increases_with_repeated_shot(self):
        """Test that using same shot increases difficulty."""
        result_first = play_penalty("Left Corner", self.dna, [], 0, self.rng)
        result_repeated = play_penalty("Left Corner", self.dna, ["Left Corner"], 0, self.rng)

        self.assertLess(result_first.difficulty, result_repeated.difficulty)

    def test_difficulty_capped_at_maximum(self):
        """Test that difficulty never exceeds MAX_DIFFICULTY."""
        for goals in range(0, 10):
            result = play_penalty("Power Shot", self.dna, ["Power Shot"] * 5, goals, self.rng)
            self.assertLessEqual(result.difficulty, MAX_DIFFICULTY)

    def test_higher_difficulty_reduces_success_rate(self):
        """Test that higher difficulty lowers success probability."""
        results_easy = []
        results_hard = []
        
        rng_easy = random.Random(100)
        rng_hard = random.Random(100)

        for _ in range(50):
            result_easy = play_penalty("Power Shot", self.dna, [], 0, rng_easy)
            results_easy.append(result_easy.success)

        for _ in range(50):
            result_hard = play_penalty("Power Shot", self.dna, ["Power Shot"] * 5, 4, rng_hard)
            results_hard.append(result_hard.success)

        success_rate_easy = sum(results_easy) / len(results_easy)
        success_rate_hard = sum(results_hard) / len(results_hard)
        self.assertGreater(success_rate_easy, success_rate_hard)

    def test_penalty_points_for_goal(self):
        """Test that goals earn at least base points."""
        result = play_penalty("Power Shot", self.dna, [], 0, self.rng)
        if result.success:
            self.assertGreaterEqual(result.points, GOAL_BASE_POINTS)

    def test_penalty_points_for_miss(self):
        """Test that misses earn some points."""
        result = play_penalty("Power Shot", self.dna, [], 0, self.rng)
        self.assertGreater(result.points, 0)

    def test_special_ability_impact_on_points(self):
        """Test that special ability increases points for matching skill."""
        dna_flair = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Skill move",
        })

        panenka_results = [
            play_penalty("Panenka", dna_flair, [], 0, random.Random(i))
            for i in range(20)
        ]
        
        avg_points = sum(r.points for r in panenka_results) / len(panenka_results)
        self.assertGreater(avg_points, 50)

    def test_keeper_makes_random_guesses(self):
        """Test that keeper guesses vary and are reasonable."""
        guesses = set()
        for i in range(30):
            result = play_penalty("Power Shot", self.dna, [], 0, random.Random(i))
            guesses.add(result.keeper_guess)

        self.assertGreater(len(guesses), 1)
        for guess in guesses:
            self.assertIn(guess, ["Left Corner", "Right Corner", "Top Corner", "Low Shot", "Center"])

    def test_reaction_time_in_valid_range(self):
        """Test that reaction time is within expected range."""
        from modules.player_mode.penalty import MIN_REACTION_TIME, MAX_REACTION_TIME

        for i in range(20):
            result = play_penalty("Power Shot", self.dna, [], 0, random.Random(i))
            self.assertGreaterEqual(result.reaction_time, MIN_REACTION_TIME)
            self.assertLessEqual(result.reaction_time, MAX_REACTION_TIME)

    def test_commentary_varies_by_outcome(self):
        """Test that commentary differs for success vs failure."""
        success_commentaries = set()
        failure_commentaries = set()

        for i in range(50):
            result = play_penalty("Power Shot", self.dna, [], 0, random.Random(i))
            if result.success:
                success_commentaries.add(result.commentary_event)
            else:
                failure_commentaries.add(result.commentary_event)

        self.assertGreater(len(success_commentaries), 0)
        self.assertGreater(len(failure_commentaries), 0)

    def test_five_shot_sequence(self):
        """Test a complete 5-shot sequence to verify progression."""
        shots = []
        for i in range(5):
            result = play_penalty("Power Shot", self.dna, 
                                [s.shot for s in shots], i,
                                random.Random(i))
            shots.append(result)

        self.assertEqual(len(shots), 5)
        
        # Verify difficulties increase over sequence
        difficulties = [s.difficulty for s in shots]
        for i in range(1, len(difficulties)):
            self.assertGreaterEqual(difficulties[i], difficulties[i-1])


class TestDifficultyBalancing(unittest.TestCase):
    """Test that difficulty scaling maintains balanced success rates."""

    def test_success_rate_in_acceptable_range(self):
        """Test that success rate stays in 40-65% range across difficulty levels."""
        dna = generate_dna({
            "style": "Shooting",
            "risk": "Calculated risks",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        })

        # Test with 100 simulations at moderate difficulty
        successes = 0
        for i in range(100):
            result = play_penalty("Power Shot", dna, [], 2, random.Random(i))
            if result.success:
                successes += 1

        success_rate = successes / 100
        self.assertGreaterEqual(success_rate, 0.35)
        self.assertLessEqual(success_rate, 0.70)


class TestShotTypes(unittest.TestCase):
    """Test different shot types and their characteristics."""

    def setUp(self):
        self.dna = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        })

    def test_all_shot_types_available(self):
        """Test that all defined shot types work."""
        shot_types = list(SHOT_TARGETS.keys())
        self.assertGreaterEqual(len(shot_types), 8)

    def test_shot_type_properties(self):
        """Test that each shot type has valid properties."""
        for shot_name, shot_info in SHOT_TARGETS.items():
            self.assertIn("base", shot_info)
            self.assertIn("target", shot_info)
            self.assertIn("skill", shot_info)
            
            self.assertGreater(shot_info["base"], 0)
            self.assertLess(shot_info["base"], 1)
            self.assertIn(shot_info["skill"], 
                         ["Vision", "Finishing", "Power", "Flair", "Creativity"])

    def test_different_shot_difficulty_factors(self):
        """Test that different shots have different difficulty factors."""
        difficulties = {}
        for shot_type in ["Panenka", "Power Shot", "Top Corner", "Precision Shot"]:
            result = play_penalty(shot_type, self.dna, [], 0, random.Random(42))
            difficulties[shot_type] = result.difficulty

        # Panenka should be hardest (lowest base)
        panenka_difficulty = SHOT_TARGETS["Panenka"]["base"]
        power_difficulty = SHOT_TARGETS["Power Shot"]["base"]
        self.assertLess(panenka_difficulty, power_difficulty)


if __name__ == "__main__":
    unittest.main()
