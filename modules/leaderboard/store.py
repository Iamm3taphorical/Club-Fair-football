from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from modules.shared.config import DATABASE_PATH
from modules.shared.models import LeaderboardEntry, Student


class LeaderboardStore:
    def __init__(self, db_path: Path = DATABASE_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_db(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS score_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    final_score INTEGER NOT NULL,
                    dna TEXT DEFAULT '',
                    goals INTEGER DEFAULT 0,
                    accuracy INTEGER DEFAULT 0,
                    coach_score INTEGER DEFAULT 0,
                    coach_rank TEXT DEFAULT '',
                    prize_tier TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_student_id ON score_events(student_id);
                CREATE INDEX IF NOT EXISTS idx_final_score ON score_events(final_score DESC);
                CREATE INDEX IF NOT EXISTS idx_mode ON score_events(mode);
                CREATE INDEX IF NOT EXISTS idx_created_at ON score_events(created_at DESC);
                """
            )

    def register_student(self, student: Student) -> None:
        now = _now()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO students(student_id, name, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id) DO UPDATE SET name = excluded.name
                """,
                (student.student_id.strip(), student.name.strip(), now),
            )

    def save_player_score(
        self,
        student: Student,
        final_score: int,
        dna: str,
        goals: int,
        accuracy: int,
    ) -> None:
        self.register_student(student)
        prize_tier = reward_tier(final_score)
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO score_events(student_id, name, mode, final_score, dna, goals, accuracy, prize_tier, created_at)
                VALUES (?, ?, 'Player Mode', ?, ?, ?, ?, ?, ?)
                """,
                (student.student_id, student.name, final_score, dna, goals, accuracy, prize_tier, _now()),
            )

    def save_coach_score(
        self,
        student: Student,
        final_score: int,
        coach_score: int,
        coach_rank: str,
    ) -> None:
        self.register_student(student)
        prize_tier = reward_tier(final_score)
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO score_events(student_id, name, mode, final_score, coach_score, coach_rank, prize_tier, created_at)
                VALUES (?, ?, 'Coach Mode', ?, ?, ?, ?, ?)
                """,
                (student.student_id, student.name, final_score, coach_score, coach_rank, prize_tier, _now()),
            )

    def leaderboard(self, limit: int = 20) -> list[LeaderboardEntry]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT e.student_id, e.name, e.final_score, e.mode AS best_mode,
                       e.dna, e.coach_rank, e.created_at
                FROM score_events e
                JOIN (
                    SELECT student_id, MAX(final_score) AS final_score
                    FROM score_events
                    GROUP BY student_id
                ) best
                ON e.student_id = best.student_id AND e.final_score = best.final_score
                GROUP BY e.student_id
                ORDER BY e.final_score DESC, e.created_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            LeaderboardEntry(
                student_id=row["student_id"],
                name=row["name"],
                final_score=int(row["final_score"]),
                best_mode=row["best_mode"],
                dna=row["dna"] or "",
                coach_rank=row["coach_rank"] or "",
                timestamp=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def section(self, metric: str, limit: int = 10) -> list[sqlite3.Row]:
        allowed = {
            "final_score": "final_score",
            "accuracy": "accuracy",
            "coach_score": "coach_score",
        }
        column = allowed.get(metric, "final_score")
        with self.connect() as connection:
            return connection.execute(
                f"""
                SELECT student_id, name, mode, final_score, accuracy, coach_score, dna, coach_rank, prize_tier, created_at
                FROM score_events
                ORDER BY {column} DESC, final_score DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def seed_demo_data(self) -> None:
        demo_rows = [
            (Student("FV-1001", "Ayaan Rahman"), 615, "Messi", 4, 80),
            (Student("FV-1002", "Nusrat Jahan"), 740, "Ronaldo", 5, 100),
            (Student("FV-1003", "Rafi Karim"), 560, "Neymar", 3, 60),
        ]
        for student, score, dna, goals, acc in demo_rows:
            self.save_player_score(student, score, dna, goals, acc)
        coach_rows = [
            (Student("FV-2001", "Tamim Chowdhury"), 312, 88, "Elite Manager"),
            (Student("FV-2002", "Sadia Islam"), 286, 76, "Tactical Analyst"),
        ]
        for student, final_score, coach_score, rank in coach_rows:
            self.save_coach_score(student, final_score, coach_score, rank)


def reward_tier(final_score: int) -> str:
    if final_score >= 700:
        return "Gold Prize"
    if final_score >= 520:
        return "Silver Prize"
    if final_score >= 350:
        return "Bronze Prize"
    return "Participation"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
