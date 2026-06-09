"""
Comprehensive tests for Football DNA engine and player archetype system.
"""
import unittest

from modules.football_dna.engine import (
    DNA_POOL,
    generate_dna,
)


class TestDNAGeneration(unittest.TestCase):
    """Test Football DNA profile generation."""

    def test_dna_generation_returns_valid_profile(self):
        """Test that DNA generation returns a valid profile."""
        profile = generate_dna({
            "style": "Passing",
            "risk": "Calculated risks",
            "role": "Attack",
            "teamwork": "Teamwork",
            "moment": "Perfect assist",
        })

        self.assertIsNotNone(profile)
        self.assertIsNotNone(profile.footballer)
        self.assertIsNotNone(profile.archetype)
        self.assertIsNotNone(profile.strength)
        self.assertIsNotNone(profile.weakness)
        self.assertIsNotNone(profile.special_ability)
        self.assertIsNotNone(profile.suggested_position)
        self.assertIsNotNone(profile.ratings)
        self.assertIsNotNone(profile.challenges)

    def test_dna_footballer_matches_pool(self):
        """Test that generated footballer is from DNA pool."""
        profile = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        })

        # Get all footballers from DNA pool
        all_footballers = []
        for category in DNA_POOL.values():
            for entries in category.values():
                for entry in entries:
                    all_footballers.append(entry["footballer"])

        self.assertIn(profile.footballer, all_footballers)

    def test_dna_ratings_are_valid(self):
        """Test that DNA ratings are in valid range."""
        profile = generate_dna({
            "style": "Passing",
            "risk": "Safe control",
            "role": "Defense",
            "teamwork": "Teamwork",
            "moment": "Perfect assist",
        })

        for skill_name, rating in profile.ratings.items():
            self.assertIsInstance(rating, int)
            self.assertGreaterEqual(rating, 1)
            self.assertLessEqual(rating, 100)

    def test_dna_ratings_count(self):
        """Test that DNA has multiple skill ratings."""
        profile = generate_dna({
            "style": "Balanced",
            "risk": "Calculated risks",
            "role": "Both",
            "teamwork": "Depends on the match",
            "moment": "Skill move",
        })

        self.assertGreaterEqual(len(profile.ratings), 5)

    def test_dna_challenges_list(self):
        """Test that DNA includes challenges."""
        profile = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Counter attack",
        })

        self.assertIsInstance(profile.challenges, list)
        self.assertGreater(len(profile.challenges), 0)
        for challenge in profile.challenges:
            self.assertIsInstance(challenge, str)
            self.assertGreater(len(challenge), 0)

    def test_dna_special_ability_exists(self):
        """Test that special ability is present and non-empty."""
        profile = generate_dna({
            "style": "Passing",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Teamwork",
            "moment": "Dominant press",
        })

        self.assertGreater(len(profile.special_ability), 0)

    def test_dna_archetype_is_valid(self):
        """Test that archetype is one of expected types."""
        valid_archetypes = [
            "Playmaker", "Finisher", "Defender", "Allrounder",
            "Speedster", "Tactician", "Showman", "Warrior"
        ]

        for style in ["Passing", "Shooting", "Balanced"]:
            for risk in ["Safe control", "Calculated risks", "High risk"]:
                for role in ["Attack", "Defense", "Both"]:
                    profile = generate_dna({
                        "style": style,
                        "risk": risk,
                        "role": role,
                        "teamwork": "Teamwork",
                        "moment": "Perfect assist",
                    })
                    self.assertIn(profile.archetype, valid_archetypes)

    def test_dna_consistency_with_same_input(self):
        """Test that same input produces same archetype and footballer."""
        input_data = {
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        }

        profile1 = generate_dna(input_data)
        profile2 = generate_dna(input_data)

        self.assertEqual(profile1.footballer, profile2.footballer)
        self.assertEqual(profile1.archetype, profile2.archetype)

    def test_all_dna_pool_archetypes_reachable(self):
        """Test that all DNA pool categories are reachable."""
        found_archetypes = set()

        # Test diverse combinations
        styles = ["Passing", "Shooting", "Balanced"]
        risks = ["Safe control", "Calculated risks", "High risk"]
        roles = ["Attack", "Defense", "Both"]
        teamworks = ["Teamwork", "Individual brilliance", "Depends on the match"]
        moments = ["Perfect assist", "Last-minute winner", "Skill move", "Counter attack", "Dominant press"]

        for style in styles:
            for risk in risks:
                for role in roles:
                    for teamwork in teamworks:
                        for moment in moments:
                            profile = generate_dna({
                                "style": style,
                                "risk": risk,
                                "role": role,
                                "teamwork": teamwork,
                                "moment": moment,
                            })
                            found_archetypes.add(profile.archetype)

        # Should find at least 6 of 8 archetypes
        self.assertGreaterEqual(len(found_archetypes), 6)

    def test_dna_pool_has_minimum_entries(self):
        """Test that DNA pool has expanded to at least 8 archetypes."""
        archetype_count = len(DNA_POOL)
        self.assertGreaterEqual(archetype_count, 8)


class TestDNARandomness(unittest.TestCase):
    """Test that DNA generation has appropriate randomness."""

    def test_different_inputs_produce_different_profiles(self):
        """Test that different inputs produce different profiles."""
        profile_passing = generate_dna({
            "style": "Passing",
            "risk": "Safe control",
            "role": "Defense",
            "teamwork": "Teamwork",
            "moment": "Perfect assist",
        })

        profile_shooting = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        })

        # Different profiles should have different archetypes or footballers
        self.assertNotEqual(profile_passing.archetype, profile_shooting.archetype)

    def test_dna_footballer_diversity(self):
        """Test that different DNA profiles have diverse footballers."""
        footballers = set()

        for i in range(20):
            profile = generate_dna({
                "style": "Shooting" if i % 2 == 0 else "Passing",
                "risk": "High risk" if i % 3 == 0 else "Calculated risks",
                "role": "Attack" if i % 4 == 0 else "Defense",
                "teamwork": "Individual brilliance" if i % 5 == 0 else "Teamwork",
                "moment": "Last-minute winner" if i % 7 == 0 else "Perfect assist",
            })
            footballers.add(profile.footballer)

        # Should have at least 5 different footballers
        self.assertGreater(len(footballers), 4)


class TestDNAExpressionSignal(unittest.TestCase):
    """Test expression signal handling in DNA generation."""

    def test_dna_accepts_expression_signal(self):
        """Test that DNA generation accepts expression signal parameter."""
        profile = generate_dna(
            {
                "style": "Shooting",
                "risk": "High risk",
                "role": "Attack",
                "teamwork": "Individual brilliance",
                "moment": "Last-minute winner",
            },
            expression_signal="confident"
        )

        self.assertIsNotNone(profile)


if __name__ == "__main__":
    unittest.main()
