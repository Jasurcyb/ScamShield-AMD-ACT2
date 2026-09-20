import React from 'react';

/**
 * ExplainPanel — Displays Explainable AI breakdowns for ScamShield analysis.
 * Features:
 * - Severity-colored indicator chips
 * - Three pure-CSS confidence bars (text, url, image)
 * - Risk-band colored recommendation banner
 * - aria-live="polite" and keyboard accessible
 */
export default function ExplainPanel({ explanation }) {
  if (!explanation) return null;

  const { indicators = [], confidence_by_modality = {}, risk_band = 'low', recommendation = '' } = explanation;

  const bandColors = {
    high: { bg: '#450a0a', border: '#ef4444', text: '#fca5a5', badge: '#991b1b', badgeText: '#fecaca' },
    medium: { bg: '#451a03', border: '#f59e0b', text: '#fcd34d', badge: '#92400e', badgeText: '#fef3c7' },
    low: { bg: '#052e16', border: '#22c55e', text: '#86efac', badge: '#166534', badgeText: '#dcfce7' },
  };

  const currentTheme = bandColors[risk_band] || bandColors.low;

  const renderConfidenceBar = (label, value) => {
    const isAvailable = value !== null && value !== undefined;
    const percentage = isAvailable ? Math.round(value * 100) : 0;

    return (
      <div className="confidence-item" style={{ marginBottom: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
          <span style={{ fontWeight: 500, color: 'var(--text-secondary, #94a3b8)' }}>{label}</span>
          <span style={{ fontWeight: 600, color: isAvailable ? 'var(--text-primary, #f8fafc)' : '#64748b' }}>
            {isAvailable ? `${percentage}%` : 'N/A'}
          </span>
        </div>
        <div
          style={{
            height: '8px',
            background: 'var(--bg-secondary, #1e293b)',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
          role="progressbar"
          aria-valuenow={isAvailable ? percentage : 0}
          aria-valuemin="0"
          aria-valuemax="100"
          aria-label={`${label} confidence`}
        >
          <div
            style={{
              height: '100%',
              width: `${percentage}%`,
              background: isAvailable
                ? percentage >= 70
                  ? '#ef4444'
                  : percentage >= 40
                  ? '#f59e0b'
                  : '#22c55e'
                : 'transparent',
              transition: 'width 0.4s ease-in-out',
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <section
      className="explain-panel"
      aria-label="Explainable AI Analysis"
      style={{
        marginTop: '20px',
        padding: '20px',
        borderRadius: '10px',
        background: 'var(--bg-card, #0f172a)',
        border: '1px solid var(--border-color, #334155)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <h3
          style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: 700,
            color: 'var(--text-primary, #f8fafc)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          🔍 Why this score?
        </h3>
        <span
          style={{
            fontSize: '12px',
            fontWeight: 600,
            textTransform: 'uppercase',
            padding: '3px 10px',
            borderRadius: '999px',
            background: currentTheme.badge,
            color: currentTheme.badgeText,
          }}
        >
          Risk Band: {risk_band}
        </span>
      </div>

      {/* Recommendation Banner */}
      <div
        role="status"
        aria-live="polite"
        style={{
          padding: '14px 16px',
          borderRadius: '8px',
          background: currentTheme.bg,
          border: `1px solid ${currentTheme.border}`,
          color: currentTheme.text,
          fontSize: '14px',
          lineHeight: '1.5',
          marginBottom: '20px',
          fontWeight: 500,
        }}
      >
        <strong>Recommendation: </strong> {recommendation}
      </div>

      {/* Detected Indicators */}
      <div style={{ marginBottom: '20px' }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: 'var(--text-secondary, #94a3b8)' }}>
          Forensic Indicators Detected ({indicators.length})
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {indicators.map((ind, idx) => {
            const label = typeof ind === 'object' ? ind.label : String(ind);
            const severity = typeof ind === 'object' ? ind.severity || 1 : 1;
            const modality = typeof ind === 'object' ? ind.modality || 'text' : 'text';

            const sevColor =
              severity === 3
                ? { bg: '#7f1d1d', text: '#fecaca', border: '#ef4444' }
                : severity === 2
                ? { bg: '#78350f', text: '#fef3c7', border: '#f59e0b' }
                : { bg: '#14532d', text: '#dcfce7', border: '#22c55e' };

            return (
              <span
                key={idx}
                tabIndex={0}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: 500,
                  background: sevColor.bg,
                  color: sevColor.text,
                  border: `1px solid ${sevColor.border}`,
                  outline: 'none',
                }}
                aria-label={`Indicator: ${label}, Severity: ${severity}`}
              >
                <span>{modality === 'url' ? '🔗' : modality === 'image' ? '🖼️' : '📝'}</span>
                <span>{label}</span>
              </span>
            );
          })}
        </div>
      </div>

      {/* Confidence by Modality Bars */}
      <div>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: 'var(--text-secondary, #94a3b8)' }}>
          Confidence by Modality (Pure CSS)
        </h4>
        {renderConfidenceBar('Text / Linguistic Patterns', confidence_by_modality.text)}
        {renderConfidenceBar('URL & Typosquat Analysis', confidence_by_modality.url)}
        {renderConfidenceBar('Visual & Stego Forensics', confidence_by_modality.image)}
      </div>
    </section>
  );
}
