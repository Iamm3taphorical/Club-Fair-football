from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

class Player(Base):
    __tablename__ = "players"
    id = Column(String, primary_key=True, index=True) # e.g., student_id
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    session_history_json = Column(Text, default="[]")
    football_dna_json = Column(Text, default="{}")

    dna = relationship("FootballDNA", back_populates="player", uselist=False)
    penalty_sessions = relationship("PenaltySession", back_populates="player")
    coach_sessions = relationship("CoachSession", back_populates="player")
    dna_evolutions = relationship("FootballDNAEvolution", back_populates="player")
    match_sessions = relationship("MatchSession", back_populates="player")

class FootballDNA(Base):
    __tablename__ = "football_dna"
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    footballer_match = Column(String)
    strengths = Column(String)
    weaknesses = Column(String)
    profile_json = Column(Text) # Store full generated profile
    style = Column(String)
    traits_json = Column(Text, default="{}")
    special_ability = Column(String)
    confidence_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="dna")

class FootballDNAEvolution(Base):
    __tablename__ = "football_dna_evolution"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    previous_match = Column(String)
    evolved_match = Column(String)
    reason = Column(String)
    profile_json = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="dna_evolutions")

class MatchSession(Base):
    __tablename__ = "match_sessions"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    mode = Column(String, index=True)
    status = Column(String, default="active")
    summary_json = Column(Text, default="{}")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)

    player = relationship("Player", back_populates="match_sessions")

class PenaltySession(Base):
    __tablename__ = "penalty_sessions"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    match_session_id = Column(Integer, ForeignKey("match_sessions.id"), index=True)
    current_challenge = Column(String) # For persistence
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    goals = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    average_reaction_time = Column(Float, default=0.0)
    dna_after_json = Column(Text, default="{}")

    player = relationship("Player", back_populates="penalty_sessions")
    attempts = relationship("PenaltyAttempt", back_populates="session")
    commentary = relationship("CommentaryLog", back_populates="session")

class PenaltyAttempt(Base):
    __tablename__ = "penalty_attempts"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("penalty_sessions.id"), index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    challenge_type = Column(String)
    gesture_used = Column(String)
    shot_type = Column(String)
    shot_target = Column(String)
    keeper_guess = Column(String)
    power = Column(Float, default=0.5)
    curve = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    reaction_time = Column(Float, default=0.0)
    result = Column(String) # 'Goal', 'Saved', 'Missed'
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("PenaltySession", back_populates="attempts")

class CoachSession(Base):
    __tablename__ = "coach_sessions"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    match_session_id = Column(Integer, ForeignKey("match_sessions.id"), index=True)
    coach_style = Column(String)
    scenario_json = Column(Text, default="{}")
    tactics_json = Column(Text, default="{}")
    result_json = Column(Text, default="{}")
    attack_score = Column(Integer)
    defense_score = Column(Integer)
    creativity_score = Column(Integer)
    tactical_rating = Column(Integer)
    final_rating = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="coach_sessions")

class CoachDecision(Base):
    __tablename__ = "coaching_decisions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("coach_sessions.id"), index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    coach_style = Column(String)
    formation = Column(String)
    pressure = Column(Integer)
    roles_json = Column(Text, default="{}")
    tactics_json = Column(Text, default="{}")
    scenario_json = Column(Text, default="{}")
    result_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CommentaryLog(Base):
    __tablename__ = "commentary_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("penalty_sessions.id"), index=True)
    style = Column(String)
    commentary_text = Column(String)
    event_type = Column(String)
    payload_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("PenaltySession", back_populates="commentary")

class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    session_type = Column(String)
    session_id = Column(Integer, index=True)
    event_type = Column(String, index=True)
    payload_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), index=True)
    total_score = Column(Integer, index=True)
    rank = Column(String)
    mode = Column(String) # 'Player', 'Coach'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
