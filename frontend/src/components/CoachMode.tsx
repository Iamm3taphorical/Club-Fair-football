import { useEffect, useRef, useState } from 'react';
import type { PointerEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { CoachResult, CoachScenario, CoachTactics, DNAProfile, UserProfile } from '../types';

const COACH_STYLES = ['Pep Guardiola', 'Klopp', 'Mourinho', 'Ancelotti', 'Custom'];
const ROLE_OPTIONS: Record<string, string[]> = {
  ST: ['False 9', 'Target Forward', 'Poacher', 'Pressing Forward'],
  DM: ['Anchor', 'Deep Playmaker', 'Ball Winner', 'Half Back'],
  LW: ['Inside Forward', 'Wide Creator', 'Touchline Winger', 'Inverted Winger'],
  RW: ['Wide Creator', 'Inside Forward', 'Touchline Winger', 'Inverted Winger'],
};

const INITIAL_POSITIONS = [
  { id: 1, label: 'GK', x: 50, y: 88 },
  { id: 2, label: 'LB', x: 20, y: 68 },
  { id: 3, label: 'CB', x: 42, y: 70 },
  { id: 4, label: 'CB', x: 58, y: 70 },
  { id: 5, label: 'RB', x: 80, y: 68 },
  { id: 6, label: 'DM', x: 50, y: 55 },
  { id: 7, label: 'LW', x: 22, y: 34 },
  { id: 8, label: 'CM', x: 43, y: 42 },
  { id: 9, label: 'CM', x: 57, y: 42 },
  { id: 10, label: 'RW', x: 78, y: 34 },
  { id: 11, label: 'ST', x: 50, y: 20 },
];

export default function CoachMode({
  user,
  dna,
  setCoachResult,
}: {
  user: UserProfile | null;
  dna: DNAProfile | null;
  setCoachResult: (result: CoachResult) => void;
}) {
  const navigate = useNavigate();
  const pitchRef = useRef<HTMLDivElement>(null);
  const [coachStyle, setCoachStyle] = useState('Pep Guardiola');
  const [scenario, setScenario] = useState<CoachScenario | null>(null);
  const [result, setResult] = useState<CoachResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [tactics, setTactics] = useState<CoachTactics>({
    coach_style: 'Pep Guardiola',
    formation: '4-2-3-1',
    attack: 76,
    defense: 58,
    possession: 72,
    pressure: 68,
    width: 66,
    roles: { ST: 'False 9', DM: 'Anchor', LW: 'Inside Forward', RW: 'Wide Creator' },
    player_positions: INITIAL_POSITIONS,
  });

  useEffect(() => {
    setTactics((current) => ({ ...current, coach_style: coachStyle }));
    api.getCoachScenario({ coach_style: coachStyle })
      .then(setScenario)
      .catch(() => setScenario({
        minute: 83,
        current_score: '1-2',
        opponent_formation: '4-4-2',
        opponent_strategy: 'Defensive Block',
        objective: 'Equalize',
        pressure_level: 'High',
        coach_style: coachStyle,
      }));
  }, [coachStyle]);

  const updateNumber = (key: keyof Pick<CoachTactics, 'attack' | 'defense' | 'possession' | 'pressure' | 'width'>, value: string) => {
    setTactics((current) => ({ ...current, [key]: Number(value) }));
  };

  const updateRole = (role: string, assignment: string) => {
    setTactics((current) => ({
      ...current,
      roles: { ...current.roles, [role]: assignment },
    }));
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (draggingId === null || !pitchRef.current) return;
    const rect = pitchRef.current.getBoundingClientRect();
    const x = Math.max(6, Math.min(94, ((event.clientX - rect.left) / rect.width) * 100));
    const y = Math.max(8, Math.min(92, ((event.clientY - rect.top) / rect.height) * 100));
    setTactics((current) => ({
      ...current,
      player_positions: current.player_positions.map((player) => (
        player.id === draggingId ? { ...player, x, y } : player
      )),
    }));
  };

  const handleSimulate = async () => {
    if (!scenario || simulating) return;
    setSimulating(true);
    try {
      const response = await api.simulateCoach({
        user_id: user?.user_id ?? 'guest',
        name: user?.name ?? 'FootballVerse Player',
        coach_style: coachStyle,
        scenario,
        tactics,
        dna: dna?.stats,
      });
      setResult(response);
      setCoachResult(response);
    } catch {
      const fallback = buildFallbackResult(scenario, tactics);
      setResult(fallback);
      setCoachResult(fallback);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <main className="coach-screen">
      <header className="screen-header compact">
        <span className="broadcast-kicker">Coach Mode</span>
        <h2>Tactical Crisis</h2>
      </header>

      <section className="coach-grid">
        <aside className="coach-controls">
          <label>
            <span>Coach Identity</span>
            <select value={coachStyle} onChange={(event) => setCoachStyle(event.target.value)}>
              {COACH_STYLES.map((style) => <option key={style}>{style}</option>)}
            </select>
          </label>

          {scenario ? (
            <div className="scenario-card">
              <span>{scenario.minute}' Minute</span>
              <strong>{scenario.current_score}</strong>
              <p>{scenario.objective} against {scenario.opponent_strategy}</p>
              <small>{scenario.opponent_formation} | {scenario.pressure_level} pressure</small>
            </div>
          ) : null}

          <label>
            <span>Formation</span>
            <select value={tactics.formation} onChange={(event) => setTactics((current) => ({ ...current, formation: event.target.value }))}>
              {['4-2-3-1', '4-3-3', '3-4-3', '3-5-2', '5-3-2'].map((formation) => <option key={formation}>{formation}</option>)}
            </select>
          </label>

          <TacticSlider label="Attack" value={tactics.attack} onChange={(value) => updateNumber('attack', value)} />
          <TacticSlider label="Defense" value={tactics.defense} onChange={(value) => updateNumber('defense', value)} />
          <TacticSlider label="Possession" value={tactics.possession} onChange={(value) => updateNumber('possession', value)} />
          <TacticSlider label="Pressure" value={tactics.pressure} onChange={(value) => updateNumber('pressure', value)} />
          <TacticSlider label="Width" value={tactics.width} onChange={(value) => updateNumber('width', value)} />

          <button className="primary-action" type="button" onClick={() => void handleSimulate()} disabled={simulating}>
            {simulating ? 'Simulating Timeline' : 'Simulate Match'}
          </button>
        </aside>

        <section className="formation-area">
          <div
            className="tactical-pitch"
            ref={pitchRef}
            onPointerMove={handlePointerMove}
            onPointerUp={() => setDraggingId(null)}
            onPointerLeave={() => setDraggingId(null)}
          >
            <div className="pitch-lines" />
            {tactics.player_positions.map((player) => (
              <button
                className="player-token"
                key={player.id}
                style={{ left: `${player.x}%`, top: `${player.y}%` }}
                type="button"
                onPointerDown={(event) => {
                  event.currentTarget.setPointerCapture(event.pointerId);
                  setDraggingId(player.id);
                }}
              >
                {player.label}
              </button>
            ))}
          </div>
          <div className="role-row">
            {Object.entries(tactics.roles).map(([role, assignment]) => (
              <label key={role}>
                <span>{role}</span>
                <select value={assignment} onChange={(event) => updateRole(role, event.target.value)}>
                  {(ROLE_OPTIONS[role] ?? [assignment]).map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </select>
              </label>
            ))}
          </div>
        </section>

        {result ? (
          <section className="coach-result">
            <div className="rating-disc">
              <span>{result.tactical_rating}</span>
              <strong>{result.ranking}</strong>
            </div>
            <div>
              <span className="panel-label">Final Score</span>
              <h3>{result.final_score}</h3>
              <p>{result.explanation}</p>
              <strong>{result.key_event}</strong>
            </div>
            <ul>
              {result.timeline.map((event) => <li key={event}>{event}</li>)}
            </ul>
            <button className="secondary-action" type="button" onClick={() => navigate('/report')}>
              Open Report
            </button>
          </section>
        ) : null}
      </section>
    </main>
  );
}

function TacticSlider({ label, value, onChange }: { label: string; value: number; onChange: (value: string) => void }) {
  return (
    <label>
      <span>{label} {value}</span>
      <input min="0" max="100" type="range" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function buildFallbackResult(scenario: CoachScenario, tactics: CoachTactics): CoachResult {
  const rating = Math.max(45, Math.min(96, Math.round((tactics.attack * 0.32) + (tactics.defense * 0.22) + (tactics.possession * 0.24) + (tactics.pressure * 0.12) + 8)));
  const equalized = rating > 76;
  return {
    final_score: equalized ? '2-2' : scenario.current_score,
    timeline: equalized
      ? [`${scenario.minute + 3}' Width overload forces a corner.`, `${Math.min(90, scenario.minute + 6)}' Equalizer from the second phase.`]
      : [`${scenario.minute + 4}' Pressure rises but the block survives.`, `${Math.min(90, scenario.minute + 7)}' Final pass is intercepted.`],
    explanation: equalized
      ? 'The wide structure stretched the defensive line and created a late second-ball chance.'
      : 'The idea had control, but the tempo was not high enough to break the defensive block.',
    key_event: equalized ? `${Math.min(90, scenario.minute + 6)}' Equalizer` : `${Math.min(90, scenario.minute + 7)}' Interception`,
    tactical_rating: rating,
    ranking: rating >= 90 ? 'Football Genius' : rating >= 78 ? 'Elite Manager' : rating >= 62 ? 'Tactical Analyst' : 'Sunday League Coach',
    chance_creation: equalized ? 3 : 1,
    possession_changes: [`${scenario.minute + 2}' regained`, `${scenario.minute + 5}' recycled`],
    scores: {
      attack: tactics.attack,
      defense: tactics.defense,
      possession: tactics.possession,
      creativity: Math.round((tactics.attack + tactics.width) / 2),
    },
  };
}
