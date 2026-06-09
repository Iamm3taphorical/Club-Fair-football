import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { CoachResult, DNAProfile, PlayerReport, UserProfile } from '../types';

export default function FinalReport({
  user,
  dna,
  playerReport,
  coachResult,
  resetExperience,
}: {
  user: UserProfile | null;
  dna: DNAProfile | null;
  playerReport: PlayerReport | null;
  coachResult: CoachResult | null;
  resetExperience: () => void;
}) {
  const navigate = useNavigate();
  const [shareStatus, setShareStatus] = useState('');
  const report = playerReport ?? (dna ? fallbackReport(dna) : null);
  const activeDna = report?.dna_after ?? dna;

  if (!activeDna || !report) {
    return (
      <main className="report-screen empty-report">
        <h1>FOOTBALLVERSE AI</h1>
        <p>No match report is available yet.</p>
        <button className="primary-action" type="button" onClick={() => navigate('/mode')}>
          Choose Mode
        </button>
      </main>
    );
  }

  const coachRating = coachResult?.tactical_rating ?? 0;
  const playerRating = report.shareable_card.rating;
  const overall = coachRating ? Math.round((playerRating + coachRating) / 2) : playerRating;
  const shareText = [
    report.shareable_card.title,
    report.shareable_card.headline,
    `Score: ${report.score}`,
    `Accuracy: ${report.accuracy}%`,
    `Suggested Role: ${report.suggested_role}`,
  ].join('\n');

  const handleShare = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: report.shareable_card.title,
          text: shareText,
        });
        setShareStatus('Shared');
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(shareText);
        setShareStatus('Copied');
      } else {
        setShareStatus('Share unavailable');
      }
    } catch {
      setShareStatus('Share cancelled');
    }
  };

  return (
    <main className="report-screen">
      <header className="screen-header compact">
        <span className="broadcast-kicker">Match Report</span>
        <h2>{user?.name ?? 'FootballVerse Player'}</h2>
      </header>

      <section className="report-grid">
        <article className="ultimate-card">
          <div className="card-rating">{overall}</div>
          <div className="card-name">{activeDna.name_match ?? activeDna.primary_match}</div>
          <div className="card-role">{activeDna.style ?? activeDna.archetype}</div>
          <div className="card-stats">
            {Object.entries(activeDna.traits ?? {}).map(([label, value]) => (
              <div key={label}>
                <strong>{value}</strong>
                <span>{label.slice(0, 3).toUpperCase()}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="report-summary">
          <h3>{report.evolution}</h3>
          <div className="summary-metrics">
            <div><span>Goals</span><strong>{report.score}</strong></div>
            <div><span>Accuracy</span><strong>{report.accuracy}%</strong></div>
            <div><span>Reaction</span><strong>{report.reaction_time}s</strong></div>
            <div><span>Role</span><strong>{report.suggested_role}</strong></div>
          </div>
          <p>{report.match_story}</p>
          <div className="insight-row">
            <div>
              <span>Best Skill</span>
              <strong>{report.best_skill}</strong>
            </div>
            <div>
              <span>Weakness</span>
              <strong>{report.weakness}</strong>
            </div>
          </div>
        </article>

        <article className="chart-panel">
          <h3>Radar</h3>
          <RadarChart data={report.radar_chart} />
        </article>

        <article className="chart-panel">
          <h3>Performance</h3>
          <div className="performance-graph">
            {report.performance_graph.map((point) => (
              <div key={point.shot}>
                <span style={{ height: `${Math.max(12, point.goals * 18)}%` }} />
                <strong>{point.shot}</strong>
                <em>{point.result}</em>
              </div>
            ))}
          </div>
        </article>

        <article className="share-card">
          <span>{report.shareable_card.title}</span>
          <strong>{report.shareable_card.headline}</strong>
          <p>Rating {report.shareable_card.rating}</p>
          {shareStatus ? <em>{shareStatus}</em> : null}
        </article>

        <article className="coach-report">
          <h3>Coach Classification</h3>
          {coachResult ? (
            <>
              <strong>{coachResult.ranking}</strong>
              <p>{coachResult.final_score} | {coachResult.key_event}</p>
            </>
          ) : (
            <>
              <strong>Not Played</strong>
              <p>Coach Mode result will appear here.</p>
            </>
          )}
        </article>
      </section>

      <footer className="report-actions">
        <button className="secondary-action" type="button" onClick={() => navigate('/mode')}>
          Mode Selection
        </button>
        <button className="secondary-action" type="button" onClick={() => void handleShare()}>
          Share Card
        </button>
        <button
          className="primary-action"
          type="button"
          onClick={() => {
            resetExperience();
            navigate('/');
          }}
        >
          New Journey
        </button>
      </footer>
    </main>
  );
}

function RadarChart({ data }: { data: Array<{ label: string; value: number }> }) {
  const points = data.length ? data : [{ label: 'Vision', value: 80 }];
  const center = 50;
  const maxRadius = 34;
  const polygon = points.map((point, index) => {
    const angle = (-90 + (360 / points.length) * index) * (Math.PI / 180);
    const radius = maxRadius * (Math.max(0, Math.min(100, point.value)) / 100);
    return `${center + Math.cos(angle) * radius},${center + Math.sin(angle) * radius}`;
  }).join(' ');

  return (
    <div className="radar-chart">
      <svg viewBox="0 0 100 100" role="img" aria-label="Football DNA radar chart">
        {[0.35, 0.7, 1].map((scale) => (
          <circle
            className="radar-ring"
            cx={center}
            cy={center}
            key={scale}
            r={maxRadius * scale}
          />
        ))}
        {points.map((point, index) => {
          const angle = (-90 + (360 / points.length) * index) * (Math.PI / 180);
          const x = center + Math.cos(angle) * maxRadius;
          const y = center + Math.sin(angle) * maxRadius;
          return <line className="radar-axis" key={point.label} x1={center} y1={center} x2={x} y2={y} />;
        })}
        <polygon className="radar-shape" points={polygon} />
      </svg>
      <div className="radar-legend">
        {points.map((point) => (
          <span key={point.label}>{point.label} {point.value}</span>
        ))}
      </div>
    </div>
  );
}

function fallbackReport(dna: DNAProfile): PlayerReport {
  return {
    player_type: `${dna.primary_match} Archetype`,
    goals: 0,
    total_shots: 0,
    score: '0/0',
    accuracy: 0,
    reaction_time: 0,
    best_skill: dna.special_ability ?? 'Curve Shot',
    weakness: dna.weakness ?? 'Power Shots',
    suggested_role: dna.suggested_role ?? 'CAM',
    dna_before: dna,
    dna_after: dna,
    evolution: `${dna.primary_match} Archetype`,
    radar_chart: Object.entries(dna.traits ?? {}).map(([label, value]) => ({ label, value })),
    performance_graph: [],
    shareable_card: {
      title: 'FootballVerse Match Report',
      headline: `${dna.name_match ?? dna.primary_match} identity revealed`,
      rating: Math.round(Object.values(dna.traits ?? { Vision: 80 }).reduce((sum, value) => sum + value, 0) / Math.max(1, Object.values(dna.traits ?? { Vision: 80 }).length)),
    },
    match_story: 'Identity scan complete. Play Player Mode to generate the full match story.',
  };
}
