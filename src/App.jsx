import React, { useState, Suspense, lazy } from 'react';
import ExplainPanel from './components/ExplainPanel';

const ThreatLab = lazy(() => import('./components/ThreatLab'));

export default function App() {
  const [activeTab, setActiveTab] = useState('lab'); // 'scan' | 'lab'
  const [scanText, setScanText] = useState('');
  const [scanFile, setScanFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [scanError, setScanError] = useState(null);

  const handleScan = async (e) => {
    e.preventDefault();
    if (!scanText.trim() && !scanFile) {
      setScanError('Please enter text or select a file to scan.');
      return;
    }

    setLoading(true);
    setScanError(null);
    setScanResult(null);

    const formData = new FormData();
    if (scanText) formData.append('text', scanText);
    if (scanFile) formData.append('file', scanFile);

    try {
      const response = await fetch('/analyze/full', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Scan failed with status ${response.status}`);
      }

      const data = await response.json();
      setScanResult(data);
    } catch (err) {
      setScanError(err.message || 'Error occurred while analyzing target.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#090d16', color: '#f8fafc', fontFamily: 'system-ui, sans-serif' }}>
      {/* Navigation Bar */}
      <header
        style={{
          borderBottom: '1px solid #1e293b',
          background: '#0b1120',
          padding: '12px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '24px' }}>🛡️</span>
          <div>
            <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 800, letterSpacing: '-0.3px' }}>ScamShield</h1>
            <span style={{ fontSize: '11px', color: '#64748b' }}>TLN Cybersecurity Challenge 2026</span>
          </div>
        </div>

        <nav style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('lab')}
            style={{
              background: activeTab === 'lab' ? '#1e293b' : 'transparent',
              color: activeTab === 'lab' ? '#38bdf8' : '#94a3b8',
              border: '1px solid',
              borderColor: activeTab === 'lab' ? '#38bdf8' : 'transparent',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            🎯 Training Lab
          </button>
          <button
            onClick={() => setActiveTab('scan')}
            style={{
              background: activeTab === 'scan' ? '#1e293b' : 'transparent',
              color: activeTab === 'scan' ? '#38bdf8' : '#94a3b8',
              border: '1px solid',
              borderColor: activeTab === 'scan' ? '#38bdf8' : 'transparent',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            🔍 Live Scanner
          </button>
        </nav>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '960px', margin: '0 auto', padding: '24px 16px' }}>
        {activeTab === 'lab' ? (
          <Suspense fallback={<div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Loading Threat Lab...</div>}>
            <ThreatLab />
          </Suspense>
        ) : (
          <section>
            <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>🔍 Multimodal Threat Scanner</h2>
            <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '20px' }}>
              Inspect suspicious emails, SMS messages, bank receipts, and files with our hybrid forensic analysis engine.
            </p>

            <form
              onSubmit={handleScan}
              style={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '24px',
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                  Suspicious Text or URL:
                </label>
                <textarea
                  rows={4}
                  value={scanText}
                  onChange={(e) => setScanText(e.target.value)}
                  placeholder="Paste email text, SMS message, or domain..."
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    background: '#020617',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    padding: '12px',
                    color: '#f8fafc',
                    fontFamily: 'inherit',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                  Optional File / Screenshot (PNG, JPG, PDF, ZIP):
                </label>
                <input
                  type="file"
                  onChange={(e) => setScanFile(e.target.files[0] || null)}
                  style={{ color: '#94a3b8', fontSize: '13px' }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  background: '#2563eb',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 24px',
                  fontWeight: 700,
                  fontSize: '14px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? 'Analyzing Content...' : '🚀 Analyze Threat'}
              </button>
            </form>

            {scanError && (
              <div style={{ padding: '14px', background: '#450a0a', border: '1px solid #ef4444', borderRadius: '8px', color: '#fecaca', marginBottom: '20px' }}>
                ⚠️ {scanError}
              </div>
            )}

            {scanResult && (
              <div>
                <div
                  style={{
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '10px',
                    padding: '20px',
                    marginBottom: '20px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, fontSize: '18px' }}>Verdict: {scanResult.overall_risk.toUpperCase()}</h3>
                    <span style={{ fontSize: '14px', fontWeight: 700, color: scanResult.fraud_probability >= 50 ? '#ef4444' : '#22c55e' }}>
                      Probability: {scanResult.fraud_probability}%
                    </span>
                  </div>
                  <p style={{ margin: 0, color: '#cbd5e1', fontSize: '14px', lineHeight: '1.6' }}>
                    {scanResult.final_summary}
                  </p>
                </div>

                {/* Explainable AI Panel */}
                {scanResult.explanation && <ExplainPanel explanation={scanResult.explanation} />}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
