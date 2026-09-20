import React, { useState, useEffect, useRef } from 'react';

const STATS_KEY = 'scamshield_lab_stats_v1';
const FALLBACK_KEY = 'scamshield_lab_stats';

const DEFAULT_STATS = { correct: 0, total: 0, streak: 0, best: 0 };

function getInitialStats() {
  try {
    const raw = localStorage.getItem(STATS_KEY) || localStorage.getItem(FALLBACK_KEY);
    if (!raw) return DEFAULT_STATS;
    const parsed = JSON.parse(raw);
    if (
      typeof parsed.correct === 'number' &&
      typeof parsed.total === 'number' &&
      typeof parsed.streak === 'number' &&
      typeof parsed.best === 'number'
    ) {
      return parsed;
    }
  } catch (err) {
    // Corrupted localStorage silently defaults
  }
  return DEFAULT_STATS;
}

export default function ThreatLab() {
  const [difficulty, setDifficulty] = useState('medium');
  const [phase, setPhase] = useState('idle'); // idle | loading | awaiting_answer | revealed
  const [threat, setThreat] = useState(null);
  const [revealData, setRevealData] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [stats, setStats] = useState(getInitialStats);

  const lastClickRef = useRef(0);

  // Sync stats to localStorage safely
  useEffect(() => {
    try {
      localStorage.setItem(STATS_KEY, JSON.stringify(stats));
    } catch (err) {
      // Storage quota or private browsing error suppressed
    }
  }, [stats]);

  // Generate a simulated threat with 500ms debounce
  const handleGenerateThreat = async (chosenDifficulty = difficulty) => {
    const now = Date.now();
    if (now - lastClickRef.current < 500) {
      return; // 500ms debounce against double clicks
    }
    lastClickRef.current = now;

    setPhase('loading');
    setErrorMessage(null);
    setRevealData(null);

    try {
      const response = await fetch('/api/simulate/threat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ difficulty: chosenDifficulty }),
      });

      if (response.status === 429) {
        setErrorMessage('Too many requests, wait a minute');
        setPhase('idle');
        return;
      }

      if (!response.ok) {
        throw new Error(`Failed to generate threat (HTTP ${response.status})`);
      }

      const data = await response.json();
      setThreat(data);
      setPhase('awaiting_answer');
    } catch (err) {
      setErrorMessage('Network error or service unavailable. Please retry.');
      setPhase('idle');
    }
  };

  // Submit user's answer (scam vs legit)
  const handleAnswer = async (userSaysScam) => {
    if (!threat || phase !== 'awaiting_answer') return;

    setPhase('loading');
    setErrorMessage(null);

    try {
      const response = await fetch('/api/simulate/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          threat_id: threat.threat_id,
          user_says_scam: userSaysScam,
        }),
      });

      if (response.status === 410 || response.status === 404) {
        setErrorMessage('Session expired, generate a new threat');
        setPhase('idle');
        return;
      }

      if (response.status === 409) {
        setErrorMessage('Threat already answered. Generate a new threat to continue.');
        setPhase('idle');
        return;
      }

      if (response.status === 429) {
        setErrorMessage('Too many requests, wait a minute');
        setPhase('awaiting_answer');
        return;
      }

      if (!response.ok) {
        throw new Error(`Evaluation failed (HTTP ${response.status})`);
      }

      const result = await response.json();
      setRevealData(result);
      setPhase('revealed');

      // Update statistics
      setStats((prev) => {
        const isCorrect = result.correct;
        const newCorrect = prev.correct + (isCorrect ? 1 : 0);
        const newTotal = prev.total + 1;
        const newStreak = isCorrect ? prev.streak + 1 : 0;
        const newBest = Math.max(prev.best, newStreak);
        return {
          correct: newCorrect,
          total: newTotal,
          streak: newStreak,
          best: newBest,
        };
      });
    } catch (err) {
      setErrorMessage('Unable to verify answer. Please check connection and try again.');
      setPhase('awaiting_answer');
    }
  };

  // Reset stats with confirmation
  const handleResetStats = () => {
    if (window.confirm('Are you sure you want to reset your training statistics?')) {
      setStats(DEFAULT_STATS);
      try {
        localStorage.removeItem(STATS_KEY);
        localStorage.removeItem(FALLBACK_KEY);
      } catch (err) {}
    }
  };

  const accuracy = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;

  const channelIcons = {
    email: '📧 EMAIL',
    sms: '💬 SMS',
    chat: '🗨️ CHAT',
  };

  return (
    <div
      className="threat-lab-container"
      style={{
        maxWidth: '860px',
        margin: '0 auto',
        padding: '24px 16px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        color: 'var(--text-primary, #f8fafc)',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '24px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '26px', fontWeight: 800, margin: '0 0 8px 0', letterSpacing: '-0.5px' }}>
          🎯 Threat Simulation Lab
        </h2>
        <p style={{ margin: 0, color: 'var(--text-secondary, #94a3b8)', fontSize: '15px' }}>
          Train your fraud detection reflexes against realistic simulated attacks across email, SMS, and messaging apps.
        </p>
      </div>

      {/* Stats Bar */}
      <div
        className="stats-bar"
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--bg-card, #0f172a)',
          border: '1px solid var(--border-color, #334155)',
          borderRadius: '10px',
          padding: '12px 20px',
          marginBottom: '20px',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', fontSize: '14px' }}>
          <div>
            <span style={{ color: 'var(--text-secondary, #94a3b8)' }}>Accuracy: </span>
            <strong style={{ color: accuracy >= 70 ? '#22c55e' : accuracy >= 40 ? '#f59e0b' : '#ef4444' }}>
              {accuracy}% ({stats.correct}/{stats.total})
            </strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-secondary, #94a3b8)' }}>Streak: </span>
            <strong>🔥 {stats.streak}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-secondary, #94a3b8)' }}>Best Streak: </span>
            <strong>⭐ {stats.best}</strong>
          </div>
        </div>
        <button
          onClick={handleResetStats}
          style={{
            background: 'transparent',
            border: '1px solid #475569',
            color: '#94a3b8',
            borderRadius: '6px',
            padding: '4px 10px',
            fontSize: '12px',
            cursor: 'pointer',
          }}
          aria-label="Reset training statistics"
        >
          Reset stats
        </button>
      </div>

      {/* Controls: Difficulty & Generate */}
      <div
        className="controls-row"
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        <div
          role="radiogroup"
          aria-label="Select threat difficulty"
          style={{
            display: 'inline-flex',
            background: 'var(--bg-card, #0f172a)',
            padding: '4px',
            borderRadius: '8px',
            border: '1px solid var(--border-color, #334155)',
          }}
        >
          {['easy', 'medium', 'hard'].map((tier) => (
            <button
              key={tier}
              role="radio"
              aria-checked={difficulty === tier}
              onClick={() => {
                setDifficulty(tier);
                if (phase === 'idle') handleGenerateThreat(tier);
              }}
              style={{
                background: difficulty === tier ? 'var(--accent-primary, #3b82f6)' : 'transparent',
                color: difficulty === tier ? '#ffffff' : 'var(--text-secondary, #94a3b8)',
                border: 'none',
                padding: '6px 16px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                textTransform: 'capitalize',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              {tier}
            </button>
          ))}
        </div>

        <button
          onClick={() => handleGenerateThreat(difficulty)}
          disabled={phase === 'loading'}
          style={{
            background: 'var(--accent-primary, #3b82f6)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            padding: '10px 20px',
            fontWeight: 700,
            fontSize: '14px',
            cursor: phase === 'loading' ? 'not-allowed' : 'pointer',
            opacity: phase === 'loading' ? 0.7 : 1,
            transition: 'opacity 0.2s ease',
          }}
          aria-label="Generate new simulation threat"
        >
          {phase === 'loading' ? 'Loading threat...' : '⚡ Generate threat'}
        </button>
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div
          role="alert"
          style={{
            padding: '14px 18px',
            background: '#450a0a',
            border: '1px solid #ef4444',
            color: '#fecaca',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>⚠️ {errorMessage}</span>
          <button
            onClick={() => handleGenerateThreat(difficulty)}
            style={{
              background: '#ef4444',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 10px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Threat Email / Message Card */}
      {threat && (
        <div
          className="mail-client-card"
          style={{
            background: 'var(--bg-card, #0f172a)',
            border: '1px solid var(--border-color, #334155)',
            borderRadius: '12px',
            overflow: 'hidden',
            marginBottom: '24px',
          }}
        >
          {/* Mail Header */}
          <div
            style={{
              padding: '16px 20px',
              background: 'rgba(255,255,255,0.02)',
              borderBottom: '1px solid var(--border-color, #334155)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  padding: '3px 10px',
                  borderRadius: '4px',
                  background: 'var(--bg-secondary, #1e293b)',
                  color: 'var(--accent-primary, #60a5fa)',
                }}
              >
                {channelIcons[threat.channel] || threat.channel.toUpperCase()}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary, #94a3b8)', textTransform: 'capitalize' }}>
                Difficulty: <strong>{threat.difficulty}</strong>
              </span>
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary, #94a3b8)', marginBottom: '4px' }}>
              <strong>From: </strong>
              <span style={{ color: 'var(--text-primary, #f8fafc)' }}>{threat.sender}</span>
            </div>
            <h3 style={{ margin: '6px 0 0 0', fontSize: '17px', fontWeight: 700, color: 'var(--text-primary, #f8fafc)' }}>
              {threat.subject}
            </h3>
          </div>

          {/* Mail Body */}
          <div style={{ padding: '20px' }}>
            <div
              style={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                fontFamily: 'inherit',
                fontSize: '14px',
                lineHeight: '1.6',
                color: 'var(--text-primary, #f1f5f9)',
                background: 'var(--bg-input, #020617)',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid var(--border-color, #1e293b)',
              }}
            >
              {threat.body}
            </div>
          </div>
        </div>
      )}

      {/* Answer Action Row */}
      {phase === 'awaiting_answer' && (
        <div
          className="answer-row"
          style={{
            display: 'flex',
            gap: '16px',
            marginBottom: '24px',
            flexWrap: 'wrap',
          }}
        >
          <button
            onClick={() => handleAnswer(true)}
            style={{
              flex: '1 1 200px',
              padding: '14px 20px',
              background: '#991b1b',
              color: '#ffffff',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
            aria-label="Classify simulated message as SCAM"
          >
            🚨 This is a SCAM
          </button>
          <button
            onClick={() => handleAnswer(false)}
            style={{
              flex: '1 1 200px',
              padding: '14px 20px',
              background: '#166534',
              color: '#ffffff',
              border: '1px solid #22c55e',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
            aria-label="Classify simulated message as LEGIT"
          >
            ✅ This is LEGIT
          </button>
        </div>
      )}

      {/* Revealed Feedback Panel */}
      {phase === 'revealed' && revealData && (
        <div
          role="status"
          className="feedback-panel"
          style={{
            background: revealData.correct ? '#052e16' : '#450a0a',
            border: `1px solid ${revealData.correct ? '#22c55e' : '#ef4444'}`,
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '24px',
            animation: 'fadeIn 0.3s ease-in',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ margin: 0, fontSize: '20px', fontWeight: 800, color: revealData.correct ? '#86efac' : '#fca5a5' }}>
              {revealData.correct ? '🎉 Correct!' : '❌ Incorrect!'} It was {revealData.was_scam ? 'a SCAM' : 'LEGIT'}
            </h3>
            <span
              style={{
                fontSize: '13px',
                fontWeight: 700,
                padding: '4px 10px',
                borderRadius: '6px',
                background: revealData.was_scam ? '#7f1d1d' : '#14532d',
                color: '#ffffff',
              }}
            >
              Risk Score: {revealData.score}/100
            </span>
          </div>

          <p style={{ margin: '0 0 16px 0', fontSize: '15px', lineHeight: '1.5', color: '#f8fafc' }}>
            {revealData.explanation}
          </p>

          {revealData.indicators && revealData.indicators.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <strong style={{ fontSize: '13px', color: '#e2e8f0', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Key Warning Indicators:
              </strong>
              <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px', color: '#cbd5e1', fontSize: '14px' }}>
                {revealData.indicators.map((ind, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>
                    {ind}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {revealData.tip && (
            <div
              style={{
                background: 'rgba(0,0,0,0.2)',
                padding: '12px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                color: '#e2e8f0',
                borderLeft: '4px solid #3b82f6',
                marginBottom: '20px',
              }}
            >
              💡 <strong>Pro Tip: </strong> {revealData.tip}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              onClick={() => handleGenerateThreat(difficulty)}
              style={{
                background: 'var(--accent-primary, #3b82f6)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 22px',
                fontWeight: 700,
                fontSize: '14px',
                cursor: 'pointer',
              }}
            >
              Next threat →
            </button>
          </div>
        </div>
      )}

      {/* Mobile Stack CSS */}
      <style>{`
        @media (max-width: 640px) {
          .answer-row button {
            flex: 1 1 100% !important;
          }
          .controls-row {
            flex-direction: column;
            align-items: stretch !important;
          }
        }
      `}</style>
    </div>
  );
}
