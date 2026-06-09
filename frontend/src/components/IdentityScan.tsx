import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import {
  attachStreamToVideo,
  cameraErrorMessage,
  cameraStateFromError,
  cameraUnavailableMessage,
  requestFrontCamera,
  stopStream,
  type CameraState,
} from '../camera';
import type { DNAProfile, UserProfile } from '../types';

const FALLBACK_DNA: DNAProfile = {
  primary_match: 'Messi',
  name_match: 'Lionel Messi',
  display_name: 'Lionel Messi',
  style: 'Playmaker',
  archetype: 'Playmaker',
  special_ability: 'Curve Shot',
  suggested_role: 'CAM',
  confidence_score: 82,
  confidence_status: 'confirmed',
  stats: { creativity: 91, finishing: 88, vision: 92, speed: 84, leadership: 74, flair: 93 },
  traits: { Vision: 92, Creativity: 91, Power: 78, Speed: 84 },
  percentages: { Messi: 82, Neymar: 74, 'De Bruyne': 71 },
  strength: 'Vision',
  weakness: 'Power',
};

const PLAYSTYLES = ['Playmaker', 'Attacking', 'Power', 'Tactical', 'Flair'];

export default function IdentityScan({
  user,
  setUser,
  setDna,
}: {
  user: UserProfile | null;
  setUser: (user: UserProfile) => void;
  setDna: (dna: DNAProfile) => void;
}) {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const progressRef = useRef<number | null>(null);
  const [phase, setPhase] = useState<'setup' | 'scanning' | 'analyzing' | 'revealed'>('setup');
  const [scanProgress, setScanProgress] = useState(0);
  const [playstyle, setPlaystyle] = useState('Playmaker');
  const [localDna, setLocalDna] = useState<DNAProfile | null>(null);
  const [cameraState, setCameraState] = useState<CameraState>('idle');
  const [cameraMessage, setCameraMessage] = useState('Front camera permission will be requested by your browser.');

  useEffect(() => {
    return () => {
      if (progressRef.current) window.clearInterval(progressRef.current);
      stopStream(streamRef.current);
    };
  }, []);

  useEffect(() => {
    if (phase !== 'setup') {
      attachStreamToVideo(videoRef.current, streamRef.current);
    }
  }, [cameraState, phase]);

  const reveal = (profile: DNAProfile, nextUser?: UserProfile) => {
    setLocalDna(profile);
    setDna(profile);
    if (nextUser) setUser(nextUser);
    playRevealCue();
    setPhase('revealed');
  };

  const captureFaceFrame = () => {
    const video = videoRef.current;
    if (!video?.videoWidth || !video.videoHeight) return undefined;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    if (!context) return undefined;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.62);
  };

  const startCamera = async () => {
    const unavailable = cameraUnavailableMessage();
    if (unavailable) {
      setCameraState('unavailable');
      setCameraMessage(unavailable);
      return false;
    }

    setCameraState('requesting');
    setCameraMessage('Waiting for browser camera permission...');
    try {
      stopStream(streamRef.current);
      const stream = await requestFrontCamera({ width: 720, height: 540 });
      streamRef.current = stream;
      setCameraState('ready');
      setCameraMessage('Front camera connected.');
      attachStreamToVideo(videoRef.current, stream);
      return true;
    } catch (error) {
      streamRef.current = null;
      setCameraState(cameraStateFromError(error));
      setCameraMessage(cameraErrorMessage(error));
      return false;
    }
  };

  const beginScan = async () => {
    if (progressRef.current) window.clearInterval(progressRef.current);
    setPhase('scanning');
    setScanProgress(0);
    const cameraReady = await startCamera();

    progressRef.current = window.setInterval(() => {
      setScanProgress((current) => {
        if (current >= 100) {
          if (progressRef.current) window.clearInterval(progressRef.current);
          return 100;
        }
        return Math.min(100, current + 3);
      });
    }, 60);

    window.setTimeout(() => setPhase('analyzing'), 1450);

    try {
      await new Promise((resolve) => window.setTimeout(resolve, cameraReady ? 520 : 120));
      const faceFrame = captureFaceFrame();
      const response = await api.scanIdentity({
        user_id: user?.user_id ?? 'guest',
        name: user?.name ?? 'FootballVerse Player',
        answers: { playstyle },
        face_detected: cameraReady && Boolean(streamRef.current),
        face_image_base64: faceFrame,
      });
      window.setTimeout(() => reveal(response.dna, response.user), 900);
    } catch {
      const tunedFallback = {
        ...FALLBACK_DNA,
        stats: playstyle === 'Power'
          ? { creativity: 78, finishing: 93, vision: 81, speed: 87, leadership: 88, flair: 82 }
          : FALLBACK_DNA.stats,
        primary_match: playstyle === 'Power' ? 'Ronaldo' : FALLBACK_DNA.primary_match,
        name_match: playstyle === 'Power' ? 'Cristiano Ronaldo' : FALLBACK_DNA.name_match,
        display_name: playstyle === 'Power' ? 'Cristiano Ronaldo' : FALLBACK_DNA.display_name,
        style: playstyle === 'Power' ? 'Explosive Finisher' : FALLBACK_DNA.style,
        special_ability: playstyle === 'Power' ? 'Power Shot' : FALLBACK_DNA.special_ability,
      };
      window.setTimeout(() => reveal(tunedFallback), 900);
    }
  };

  return (
    <main className="scan-screen">
      <header className="screen-header compact">
        <span className="broadcast-kicker">Football Identity Analysis</span>
        <h2>{user?.name ?? 'Player'} DNA Scan</h2>
      </header>

      {phase === 'setup' ? (
        <section className="scan-setup">
          <div className="scan-copy">
            <span className="panel-label">Identity Layer</span>
            <h3>Camera scan plus personality signal</h3>
          </div>
          <div className="segmented-control">
            {PLAYSTYLES.map((style) => (
              <button
                className={style === playstyle ? 'selected' : ''}
                key={style}
                type="button"
                onClick={() => setPlaystyle(style)}
              >
                {style}
              </button>
            ))}
          </div>
          <button className="primary-action" type="button" onClick={beginScan} disabled={cameraState === 'requesting'}>
            {cameraState === 'requesting' ? 'Requesting Camera' : 'Start Scan'}
          </button>
          <p className={`camera-status ${cameraState}`}>{cameraMessage}</p>
        </section>
      ) : null}

      {phase !== 'setup' && phase !== 'revealed' ? (
        <section className="scan-lab">
          <div className="camera-frame scan-camera">
            <video ref={videoRef} autoPlay playsInline muted />
            <div className="scan-line" />
            <div className="face-reticle">
              <span />
              <span />
              <span />
              <span />
            </div>
          </div>

          <div className="analysis-stack">
            <ScanStep label="Scanning face" active={scanProgress < 42} done={scanProgress >= 42} />
            <ScanStep label="Analyzing football identity" active={scanProgress >= 42 && scanProgress < 76} done={scanProgress >= 76} />
            <ScanStep label="Comparing legends" active={scanProgress >= 76} done={scanProgress >= 100} />
            <div className="progress-track">
              <span style={{ width: `${scanProgress}%` }} />
            </div>
            <p className={`camera-status ${cameraState}`}>{cameraMessage}</p>
            <p>{phase === 'scanning' ? 'Scanning face...' : 'Comparing legends...'}</p>
          </div>
        </section>
      ) : null}

      {phase === 'revealed' && localDna ? (
        <section className="identity-reveal">
          {(() => {
            const scanStatus = localDna.scan?.status === 'deepface_confirmed' ? 'Face Match' : 'Adapter Fallback';
            return <span className="scan-status">{scanStatus} | Threshold {Math.round((localDna.scan?.confidence_threshold ?? 0.6) * 100)}%</span>;
          })()}
          <div className="reveal-burst" />
          <span className="broadcast-kicker">YOU ARE</span>
          <h1>{(localDna.name_match ?? localDna.display_name ?? localDna.primary_match).toUpperCase()}</h1>
          <div className="identity-card">
            <div>
              <span>Name Match</span>
              <strong>{localDna.name_match ?? localDna.primary_match}</strong>
            </div>
            <div>
              <span>Style</span>
              <strong>{localDna.style ?? localDna.archetype}</strong>
            </div>
            <div>
              <span>Special Ability</span>
              <strong>{localDna.special_ability}</strong>
            </div>
            <div>
              <span>Confidence</span>
              <strong>{localDna.confidence_score ?? 82}%</strong>
            </div>
          </div>
          <div className="stat-grid">
            {Object.entries(localDna.traits ?? {}).map(([stat, value]) => (
              <div className="stat-tile" key={stat}>
                <strong>{value}</strong>
                <span>{stat}</span>
              </div>
            ))}
          </div>
          <button className="primary-action" type="button" onClick={() => navigate('/play')}>
            Enter the Pitch
          </button>
        </section>
      ) : null}
    </main>
  );
}

function ScanStep({ label, active, done }: { label: string; active: boolean; done: boolean }) {
  return (
    <div className={`scan-step ${active ? 'active' : ''} ${done ? 'done' : ''}`}>
      <span />
      <strong>{label}</strong>
    </div>
  );
}

function playRevealCue() {
  try {
    type AudioContextConstructor = typeof AudioContext;
    const audioWindow = window as Window & { webkitAudioContext?: AudioContextConstructor };
    const AudioCtor = window.AudioContext ?? audioWindow.webkitAudioContext;
    if (!AudioCtor) return;
    const context = new AudioCtor();
    const gain = context.createGain();
    gain.gain.setValueAtTime(0.0001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.18, context.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.42);
    gain.connect(context.destination);

    [220, 330, 495].forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      oscillator.type = 'triangle';
      oscillator.frequency.setValueAtTime(frequency, context.currentTime + index * 0.07);
      oscillator.connect(gain);
      oscillator.start(context.currentTime + index * 0.07);
      oscillator.stop(context.currentTime + 0.45);
    });
  } catch {
    // Browser audio may be unavailable or blocked until user interaction.
  }
}
