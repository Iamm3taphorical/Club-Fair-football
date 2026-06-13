import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { playClueCue, speakCommentary } from '../audio';
import type { UserProfile } from '../types';

type Challenge = {
  category: keyof Scores;
  clues: string[];
  options: string[];
  answer: string;
};

type Scores = {
  player: number;
  coach: number;
  stadium: number;
  match: number;
};

const TOTAL_TIME = 120;

const CATEGORIES: Array<{ id: keyof Scores; label: string }> = [
  { id: 'player', label: 'Guess The Player' },
  { id: 'coach', label: 'Guess The Coach' },
  { id: 'stadium', label: 'Guess The Stadium' },
  { id: 'match', label: 'Guess The Iconic Match' },
];

function titleForScore(totalPoints: number) {
  if (totalPoints >= 35) return 'FootballVerse Immortal';
  if (totalPoints >= 30) return 'Tactical Genius';
  if (totalPoints >= 20) return 'Football Historian';
  if (totalPoints >= 10) return 'Matchday Expert';
  return 'Sunday Fan';
}

export default function FanMode({ user }: { user: UserProfile | null }) {
  const navigate = useNavigate();
  const [stage, setStage] = useState<'loading' | 'playing' | 'completed'>('loading');
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [challengeIndex, setChallengeIndex] = useState(0);
  const [clueIndex, setClueIndex] = useState(0);
  const [scores, setScores] = useState<Scores>({ player: 0, coach: 0, stadium: 0, match: 0 });
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME);
  const [title, setTitle] = useState('');
  const [feedback, setFeedback] = useState<{ option: string; correct: boolean } | null>(null);
  const [transitionLabel, setTransitionLabel] = useState<string | null>(null);
  const [loadError, setLoadError] = useState('');
  const deadlineRef = useRef<number | null>(null);
  const endedRef = useRef(false);

  const applyChallenges = useCallback((nextChallenges: Challenge[]) => {
    setChallenges(nextChallenges);
    setChallengeIndex(0);
    setClueIndex(0);
    setScores({ player: 0, coach: 0, stadium: 0, match: 0 });
    setTimeLeft(TOTAL_TIME);
    deadlineRef.current = null;
    endedRef.current = false;
    setStage('playing');
  }, []);

  const loadChallenges = useCallback(() => {
    setLoadError('');
    setStage('loading');
    api.startFanGame()
      .then((res) => applyChallenges(res.challenges as Challenge[]))
      .catch(() => {
        setLoadError('Trivia archives are unreachable. Check the backend connection and retry.');
      });
  }, [applyChallenges]);

  useEffect(() => {
    let cancelled = false;
    api.startFanGame()
      .then((res) => {
        if (!cancelled) applyChallenges(res.challenges as Challenge[]);
      })
      .catch(() => {
        if (!cancelled) setLoadError('Trivia archives are unreachable. Check the backend connection and retry.');
      });
    return () => {
      cancelled = true;
    };
  }, [applyChallenges]);

  const endGame = useCallback((finalScores = scores, finalTimeLeft = timeLeft) => {
    if (endedRef.current) return;
    endedRef.current = true;
    const totalPoints = finalScores.player + finalScores.coach + finalScores.stadium + finalScores.match;
    const earnedTitle = titleForScore(totalPoints);
    setTitle(earnedTitle);
    setStage('completed');
    speakCommentary(`Final whistle. ${earnedTitle}.`);

    api.completeFanGame({
      user_id: user?.user_id ?? 'guest',
      name: user?.name ?? 'FootballVerse Player',
      total_points: totalPoints,
      completion_time: TOTAL_TIME - finalTimeLeft,
      title: earnedTitle,
    }).catch(console.error);
  }, [scores, timeLeft, user?.name, user?.user_id]);

  useEffect(() => {
    if (stage !== 'playing') return;
    if (deadlineRef.current === null) deadlineRef.current = Date.now() + timeLeft * 1000;
    const timer = window.setInterval(() => {
      const remaining = Math.max(0, Math.ceil(((deadlineRef.current ?? Date.now()) - Date.now()) / 1000));
      setTimeLeft(remaining);
      if (remaining <= 0) endGame(scores, 0);
    }, 250);
    return () => window.clearInterval(timer);
  }, [endGame, scores, stage, timeLeft]);

  useEffect(() => {
    if (stage === 'playing') playClueCue();
  }, [challengeIndex, clueIndex, stage]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const advanceCategory = useCallback((nextScores = scores) => {
    setFeedback(null);
    if (challengeIndex < CATEGORIES.length - 1) {
      const nextLabel = CATEGORIES[challengeIndex + 1].label.toUpperCase();
      setTransitionLabel(`NEXT UP: ${nextLabel}`);
      speakCommentary(nextLabel);
      window.setTimeout(() => {
        setChallengeIndex((prev) => prev + 1);
        setClueIndex(0);
        setTransitionLabel(null);
      }, 850);
      return;
    }
    endGame(nextScores, timeLeft);
  }, [challengeIndex, endGame, scores, timeLeft]);

  const revealNextClue = useCallback(() => {
    const current = challenges[challengeIndex];
    if (!current || feedback) return;
    if (clueIndex < 9) {
      setClueIndex((prev) => prev + 1);
      return;
    }
    const nextScores = { ...scores, [current.category]: 0 };
    setScores(nextScores);
    advanceCategory(nextScores);
  }, [advanceCategory, challengeIndex, challenges, clueIndex, feedback, scores]);

  const handleGuess = (selectedOption: string) => {
    const current = challenges[challengeIndex];
    if (!current || feedback) return;

    if (selectedOption === current.answer) {
      const nextScores = { ...scores, [current.category]: 10 - clueIndex };
      setFeedback({ option: selectedOption, correct: true });
      setScores(nextScores);
      window.setTimeout(() => advanceCategory(nextScores), 650);
      return;
    }

    setFeedback({ option: selectedOption, correct: false });
    window.setTimeout(() => {
      setFeedback(null);
      if (clueIndex < 9) {
        setClueIndex((prev) => prev + 1);
      } else {
        const nextScores = { ...scores, [current.category]: 0 };
        setScores(nextScores);
        advanceCategory(nextScores);
      }
    }, 650);
  };

  const skipCategory = () => {
    const current = challenges[challengeIndex];
    if (!current || feedback) return;
    const nextScores = { ...scores, [current.category]: 0 };
    setScores(nextScores);
    advanceCategory(nextScores);
  };

  if (stage === 'loading') {
    return (
      <main className="fan-screen fan-cinematic loading-fan">
        <h2>Loading Trivia Archives...</h2>
        {loadError ? (
          <div className="fan-load-error">
            <p>{loadError}</p>
            <button className="secondary-action" type="button" onClick={loadChallenges}>Retry</button>
            <button className="primary-action" type="button" onClick={() => navigate('/mode')}>Back to Tunnel</button>
          </div>
        ) : null}
      </main>
    );
  }

  if (stage === 'completed') {
    const totalPoints = scores.player + scores.coach + scores.stadium + scores.match;
    return (
      <main className="fan-screen fan-cinematic fan-complete">
        <section className="fan-result-card">
          <h1>TRIVIA COMPLETE</h1>
          <h3>{title}</h3>
          <div className="fan-score-list">
            {CATEGORIES.map((category) => (
              <div key={category.id}>
                <span>{category.label}</span>
                <strong>{scores[category.id]} pts</strong>
              </div>
            ))}
            <div className="fan-total">
              <span>Total Score</span>
              <strong>{totalPoints} / 40</strong>
            </div>
            <div>
              <span>Time Taken</span>
              <strong>{formatTime(TOTAL_TIME - timeLeft)}</strong>
            </div>
          </div>
          <div className="fan-actions centered">
            <button className="secondary-action" type="button" onClick={() => navigate('/mode')}>Back to Tunnel</button>
            <button className="primary-action" type="button" onClick={() => navigate('/leaderboards')}>View Leaderboard</button>
          </div>
        </section>
      </main>
    );
  }

  const currentChallenge = challenges[challengeIndex];
  if (!currentChallenge) {
    return (
      <main className="fan-screen fan-cinematic loading-fan">
        <h2>Trivia challenge unavailable</h2>
        <div className="fan-load-error">
          <p>The current category could not be loaded.</p>
          <button className="secondary-action" type="button" onClick={loadChallenges}>Restart Trivia</button>
          <button className="primary-action" type="button" onClick={() => navigate('/mode')}>Back to Tunnel</button>
        </div>
      </main>
    );
  }

  return (
    <main className="fan-screen fan-cinematic">
      {transitionLabel ? <div className="category-transition">{transitionLabel}</div> : null}
      <header className="fan-header">
        <div>
          <span>CATEGORY {challengeIndex + 1} OF 4</span>
          <h2>{CATEGORIES[challengeIndex].label}</h2>
        </div>
        <div className={timeLeft <= 30 ? 'fan-timer danger' : 'fan-timer'}>
          {formatTime(timeLeft)}
        </div>
      </header>

      <section className="fan-play-area">
        <div className="fan-clue-meta">
          <h3>Clue {clueIndex + 1} of 10</h3>
          <span>Potential Points: {10 - clueIndex}</span>
        </div>

        <div className="fan-clue-card" key={`${challengeIndex}-${clueIndex}`}>
          {currentChallenge.clues[clueIndex]}
        </div>

        <div className="fan-actions">
          <button className="secondary-action" type="button" onClick={revealNextClue} disabled={feedback !== null}>
            Next Clue
          </button>
          <button className="secondary-action" type="button" onClick={skipCategory} disabled={feedback !== null}>
            Skip
          </button>
        </div>

        <div className="fan-options">
          {currentChallenge.options.map((option, index) => (
            <button
              key={option}
              className={[
                'fan-option',
                feedback?.option === option ? (feedback.correct ? 'correct' : 'wrong') : '',
              ].join(' ')}
              type="button"
              onClick={() => handleGuess(option)}
              disabled={feedback !== null}
            >
              <span>{['A', 'B', 'C', 'D'][index]}</span>
              {option}
            </button>
          ))}
        </div>
      </section>

      <footer className="fan-progress">
        {CATEGORIES.map((cat, idx) => (
          <div
            key={cat.id}
            className={idx < challengeIndex ? 'done' : idx === challengeIndex ? 'active' : ''}
          />
        ))}
      </footer>
    </main>
  );
}
