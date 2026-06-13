import { useNavigate } from 'react-router-dom';

export default function Contributors() {
  const navigate = useNavigate();
  const contributors = [
    {
      name: 'Mahir Dyan',
      designation: 'Developer, Senior Executive',
      department: 'Human Resources Department, BRAC University Computer Club',
      photo: '/images/mahir.webp',
      objectPosition: 'center',
      scale: 1,
      facebook: 'https://www.facebook.com/mahir.dyan.554260',
      instagram: 'https://www.instagram.com/_.mahirdyan_._/',
      github: 'https://github.com/Iamm3taphorical',

    },
    {
      name: 'Dibyo Singho Barua Subrajit',
      designation: 'Developer, Senior Executive',
      department: 'Human Resources Department, BRAC University Computer Club',
      photo: '/images/subrajit.JPG',
      objectPosition: 'center 40%',
      scale: 1,
      facebook: 'https://www.facebook.com/iamsubrajit',
      instagram: 'https://www.instagram.com/subra.lmao/',
      github: 'https://github.com/whosubrajit',

    },
    {
      name: 'Adittya Dey',
      designation: 'Developer, Senior Executive',
      department: 'Human Resources Department, BRAC University Computer Club',
      photo: '/images/adittya.jpg',
      objectPosition: '80% center', // shifts the image left to show more of the right side
      scale: 1,
      facebook: 'https://www.facebook.com/13.adityatoton',
      instagram: 'https://www.instagram.com/_colo_ssus_/',
      github: 'https://github.com/Adittya202',

    },
  ];

  return (
    <main className="mode-screen">
      <header className="screen-header">
        <span className="broadcast-kicker">Credits</span>
        <h2>OUR CONTRIBUTORS</h2>
      </header>

      <style>{`
        .contrib-card:hover .contrib-img {
          transform: scale(calc(var(--base-scale) * 1.06)) !important;
        }
        .contrib-info {
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.4s ease;
          pointer-events: none;
        }
        .contrib-card:hover .contrib-info {
          opacity: 1;
          transform: translateY(0);
          pointer-events: auto;
        }
        .social-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 42px;
          height: 42px;
          border-radius: 50%;
          background: rgba(255,255,255,0.15);
          transition: transform 0.2s, background 0.2s;
          backdrop-filter: blur(4px);
        }
        .social-icon img {
          width: 22px;
          height: 22px;
          object-fit: contain;
        }
        .social-icon:hover {
          background: var(--accent-color, #ffb703) !important;
          transform: scale(1.15);
        }
      `}</style>

      <section style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '2rem' }}>
        {contributors.map((c, i) => (
          <div key={i} className="contrib-card" style={{
            position: 'relative',
            width: '280px',
            height: '400px',
            borderRadius: '12px',
            overflow: 'hidden',
            border: '1px solid rgba(255,255,255,0.1)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            cursor: 'pointer'
          }}>
            <img className="contrib-img" src={c.photo} alt={c.name} style={{
              width: '100%', height: '100%', objectFit: 'cover', objectPosition: c.objectPosition,
              transform: `scale(${c.scale})`,
              transition: 'transform 0.4s ease',
              '--base-scale': c.scale
            } as React.CSSProperties} />
            <div className="contrib-info" style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              padding: '3rem 1.5rem 1.5rem',
              background: 'linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.8) 40%, transparent 100%)',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 0.3rem 0', color: 'white', fontSize: '1.25rem', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>{c.name}</h3>
              <p style={{ margin: '0 0 0.4rem 0', color: 'var(--accent-color, #ffb703)', fontWeight: 'bold', textShadow: '0 1px 2px rgba(0,0,0,0.8)' }}>{c.designation}</p>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: '#ddd', lineHeight: '1.3' }}>{c.department}</p>

              <div className="contrib-social" style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '1rem'
              }}>
                <a href={c.facebook} target="_blank" rel="noreferrer" className="social-icon" title="Facebook">
                  <img src="/images/facebook.png" alt="Facebook" />
                </a>
                <a href={c.instagram} target="_blank" rel="noreferrer" className="social-icon" title="Instagram">
                  <img src="/images/instagram.png" alt="Instagram" />
                </a>
                <a href={c.github} target="_blank" rel="noreferrer" className="social-icon" title="GitHub">
                  <img src="/images/github.svg" alt="GitHub" />
                </a>


              </div>
            </div>
          </div>
        ))}
      </section>

      <section style={{ marginTop: '3rem', display: 'flex', justifyContent: 'center' }}>
        <button className="secondary-action" type="button" onClick={() => navigate(-1)} style={{ padding: '1rem 3rem', fontSize: '1.1rem' }}>
          Back
        </button>
      </section>
    </main>
  );
}
