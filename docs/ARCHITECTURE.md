# Architecture

FootballVerse AI currently has two runnable layers:

- Primary V3 product: React + FastAPI.
- Legacy MVP/demo: Streamlit + shared `modules/`.

## Primary V3 Flow

```text
Browser
  -> React / Vite frontend
     -> REST API calls for auth, DNA, penalty sessions, coach simulation
     -> WebSocket video stream for gesture detection
  -> FastAPI backend
     -> Football DNA engine
     -> MediaPipe gesture adapter
     -> Penalty game engine
     -> Commentary provider
     -> Coach scenario and simulation engines
  -> SQLite database
```

## Frontend

Location: `frontend/`

Key screens:

- `src/App.tsx`: routing, login/register, mode selection, persistent local state.
- `src/components/IdentityScan.tsx`: webcam scan flow, football identity reveal, DNA card.
- `src/components/PenaltyGame.tsx`: split-screen gesture feed, stadium penalty loop, generated audio cues, and active-session resume.
- `src/components/CoachMode.tsx`: coach identity, tactical scenario, custom pointer-drag formation board, simulation.
- `src/components/FinalReport.tsx`: player report, radar chart, performance graph, share/export card, coach classification.

The frontend falls back to local deterministic gameplay/report generation if the backend is unavailable, which keeps demos usable. Protected player, coach, and report routes require an authenticated local profile.

## Backend

Location: `backend/`

Key modules:

- `main.py`: FastAPI routes and event logging.
- `database.py`: SQLite engine, WAL mode, session dependency.
- `models.py`: persistent tables for players, DNA, DNA evolution, match sessions, penalty attempts, coach sessions, coaching decisions, commentary logs, event logs, and leaderboard entries.
- `cv_engine.py`: MediaPipe Tasks hand gesture recognizer with `FOOTBALLVERSE_DISABLE_CV=1` opt-out.
- `dna_engine.py`: V3 DNA scoring and evolution engine.
- `game_logic.py`: adaptive AI goalkeeper and penalty shot resolution.
- `coach_mode.py`: tactical scenario and simulation logic.
- `llm_provider.py`: commentary provider interface and current mock/Ollama adapter.
- `face_identity.py`: optional DeepFace/Kaggle embedding-index adapter with explicit fallback metadata.

Read endpoints support profile/history and penalty-session resume:

- `GET /api/v3/users/{player_id}`
- `GET /api/v3/users/{player_id}/history`
- `GET /api/v3/game/session/{session_id}?user_id=...`
- `GET /api/v3/identity/config`

## Legacy MVP

Location: `app.py`, `modules/`

The Streamlit MVP is still valuable for:

- quick single-process demos,
- legacy regression tests,
- reusable football logic modules,
- leaderboard/prize tier behavior.

It should not be treated as the product architecture target.

## Known Architecture Gaps

- A Kaggle face embedding index still needs to be generated before real DeepFace matching can be confirmed in normal demos.
- Coach board uses a custom pointer-drag pitch, not Konva. This is the current supported implementation unless the product explicitly needs Konva.
- Share/export currently emits text through Web Share or clipboard, not an image export.
