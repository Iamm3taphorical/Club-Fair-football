import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, apiWebSocketUrl } from '../api';
import { initAudio, playCrowdCue, playShotStrike, speakCommentary } from '../audio';
import {
  attachStreamToVideo,
  cameraErrorMessage,
  cameraStateFromError,
  cameraUnavailableMessage,
  requestFrontCamera,
  stopStream,
  type CameraState,
} from '../camera';
import type { DNAProfile, PenaltyAttempt, PlayerReport, UserProfile } from '../types';

const MAX_SHOTS = 5;

const FALLBACK_DNA: DNAProfile = {
  primary_match: 'Messi',
  name_match: 'Lionel Messi',
  display_name: 'Lionel Messi',
  style: 'Playmaker',
  special_ability: 'Curve Shot',
  suggested_role: 'CAM',
  stats: { creativity: 91, finishing: 88, vision: 92, speed: 84, leadership: 74, flair: 93 },
  traits: { Vision: 92, Creativity: 91, Power: 78, Speed: 84 },
  percentages: { Messi: 82, Neymar: 74, 'De Bruyne': 71 },
};

const GESTURES: Record<string, { shot: string; target: string; zone: string; key: string }> = {
  'Point Left': { shot: 'Left Shot', target: 'Left Corner', zone: 'left-low', key: 'Left' },
  'Point Right': { shot: 'Right Shot', target: 'Right Corner', zone: 'right-low', key: 'Right' },
  'Point Up': { shot: 'Top Corner', target: 'Top Corner', zone: 'top-right', key: 'Top' },
  'Point Down': { shot: 'Low Shot', target: 'Low Shot', zone: 'center-low', key: 'Low' },
  Flick: { shot: 'Flick Shot', target: 'Top Corner', zone: 'top-right', key: 'Flick' },
  Fist: { shot: 'Power Shot', target: 'Power Shot', zone: 'right-high', key: 'Power' },
};

const TARGET_TO_ZONE: Record<string, string> = {
  'Left Corner': 'left-low',
  'Right Corner': 'right-low',
  'Top Corner': 'top-right',
  'Low Shot': 'center-low',
  'Power Shot': 'right-high',
};

const COMMENTARY_STYLES = ['Professional', 'Emotional Uncle', 'Conspiracy Analyst', 'Robot AI'];

type StoredPenaltySession = {
  sessionId?: number;
  attempts: PenaltyAttempt[];
  updatedAt: string;
};

type InitialPenaltySession = {
  sessionId?: number;
  attempts: PenaltyAttempt[];
};

type VisionDebug = {
  landmarks?: Array<{ x: number; y: number; z?: number }>;
  raw_landmarks?: Array<{ x: number; y: number; z?: number }>;
  gesture?: string | null;
  confidence?: number;
  palm_scale?: number;
};

function penaltyStorageKey(userId?: string) {
  return `fv_penalty_session_${userId ?? 'guest'}`;
}

function readStoredPenaltySession(userId?: string): StoredPenaltySession | null {
  try {
    const raw = window.localStorage.getItem(penaltyStorageKey(userId));
    return raw ? JSON.parse(raw) as StoredPenaltySession : null;
  } catch {
    return null;
  }
}

function readInitialPenaltySession(userId?: string): InitialPenaltySession {
  const stored = readStoredPenaltySession(userId);
  return {
    sessionId: stored?.sessionId,
    attempts: stored?.attempts ?? [],
  };
}

export default function PenaltyGame({
  user,
  dna,
  setDna,
  setPlayerReport,
}: {
  user: UserProfile | null;
  dna: DNAProfile | null;
  setDna: (dna: DNAProfile) => void;
  setPlayerReport: (report: PlayerReport) => void;
}) {
  const navigate = useNavigate();
  const activeDna = dna ?? FALLBACK_DNA;
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const attemptsRef = useRef<PenaltyAttempt[]>([]);
  const animatingRef = useRef(false);
  const sessionIdRef = useRef<number | undefined>(undefined);
  const [initialPenaltySession] = useState(() => readInitialPenaltySession(user?.user_id));

  const [sessionId, setSessionId] = useState<number | undefined>(initialPenaltySession.sessionId);
  const [wsStatus, setWsStatus] = useState('Offline fallback');
  const [activeGesture, setActiveGesture] = useState<string | null>(null);
  const [commentaryStyle, setCommentaryStyle] = useState('Professional');
  const [difficulty, setDifficulty] = useState('Hard');
  const [commentary, setCommentary] = useState('Step up to the spot. The stadium is waiting.');
  const [attempts, setAttempts] = useState<PenaltyAttempt[]>(initialPenaltySession.attempts);
  const [shotResult, setShotResult] = useState<'Goal' | 'Saved' | 'Missed' | null>(null);
  const [ballPos, setBallPos] = useState<{ left: string; top: string } | null>(null);
  const [keeperZone, setKeeperZone] = useState('center');
  const [chargePower, setChargePower] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [cameraState, setCameraState] = useState<CameraState>('idle');
  const [cameraMessage, setCameraMessage] = useState('Front camera feed waiting.');
  const [visionMessage, setVisionMessage] = useState('Gesture detector waiting for the backend.');
  const [pointerPos, setPointerPos] = useState<{x: number, y: number} | null>(null);
  const [debugOverlay, setDebugOverlay] = useState(false);
  const [visionDebug, setVisionDebug] = useState<VisionDebug | null>(null);
  const [powerTimer, setPowerTimer] = useState<number | null>(null);
  const [gamePhase, setGamePhase] = useState<'idle' | 'charging' | 'aiming' | 'shooting'>('idle');

  const powerTimerRef = useRef<number | null>(null);
  const chargePowerRef = useRef(0);
  const pointerPosRef = useRef<{ x: number; y: number } | null>(null);
  const gamePhaseRef = useRef<'idle' | 'charging' | 'aiming' | 'shooting'>('idle');

  useEffect(() => { powerTimerRef.current = powerTimer; }, [powerTimer]);
  useEffect(() => { chargePowerRef.current = chargePower; }, [chargePower]);
  useEffect(() => { pointerPosRef.current = pointerPos; }, [pointerPos]);
  useEffect(() => { gamePhaseRef.current = gamePhase; }, [gamePhase]);

  useEffect(() => {
    if (powerTimer === null) return;
    if (powerTimer <= 0) {
      if (gamePhaseRef.current === 'charging') {
        // Time expired while charging - auto lock power and transition to aiming
        setGamePhase('aiming');
        setPowerTimer(5); // 5s to aim
        setVisionMessage('Power auto-locked! You have 5s to point your direction.');
      } else if (gamePhaseRef.current === 'aiming') {
        // Time expired while aiming - auto fire center shot
        void handleShotRef.current('Point Down', chargePowerRef.current, 0);
        setPowerTimer(null);
        setPointerPos(null);
      }
      return;
    }
    const timerId = window.setTimeout(() => setPowerTimer(prev => prev !== null ? prev - 1 : null), 1000);
    return () => window.clearTimeout(timerId);
  }, [powerTimer]);

  useEffect(() => {
    if (commentary && commentary !== 'Step up to the spot. The stadium is waiting.') {
      speakCommentary(commentary);
    }
  }, [commentary]);

  const goals = attempts.filter((attempt) => attempt.result === 'Goal').length;
  const accuracy = attempts.length ? Math.round((goals / attempts.length) * 100) : 0;
  const averageReaction = attempts.length
    ? (attempts.reduce((sum, attempt) => sum + attempt.reaction_time, 0) / attempts.length).toFixed(2)
    : '0.00';

  const startCamera = useCallback(async () => {
    initAudio(); // Initialize background audio on user interaction
    const unavailable = cameraUnavailableMessage();
    if (unavailable) {
      setCameraState('unavailable');
      setCameraMessage(unavailable);
      return;
    }

    setCameraState('requesting');
    setCameraMessage('Waiting for browser camera permission...');
    try {
      stopStream(streamRef.current);
      const stream = await requestFrontCamera({ width: 640, height: 480 });
      streamRef.current = stream;
      setCameraState('ready');
      setCameraMessage('Front camera connected.');
      attachStreamToVideo(videoRef.current, stream);
    } catch (error) {
      streamRef.current = null;
      setCameraState(cameraStateFromError(error));
      setCameraMessage(cameraErrorMessage(error));
    }
  }, []);

  useEffect(() => {
    if (cameraState === 'ready') {
      attachStreamToVideo(videoRef.current, streamRef.current);
    }
  }, [cameraState]);

  useEffect(() => () => stopStream(streamRef.current), []);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  useEffect(() => {
    attemptsRef.current = attempts;
  }, [attempts]);

  useEffect(() => {
    let cancelled = false;
    const userId = user?.user_id;
    const userName = user?.name ?? 'FootballVerse Player';
    if (!userId) return undefined;

    const startNewSession = () => {
      api.startPenaltySession({ user_id: userId, name: userName })
        .then((response) => {
          if (!cancelled) setSessionId(response.session_id);
        })
        .catch(() => {
          if (!cancelled) setSessionId(undefined);
        });
    };

    const stored = readStoredPenaltySession(userId);
    if (stored?.sessionId) {
      window.queueMicrotask(() => {
        if (cancelled) return;
        setSessionId(stored.sessionId);
        setAttempts(stored.attempts);
        attemptsRef.current = stored.attempts;
      });
      api.getPenaltySession(stored.sessionId, userId)
        .then((snapshot) => {
          if (cancelled) return;
          if (snapshot.status === 'active' && snapshot.attempts.length < MAX_SHOTS) {
            const hydratedAttempts = snapshot.attempts.map((attempt, index) => ({
              ...attempt,
              commentary: attempt.commentary || stored.attempts[index]?.commentary || `${attempt.shot_type} recorded.`,
            }));
            setSessionId(snapshot.session_id);
            setAttempts(hydratedAttempts);
            attemptsRef.current = hydratedAttempts;
            setWsStatus('Session resumed');
          } else {
            window.localStorage.removeItem(penaltyStorageKey(userId));
            setAttempts([]);
            attemptsRef.current = [];
            startNewSession();
          }
        })
        .catch(() => {
          if (!cancelled && stored.attempts.length) setWsStatus('Local session restored');
          if (!cancelled && !stored.attempts.length) startNewSession();
        });
    } else {
      startNewSession();
    }

    return () => {
      cancelled = true;
    };
  }, [user?.name, user?.user_id]);

  useEffect(() => {
    const userId = user?.user_id;
    if (!userId) return;
    if (gameOver) {
      window.localStorage.removeItem(penaltyStorageKey(userId));
      return;
    }
    if (sessionId || attempts.length) {
      window.localStorage.setItem(
        penaltyStorageKey(userId),
        JSON.stringify({ sessionId, attempts, updatedAt: new Date().toISOString() }),
      );
    }
  }, [attempts, gameOver, sessionId, user?.user_id]);

  const completeSession = useCallback(async (finalAttempts: PenaltyAttempt[]) => {
    setGameOver(true);
    try {
      const report = await api.completePenaltySession({
        user_id: user?.user_id ?? 'guest',
        name: user?.name ?? 'FootballVerse Player',
        session_id: sessionIdRef.current,
        attempts: finalAttempts,
        dna_profile: activeDna,
      });
      setPlayerReport(report);
      setDna(report.dna_after);
    } catch {
      const report = buildFallbackReport(user, activeDna, finalAttempts);
      setPlayerReport(report);
      setDna(report.dna_after);
    }
    if (user?.user_id) window.localStorage.removeItem(penaltyStorageKey(user.user_id));
    window.setTimeout(() => navigate('/report'), 1150);
  }, [activeDna, navigate, setDna, setPlayerReport, user]);

  const handleShot = useCallback(async (gesture: string, power = 0.62, curve = 0.18) => {
    initAudio(); // Ensure audio starts on any shot interaction
    if (animatingRef.current || attemptsRef.current.length >= MAX_SHOTS) return;
    const gestureConfig = GESTURES[gesture];
    if (!gestureConfig) return;

    animatingRef.current = true;
    setGamePhase('shooting');
    setPowerTimer(null);
    setActiveGesture(gesture);
    setChargePower(gesture === 'Fist' ? power : chargePowerRef.current || power);
    setCommentary(`${gestureConfig.shot} selected.`);
    playShotStrike();

    let nextAttempt: PenaltyAttempt;
    try {
      const response = await api.executeShot({
        user_id: user?.user_id ?? 'guest',
        name: user?.name ?? 'FootballVerse Player',
        session_id: sessionIdRef.current,
        gesture,
        history: attemptsRef.current.map((attempt) => attempt.shot_target),
        power,
        curve,
        difficulty,
        commentary_style: commentaryStyle,
      });
      if (!sessionIdRef.current) setSessionId(response.session_id);
      const result = response.shot_result;
      nextAttempt = {
        gesture,
        shot_type: result.shot_type,
        shot_target: result.shot_target,
        result: result.result,
        keeper_guess: result.keeper_guess,
        reaction_time: result.reaction_time,
        power: result.power_registered,
        curve: result.curve_registered,
        commentary: response.commentary,
      };
    } catch {
      nextAttempt = fallbackShot(gesture, attemptsRef.current, commentaryStyle);
    }

    setKeeperZone(TARGET_TO_ZONE[nextAttempt.keeper_guess] ?? 'center');
    const vertical = pointerPosRef.current ? 1.0 - pointerPosRef.current.y : 0.5;
    const horizontal = pointerPosRef.current ? pointerPosRef.current.x : 0.5;
    const powerValue = chargePowerRef.current || power;
    const { leftPct, topPct } = calculateKickPhysics(vertical, horizontal, powerValue);
    setBallPos({ left: `${leftPct}%`, top: `${topPct}%` });
    window.setTimeout(() => setShotResult(nextAttempt.result), 360);
    setCommentary(nextAttempt.commentary);
    playCrowdCue(nextAttempt.result);
    const updatedAttempts = [...attemptsRef.current, nextAttempt];
    attemptsRef.current = updatedAttempts;
    setAttempts(updatedAttempts);

    window.setTimeout(() => {
      setShotResult(null);
      setBallPos(null);
      setKeeperZone('center');
      setActiveGesture(null);
      setChargePower(0);
      setGamePhase('idle');
      animatingRef.current = false;

      if (updatedAttempts.length >= MAX_SHOTS) {
        void completeSession(updatedAttempts);
      }
    }, 1450);
  }, [commentaryStyle, completeSession, difficulty, user]);

  const handleShotRef = useRef(handleShot);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/immutability
    handleShotRef.current = handleShot;
  }, [handleShot]);

  useEffect(() => {
    let frameTimer: number | undefined;
    try {
      const ws = new WebSocket(apiWebSocketUrl('/ws/video'));
      wsRef.current = ws;
      ws.onopen = () => {
        setWsStatus('Vision linked');
        setVisionMessage('Gesture detector connected. Show a clear hand gesture.');
      };
      ws.onclose = () => {
        setWsStatus('Offline fallback');
        setVisionMessage('Backend vision socket is offline. Button controls still work.');
      };
      ws.onerror = () => {
        setWsStatus('Offline fallback');
        setVisionMessage('Backend vision socket is offline. Button controls still work.');
      };
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data) as {
          type?: string;
          gesture?: string;
          power?: number;
          curve?: number;
          pointer?: {x: number, y: number};
          debug?: VisionDebug;
          available?: boolean;
          detail?: string;
        };
        if (data.debug) setVisionDebug(data.debug);
        if (data.type === 'VISION_STATUS') {
          if (data.available) {
            setWsStatus('Vision ready');
            setVisionMessage(data.detail ?? 'Gesture detector ready.');
          } else {
            setWsStatus('Vision unavailable');
            setVisionMessage(data.detail ?? 'Gesture recognition is unavailable on the backend.');
          }
          return;
        }

        if (data.type === 'POINTER_UPDATE' && data.pointer) {
          setPointerPos(data.pointer);
          if (powerTimerRef.current !== null) {
             const computedPower = Math.max(0, Math.min(1, 1.0 - data.pointer.y));
             setChargePower(computedPower);
             setVisionMessage(`Adjusting power: ${Math.round(computedPower * 100)}%. Shooting in ${powerTimerRef.current}s`);
          }
          return;
        }

        if (data.pointer) {
          setPointerPos(data.pointer);
        }

        if (data.type !== 'GESTURE_DETECTED' || !data.gesture) return;
        
        if (gamePhaseRef.current === 'idle') {
           if (data.gesture === 'Charging') {
               setGamePhase('charging');
               setPowerTimer(5);
               setActiveGesture('Fist');
               setVisionMessage('⚡ Charging power! Release fist to lock.');
           }
        } else if (gamePhaseRef.current === 'charging') {
           if (data.gesture === 'Fist Released') {
               setChargePower(data.power ?? 1.0);
               setPowerTimer(null);
               const releasePointer = data.pointer ?? pointerPosRef.current ?? { x: 0.5, y: 0.62 };
               setPointerPos(releasePointer);
               setVisionMessage(`Release detected. Shot sent from ${Math.round(releasePointer.x * 100)}%, ${Math.round(releasePointer.y * 100)}%.`);
               void handleShotRef.current(gestureFromPointer(releasePointer), data.power ?? chargePowerRef.current, data.curve ?? 0);
           } else if (data.gesture === 'Charging') {
               setChargePower(data.power ?? 0.0);
           }
        } else if (gamePhaseRef.current === 'aiming') {
           if (['Point Left', 'Point Right', 'Point Up', 'Point Down', 'Flick'].includes(data.gesture)) {
               setPowerTimer(null);
               void handleShotRef.current(data.gesture, chargePowerRef.current, data.curve ?? 0);
           }
        }
      };

      frameTimer = window.setInterval(() => {
        if (ws.readyState !== WebSocket.OPEN || !videoRef.current || !canvasRef.current) return;
        const video = videoRef.current;
        if (!video.videoWidth) return;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        if (!context) return;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (blob && ws.readyState === WebSocket.OPEN) ws.send(blob);
        }, 'image/jpeg', 0.48);
      }, 110);
    } catch {
      // Keep the existing offline fallback state when WebSocket construction fails.
    }

    return () => {
      if (frameTimer) window.clearInterval(frameTimer);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, []);

  return (
    <main className="penalty-screen">
      <section className="vision-panel">
        <header className="panel-header">
          <div>
            <span className="panel-label">Live Gesture Feed</span>
            <strong>{wsStatus}</strong>
          </div>
          <button
            className="secondary-action camera-action"
            type="button"
            onClick={() => void startCamera()}
            disabled={cameraState === 'requesting' || cameraState === 'ready'}
          >
            {cameraState === 'ready' ? 'Camera On' : cameraState === 'requesting' ? 'Requesting Camera' : 'Enable Camera'}
          </button>
          <span className="pill">{attempts.length}/{MAX_SHOTS}</span>
        </header>
        <button
          className="secondary-action camera-action"
          type="button"
          onClick={() => setDebugOverlay((current) => !current)}
        >
          {debugOverlay ? 'Hide Debug' : 'Show Debug'}
        </button>

        <div className="camera-frame gesture-camera">
          <video ref={videoRef} autoPlay playsInline muted />
          <canvas ref={canvasRef} />
          <div className="hand-skeleton">
            <span className="palm" />
            <span className="finger finger-one" />
            <span className="finger finger-two" />
            <span className="finger finger-three" />
            <span className="finger finger-four" />
          </div>
          {pointerPos && (
             <div className="finger-tracker" style={{ left: `${pointerPos.x * 100}%`, top: `${pointerPos.y * 100}%` }} />
          )}
          {debugOverlay ? (
            <div className="vision-debug-overlay">
              {visionDebug?.landmarks?.map((landmark, index) => (
                <span
                  key={`lm-${index}`}
                  className={index === 8 ? 'index-tip' : ''}
                  style={{ left: `${landmark.x * 100}%`, top: `${landmark.y * 100}%` }}
                />
              ))}
              <div className="vision-debug-readout">
                <strong>{visionDebug?.gesture ?? activeGesture ?? 'No gesture'}</strong>
                <small>conf {Math.round((visionDebug?.confidence ?? 0) * 100)}% | palm {visionDebug?.palm_scale?.toFixed(3) ?? 'n/a'}</small>
                {pointerPos ? <small>x {pointerPos.x.toFixed(2)} y {pointerPos.y.toFixed(2)}</small> : null}
              </div>
            </div>
          ) : null}
          {powerTimer !== null && (
             <div className="power-countdown">{powerTimer}s</div>
          )}
          {gamePhase !== 'idle' ? (
            <div className="gesture-badge">
              {gamePhase === 'charging' ? `⚡ Power ${Math.round(chargePower * 100)}%` : 
               gamePhase === 'aiming' ? `🎯 Aiming (${Math.round(chargePower * 100)}%)` : 
               activeGesture ? GESTURES[activeGesture]?.shot : ''}
            </div>
          ) : null}
          {cameraState !== 'ready' ? (
            <div className="camera-overlay">
              <strong>{cameraState === 'requesting' ? 'Requesting Camera' : 'Camera Offline'}</strong>
              <span>{cameraMessage}</span>
              {cameraState !== 'requesting' ? (
                <button className="secondary-action camera-action" type="button" onClick={() => void startCamera()}>
                  Retry Camera
                </button>
              ) : null}
            </div>
          ) : null}
        </div>
        <p className={`camera-status ${cameraState}`} aria-live="polite">
          {cameraState === 'ready' ? visionMessage : cameraMessage}
        </p>

        <div className="control-row">
          <label>
            <span>Commentary</span>
            <select value={commentaryStyle} onChange={(event) => setCommentaryStyle(event.target.value)}>
              {COMMENTARY_STYLES.map((style) => <option key={style}>{style}</option>)}
            </select>
          </label>
          <label>
            <span>Difficulty</span>
            <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
              {['Easy', 'Medium', 'Hard', 'Legendary'].map((level) => <option key={level}>{level}</option>)}
            </select>
          </label>
        </div>

        {(wsStatus.includes('Offline') || wsStatus.includes('unavailable')) && (
          <div className="gesture-grid">
            {Object.entries(GESTURES).map(([gesture, config]) => (
              <button
                className={activeGesture === gesture ? 'selected' : ''}
                key={gesture}
                type="button"
                onClick={() => void handleShot(gesture, gesture === 'Fist' ? 0.9 : 0.62, gesture === 'Pinch' ? 0.05 : 0.2)}
                disabled={gameOver || attempts.length >= MAX_SHOTS}
              >
                <span>{config.key}</span>
                <strong>{config.shot}</strong>
              </button>
            ))}
          </div>
        )}

      </section>

      <section className="stadium-panel">
        <div className="score-hud">
          <div><span>Goals</span><strong>{goals}</strong></div>
          <div><span>Accuracy</span><strong>{accuracy}%</strong></div>
          <div><span>Reaction</span><strong>{averageReaction}s</strong></div>
        </div>

        <div className="stadium-bowl">
          <div className="crowd-rings" />
          <div className="goal-mouth">
            <div className="net-grid" />
            <div className={`keeper keeper-${keeperZone}`} />
            {ballPos ? <div className="match-ball physics-ball" style={{ top: ballPos.top, left: ballPos.left }} /> : null}
            <div className="goal-frame" />
          </div>
          <div className="penalty-spot" />
        </div>

        {shotResult ? (
          <div className={`result-flash ${shotResult.toLowerCase()}`}>
            {shotResult === 'Goal' ? 'GOAL' : shotResult.toUpperCase()}
          </div>
        ) : null}

        <div className="commentary-bar">
          <span>LIVE</span>
          <p>{commentary}</p>
        </div>

        <div className="attempt-strip">
          {Array.from({ length: MAX_SHOTS }).map((_, index) => {
            const attempt = attempts[index];
            return (
              <span
                className={attempt ? `attempt-dot ${attempt.result.toLowerCase()}` : 'attempt-dot'}
                key={`attempt-${index}`}
              />
            );
          })}
        </div>

        {gameOver ? (
          <div className="session-overlay">
            <h2>Session Complete</h2>
            <p>{goals}/{MAX_SHOTS} penalties converted</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}

function fallbackShot(gesture: string, history: PenaltyAttempt[], style: string): PenaltyAttempt {
  const config = GESTURES[gesture];
  const rollSource = `${gesture}-${history.length}-${style}`;
  const roll = rollSource.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0) % 100;
  const repeated = history.filter((attempt) => attempt.shot_target === config.target).length;
  const keeperGuess = repeated > 0 ? config.target : ['Left Corner', 'Right Corner', 'Top Corner', 'Low Shot', 'Panenka'][roll % 5];
  const saved = keeperGuess === config.target && roll < 74;
  const missed = !saved && roll < 22;
  const result = saved ? 'Saved' : missed ? 'Missed' : 'Goal';
  const commentary = result === 'Goal'
    ? `${config.shot} finds the net. The crowd erupts.`
    : `${config.shot} is denied. The keeper has read the pattern.`;

  return {
    gesture,
    shot_type: config.shot,
    shot_target: config.target,
    result,
    keeper_guess: keeperGuess,
    reaction_time: Number((0.62 + repeated * 0.05).toFixed(2)),
    power: gesture === 'Fist' ? 0.9 : 0.62,
    curve: gesture === 'Pinch' ? 0.05 : 0.2,
    commentary,
  };
}

function gestureFromPointer(pointer: { x: number; y: number }) {
  if (pointer.y < 0.34) return 'Point Up';
  if (pointer.x < 0.38) return 'Point Left';
  if (pointer.x > 0.62) return 'Point Right';
  if (pointer.y > 0.68) return 'Point Down';
  return 'Pinch';
}

function buildFallbackReport(user: UserProfile | null, dna: DNAProfile, attempts: PenaltyAttempt[]): PlayerReport {
  const total = Math.max(attempts.length, 1);
  const goals = attempts.filter((attempt) => attempt.result === 'Goal').length;
  const accuracy = Math.round((goals / total) * 100);
  const evolved = {
    ...dna,
    primary_match: attempts.filter((attempt) => attempt.shot_type === 'Power Shot').length >= 2 ? 'Ronaldo' : dna.primary_match,
    name_match: attempts.filter((attempt) => attempt.shot_type === 'Power Shot').length >= 2 ? 'Cristiano Ronaldo' : dna.name_match,
    style: attempts.filter((attempt) => attempt.shot_type === 'Power Shot').length >= 2 ? 'Hybrid Finisher' : dna.style,
  };

  return {
    player_type: `${evolved.primary_match} Archetype`,
    goals,
    total_shots: attempts.length,
    score: `${goals}/${attempts.length}`,
    accuracy,
    reaction_time: Number((attempts.reduce((sum, attempt) => sum + attempt.reaction_time, 0) / total).toFixed(2)),
    best_skill: attempts.find((attempt) => attempt.result === 'Goal')?.shot_type ?? evolved.special_ability ?? 'Curve Shot',
    weakness: attempts.find((attempt) => attempt.result !== 'Goal')?.shot_type ?? 'Power Shots',
    suggested_role: evolved.suggested_role ?? 'CAM',
    dna_before: dna,
    dna_after: evolved,
    evolution: evolved.primary_match === 'Ronaldo' ? 'Hybrid Messi-Ronaldo' : `${evolved.primary_match} Archetype`,
    radar_chart: Object.entries(evolved.traits ?? {}).map(([label, value]) => ({ label, value })),
    performance_graph: attempts.map((attempt, index) => ({
      shot: index + 1,
      goals: attempts.slice(0, index + 1).filter((item) => item.result === 'Goal').length,
      result: attempt.result,
    })),
    shareable_card: {
      title: 'FootballVerse Match Report',
      headline: `${user?.name ?? 'Player'} is ${evolved.primary_match}`,
      rating: Math.round((accuracy + 86) / 2),
    },
    match_story: `${user?.name ?? 'Player'} finished with ${goals} goals from ${attempts.length} penalties.`,
  };
}

function calculateKickPhysics(vertical: number, horizontal: number, power: number) {
  // Blenderous formula: designed for an 810x440 canvas where the penalty spot
  // is at (390, 440) and the goal frame spans roughly x:[114..710], y:[98..292].
  const rawTop = 440 - ((0.8 + vertical) / 1.8) * power * 440 + 0.3 * power * ((Math.abs(0.5 - horizontal)) / 0.5) * 440;
  const rawLeft = 405 + power * (horizontal - 0.5) * 810;

  // Goal-mouth bounding box in blenderous pixel space
  const goalLeft = 114;
  const goalRight = 710;
  const goalTop = 98;
  const goalBottom = 292;

  // Clamp to goal-mouth bounds so the ball always lands inside the visible frame
  const clampedLeft = Math.max(goalLeft, Math.min(goalRight, rawLeft));
  const clampedTop = Math.max(goalTop, Math.min(goalBottom, rawTop));

  // Convert to percentage within the goal-mouth container (0-100%)
  const leftPct = ((clampedLeft - goalLeft) / (goalRight - goalLeft)) * 100;
  const topPct = ((clampedTop - goalTop) / (goalBottom - goalTop)) * 100;

  return { leftPct, topPct };
}
