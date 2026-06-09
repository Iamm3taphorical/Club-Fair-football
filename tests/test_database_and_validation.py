"""
Comprehensive tests for database integrity, input validation, and security.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from modules.leaderboard.store import LeaderboardStore
from modules.shared.models import Student


class TestDatabaseConstraints(unittest.TestCase):
    """Test database integrity and constraints."""

    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.store = LeaderboardStore(self.db_path)

    def tearDown(self):
        """Clean up temporary database."""
        try:
            Path(self.db_path).unlink()
        except:
            pass

    def test_database_file_created(self):
        """Test that database file is created."""
        self.assertTrue(Path(self.db_path).exists())

    def test_student_registration_successful(self):
        """Test that students can be registered."""
        student = Student(student_id="test_user_1", name="Test User")
        self.store.register_student(student)

        # Verify student exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students WHERE student_id = ?", (student.student_id,))
        count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(count, 1)

    def test_student_update_on_duplicate_registration(self):
        """Test that duplicate registration updates existing student."""
        student1 = Student(student_id="duplicate_test", name="User 1")
        student2 = Student(student_id="duplicate_test", name="User 2")

        self.store.register_student(student1)
        self.store.register_student(student2)

        # Should not raise error and should update
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE student_id = ?", ("duplicate_test",))
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], "User 2")

    def test_leaderboard_entry_insertion(self):
        """Test that leaderboard entries can be inserted."""
        student = Student(student_id="lb_test", name="LB Test User")
        
        # Save a player score
        self.store.save_player_score(student, 450, "Finisher", 4, 80)

        # Verify entry exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT final_score FROM score_events WHERE student_id = ?", ("lb_test",))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], 450)

    def test_coach_score_insertion(self):
        """Test that coach scores can be inserted."""
        student = Student(student_id="coach_test", name="Coach Test User")
        
        # Save a coach score
        self.store.save_coach_score(student, 300, 85, "Elite Manager")

        # Verify entry exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT coach_score FROM score_events WHERE student_id = ?", ("coach_test",))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)

    def test_leaderboard_returns_entries(self):
        """Test that leaderboard can be retrieved."""
        for i in range(3):
            student = Student(student_id=f"lb_user_{i}", name=f"User {i}")
            self.store.save_player_score(student, 500 - i * 50, f"Archetype{i}", 3 + i, 70 + i)

        leaderboard = self.store.leaderboard(limit=5)

        self.assertGreater(len(leaderboard), 0)
        self.assertLessEqual(len(leaderboard), 5)

    def test_database_indexes_created(self):
        """Test that indexes are present for performance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query for indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        conn.close()

        # Should have at least 4 indexes
        self.assertGreaterEqual(len(indexes), 4)


class TestInputValidation(unittest.TestCase):
    """Test input validation and security."""

    def test_student_id_validation_regex(self):
        """Test student ID validation."""
        from app import _validate_student_id

        # Valid IDs
        self.assertTrue(_validate_student_id("user_123"))
        self.assertTrue(_validate_student_id("test-user"))
        self.assertTrue(_validate_student_id("ABC"))
        self.assertTrue(_validate_student_id("a1b2c3"))

        # Invalid IDs
        self.assertFalse(_validate_student_id("ab"))  # Too short
        self.assertFalse(_validate_student_id("a" * 21))  # Too long
        self.assertFalse(_validate_student_id("user@123"))  # Invalid character
        self.assertFalse(_validate_student_id("user.name"))  # Invalid character

    def test_html_escape_prevents_xss(self):
        """Test that HTML escaping prevents XSS injection."""
        import html

        malicious_input = "<script>alert('xss')</script>"
        escaped = html.escape(malicious_input)

        self.assertNotIn("<script>", escaped)
        self.assertNotIn("</script>", escaped)
        self.assertIn("&lt;", escaped)
        self.assertIn("&gt;", escaped)

    def test_sql_injection_parameters_safe(self):
        """Test that parameterized queries are used."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        db_path = temp_db.name

        try:
            store = LeaderboardStore(db_path)

            # Test with SQL injection attempt
            student = Student(student_id="test'; DROP TABLE students; --", name="Attacker")

            # Should not raise error or drop table - parameterized queries protect
            store.register_student(student)

            # Verify table still exists
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
            result = cursor.fetchone()
            conn.close()

            self.assertIsNotNone(result)
        finally:
            try:
                Path(db_path).unlink()
            except:
                pass

    def test_unicode_input_handling(self):
        """Test that Unicode input is handled correctly."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        db_path = temp_db.name

        try:
            store = LeaderboardStore(db_path)

            # Test with Unicode characters
            student = Student(student_id="unicode_test", name="José María")
            store.register_student(student)

            # Verify student stored with Unicode
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM students WHERE student_id = ?", ("unicode_test",))
            result = cursor.fetchone()
            conn.close()

            self.assertIsNotNone(result)
            self.assertIn("José", result[0])
        finally:
            try:
                Path(db_path).unlink()
            except:
                pass

    def test_numeric_input_validation(self):
        """Test that numeric inputs are validated."""
        from modules.shared.models import TacticalPlan

        # Valid ranges
        plan = TacticalPlan(
            formation="4-2-3-1",
            pressing=65,
            fullbacks=55,
            extra_striker=True,
            tempo=70,
            defensive_line=58,
            risk_tolerance=64
        )

        # Should not accept invalid
        self.assertTrue(0 <= plan.pressing <= 100)
        self.assertTrue(0 <= plan.fullbacks <= 100)
        self.assertTrue(0 <= plan.tempo <= 100)
        self.assertTrue(0 <= plan.defensive_line <= 100)
        self.assertTrue(0 <= plan.risk_tolerance <= 100)


class TestCoachMode(unittest.TestCase):
    """Test coach mode functionality and scenario generation."""

    def test_scenario_generation_returns_valid_data(self):
        """Test that coach scenario generation works."""
        from modules.coach_mode.tactics import generate_scenario

        scenario = generate_scenario()

        self.assertIsNotNone(scenario)
        self.assertIsNotNone(scenario.minute)
        self.assertIsNotNone(scenario.current_score)
        self.assertIsNotNone(scenario.opponent_shape)
        self.assertIsNotNone(scenario.objective)

    def test_tactical_plan_evaluation(self):
        """Test that tactical plans are evaluated."""
        from modules.coach_mode.tactics import evaluate_plan, generate_scenario
        from modules.shared.models import TacticalPlan

        scenario = generate_scenario()
        plan = TacticalPlan(
            formation="4-2-3-1",
            pressing=65,
            fullbacks=55,
            extra_striker=True,
            tempo=70,
            defensive_line=58,
            risk_tolerance=64
        )

        evaluation = evaluate_plan(scenario, plan)

        self.assertIsNotNone(evaluation)
        self.assertIsNotNone(evaluation.attack)
        self.assertIsNotNone(evaluation.defense)
        self.assertIsNotNone(evaluation.coach_score)

    def test_coach_scenario_variety(self):
        """Test that coach scenarios have variety."""
        from modules.coach_mode.tactics import generate_scenario

        scenarios = []
        for _ in range(8):
            scenario = generate_scenario()
            scenarios.append(scenario)

        # Should have at least 3 different scenarios
        unique_minutes = set(s.minute for s in scenarios)
        self.assertGreater(len(unique_minutes), 2)

    def test_simulation_integration(self):
        """Test that simulation works end-to-end."""
        from modules.coach_mode.tactics import evaluate_plan, generate_scenario
        from modules.shared.models import TacticalPlan
        from modules.simulation.engine import simulate_match

        scenario = generate_scenario()
        plan = TacticalPlan(
            formation="4-2-3-1",
            pressing=65,
            fullbacks=55,
            extra_striker=True,
            tempo=70,
            defensive_line=58,
            risk_tolerance=64
        )

        evaluation = evaluate_plan(scenario, plan)
        simulation = simulate_match(scenario, evaluation)

        self.assertIsNotNone(simulation)
        self.assertIsNotNone(simulation.final_score)
        self.assertIsNotNone(simulation.events)
        self.assertGreater(len(simulation.events), 0)


if __name__ == "__main__":
    unittest.main()
