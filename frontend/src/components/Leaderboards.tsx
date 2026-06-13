import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { UserProfile } from '../types';

type LeaderboardEntry = {
  player_id: string;
  name: string;
  score: number;
  rank: string;
  title: string;
};

export default function Leaderboards({ user }: { user: UserProfile | null }) {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'Player' | 'Coach' | 'Fan'>('Player');
  const [data, setData] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    api.getLeaderboard(activeTab)
      .then(setData)
      .catch((err) => {
        console.error("Failed to load leaderboard:", err);
        setData([]);
      })
      .finally(() => setLoading(false));
  }, [activeTab]);

  return (
    <main className="leaderboard-screen">
      <header className="screen-header compact">
        <span className="broadcast-kicker">Global Rankings</span>
        <h2>LEADERBOARDS</h2>
        <button className="secondary-action" type="button" onClick={() => navigate('/mode')} style={{ marginTop: '1rem' }}>
          Back to Tunnel
        </button>
      </header>

      <section className="leaderboard-container">
        <div className="leaderboard-tabs">
          <button 
            className={`tab-button ${activeTab === 'Player' ? 'active' : ''}`}
            onClick={() => setActiveTab('Player')}
            type="button"
          >
            Player Arena
          </button>
          <button 
            className={`tab-button ${activeTab === 'Coach' ? 'active' : ''}`}
            onClick={() => setActiveTab('Coach')}
            type="button"
          >
            Tactical Coach
          </button>
          <button 
            className={`tab-button ${activeTab === 'Fan' ? 'active' : ''}`}
            onClick={() => setActiveTab('Fan')}
            type="button"
          >
            Fan Trivia
          </button>
        </div>

        <div className="leaderboard-list">
          {loading ? (
            <div className="loading-state">Loading rankings...</div>
          ) : data.length === 0 ? (
            <div className="empty-state">No rankings yet. Play a game to be the first!</div>
          ) : (
            <table className="leaderboard-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Player</th>
                  <th>Score</th>
                  <th>Title</th>
                </tr>
              </thead>
              <tbody>
                {data.map((entry) => (
                  <tr key={entry.player_id} className={user?.user_id === entry.player_id ? 'highlight-row' : ''}>
                    <td>
                      {entry.rank === '1' ? '🥇' : entry.rank === '2' ? '🥈' : entry.rank === '3' ? '🥉' : `#${entry.rank}`}
                    </td>
                    <td>{entry.name} {user?.user_id === entry.player_id && '(You)'}</td>
                    <td>{entry.score.toLocaleString()}</td>
                    <td>{entry.title}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </main>
  );
}
