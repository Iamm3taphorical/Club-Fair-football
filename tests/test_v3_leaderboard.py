import os
import unittest

os.environ.setdefault("FOOTBALLVERSE_DISABLE_CV", "1")

from backend import database, models
from backend.main import _upsert_leaderboard


class V3LeaderboardTests(unittest.TestCase):
    prefix = "LBTEST-"

    def setUp(self):
        self.db = database.SessionLocal()
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        self.db.close()

    def _cleanup(self):
        self.db.query(models.Leaderboard).filter(models.Leaderboard.player_id.like(f"{self.prefix}%")).delete(synchronize_session=False)
        self.db.query(models.Player).filter(models.Player.id.like(f"{self.prefix}%")).delete(synchronize_session=False)
        self.db.commit()

    def _player(self, suffix: str):
        player = models.Player(id=f"{self.prefix}{suffix}", name=f"Leaderboard Test {suffix}")
        self.db.add(player)
        self.db.flush()
        return player

    def test_lower_score_does_not_downgrade_best_score_or_title(self):
        player = self._player("BEST")

        _upsert_leaderboard(self.db, player.id, "Player", 500, "High Title")
        _upsert_leaderboard(self.db, player.id, "Player", 100, "Low Title")
        self.db.commit()

        entry = self.db.query(models.Leaderboard).filter_by(player_id=player.id, mode="Player").one()
        self.assertEqual(entry.total_score, 500)
        self.assertEqual(entry.mode_title, "High Title")

    def test_mode_leaderboard_is_trimmed_to_top_100(self):
        for index in range(105):
            player = self._player(f"CAP-{index:03d}")
            _upsert_leaderboard(self.db, player.id, "Fan", index)
        self.db.commit()

        entries = (
            self.db.query(models.Leaderboard)
            .filter(models.Leaderboard.player_id.like(f"{self.prefix}CAP-%"), models.Leaderboard.mode == "Fan")
            .order_by(models.Leaderboard.total_score.desc())
            .all()
        )
        self.assertEqual(len(entries), 100)
        self.assertEqual(entries[0].rank, "1")
        self.assertEqual(entries[0].total_score, 104)
        self.assertEqual(entries[-1].total_score, 5)


if __name__ == "__main__":
    unittest.main()
