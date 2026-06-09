import os
from contextlib import contextmanager

os.environ.setdefault("FOOTBALLVERSE_DISABLE_CV", "1")

import pytest
from fastapi import HTTPException
from backend import database, schemas
from backend.main import (
    check_in_player,
    execute_shot,
    get_dna,
    get_penalty_session,
    get_user_history,
    login,
    read_root,
    save_dna,
    scan_identity,
    start_penalty_session,
)


@contextmanager
def db_session():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_read_root():
    assert read_root() == {"status": "ok", "message": "FootballVerse AI API is running"}

def test_check_in_player():
    with db_session() as db:
        player = check_in_player(
            schemas.PlayerCreate(student_id="TEST-123", name="Test User"),
            db=db,
        )
        assert player.id == "TEST-123"
        assert player.name == "Test User"

def test_save_and_get_dna():
    dna_payload = schemas.DNACreate(
        footballer_match="Messi",
        strengths="Dribbling",
        weaknesses="Heading",
        profile_json="{}",
    )

    with db_session() as db:
        dna = save_dna("TEST-123", dna_payload, db=db)
        assert dna.footballer_match == "Messi"

    with db_session() as db:
        dna = get_dna("TEST-123", db=db)
        assert dna.strengths == "Dribbling"

def test_login_rejects_invalid_user_id():
    with db_session() as db:
        with pytest.raises(HTTPException) as exc:
            login({"user_id": "bad.user", "name": "Bad User"}, db=db)
        assert exc.value.status_code == 422

def test_identity_scan_returns_honest_fallback_metadata():
    with db_session() as db:
        response = scan_identity(
            {
                "user_id": "SCAN-123",
                "name": "Scan User",
                "answers": {"playstyle": "Playmaker"},
                "face_detected": False,
            },
            db=db,
        )
        scan = response["dna"]["scan"]
        assert scan["status"] in {"adapter_fallback", "deepface_confirmed"}
        if scan["status"] == "adapter_fallback":
            assert "fallback_reason" in scan
            assert scan["matching_method"] == "personality/DNA similarity fallback"

def test_history_and_penalty_session_read_models():
    with db_session() as db:
        login({"user_id": "HIST-123", "name": "History User"}, db=db)
        started = start_penalty_session({"user_id": "HIST-123", "name": "History User"}, db=db)
        shot = execute_shot(
            {
                "user_id": "HIST-123",
                "name": "History User",
                "session_id": started["session_id"],
                "gesture": "Point Left",
                "history": [],
                "power": 0.62,
                "curve": 0.18,
                "difficulty": "Hard",
                "commentary_style": "Professional",
            },
            db=db,
        )
        snapshot = get_penalty_session(started["session_id"], user_id="HIST-123", db=db)
        assert snapshot["status"] == "active"
        assert snapshot["attempts"][0]["id"] == shot["attempt_id"]
        history = get_user_history("HIST-123", limit=5, db=db)
        assert history["penalty_sessions"]

# def test_websocket_cv_engine():
#     # A basic test of the cv_engine directly to ensure it handles bad data
#     from backend.cv_engine import GestureRecognizer
#     recognizer = GestureRecognizer()
#     
#     # Invalid image bytes should return error
#     result = recognizer.process_frame(b"not an image")
#     assert "error" in result

def test_penalty_game_logic():
    from backend.game_logic import PenaltyGameEngine
    engine = PenaltyGameEngine()
    result = engine.play_shot("TEST-123", "Fist", "Power Shot", ["Power Shot", "Power Shot"], "Legendary", 0.9, 0.0)
    assert "result" in result
    assert result["difficulty_applied"] == 0.95
    assert "keeper_guess" in result

def test_llm_commentary():
    from backend.llm_provider import get_commentary_provider
    provider = get_commentary_provider("mock")
    history = [{"result": "Missed"}, {"result": "Missed"}]
    commentary = provider.generate_shot_commentary({"result": "Goal"}, "Professional", history)
    assert "finally makes up" in commentary or "clinical" in commentary

def test_dna_engine():
    from backend.dna_engine import FootballDNAEvolutionEngine
    engine = FootballDNAEvolutionEngine()
    result = engine.generate_initial_score({"playstyle": "Playmaker"})
    assert result["stats"]["creativity"] == 85
    assert "primary_match" in result

def test_coach_mode():
    from backend.coach_mode import TacticalGenerator, MatchSimulationEngine
    generator = TacticalGenerator()
    scenario = generator.generate_scenario()
    assert "minute" in scenario
    
    simulator = MatchSimulationEngine()
    tactics = {"formation": "4-3-3", "attack": 85, "defense": 60, "possession": 65}
    dna = {"vision": 90, "leadership": 80}
    result = simulator.simulate_match(scenario, tactics, dna)
    
    assert "final_score" in result
    assert len(result["timeline"]) > 0
    assert "explanation" in result
