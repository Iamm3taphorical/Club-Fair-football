import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { api } from './api';
import { initAudio, isMuted, playUiClick, setMuted as setGlobalMuted } from './audio';
import CoachMode from './components/CoachMode';
import FanMode from './components/FanMode';
import FinalReport from './components/FinalReport';
import IdentityScan from './components/IdentityScan';
import PenaltyGame from './components/PenaltyGame';
import Leaderboards from './components/Leaderboards';
import type { CoachResult, DNAProfile, PlayerReport, UserProfile } from './types';
import './App.css';
import bracuLogo from './components/bracu_logo_12-0-2022.png';
import buccLogo from './components/bucc_logoo.png';

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
  const [muted, setMuted] = useState(isMuted);

  useEffect(() => {
    if (user) window.localStorage.setItem('fv_user', JSON.stringify(user));
  }, [user]);

  useEffect(() => {
    if (!dna && isDNAProfile(user?.dna)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
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

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      const target = event.target;
      if (target instanceof Element && target.closest('button')) {
        initAudio();
        playUiClick();
      }
    };
    const handleMute = (event: Event) => setMuted(Boolean((event as CustomEvent<boolean>).detail));
    document.addEventListener('click', handleClick, true);
    window.addEventListener('fv-audio-muted', handleMute);
    return () => {
      document.removeEventListener('click', handleClick, true);
      window.removeEventListener('fv-audio-muted', handleMute);
    };
  }, []);

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
        <button
          className="global-mute"
          type="button"
          aria-pressed={muted}
          onClick={() => setGlobalMuted(!muted)}
        >
          {muted ? 'Audio Off' : 'Audio On'}
        </button>
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
          <Route path="/fan" element={<RequireUser user={user}><FanMode user={user} /></RequireUser>} />
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
          <Route path="/leaderboards" element={<Leaderboards user={user} />} />
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
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  if (showSplash) {
    return (
      <main className="mode-screen splash-screen relative">
        <div className="splash-logos">
          <img src={bracuLogo} alt="BRAC University" className="splash-logo" />
          <div className="splash-divider" />
          <img src={buccLogo} alt="BUCC" className="splash-logo" />
        </div>
        <div className="splash-ball-container">
          <div className="splash-ball">⚽</div>
          <div className="splash-trail"></div>
        </div>
        <h1 className="splash-text">GET READY</h1>
        <div className="splash-footer">
          <p>MADE WITH ENTHUSIASM BY BUCC HR</p>
        </div>
      </main>
    );
  }

  return (
    <main className="mode-screen">
      <header className="screen-header">
        <span className="broadcast-kicker">Tunnel Selection</span>
        <h2>{(user?.name ?? 'FootballVerse Player').toUpperCase()}, ARE YOU A</h2>
      </header>

      <section className="mode-triangle">
        <div className="mode-row top-row">
          <button className="mode-card player-card" type="button" onClick={() => navigate('/scan')}>
            <span>PLAYER</span>
            <strong>Identity scan and penalty arena</strong>
          </button>
          <button className="mode-card coach-card" type="button" onClick={() => navigate('/coach')}>
            <span>COACH</span>
            <strong>Tactical board and match simulation</strong>
          </button>
        </div>
        <div className="mode-row bottom-row">
          <button className="mode-card fan-card" type="button" onClick={() => navigate('/fan')}>
            <span>FAN</span>
            <strong>2-Min Trivia: Player, Coach, Stadium, Match</strong>
          </button>
        </div>
      </section>

      <section style={{ marginTop: '3rem', display: 'flex', justifyContent: 'center' }}>
        <button className="secondary-action" type="button" onClick={() => navigate('/leaderboards')} style={{ padding: '1rem 3rem', fontSize: '1.1rem' }}>
          🏆 View Global Leaderboards
        </button>
      </section>
    </main>
  );
}
