import type {
  CoachScenario,
  CoachTactics,
  DNAProfile,
  PenaltyAttempt,
  PenaltySessionSnapshot,
  PlayerReport,
  UserProfile,
} from './types';

export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export function apiWebSocketUrl(path: string) {
  const url = new URL(API_BASE, window.location.origin);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  url.pathname = path.startsWith('/') ? path : `/${path}`;
  url.search = '';
  url.hash = '';
  return url.toString();
}

async function postJSON<T>(path: string, payload: unknown, timeoutMs = 3800): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    return await response.json() as T;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function getJSON<T>(path: string, timeoutMs = 3800): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'GET',
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    return await response.json() as T;
  } finally {
    window.clearTimeout(timeout);
  }
}

export const api = {
  login(payload: { user_id: string; name: string }) {
    return postJSON<{ user: UserProfile }>('/api/v3/auth/login', payload);
  },

  getLeaderboard(mode: 'Player' | 'Coach' | 'Fan') {
    return getJSON<Array<{ player_id: string; name: string; score: number; rank: string; title: string }>>(`/api/v3/leaderboard/${mode}`);
  },

  getUserHistory(userId: string) {
    return getJSON<{
      user: UserProfile;
      dna: DNAProfile | Record<string, never>;
      session_history: unknown[];
      penalty_sessions: PenaltySessionSnapshot[];
      reports: unknown[];
    }>(`/api/v3/users/${encodeURIComponent(userId)}/history`);
  },

  scanIdentity(payload: {
    user_id: string;
    name: string;
    answers: Record<string, string>;
    face_detected: boolean;
    face_image_base64?: string;
  }) {
    return postJSON<{ user: UserProfile; dna: DNAProfile }>('/api/v3/identity/scan', payload, 5200);
  },

  startPenaltySession(payload: { user_id: string; name: string }) {
    return postJSON<{ session_id: number; match_session_id: number; challenge: string }>('/api/v3/game/session/start', payload);
  },

  executeShot(payload: {
    user_id: string;
    name: string;
    session_id?: number;
    gesture: string;
    history: string[];
    power: number;
    curve: number;
    difficulty: string;
    commentary_style: string;
  }) {
    return postJSON<{
      session_id: number;
      attempt_id: number;
      shot_result: {
        result: 'Goal' | 'Saved' | 'Missed';
        keeper_guess: string;
        shot_target: string;
        shot_type: string;
        gesture: string;
        power_registered: number;
        curve_registered: number;
        reaction_time: number;
        adaptive_difficulty: number;
        prediction_basis: string;
      };
      commentary: string;
    }>('/api/v3/game/shot', payload);
  },

  completePenaltySession(payload: {
    user_id: string;
    name: string;
    session_id?: number;
    attempts: PenaltyAttempt[];
    dna_profile: DNAProfile;
  }) {
    return postJSON<PlayerReport>('/api/v3/game/session/complete', payload);
  },

  getPenaltySession(sessionId: number, userId: string) {
    return getJSON<PenaltySessionSnapshot>(`/api/v3/game/session/${sessionId}?user_id=${encodeURIComponent(userId)}`);
  },

  getCoachScenario(payload: { segment: string; current_score: string; coach_style: string }) {
    return postJSON<CoachScenario>('/api/v3/coach/scenario', payload);
  },

  simulateSegment(payload: {
    user_id: string;
    name: string;
    scenario: CoachScenario;
    tactics: CoachTactics;
    dna?: Record<string, number>;
  }) {
    return postJSON<{
      new_score: string;
      segment_goals_for: number;
      segment_goals_against: number;
      timeline: string[];
      stats: { passes: number; shots: number; fouls: number; offsides: number };
      segment_points: number;
    }>('/api/v3/coach/simulate_segment', payload);
  },

  completeCoachMatch(payload: {
    user_id: string;
    name: string;
    final_score: string;
    total_points: number;
    coach_style: string;
    timeline: string[];
  }) {
    return postJSON<{ session_id: number; status: string; manager_title: string }>('/api/v3/coach/complete', payload, 5200);
  },

  startFanGame() {
    return postJSON<{
      challenges: Array<{
        category: string;
        clues: string[];
        options: string[];
        answer: string;
      }>;
    }>('/api/v3/fan/start', {});
  },

  completeFanGame(payload: {
    user_id: string;
    name: string;
    total_points: number;
    completion_time: number;
    title: string;
  }) {
    return postJSON<{ status: string; title: string }>('/api/v3/fan/complete', payload);
  },
};
