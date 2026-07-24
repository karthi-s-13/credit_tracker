export default function CategoryCard({ category, earned, required, color }) {
  const pct = required > 0 ? Math.min((earned / required) * 100, 100) : 0;
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDash = (pct / 100) * circumference;

  const colorMap = {
    HS: { bg: '#eff6ff', ring: '#3b82f6', text: '#1d4ed8' },
    BS: { bg: '#f0fdf4', ring: '#22c55e', text: '#15803d' },
    ES: { bg: '#fefce8', ring: '#eab308', text: '#854d0e' },
    PC: { bg: '#fdf4ff', ring: '#a855f7', text: '#7e22ce' },
    PE: { bg: '#fff7ed', ring: '#f97316', text: '#c2410c' },
    OE: { bg: '#f0f9ff', ring: '#06b6d4', text: '#0e7490' },
    EEC: { bg: '#fdf2f8', ring: '#ec4899', text: '#be185d' },
    MC: { bg: '#f0fdf4', ring: '#10b981', text: '#065f46' },
  };
  const c = colorMap[category.code] || { bg: '#eff6ff', ring: '#3b82f6', text: '#1d4ed8' };

  return (
    <div className="card card-hover" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
      {/* Top row: label + badge */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
        <div>
          <div style={{
            display: 'inline-block', padding: '0.15rem 0.5rem',
            background: c.bg, color: c.text,
            borderRadius: 99, fontSize: '0.7rem', fontWeight: 700,
            marginBottom: '0.375rem',
          }}>
            {category.code}
          </div>
          <div style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--neutral-800)', lineHeight: 1.3 }}>
            {category.label}
          </div>
        </div>

        {/* Circular progress */}
        <div className="progress-ring-wrapper" style={{ flexShrink: 0 }}>
          <svg width={86} height={86} viewBox="0 0 86 86">
            {/* Track */}
            <circle cx={43} cy={43} r={radius} fill="none" strokeWidth={7} stroke="var(--neutral-100)" />
            {/* Progress */}
            <circle
              cx={43} cy={43} r={radius}
              fill="none" strokeWidth={7}
              stroke={c.ring}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={circumference - strokeDash}
              style={{ transition: 'stroke-dashoffset 0.8s ease' }}
            />
          </svg>
          <div className="progress-ring-text">
            <span style={{ fontSize: '1.05rem', fontWeight: 800, color: c.text }}>{earned}</span>
            <span style={{ fontSize: '0.65rem', color: 'var(--neutral-400)', lineHeight: 1 }}>/{required}</span>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem', fontSize: '0.75rem' }}>
          <span style={{ color: 'var(--neutral-600)' }}>{earned} credits earned</span>
          <span style={{ fontWeight: 600, color: c.text }}>{Math.round(pct)}%</span>
        </div>
        <div style={{ height: 6, background: 'var(--neutral-100)', borderRadius: 99, overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${c.ring}, ${c.text})`,
            borderRadius: 99,
            transition: 'width 0.8s ease',
          }} />
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--neutral-400)', marginTop: '0.25rem' }}>
          {required - earned > 0 ? `${required - earned} credits remaining` : '✓ Target achieved!'}
        </div>
      </div>
    </div>
  );
}
