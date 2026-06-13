import { useEffect, useRef, useState } from 'react';
import type { PointerEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { CoachResult, CoachScenario, CoachTactics, DNAProfile, UserProfile } from '../types';

const COACH_STYLES = [
  'Pep Guardiola', 'Jurgen Klopp', 'Jose Mourinho', 'Carlo Ancelotti', 
  'Mikel Arteta', 'Diego Simeone', 'Erik ten Hag', 'Xabi Alonso', 
  'Roberto De Zerbi', 'Zinedine Zidane'
];

const SEGMENTS = ['0-15', '16-30', '31-45', 'HT', '46-60', '61-75', '76-90'];
const MATCH_SEGMENT_TOTAL = SEGMENTS.filter((segment) => segment !== 'HT').length;

const FORMATIONS: Record<string, { id: number; label: string; x: number; y: number }[]> = {
  '4-3-3': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'LCM', x: 35, y: 45 }, { id: 7, label: 'DM', x: 50, y: 55 }, { id: 8, label: 'RCM', x: 65, y: 45 },
    { id: 9, label: 'LW', x: 25, y: 25 }, { id: 10, label: 'ST', x: 50, y: 15 }, { id: 11, label: 'RW', x: 75, y: 25 },
  ],
  '4-2-3-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'LDM', x: 40, y: 55 }, { id: 7, label: 'RDM', x: 60, y: 55 },
    { id: 8, label: 'LAM', x: 25, y: 35 }, { id: 9, label: 'CAM', x: 50, y: 30 }, { id: 10, label: 'RAM', x: 75, y: 35 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
  '4-4-2': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'LM', x: 20, y: 45 }, { id: 7, label: 'CM', x: 40, y: 45 }, { id: 8, label: 'CM', x: 60, y: 45 }, { id: 9, label: 'RM', x: 80, y: 45 },
    { id: 10, label: 'ST', x: 40, y: 20 }, { id: 11, label: 'ST', x: 60, y: 20 },
  ],
  '3-5-2': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LCB', x: 30, y: 75 }, { id: 3, label: 'CB', x: 50, y: 75 }, { id: 4, label: 'RCB', x: 70, y: 75 },
    { id: 5, label: 'LWB', x: 15, y: 50 }, { id: 6, label: 'DM', x: 50, y: 55 }, { id: 7, label: 'RWB', x: 85, y: 50 },
    { id: 8, label: 'CM', x: 35, y: 40 }, { id: 9, label: 'CM', x: 65, y: 40 },
    { id: 10, label: 'ST', x: 40, y: 20 }, { id: 11, label: 'ST', x: 60, y: 20 },
  ],
  '3-4-3': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LCB', x: 30, y: 75 }, { id: 3, label: 'CB', x: 50, y: 75 }, { id: 4, label: 'RCB', x: 70, y: 75 },
    { id: 5, label: 'LM', x: 15, y: 45 }, { id: 6, label: 'CM', x: 40, y: 45 }, { id: 7, label: 'CM', x: 60, y: 45 }, { id: 8, label: 'RM', x: 85, y: 45 },
    { id: 9, label: 'LW', x: 25, y: 25 }, { id: 10, label: 'ST', x: 50, y: 15 }, { id: 11, label: 'RW', x: 75, y: 25 },
  ],
  '4-1-4-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'DM', x: 50, y: 55 },
    { id: 7, label: 'LM', x: 20, y: 40 }, { id: 8, label: 'CM', x: 40, y: 40 }, { id: 9, label: 'CM', x: 60, y: 40 }, { id: 10, label: 'RM', x: 80, y: 40 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
  '4-3-2-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'CM', x: 30, y: 50 }, { id: 7, label: 'CM', x: 50, y: 50 }, { id: 8, label: 'CM', x: 70, y: 50 },
    { id: 9, label: 'AM', x: 35, y: 30 }, { id: 10, label: 'AM', x: 65, y: 30 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
  '5-3-2': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LWB', x: 15, y: 65 }, { id: 3, label: 'LCB', x: 35, y: 75 }, { id: 4, label: 'CB', x: 50, y: 80 }, { id: 5, label: 'RCB', x: 65, y: 75 }, { id: 6, label: 'RWB', x: 85, y: 65 },
    { id: 7, label: 'CM', x: 35, y: 45 }, { id: 8, label: 'DM', x: 50, y: 55 }, { id: 9, label: 'CM', x: 65, y: 45 },
    { id: 10, label: 'ST', x: 40, y: 20 }, { id: 11, label: 'ST', x: 60, y: 20 },
  ],
  '5-4-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LWB', x: 15, y: 65 }, { id: 3, label: 'LCB', x: 35, y: 75 }, { id: 4, label: 'CB', x: 50, y: 80 }, { id: 5, label: 'RCB', x: 65, y: 75 }, { id: 6, label: 'RWB', x: 85, y: 65 },
    { id: 7, label: 'LM', x: 20, y: 45 }, { id: 8, label: 'CM', x: 40, y: 45 }, { id: 9, label: 'CM', x: 60, y: 45 }, { id: 10, label: 'RM', x: 80, y: 45 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
  '4-2-2-2': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'DM', x: 40, y: 55 }, { id: 7, label: 'DM', x: 60, y: 55 },
    { id: 8, label: 'AM', x: 25, y: 35 }, { id: 9, label: 'AM', x: 75, y: 35 },
    { id: 10, label: 'ST', x: 40, y: 20 }, { id: 11, label: 'ST', x: 60, y: 20 },
  ],
  '4-4-1-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'LM', x: 20, y: 45 }, { id: 7, label: 'CM', x: 40, y: 45 }, { id: 8, label: 'CM', x: 60, y: 45 }, { id: 9, label: 'RM', x: 80, y: 45 },
    { id: 10, label: 'CF', x: 50, y: 30 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
  '3-4-2-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LCB', x: 30, y: 75 }, { id: 3, label: 'CB', x: 50, y: 75 }, { id: 4, label: 'RCB', x: 70, y: 75 },
    { id: 5, label: 'LM', x: 15, y: 45 }, { id: 6, label: 'CM', x: 40, y: 45 }, { id: 7, label: 'CM', x: 60, y: 45 }, { id: 8, label: 'RM', x: 85, y: 45 },
    { id: 9, label: 'AM', x: 35, y: 30 }, { id: 10, label: 'AM', x: 65, y: 30 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
  '3-4-1-2': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LCB', x: 30, y: 75 }, { id: 3, label: 'CB', x: 50, y: 75 }, { id: 4, label: 'RCB', x: 70, y: 75 },
    { id: 5, label: 'LM', x: 15, y: 45 }, { id: 6, label: 'CM', x: 40, y: 45 }, { id: 7, label: 'CM', x: 60, y: 45 }, { id: 8, label: 'RM', x: 85, y: 45 },
    { id: 9, label: 'CAM', x: 50, y: 30 },
    { id: 10, label: 'ST', x: 40, y: 15 }, { id: 11, label: 'ST', x: 60, y: 15 },
  ],
  '4-1-2-1-2': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'DM', x: 50, y: 55 },
    { id: 7, label: 'CM', x: 30, y: 45 }, { id: 8, label: 'CM', x: 70, y: 45 },
    { id: 9, label: 'CAM', x: 50, y: 30 },
    { id: 10, label: 'ST', x: 40, y: 15 }, { id: 11, label: 'ST', x: 60, y: 15 },
  ],
  '4-5-1': [
    { id: 1, label: 'GK', x: 50, y: 92 },
    { id: 2, label: 'LB', x: 20, y: 70 }, { id: 3, label: 'CB', x: 40, y: 75 }, { id: 4, label: 'CB', x: 60, y: 75 }, { id: 5, label: 'RB', x: 80, y: 70 },
    { id: 6, label: 'LM', x: 20, y: 45 }, { id: 7, label: 'CM', x: 35, y: 50 }, { id: 8, label: 'CM', x: 50, y: 45 }, { id: 9, label: 'CM', x: 65, y: 50 }, { id: 10, label: 'RM', x: 80, y: 45 },
    { id: 11, label: 'ST', x: 50, y: 15 },
  ],
};

const SUB_POSITIONS = ['GK', 'DEF', 'DEF', 'MID', 'MID', 'MID', 'FWD', 'FWD', 'FWD'];
const INITIAL_ROSTER = Array.from({ length: 20 }).map((_, i) => ({
  id: i + 1,
  name: i < 11 ? `Player ${i + 1}` : `Sub ${i - 10}`,
  isStarter: i < 11,
  stamina: 100,
  position: i < 11 ? 'Starter' : SUB_POSITIONS[(i - 11) % SUB_POSITIONS.length]
}));

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
  
  // Game State
  const [segmentIndex, setSegmentIndex] = useState(0);
  const [currentScore, setCurrentScore] = useState('0-0');
  const [totalPoints, setTotalPoints] = useState(0);
  const [fullTimeline, setFullTimeline] = useState<string[]>([]);
  const [matchStats, setMatchStats] = useState({ passes: 0, shots: 0, fouls: 0, offsides: 0 });
  const [scenario, setScenario] = useState<CoachScenario | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [simulateError, setSimulateError] = useState<string | null>(null);
  const [htTimer, setHtTimer] = useState<number | null>(null);
  
  // Tactical State
  const [coachStyle, setCoachStyle] = useState('Pep Guardiola');
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [subOutId, setSubOutId] = useState('');
  const [subInId, setSubInId] = useState('');
  const [subsLeft, setSubsLeft] = useState(5);
  const [roster, setRoster] = useState(INITIAL_ROSTER);
  const [tactics, setTactics] = useState<CoachTactics>({
    coach_style: 'Pep Guardiola',
    formation: '4-3-3',
    attack: 76,
    defense: 58,
    possession: 72,
    pressure: 68,
    width: 66,
    roles: {},
    player_positions: FORMATIONS['4-3-3'],
  });

  // HT Timer
  useEffect(() => {
    if (htTimer === null) return;
    if (htTimer <= 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHtTimer(null);
      setSegmentIndex(4); // Move to 46-60
      return;
    }
    const id = window.setTimeout(() => setHtTimer(prev => (prev ? prev - 1 : null)), 1000);
    return () => window.clearTimeout(id);
  }, [htTimer]);

  // Load Scenario for Segment
  useEffect(() => {
    const segment = SEGMENTS[segmentIndex];
    if (!segment) return;
    
    if (segment === 'HT') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHtTimer(60);
      setScenario(null);
      return;
    }

    setTactics((current) => ({ ...current, coach_style: coachStyle }));
    
    api.getCoachScenario({ segment, current_score: currentScore, coach_style: coachStyle })
      .then(setScenario)
      .catch(() => setScenario({
        segment,
        current_score: currentScore,
        opponent_formation: '4-4-2',
        opponent_strategy: 'Defensive Block',
        objective: 'Win the segment',
        pressure_level: 'Medium',
        coach_style: coachStyle,
      }));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [segmentIndex, currentScore]); // Intentionally leaving out coachStyle to not re-fetch unecessarily

  const handleFormationChange = (formation: string) => {
    setTactics((current) => ({
      ...current,
      formation,
      player_positions: FORMATIONS[formation] || current.player_positions,
    }));
  };

  const updateNumber = (key: keyof Pick<CoachTactics, 'attack' | 'defense' | 'possession' | 'pressure' | 'width'>, value: string) => {
    setTactics((current) => ({ ...current, [key]: Number(value) }));
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

  const handleSub = (outId: number, inId: number) => {
    if (subsLeft <= 0) return;
    setRoster(current => current.map(p => {
      if (p.id === outId) return { ...p, isStarter: false };
      if (p.id === inId) return { ...p, isStarter: true, stamina: Math.max(p.stamina, 78) };
      return p;
    }));
    setSubOutId('');
    setSubInId('');
    setSubsLeft(prev => prev - 1);
  };

  const drainStamina = () => {
    setRoster(current => current.map(p => {
      if (p.isStarter) return { ...p, stamina: Math.max(10, p.stamina - Math.floor(Math.random() * 15 + 10)) };
      return p;
    }));
  };

  const handleSimulateSegment = async () => {
    if (!scenario || simulating) return;
    setSimulating(true);
    setSimulateError(null);
    
    try {
      const response = await api.simulateSegment({
        user_id: user?.user_id ?? 'guest',
        name: user?.name ?? 'FootballVerse Player',
        scenario,
        tactics,
        dna: dna?.stats,
      });

      setCurrentScore(response.new_score);
      setTotalPoints(prev => prev + response.segment_points);
      setFullTimeline(prev => [...prev, ...response.timeline]);
      setMatchStats(prev => ({
        passes: prev.passes + response.stats.passes,
        shots: prev.shots + response.stats.shots,
        fouls: prev.fouls + response.stats.fouls,
        offsides: prev.offsides + response.stats.offsides,
      }));
      drainStamina();

      // Move to next segment
      if (segmentIndex < SEGMENTS.length - 1) {
        setSegmentIndex(prev => prev + 1);
      } else {
        // Match Over
        const homeGoals = Number(response.new_score.split('-')[0]);
        const awayGoals = Number(response.new_score.split('-')[1]);
        const finalPts = totalPoints + response.segment_points + (
          homeGoals > awayGoals ? 300 :
          homeGoals === awayGoals ? 100 : 0
        );
        
        const finalResult = {
          final_score: response.new_score,
          total_points: finalPts,
          timeline: [...fullTimeline, ...response.timeline]
        };

        const completed = await api.completeCoachMatch({
          user_id: user?.user_id ?? 'guest',
          name: user?.name ?? 'FootballVerse Player',
          coach_style: coachStyle,
          ...finalResult
        });
        
        setCoachResult({ ...finalResult, session_id: completed.session_id, manager_title: completed.manager_title });
        navigate('/report');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to simulate segment. Please try again.';
      setSimulateError(message);
    } finally {
      setSimulating(false);
    }
  };

  if (htTimer !== null) {
    const starters = roster.filter(p => p.isStarter);
    const bench = roster.filter(p => !p.isStarter);
    
    return (
      <main className="coach-screen ht-screen">
        <div className="ht-modal">
          <h2 style={{ fontSize: '2.5rem', margin: 0 }}>HALF TIME</h2>
          <div className="ht-timer" style={{ fontSize: '4rem', color: '#ffd24d', fontWeight: 900, margin: '1rem 0' }}>{htTimer}s</div>
          <p style={{ fontSize: '1.2rem', opacity: 0.8 }}>You have 60 seconds to review stats and make substitutions.</p>
          
          <div className="ht-stats" style={{ display: 'flex', justifyContent: 'space-around', margin: '2rem 0', padding: '1.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '1rem' }}>
            <div><span style={{opacity: 0.6}}>Score</span><br/><strong style={{fontSize: '2rem', color: '#ffd24d'}}>{currentScore}</strong></div>
            <div><span style={{opacity: 0.6}}>Passes</span><br/><strong style={{fontSize: '2rem'}}>{matchStats.passes}</strong></div>
            <div><span style={{opacity: 0.6}}>Shots</span><br/><strong style={{fontSize: '2rem'}}>{matchStats.shots}</strong></div>
            <div><span style={{opacity: 0.6}}>Fouls</span><br/><strong style={{fontSize: '2rem'}}>{matchStats.fouls}</strong></div>
          </div>
          
          <section className="ht-layout">
            <div className="ht-player-grid">
              {starters.map((player) => {
                const pos = tactics.player_positions.find(position => position.id === player.id)?.label || 'XI';
                const staminaClass = player.stamina > 70 ? 'good' : player.stamina >= 40 ? 'warn' : 'danger';
                return (
                  <article className="ht-player-card" key={player.id}>
                    <strong>{player.name}</strong>
                    <span>{pos}</span>
                    <div className={`stamina-bar ${staminaClass}`}>
                      <i style={{ width: `${player.stamina}%` }} />
                    </div>
                    <small>{player.stamina}% stamina</small>
                  </article>
                );
              })}
            </div>

            <div
              className="tactical-pitch ht-pitch"
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
          </section>

          <div className="roster-panel ht-sub-panel">
            <h4>Half-Time Substitutions ({subsLeft}/5 left)</h4>
            <div className="sub-row">
              <select value={subOutId} onChange={(event) => setSubOutId(event.target.value)}>
                <option value="">-- Starter to Sub --</option>
                {starters.map(p => {
                  const pos = tactics.player_positions.find(pos => pos.id === p.id)?.label || 'Bench';
                  return <option key={p.id} value={p.id}>{pos} | {p.name} (Stamina {p.stamina}%)</option>;
                })}
              </select>
              <select value={subInId} onChange={(event) => setSubInId(event.target.value)}>
                <option value="">-- Bench Player --</option>
                {bench.map(p => <option key={p.id} value={p.id}>{p.position} | {p.name}</option>)}
              </select>
              <button 
                className="secondary-action"
                type="button" 
                onClick={() => {
                  const outId = parseInt(subOutId);
                  const inId = parseInt(subInId);
                  if (outId && inId) handleSub(outId, inId);
                }}
                disabled={subsLeft <= 0 || !subOutId || !subInId}
              >
                Make Sub
              </button>
            </div>
          </div>

          <p className="ht-lock-message">Second half unlocks when the half-time clock reaches zero.</p>
        </div>
      </main>
    );
  }

  const starters = roster.filter(p => p.isStarter);
  const bench = roster.filter(p => !p.isStarter);
  const matchSegmentNumber = SEGMENTS.slice(0, segmentIndex + 1).filter((segment) => segment !== 'HT').length;

  return (
    <main className="coach-screen">
      <header className="screen-header compact">
        <span className="broadcast-kicker">Segment {matchSegmentNumber} / {MATCH_SEGMENT_TOTAL}</span>
        <h2>{SEGMENTS[segmentIndex]}' Minute</h2>
        <div style={{ fontSize: '2.5rem', fontWeight: 900, color: '#ffd24d' }}>{currentScore}</div>
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
              <span style={{ color: 'var(--fv-primary)', fontWeight: 'bold', fontSize: '0.8rem' }}>OBJECTIVE: {scenario.objective.toUpperCase()}</span>
              <h3 style={{ margin: '0.5rem 0' }}>Opponent: {scenario.opponent_strategy}</h3>
              <small style={{ opacity: 0.7 }}>{scenario.opponent_formation} | {scenario.pressure_level} pressure</small>
            </div>
          ) : null}

          <label>
            <span>Formation</span>
            <select value={tactics.formation} onChange={(event) => handleFormationChange(event.target.value)}>
              {Object.keys(FORMATIONS).map((formation) => <option key={formation}>{formation}</option>)}
            </select>
          </label>

          <TacticSlider label="Attack" value={tactics.attack} onChange={(value) => updateNumber('attack', value)} />
          <TacticSlider label="Defense" value={tactics.defense} onChange={(value) => updateNumber('defense', value)} />
          <TacticSlider label="Possession" value={tactics.possession} onChange={(value) => updateNumber('possession', value)} />
          <TacticSlider label="Pressure" value={tactics.pressure} onChange={(value) => updateNumber('pressure', value)} />
          <TacticSlider label="Width" value={tactics.width} onChange={(value) => updateNumber('width', value)} />

          {simulateError ? (
            <div style={{ padding: '0.75rem 1rem', background: 'rgba(255,91,91,0.15)', border: '1px solid #ff5b5b', borderRadius: '8px', color: '#ff5b5b', fontSize: '0.85rem' }}>
              ⚠️ {simulateError}
            </div>
          ) : null}

          <button className="primary-action" type="button" onClick={() => void handleSimulateSegment()} disabled={simulating}>
            {simulating ? 'Simulating Segment...' : 'Simulate Segment'}
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
            {tactics.player_positions.map((player, idx) => {
              const rPlayer = starters[idx] || starters[0];
              const staminaColor = rPlayer.stamina > 70 ? '#4CAF50' : rPlayer.stamina > 30 ? '#FFC107' : '#F44336';
              return (
                <button
                  className="player-token"
                  key={player.id}
                  style={{ left: `${player.x}%`, top: `${player.y}%`, borderBottom: `4px solid ${staminaColor}` }}
                  type="button"
                  onPointerDown={(event) => {
                    event.currentTarget.setPointerCapture(event.pointerId);
                    setDraggingId(player.id);
                  }}
                  title={`${rPlayer.name} (Stamina: ${rPlayer.stamina}%)`}
                >
                  {player.label}
                </button>
              );
            })}
          </div>
          
          <div className="roster-panel" style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.5)', padding: '1rem', borderRadius: '1rem' }}>
            <h4 style={{ margin: '0 0 1rem 0' }}>Substitutions ({subsLeft} left)</h4>
            <div className="sub-row">
              <select value={subOutId} onChange={(event) => setSubOutId(event.target.value)}>
                <option value="">-- Starter to Sub --</option>
                {starters.map(p => {
                  const pos = tactics.player_positions.find(pos => pos.id === p.id)?.label || 'Bench';
                  return <option key={p.id} value={p.id}>{pos} | {p.name} (Stamina {p.stamina}%)</option>;
                })}
              </select>
              <select value={subInId} onChange={(event) => setSubInId(event.target.value)}>
                <option value="">-- Bench Player --</option>
                {bench.map(p => <option key={p.id} value={p.id}>{p.position} | {p.name}</option>)}
              </select>
              <button 
                type="button" 
                onClick={() => {
                  const outId = parseInt(subOutId);
                  const inId = parseInt(subInId);
                  if (outId && inId) handleSub(outId, inId);
                }}
                disabled={subsLeft <= 0 || !subOutId || !subInId}
                style={{ padding: '0.5rem 1rem', background: 'var(--fv-primary)', color: '#000', border: 'none', borderRadius: '0.5rem', fontWeight: 'bold', cursor: 'pointer' }}
              >
                Make Sub
              </button>
            </div>
          </div>
          {/* ── Live Match Timeline ── */}
          {fullTimeline.length > 0 && (
            <div style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.55)', border: '1px solid rgba(112,226,255,0.18)', borderRadius: '1rem', padding: '1rem' }}>
              <h4 style={{ margin: '0 0 0.75rem', color: '#70e2ff', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1rem' }}>Match Timeline</h4>
              <div style={{ display: 'grid', gap: '0.45rem', maxHeight: '14rem', overflowY: 'auto' }}>
                {[...fullTimeline].reverse().map((event, idx) => (
                  <div key={idx} style={{
                    fontSize: '0.82rem',
                    padding: '0.4rem 0.65rem',
                    borderRadius: '6px',
                    borderLeft: `3px solid ${event.includes('GOAL!') ? '#70e2ff' : event.includes('conceded') ? '#ff5b5b' : 'rgba(255,255,255,0.2)'}`,
                    background: event.includes('GOAL!') ? 'rgba(112,226,255,0.08)' : event.includes('conceded') ? 'rgba(255,91,91,0.08)' : 'rgba(255,255,255,0.04)',
                    color: event.includes('GOAL!') ? '#70e2ff' : event.includes('conceded') ? '#ff8080' : '#dce7f7',
                  }}>
                    {event}
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.78rem', color: '#aab8cc' }}>
                <span>Passes <strong style={{ color: '#f5f8ff' }}>{matchStats.passes}</strong></span>
                <span>Shots <strong style={{ color: '#f5f8ff' }}>{matchStats.shots}</strong></span>
                <span>Fouls <strong style={{ color: '#f5f8ff' }}>{matchStats.fouls}</strong></span>
                <span>Points <strong style={{ color: '#ffd24d' }}>{totalPoints}</strong></span>
              </div>
            </div>
          )}
        </section>
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
