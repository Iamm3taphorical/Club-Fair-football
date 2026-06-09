# FootballVerse AI Frontend

React + TypeScript + Vite frontend for the FootballVerse AI V3 experience.

## Run

```bash
cd /home/mahir/footballverse-ai/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Backend default:

```text
http://localhost:8000
```

Override it with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Build

```bash
npm run build
```

## Product Screens

- `/`: cinematic login/register.
- `/mode`: Player vs Coach tunnel selection.
- `/scan`: webcam identity scan and DNA reveal.
- `/play`: gesture-controlled penalty session.
- `/coach`: tactical coach mode.
- `/report`: player/coach match report.

If the backend is unavailable, core demo flows use local fallback data so the UI remains usable.
