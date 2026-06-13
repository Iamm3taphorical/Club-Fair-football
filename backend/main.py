import json
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import Body, Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend import database, models, schemas
from backend.coach_mode import MatchSimulationEngine, TacticalGenerator
from backend.cv_engine import GestureRecognizer
from backend.dna_engine import FootballDNAEvolutionEngine
from backend.face_identity import FaceIdentityMatcher
from backend.game_logic import PenaltyGameEngine
from backend.llm_provider import get_commentary_provider
from backend import fan_mode


cv_recognizer = GestureRecognizer()
penalty_engine = PenaltyGameEngine()
dna_engine = FootballDNAEvolutionEngine()
face_matcher = FaceIdentityMatcher()
tactical_gen = TacticalGenerator()
match_sim = MatchSimulationEngine()
commentary_provider = get_commentary_provider("mock")
USER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")


models.Base.metadata.create_all(bind=database.engine)


def _ensure_schema_compatibility() -> None:
    additions = {
        "players": [
            ("last_login_at", "DATETIME"),
            ("session_history_json", "TEXT DEFAULT '[]'"),
            ("football_dna_json", "TEXT DEFAULT '{}'"),
        ],
        "football_dna": [
            ("style", "VARCHAR"),
            ("traits_json", "TEXT DEFAULT '{}'"),
            ("special_ability", "VARCHAR"),
            ("confidence_score", "FLOAT DEFAULT 0.0"),
            ("updated_at", "DATETIME"),
        ],
        "penalty_sessions": [
            ("match_session_id", "INTEGER"),
            ("completed_at", "DATETIME"),
            ("goals", "INTEGER DEFAULT 0"),
            ("accuracy", "FLOAT DEFAULT 0.0"),
            ("average_reaction_time", "FLOAT DEFAULT 0.0"),
            ("dna_after_json", "TEXT DEFAULT '{}'"),
        ],
        "penalty_attempts": [
            ("shot_type", "VARCHAR"),
            ("shot_target", "VARCHAR"),
            ("keeper_guess", "VARCHAR"),
            ("power", "FLOAT DEFAULT 0.5"),
            ("curve", "FLOAT DEFAULT 0.0"),
            ("confidence_score", "FLOAT DEFAULT 0.0"),
            ("reaction_time", "FLOAT DEFAULT 0.0"),
        ],
        "coach_sessions": [
            ("match_session_id", "INTEGER"),
            ("coach_style", "VARCHAR"),
            ("scenario_json", "TEXT DEFAULT '{}'"),
            ("tactics_json", "TEXT DEFAULT '{}'"),
            ("result_json", "TEXT DEFAULT '{}'"),
            ("tactical_rating", "INTEGER"),
        ],
        "commentary_logs": [
            ("event_type", "VARCHAR"),
            ("payload_json", "TEXT DEFAULT '{}'"),
        ],
        "leaderboard": [
            ("mode_title", "VARCHAR"),
        ],
    }
    with database.engine.begin() as conn:
        for table_name, columns in additions.items():
            existing = {
                row["name"]
                for row in conn.execute(text(f"PRAGMA table_info({table_name})")).mappings()
            }
            for column_name, ddl in columns:
                if column_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))


_ensure_schema_compatibility()


app = FastAPI(title="FootballVerse AI V3", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, default=str)


def _json_loads(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _player_id_from(payload: Dict[str, Any], required: bool = True) -> str:
    raw = payload.get("user_id") or payload.get("player_id") or payload.get("student_id")
    cleaned = str(raw or "").strip()
    if not cleaned:
        if required:
            raise HTTPException(status_code=422, detail="A valid user_id is required.")
        return "guest"
    if not USER_ID_RE.fullmatch(cleaned):
        raise HTTPException(
            status_code=422,
            detail="User ID must be 3-20 characters and use only letters, numbers, underscores, or hyphens.",
        )
    return cleaned


def _validate_player_id(player_id: str) -> str:
    return _player_id_from({"user_id": player_id}, required=True)


def _name_from(payload: Dict[str, Any], default: str = "FootballVerse Player") -> str:
    cleaned = str(payload.get("name") or default).strip()
    if not 2 <= len(cleaned) <= 60:
        raise HTTPException(status_code=422, detail="Name must be 2-60 characters.")
    if any(char in cleaned for char in "<>{}[]"):
        raise HTTPException(status_code=422, detail="Name contains unsupported characters.")
    return cleaned


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None or value == "":
        return None
    try:
        next_value = int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"{field_name} must be an integer.") from exc
    if next_value <= 0:
        raise HTTPException(status_code=422, detail=f"{field_name} must be positive.")
    return next_value


def _get_player_penalty_session(db: Session, session_id: int | None, player_id: str) -> models.PenaltySession | None:
    if session_id is None:
        return None
    session = db.get(models.PenaltySession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Penalty session not found.")
    if session.player_id != player_id:
        raise HTTPException(status_code=403, detail="Penalty session belongs to another user.")
    return session


def _get_or_create_player(db: Session, player_id: str, name: str | None = None) -> models.Player:
    player = db.get(models.Player, player_id)
    if player is None:
        player = models.Player(
            id=player_id,
            name=name or "FootballVerse Player",
            created_at=_now(),
            last_login_at=_now(),
            session_history_json="[]",
            football_dna_json="{}",
        )
        db.add(player)
        db.flush()
    else:
        if name:
            player.name = name
        player.last_login_at = _now()
    return player


def _profile_response(player: models.Player) -> Dict[str, Any]:
    return {
        "user_id": player.id,
        "id": player.id,
        "name": player.name,
        "timestamp": (player.created_at or _now()).isoformat(),
        "last_login_at": (player.last_login_at or _now()).isoformat(),
        "session_history": _json_loads(player.session_history_json, []),
        "dna": _json_loads(player.football_dna_json, {}),
    }


def _append_session_history(player: models.Player, entry: Dict[str, Any]) -> None:
    history = _json_loads(player.session_history_json, [])
    history.append({**entry, "timestamp": _now().isoformat()})
    player.session_history_json = _json_dumps(history[-25:])


def _log_event(
    db: Session,
    player_id: str,
    event_type: str,
    payload: Dict[str, Any],
    session_type: str = "system",
    session_id: int | None = None,
) -> None:
    db.add(
        models.EventLog(
            player_id=player_id,
            session_type=session_type,
            session_id=session_id,
            event_type=event_type,
            payload_json=_json_dumps(payload),
            created_at=_now(),
        )
    )


def _top_bottom_stats(stats: Dict[str, int]) -> tuple[str, str]:
    if not stats:
        return "Vision", "Power"
    ordered = sorted(stats.items(), key=lambda item: item[1], reverse=True)
    return ordered[0][0].title(), ordered[-1][0].title()


def _upsert_dna(db: Session, player: models.Player, profile: Dict[str, Any]) -> models.FootballDNA:
    strength, weakness = _top_bottom_stats(profile.get("stats", {}))
    dna = db.get(models.FootballDNA, player.id)
    if dna is None:
        dna = models.FootballDNA(player_id=player.id)
        db.add(dna)
    dna.footballer_match = profile.get("name_match") or profile.get("display_name") or profile.get("primary_match")
    dna.strengths = strength
    dna.weaknesses = weakness
    dna.profile_json = _json_dumps(profile)
    dna.style = profile.get("style")
    dna.traits_json = _json_dumps(profile.get("traits", {}))
    dna.special_ability = profile.get("special_ability")
    dna.confidence_score = float(profile.get("confidence_score", 0.0))
    dna.updated_at = _now()
    player.football_dna_json = _json_dumps(profile)
    return dna

def _title_for_leaderboard(mode: str, score: int) -> str:
    if mode == "Player":
        if score >= 480:
            return "Penalty Royalty"
        if score >= 380:
            return "Clutch Finisher"
        if score >= 250:
            return "Spot-Kick Specialist"
        return "Training Ground Prospect"
    if mode == "Coach":
        if score >= 520:
            return "Elite Manager"
        if score >= 380:
            return "Tactical Genius"
        if score >= 240:
            return "Matchday Strategist"
        return "Assistant Coach"
    if score >= 35:
        return "FootballVerse Immortal"
    if score >= 30:
        return "Tactical Genius"
    if score >= 20:
        return "Football Historian"
    if score >= 10:
        return "Matchday Expert"
    return "Sunday Fan"


def _upsert_leaderboard(db: Session, player_id: str, mode: str, score: int, mode_title: str | None = None):
    normalized_mode = mode.capitalize()
    if normalized_mode not in {"Player", "Coach", "Fan"}:
        raise HTTPException(status_code=400, detail="Invalid leaderboard mode.")
    safe_score = max(0, int(score))
    lb = db.query(models.Leaderboard).filter_by(player_id=player_id, mode=normalized_mode).first()
    if lb:
        previous_score = lb.total_score or 0
        stored_score = max(previous_score, safe_score)
        lb.total_score = stored_score
        if safe_score >= previous_score:
            lb.mode_title = mode_title or _title_for_leaderboard(normalized_mode, stored_score)
        elif not lb.mode_title:
            lb.mode_title = _title_for_leaderboard(normalized_mode, stored_score)
    else:
        stored_score = safe_score
        lb = models.Leaderboard(
            player_id=player_id,
            mode=normalized_mode,
            total_score=stored_score,
            rank="Unranked",
            mode_title=mode_title or _title_for_leaderboard(normalized_mode, stored_score),
        )
        db.add(lb)
    db.flush()
    
    # Update ranks for this mode
    all_lbs = db.query(models.Leaderboard).filter_by(mode=normalized_mode).order_by(models.Leaderboard.total_score.desc()).all()
    for i, entry in enumerate(all_lbs):
        entry.rank = str(i + 1)
    for entry in all_lbs[100:]:
        db.delete(entry)
    return lb


def _gesture_to_shot(gesture: str) -> Dict[str, str]:
    shot_map = {
        "Point Left": {"shot_type": "Left Shot", "target": "Left Corner"},
        "Point Right": {"shot_type": "Right Shot", "target": "Right Corner"},
        "Point Up": {"shot_type": "Top Corner", "target": "Top Corner"},
        "Point Down": {"shot_type": "Low Shot", "target": "Low Shot"},
        "Pinch": {"shot_type": "Panenka", "target": "Panenka"},
        "Fist": {"shot_type": "Power Shot", "target": "Power Shot"},
        "Power Shot": {"shot_type": "Power Shot", "target": "Power Shot"},
    }
    return shot_map.get(gesture, {"shot_type": "Center Shot", "target": "Low Shot"})


def _normalize_history(history: List[Any]) -> List[str]:
    valid_targets = {"Left Corner", "Right Corner", "Top Corner", "Low Shot", "Panenka", "Power Shot"}
    normalized: List[str] = []
    for entry in history:
        if isinstance(entry, str) and entry in valid_targets:
            normalized.append(entry)
        elif isinstance(entry, dict):
            target = entry.get("shot_target") or entry.get("target")
            if target in valid_targets:
                normalized.append(target)
    return normalized


def _events_from_attempts(attempts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    for attempt in attempts:
        result = attempt.get("result")
        shot_type = attempt.get("shot_type") or attempt.get("shotType")
        if result != "Goal":
            if shot_type == "Power Shot":
                events.append({"type": "SAVED_POWER_SHOT"})
            continue
        if shot_type == "Power Shot":
            events.append({"type": "POWER_SHOT_GOAL"})
        elif shot_type == "Panenka":
            events.append({"type": "PANENKA_GOAL"})
        elif shot_type in {"Top Corner", "Left Shot", "Right Shot"}:
            events.append({"type": "CURVE_SHOT_GOAL"})
        elif shot_type == "Low Shot":
            events.append({"type": "LOW_SHOT_GOAL"})
    return events


def _build_report(
    player: models.Player,
    session_id: int | None,
    attempts: List[Dict[str, Any]],
    current_dna: Dict[str, Any],
    evolved_dna: Dict[str, Any],
) -> Dict[str, Any]:
    total = max(len(attempts), 1)
    goals = sum(1 for attempt in attempts if attempt.get("result") == "Goal")
    accuracy = round((goals / total) * 100)
    average_reaction = round(
        sum(float(attempt.get("reaction_time") or attempt.get("reactionTime") or 0.72) for attempt in attempts) / total,
        2,
    )
    shot_frequency = Counter(attempt.get("shot_type") or attempt.get("shotType") or "Shot" for attempt in attempts)
    successful_frequency = Counter(
        attempt.get("shot_type") or attempt.get("shotType") or "Shot"
        for attempt in attempts
        if attempt.get("result") == "Goal"
    )
    failed_frequency = Counter(
        attempt.get("shot_type") or attempt.get("shotType") or "Shot"
        for attempt in attempts
        if attempt.get("result") != "Goal"
    )
    previous_match = current_dna.get("primary_match", "Messi")
    evolved_match = evolved_dna.get("primary_match", previous_match)
    evolution_label = dna_engine.build_evolution_label(previous_match, evolved_match, dict(shot_frequency))
    best_skill = successful_frequency.most_common(1)[0][0] if successful_frequency else evolved_dna.get("special_ability", "Curve Shot")
    weakness = failed_frequency.most_common(1)[0][0] if failed_frequency else current_dna.get("weakness", "Power Shots")
    graph = []
    running_goals = 0
    for index, attempt in enumerate(attempts, start=1):
        if attempt.get("result") == "Goal":
            running_goals += 1
        graph.append({"shot": index, "goals": running_goals, "result": attempt.get("result")})

    return {
        "session_id": session_id,
        "player": {"user_id": player.id, "name": player.name},
        "player_type": f"{evolved_match} Archetype",
        "goals": goals,
        "total_shots": len(attempts),
        "score": f"{goals}/{len(attempts)}",
        "accuracy": accuracy,
        "reaction_time": average_reaction,
        "best_skill": best_skill,
        "weakness": weakness,
        "suggested_role": evolved_dna.get("suggested_role", "CAM"),
        "dna_before": current_dna,
        "dna_after": evolved_dna,
        "evolution": evolution_label,
        "radar_chart": [
            {"label": label, "value": value}
            for label, value in evolved_dna.get("traits", evolved_dna.get("stats", {})).items()
        ],
        "performance_graph": graph,
        "shareable_card": {
            "title": "FootballVerse Match Report",
            "headline": f"{player.name} is {evolution_label}",
            "rating": round((accuracy + sum(evolved_dna.get("traits", {}).values()) / 4) / 2)
            if evolved_dna.get("traits")
            else accuracy,
        },
        "match_story": commentary_provider.generate_match_story(
            "Penalty Session",
            attempts,
            evolved_dna,
        ),
    }


def _serialize_attempt(attempt: models.PenaltyAttempt) -> Dict[str, Any]:
    return {
        "id": attempt.id,
        "gesture": attempt.gesture_used,
        "shot_type": attempt.shot_type,
        "shot_target": attempt.shot_target,
        "result": attempt.result,
        "keeper_guess": attempt.keeper_guess,
        "reaction_time": attempt.reaction_time,
        "power": attempt.power,
        "curve": attempt.curve,
        "confidence_score": attempt.confidence_score,
        "commentary": "",
        "timestamp": (attempt.timestamp or _now()).isoformat(),
    }


def _serialize_penalty_session(session: models.PenaltySession) -> Dict[str, Any]:
    attempts = sorted(session.attempts, key=lambda attempt: attempt.id)
    return {
        "session_id": session.id,
        "match_session_id": session.match_session_id,
        "player_id": session.player_id,
        "challenge": session.current_challenge,
        "status": "completed" if session.completed_at else "active",
        "started_at": (session.started_at or _now()).isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "goals": session.goals,
        "accuracy": session.accuracy,
        "average_reaction_time": session.average_reaction_time,
        "dna_after": _json_loads(session.dna_after_json, {}),
        "attempts": [_serialize_attempt(attempt) for attempt in attempts],
    }


def _serialize_coach_session(session: models.CoachSession) -> Dict[str, Any]:
    return {
        "session_id": session.id,
        "match_session_id": session.match_session_id,
        "player_id": session.player_id,
        "coach_style": session.coach_style,
        "scenario": _json_loads(session.scenario_json, {}),
        "tactics": _json_loads(session.tactics_json, {}),
        "result": _json_loads(session.result_json, {}),
        "tactical_rating": session.tactical_rating,
        "ranking": session.final_rating,
        "created_at": (session.created_at or _now()).isoformat(),
    }


def _latest_reports(player: models.Player, limit: int) -> List[Dict[str, Any]]:
    sessions = sorted(player.match_sessions, key=lambda session: session.started_at or _now(), reverse=True)
    reports: List[Dict[str, Any]] = []
    for session in sessions[:limit]:
        reports.append(
            {
                "match_session_id": session.id,
                "mode": session.mode,
                "status": session.status,
                "started_at": (session.started_at or _now()).isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "summary": _json_loads(session.summary_json, {}),
            }
        )
    return reports


@app.get("/")
def read_root():
    return {"status": "ok", "message": "FootballVerse AI API is running"}


@app.get("/api/v3/identity/config")
def identity_config():
    return face_matcher.status()


@app.get("/api/v3/users/{player_id}")
def get_user_profile(player_id: str, db: Session = Depends(database.get_db)):
    player = db.get(models.Player, _validate_player_id(player_id))
    if player is None:
        raise HTTPException(status_code=404, detail="User profile not found.")
    return {"user": _profile_response(player)}


@app.get("/api/v3/users/{player_id}/history")
def get_user_history(player_id: str, limit: int = Query(default=10, ge=1, le=25), db: Session = Depends(database.get_db)):
    player = db.get(models.Player, _validate_player_id(player_id))
    if player is None:
        raise HTTPException(status_code=404, detail="User profile not found.")
    penalty_sessions = sorted(player.penalty_sessions, key=lambda session: session.started_at or _now(), reverse=True)
    coach_sessions = sorted(player.coach_sessions, key=lambda session: session.created_at or _now(), reverse=True)
    return {
        "user": _profile_response(player),
        "dna": _json_loads(player.football_dna_json, {}),
        "session_history": _json_loads(player.session_history_json, []),
        "penalty_sessions": [_serialize_penalty_session(session) for session in penalty_sessions[:limit]],
        "coach_sessions": [_serialize_coach_session(session) for session in coach_sessions[:limit]],
        "reports": _latest_reports(player, limit),
    }


@app.get("/api/v3/game/session/{session_id}")
def get_penalty_session(session_id: int, user_id: str = Query(...), db: Session = Depends(database.get_db)):
    valid_user_id = _validate_player_id(user_id)
    session = _get_player_penalty_session(db, session_id, valid_user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Penalty session not found.")
    return _serialize_penalty_session(session)


@app.post("/players/", response_model=schemas.PlayerResponse)
def check_in_player(payload: schemas.PlayerCreate, db: Session = Depends(database.get_db)):
    player = _get_or_create_player(db, schemas.validate_user_id(payload.student_id), schemas.validate_display_name(payload.name))
    db.commit()
    db.refresh(player)
    return player


@app.post("/dna/", response_model=schemas.DNAResponse)
def save_dna(player_id: str, payload: schemas.DNACreate, db: Session = Depends(database.get_db)):
    valid_player_id = _validate_player_id(player_id)
    player = _get_or_create_player(db, valid_player_id, valid_player_id)
    dna = db.get(models.FootballDNA, player.id)
    if dna is None:
        dna = models.FootballDNA(player_id=player.id)
        db.add(dna)
    dna.footballer_match = payload.footballer_match
    dna.strengths = payload.strengths
    dna.weaknesses = payload.weaknesses
    dna.profile_json = payload.profile_json
    player.football_dna_json = payload.profile_json
    db.commit()
    db.refresh(dna)
    return dna


@app.get("/dna/{player_id}", response_model=schemas.DNAResponse)
def get_dna(player_id: str, db: Session = Depends(database.get_db)):
    dna = db.get(models.FootballDNA, _validate_player_id(player_id))
    if dna is None:
        raise HTTPException(status_code=404, detail="DNA profile not found")
    return dna


@app.websocket("/ws/video")
async def video_websocket(websocket: WebSocket):
    await websocket.accept()
    initial_status = cv_recognizer.status()
    await websocket.send_json({
        "type": "VISION_STATUS",
        **initial_status,
    })
    reported_unavailable = not initial_status.get("available")
    try:
        while True:
            data = await websocket.receive_bytes()
            result = cv_recognizer.process_frame(data)

            # Always send pointer tracking data when available
            pointer = result.get("pointer")
            debug = result.get("debug")
            if pointer:
                await websocket.send_json({
                    "type": "POINTER_UPDATE",
                    "pointer": pointer,
                    "debug": debug,
                })

            if result.get("gesture"):
                await websocket.send_json({
                    "type": "GESTURE_DETECTED",
                    "gesture": result["gesture"],
                    "confidence": result.get("confidence", 0.0),
                    "power": result.get("power", 0.0),
                    "curve": result.get("curve", 0.0),
                    "pointer": pointer,
                    "debug": debug,
                })
            elif result.get("status") in {"cv_disabled", "cv_unavailable"} and not reported_unavailable:
                await websocket.send_json({
                    "type": "VISION_STATUS",
                    "available": False,
                    "status": result["status"],
                    "detail": result.get("detail", "Gesture recognition is unavailable."),
                })
                reported_unavailable = True
    except WebSocketDisconnect:
        print("Client disconnected from video feed")


@app.post("/api/v3/auth/login")
def login(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    name = _name_from(payload)
    player = _get_or_create_player(db, player_id, name)
    _log_event(db, player.id, "LOGIN_SUCCESS", {"name": player.name})
    db.commit()
    db.refresh(player)
    return {"created": True, "user": _profile_response(player)}


@app.post("/api/v3/dna/init")
def initialize_dna(answers: Dict[str, Any], db: Session = Depends(database.get_db)):
    profile = dna_engine.generate_initial_score(answers or {})
    player_id = answers.get("player_id") or answers.get("user_id")
    if player_id:
        player = _get_or_create_player(
            db,
            _player_id_from({"user_id": player_id}),
            _name_from(answers, default=str(player_id)),
        )
        _upsert_dna(db, player, profile)
        _log_event(db, player.id, "DNA_UPDATED", profile)
        db.commit()
    return profile


@app.post("/api/v3/identity/scan")
def scan_identity(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    answers = payload.get("answers") or {}
    if "playstyle" not in answers:
        answers["playstyle"] = payload.get("playstyle", "Playmaker")
    profile = dna_engine.generate_initial_score(answers)
    scan_result = face_matcher.match(payload, profile)
    if scan_result.get("status") == "deepface_confirmed" and scan_result.get("primary_match") in dna_engine.profiles:
        profile = dna_engine.profile_for_match(
            profile.get("stats", {}),
            scan_result["primary_match"],
            int(scan_result.get("confidence_score", profile.get("confidence_score", 0))),
            profile.get("percentages", {}),
        )
    profile["confidence_score"] = int(scan_result.get("confidence_score", profile.get("confidence_score", 0)))
    profile["confidence_status"] = "confirmed" if profile["confidence_score"] >= 60 else "provisional"
    profile["scan"] = scan_result
    profile["identity_basis"] = scan_result.get("identity_basis", profile.get("identity_basis"))
    _upsert_dna(db, player, profile)
    _append_session_history(player, {"mode": "Player", "event": "Identity Scan", "match": profile["name_match"]})
    _log_event(db, player.id, "DNA_UPDATED", profile)
    db.commit()
    db.refresh(player)
    return {"user": _profile_response(player), "dna": profile}


@app.post("/api/v3/game/session/start")
def start_penalty_session(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    match = models.MatchSession(player_id=player.id, mode="Player", status="active", started_at=_now())
    db.add(match)
    db.flush()
    session = models.PenaltySession(
        player_id=player.id,
        match_session_id=match.id,
        current_challenge="5 Penalty Shots",
        started_at=_now(),
    )
    db.add(session)
    db.flush()
    _log_event(db, player.id, "MATCH_STARTED", {"mode": "Player"}, "penalty", session.id)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, "match_session_id": match.id, "challenge": session.current_challenge}


@app.post("/api/v3/game/shot")
def execute_shot(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    session_id = _optional_int(payload.get("session_id"), "session_id")
    session = _get_player_penalty_session(db, session_id, player.id)
    if session and session.completed_at:
        raise HTTPException(status_code=409, detail="Penalty session is already completed.")
    if session and len(session.attempts) >= 5:
        raise HTTPException(status_code=409, detail="Penalty session already has five attempts.")
    if session is None:
        match = models.MatchSession(player_id=player.id, mode="Player", status="active", started_at=_now())
        db.add(match)
        db.flush()
        session = models.PenaltySession(
            player_id=player.id,
            match_session_id=match.id,
            current_challenge="5 Penalty Shots",
            started_at=_now(),
        )
        db.add(session)
        db.flush()

    gesture = str(payload.get("gesture") or "Point Left")
    shot = _gesture_to_shot(gesture)
    db_history = [attempt.shot_target for attempt in session.attempts if attempt.shot_target]
    previous_targets = _normalize_history(payload.get("history", [])) or db_history
    power = float(payload.get("power", 0.5))
    curve = float(payload.get("curve", 0.0))
    difficulty = str(payload.get("difficulty", "Hard"))
    result = penalty_engine.play_shot(
        player.id,
        gesture,
        shot["target"],
        previous_targets,
        difficulty,
        power,
        curve,
    )
    result["shot_type"] = shot["shot_type"]
    result["score_state"] = f"{sum(1 for attempt in session.attempts if attempt.result == 'Goal')}/{len(session.attempts)}"

    history_for_commentary = [
        {"result": attempt.result, "shot_type": attempt.shot_type}
        for attempt in session.attempts
    ]
    style = str(payload.get("commentary_style") or "Professional")
    commentary = commentary_provider.generate_shot_commentary(result, style, history_for_commentary)

    attempt = models.PenaltyAttempt(
        session_id=session.id,
        player_id=player.id,
        challenge_type=shot["shot_type"],
        gesture_used=gesture,
        shot_type=shot["shot_type"],
        shot_target=shot["target"],
        keeper_guess=result["keeper_guess"],
        power=power,
        curve=curve,
        confidence_score=float(payload.get("confidence", 1.0)),
        reaction_time=float(result.get("reaction_time", 0.72)),
        result=result["result"],
        timestamp=_now(),
    )
    db.add(attempt)
    db.add(
        models.CommentaryLog(
            session_id=session.id,
            style=style,
            commentary_text=commentary,
            event_type="SHOT_EXECUTED",
            payload_json=_json_dumps(result),
            timestamp=_now(),
        )
    )
    _log_event(db, player.id, "GESTURE_DETECTED", {"gesture": gesture}, "penalty", session.id)
    _log_event(db, player.id, "SHOT_EXECUTED", result, "penalty", session.id)
    if result["result"] == "Goal":
        _log_event(db, player.id, "GOAL_SCORED", result, "penalty", session.id)
    elif result["result"] == "Saved":
        _log_event(db, player.id, "SAVE_MADE", result, "penalty", session.id)
    else:
        _log_event(db, player.id, "SHOT_MISSED", result, "penalty", session.id)
    db.commit()
    db.refresh(attempt)

    terminal_event = "GOAL_SCORED" if result["result"] == "Goal" else "SAVE_MADE" if result["result"] == "Saved" else "SHOT_MISSED"
    return {
        "session_id": session.id,
        "attempt_id": attempt.id,
        "shot_result": result,
        "commentary": commentary,
        "events": ["GESTURE_DETECTED", "SHOT_EXECUTED", terminal_event],
    }


@app.post("/api/v3/game/session/complete")
def complete_penalty_session(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    session_id = _optional_int(payload.get("session_id"), "session_id")
    session = _get_player_penalty_session(db, session_id, player.id)
    if session:
        attempts = [
            {
                "result": attempt.result,
                "shot_type": attempt.shot_type,
                "shot_target": attempt.shot_target,
                "gesture": attempt.gesture_used,
                "reaction_time": attempt.reaction_time,
            }
            for attempt in session.attempts
        ]
    else:
        attempts = payload.get("attempts", [])

    current_dna = payload.get("dna_profile") or _json_loads(player.football_dna_json, {})
    if not current_dna:
        current_dna = dna_engine.generate_initial_score({"playstyle": "Playmaker"})
    evolution_events = _events_from_attempts(attempts)
    evolved_dna = dna_engine.evolve_dna(current_dna.get("stats", {}), evolution_events)
    report = _build_report(player, session.id if session else None, attempts, current_dna, evolved_dna)

    if session:
        session.completed_at = _now()
        session.goals = int(report["goals"])
        session.accuracy = float(report["accuracy"])
        session.average_reaction_time = float(report["reaction_time"])
        session.dna_after_json = _json_dumps(evolved_dna)
        if session.match_session_id:
            match = db.get(models.MatchSession, session.match_session_id)
            if match:
                match.status = "completed"
                match.completed_at = _now()
                match.summary_json = _json_dumps(report)

    db.add(
        models.FootballDNAEvolution(
            player_id=player.id,
            previous_match=current_dna.get("primary_match", "Unknown"),
            evolved_match=evolved_dna.get("primary_match", "Unknown"),
            reason=report["evolution"],
            profile_json=_json_dumps(evolved_dna),
            created_at=_now(),
        )
    )
    _upsert_dna(db, player, evolved_dna)
    _append_session_history(player, {"mode": "Player", "event": "Match Completed", "score": report["score"]})
    _log_event(db, player.id, "DNA_UPDATED", evolved_dna, "penalty", session.id if session else None)
    _log_event(db, player.id, "MATCH_COMPLETED", report, "penalty", session.id if session else None)
    player_score = (int(report["goals"]) * 100) + int(report["accuracy"])
    _upsert_leaderboard(db, player.id, "Player", player_score, str(report.get("player_type") or "Penalty Player"))
    db.commit()
    return report


@app.post("/api/v3/coach/scenario")
def get_scenario(payload: Dict[str, Any] = Body(default_factory=dict)):
    segment = payload.get("segment", "0-15")
    current_score = payload.get("current_score", "0-0")
    scenario = tactical_gen.generate_segment_scenario(segment, current_score)
    scenario["coach_style"] = payload.get("coach_style", "Pep Guardiola")
    return scenario


@app.post("/api/v3/coach/simulate_segment")
def simulate_segment(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    scenario = payload.get("scenario") or tactical_gen.generate_segment_scenario("0-15", "0-0")
    tactics = payload.get("tactics") or {}
    dna = payload.get("dna") or _json_loads(player.football_dna_json, {}).get("stats", {})
    
    result = match_sim.simulate_segment(scenario, tactics, dna or {})
    return result

@app.post("/api/v3/coach/complete")
def complete_coach_match(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    
    final_score = payload.get("final_score", "0-0")
    total_points = payload.get("total_points", 0)
    coach_style = payload.get("coach_style", "Custom")
    match_timeline = payload.get("timeline", [])
    
    match = models.MatchSession(player_id=player.id, mode="Coach", status="completed", started_at=_now(), completed_at=_now())
    db.add(match)
    db.flush()
    
    manager_title = _title_for_leaderboard("Coach", int(total_points))
    result_json = {
        "final_score": final_score,
        "total_points": total_points,
        "timeline": match_timeline,
        "manager_title": manager_title,
    }
    
    coach_session = models.CoachSession(
        player_id=player.id,
        match_session_id=match.id,
        coach_style=coach_style,
        result_json=_json_dumps(result_json),
        tactical_rating=total_points,
        final_rating=manager_title,
        created_at=_now(),
    )
    db.add(coach_session)
    db.flush()
    
    match.summary_json = _json_dumps(result_json)
    _append_session_history(player, {"mode": "Coach", "event": "Match Completed", "score": total_points})
    _log_event(db, player.id, "MATCH_COMPLETED", result_json, "coach", coach_session.id)
    _upsert_leaderboard(db, player.id, "Coach", total_points, manager_title)
    db.commit()
    
    return {"session_id": coach_session.id, "status": "success", "manager_title": manager_title}

@app.get("/api/v3/leaderboard/{mode}")
def get_leaderboard(mode: str, db: Session = Depends(database.get_db)):
    mode_cap = mode.capitalize()
    if mode_cap not in {"Player", "Coach", "Fan"}:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    entries = db.query(models.Leaderboard).filter_by(mode=mode_cap).order_by(models.Leaderboard.total_score.desc()).limit(100).all()
    
    result = []
    for entry in entries:
        player = db.get(models.Player, entry.player_id)
        result.append({
            "player_id": entry.player_id,
            "name": player.name if player else "Unknown",
            "score": entry.total_score,
            "rank": entry.rank,
            "title": entry.mode_title or _title_for_leaderboard(mode_cap, entry.total_score or 0),
        })
    return result

@app.post("/api/v3/fan/start")
def start_fan_game():
    return fan_mode.start_fan_game()

@app.post("/api/v3/fan/complete")
def complete_fan_match(payload: Dict[str, Any], db: Session = Depends(database.get_db)):
    player_id = _player_id_from(payload)
    player = _get_or_create_player(db, player_id, _name_from(payload))
    
    try:
        total_points = int(payload.get("total_points", 0))
        completion_time = int(payload.get("completion_time", 120))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Fan score and completion time must be integers.") from exc
    if not 0 <= total_points <= 40:
        raise HTTPException(status_code=422, detail="Fan score must be between 0 and 40.")
    if not 0 <= completion_time <= 120:
        raise HTTPException(status_code=422, detail="Fan completion time must be between 0 and 120 seconds.")
    title = str(payload.get("title") or _title_for_leaderboard("Fan", total_points))
    
    _append_session_history(player, {"mode": "Fan", "event": "Match Completed", "score": total_points, "title": title})
    _log_event(db, player.id, "MATCH_COMPLETED", {"total_points": total_points, "time": completion_time}, "fan", None)
    
    _upsert_leaderboard(db, player.id, "Fan", total_points, title)
    db.commit()
    
    return {"status": "success", "title": title}
