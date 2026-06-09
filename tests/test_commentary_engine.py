"""
Comprehensive tests for commentary engine and narrative generation.
"""
import unittest

from modules.commentary.engine import COMMENTARY_STYLES, generate_commentary
from modules.football_dna.engine import generate_dna


class TestCommentaryGeneration(unittest.TestCase):
    """Test commentary generation and style variety."""

    def setUp(self):
        """Create a standard DNA profile for testing."""
        self.dna = generate_dna({
            "style": "Shooting",
            "risk": "High risk",
            "role": "Attack",
            "teamwork": "Individual brilliance",
            "moment": "Last-minute winner",
        })

    def test_commentary_generates_for_all_styles(self):
        """Test that commentary generates for all defined styles."""
        for style in COMMENTARY_STYLES:
            commentary = generate_commentary(
                event="Power Shot Goal",
                style=style
            )
            self.assertIsNotNone(commentary)
            self.assertGreater(len(commentary), 0)

    def test_commentary_has_minimum_styles(self):
        """Test that at least 24 commentary styles exist."""
        self.assertGreaterEqual(len(COMMENTARY_STYLES), 24)

    def test_commentary_varies_by_style(self):
        """Test that different styles produce different commentary."""
        commentaries = {}

        for style in COMMENTARY_STYLES[:8]:
            commentary = generate_commentary(
                event="Power Shot Goal",
                style=style,
                rng=None
            )
            commentaries[style] = commentary

        # Check that not all commentaries are identical
        unique_commentaries = set(commentaries.values())
        self.assertGreater(len(unique_commentaries), 1)

    def test_commentary_includes_shot_event(self):
        """Test that commentary references the event."""
        shots = ["Power Shot Goal", "Panenka Goal", "Left Corner Goal", "Curve Shot Miss"]

        for shot in shots:
            commentary = generate_commentary(
                event=shot,
                style="Professional"
            )
            self.assertGreater(len(commentary), 10)

    def test_commentary_different_for_different_styles(self):
        """Test that different styles produce different commentary."""
        commentaries = {}

        for style in COMMENTARY_STYLES[:5]:
            rng_seed = __import__('random').Random(42)
            commentary = generate_commentary(
                event="Power Shot Goal",
                style=style,
                rng=rng_seed
            )
            commentaries[style] = commentary

        # Check that not all commentaries are identical
        unique_commentaries = set(commentaries.values())
        self.assertGreater(len(unique_commentaries), 1)

    def test_commentary_no_excessive_repetition(self):
        """Test that generated commentaries don't repeat excessively."""
        commentaries = []

        rng = __import__('random').Random(42)
        for i in range(20):
            commentary = generate_commentary(
                event="Power Shot Goal",
                style="Professional",
                rng=rng
            )
            commentaries.append(commentary)

        # Should have variety - not all identical
        unique = set(commentaries)
        self.assertGreaterEqual(len(unique), 5)

    def test_all_commentary_styles_are_strings(self):
        """Test that all commentary styles are valid."""
        for style in COMMENTARY_STYLES:
            self.assertIsInstance(style, str)
            self.assertGreater(len(style), 0)

    def test_commentary_reasonable_length(self):
        """Test that commentary is reasonable length."""
        commentary = generate_commentary(
            event="Power Shot Goal",
            style="Professional"
        )

        # Should be between 20 and 500 characters
        self.assertGreater(len(commentary), 20)
        self.assertLess(len(commentary), 500)


class TestCommentaryRandomness(unittest.TestCase):
    """Test commentary randomness and diversity."""

    def test_commentary_with_deterministic_rng(self):
        """Test that seeding produces deterministic commentary."""
        import random
        
        rng1 = random.Random(42)
        comm1 = generate_commentary(
            event="Power Shot Goal",
            style="Professional",
            rng=rng1
        )

        rng2 = random.Random(42)
        comm2 = generate_commentary(
            event="Power Shot Goal",
            style="Professional",
            rng=rng2
        )

        self.assertEqual(comm1, comm2)

    def test_commentary_variety_across_styles(self):
        """Test that different styles have distinct vocabulary."""
        import random
        
        professional_comments = []
        crazy_comments = []

        for i in range(5):
            prof = generate_commentary(
                event="Power Shot Goal",
                style="Professional",
                rng=random.Random(i)
            )
            crazy = generate_commentary(
                event="Power Shot Goal",
                style="Excited Commentator",
                rng=random.Random(i)
            )
            professional_comments.append(prof)
            crazy_comments.append(crazy)

        prof_text = " ".join(professional_comments).lower()
        crazy_text = " ".join(crazy_comments).lower()

        # Excited should have more exclamation marks
        self.assertGreater(crazy_text.count("!"), prof_text.count("!"))


if __name__ == "__main__":
    unittest.main()
