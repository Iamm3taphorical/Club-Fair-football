import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { api } from './api';
import CoachMode from './components/CoachMode';
import FinalReport from './components/FinalReport';
import IdentityScan from './components/IdentityScan';
import PenaltyGame from './components/PenaltyGame';
import type { CoachResult, DNAProfile, PlayerReport, UserProfile } from './types';
import './App.css';

function readStored<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) as T : fallback;
  } catch {
    return fallback;
  }
}

function isDNAProfile(value: unknown): value is DNAProfile {
  return Boolean(value && typeof value === 'object' && 'primary_match' in value && 'stats' in value);
}

export default function App() {
  const [user, setUser] = useState<UserProfile | null>(() => readStored<UserProfile | null>('fv_user', null));
  const [dna, setDna] = useState<DNAProfile | null>(() => readStored<DNAProfile | null>('fv_dna', null));
  const [playerReport, setPlayerReport] = useState<PlayerReport | null>(() => readStored<PlayerReport | null>('fv_player_report', null));
  const [coachResult, setCoachResult] = useState<CoachResult | null>(() => readStored<CoachResult | null>('fv_coach_result', null));

  useEffect(() => {
    if (user) window.localStorage.setItem('fv_user', JSON.stringify(user));
  }, [user]);

  useEffect(() => {
    if (!dna && isDNAProfile(user?.dna)) {
      setDna(user.dna);
    }
  }, [dna, user?.dna]);

  useEffect(() => {
    if (dna) window.localStorage.setItem('fv_dna', JSON.stringify(dna));
  }, [dna]);

  useEffect(() => {
    if (playerReport) window.localStorage.setItem('fv_player_report', JSON.stringify(playerReport));
  }, [playerReport]);

  useEffect(() => {
    if (coachResult) window.localStorage.setItem('fv_coach_result', JSON.stringify(coachResult));
  }, [coachResult]);

  const resetExperience = () => {
    setUser(null);
    setDna(null);
    setPlayerReport(null);
    setCoachResult(null);
    window.localStorage.removeItem('fv_user');
    window.localStorage.removeItem('fv_dna');
    window.localStorage.removeItem('fv_player_report');
    window.localStorage.removeItem('fv_coach_result');
  };

  return (
    <BrowserRouter>
      <div className="app-shell">
        <StadiumAtmosphere />
        <Routes>
          <Route path="/" element={<Home user={user} setUser={setUser} setDna={setDna} />} />
          <Route path="/mode" element={<RequireUser user={user}><ModeSelection user={user} /></RequireUser>} />
          <Route
            path="/scan"
            element={<RequireUser user={user}><IdentityScan user={user} setUser={setUser} setDna={setDna} /></RequireUser>}
          />
          <Route
            path="/play"
            element={
              <RequireUser user={user}>
                <RequireDna dna={dna ?? (isDNAProfile(user?.dna) ? user.dna : null)}>
                  <PenaltyGame user={user} dna={dna ?? (isDNAProfile(user?.dna) ? user.dna : null)} setDna={setDna} setPlayerReport={setPlayerReport} />
                </RequireDna>
              </RequireUser>
            }
          />
          <Route path="/coach" element={<RequireUser user={user}><CoachMode user={user} dna={dna} setCoachResult={setCoachResult} /></RequireUser>} />
          <Route
            path="/report"
            element={
              <RequireUser user={user}>
                <FinalReport
                  user={user}
                  dna={dna}
                  playerReport={playerReport}
                  coachResult={coachResult}
                  resetExperience={resetExperience}
                />
              </RequireUser>
            }
          />
          <Route path="*" element={<Navigate to={user ? '/mode' : '/'} replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

function RequireUser({ user, children }: { user: UserProfile | null; children: ReactNode }) {
  if (!user) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function RequireDna({ dna, children }: { dna: DNAProfile | null; children: ReactNode }) {
  if (!dna) return <Navigate to="/scan" replace />;
  return <>{children}</>;
}

function StadiumAtmosphere() {
  return (
    <div className="stadium-atmosphere" aria-hidden="true">
      <div className="floodlight floodlight-left" />
      <div className="floodlight floodlight-right" />
      <div className="crowd-band crowd-band-one" />
      <div className="crowd-band crowd-band-two" />
      <div className="pitch-grid" />
      <div className="rain-layer" />
    </div>
  );
}

function Home({
  user,
  setUser,
  setDna,
}: {
  user: UserProfile | null;
  setUser: (user: UserProfile) => void;
  setDna: (dna: DNAProfile) => void;
}) {
  const navigate = useNavigate();
  const [stage, setStage] = useState<'start' | 'login' | 'success'>(user ? 'login' : 'start');
  const [name, setName] = useState(user?.name ?? '');
  const [userId, setUserId] = useState(user?.user_id ?? '');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim() || !userId.trim() || submitting) return;
    setSubmitting(true);
    try {
      const response = await api.login({ user_id: userId.trim(), name: name.trim() });
      setUser(response.user);
      if (isDNAProfile(response.user.dna)) setDna(response.user.dna);
    } catch {
      setUser({
        user_id: userId.trim(),
        name: name.trim(),
        timestamp: new Date().toISOString(),
        session_history: [],
        dna: {},
      });
    } finally {
      setSubmitting(false);
      setStage('success');
      window.setTimeout(() => navigate('/mode'), 1050);
    }
  };

  return (
    <main className="entry-screen">
      <section className="entry-panel">
        <div className="broadcast-kicker">Discover. Play. Coach.</div>
        <h1>FOOTBALLVERSE AI</h1>
        {stage === 'start' ? (
          <button className="primary-action entry-action" type="button" onClick={() => setStage('login')}>
            Enter FootballVerse
          </button>
        ) : null}

        {stage === 'login' ? (
          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              <span>Name</span>
              <input value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" required />
            </label>
            <label>
              <span>User ID</span>
              <input value={userId} onChange={(event) => setUserId(event.target.value)} autoComplete="username" required />
            </label>
            <button className="primary-action" type="submit" disabled={submitting}>
              {submitting ? 'Saving Profile' : 'Login / Register'}
            </button>
          </form>
        ) : null}

        {stage === 'success' ? (
          <div className="auth-success">
            <div className="success-ring" />
            <p>Authentication locked</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}

function ModeSelection({ user }: { user: UserProfile | null }) {
  const navigate = useNavigate();

  return (
    <main className="mode-screen">
      <header className="screen-header">
        <span className="broadcast-kicker">Tunnel Selection</span>
        <h2>ARE YOU A</h2>
        <p>{user?.name ?? 'FootballVerse Player'}</p>
      </header>

      <section className="mode-split">
        <button className="mode-card player-card" type="button" onClick={() => navigate('/scan')}>
          <span>PLAYER</span>
          <strong>Identity scan and penalty arena</strong>
          <div className="mode-visual attacking-lines" />
        </button>
        <button className="mode-card coach-card" type="button" onClick={() => navigate('/coach')}>
          <span>COACH</span>
          <strong>Tactical board and match simulation</strong>
          <div className="mode-visual tactics-board" />
        </button>
      </section>
    </main>
  );
}
