import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, ArrowRight, BookOpen, BarChart3, Shield } from 'lucide-react';
import api from '../api';
import { useToast } from '../components/ToastProvider';
import '../index.css';

const FEATURES = [
  { icon: BookOpen, title: 'Full Curriculum', desc: 'View all 259 courses across 8 categories' },
  { icon: BarChart3, title: 'Credit Tracker', desc: 'Real-time progress against 169 required credits' },
  { icon: Shield, title: 'OCR Upload', desc: 'Auto-extract results from PDF marksheets' },
];

const SUPPORTED_DEPTS = {
  '02': 'BME',
  '03': 'CIVIL',
  '04': 'CSE',
  '05': 'EEE',
  '06': 'ECE',
  '08': 'MECH',
  '10': 'CSECS',
  '11': 'CSEIOT',
  '21': 'CHEM',
  '22': 'IT',
  '23': 'AIDS',
  '24': 'AIML',
  '25': 'AGRI',
};

export default function LoginPage() {
  const [regNo, setRegNo] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const validateRegNo = (val) => {
    if (!/^\d{12}$/.test(val)) return 'Register number must be exactly 12 digits';
    const deptCode = val.slice(6, 8);
    if (!SUPPORTED_DEPTS[deptCode]) return `Department code "${deptCode}" is not supported`;
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const err = validateRegNo(regNo);
    if (err) { setError(err); return; }
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', {
        register_number: regNo,
        name: name.trim() || undefined,
      });
      localStorage.setItem('student', JSON.stringify(data.student));
      toast('Welcome! Redirecting to your dashboard…', 'success');
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(msg);
      toast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const deptCode = regNo.length >= 8 ? regNo.slice(6, 8) : null;
  const yearJoining = regNo.length >= 6 ? '20' + regNo.slice(4, 6) : null;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'linear-gradient(135deg, #eff6ff 0%, #ffffff 50%, #dbeafe 100%)' }}>

      {/* ─── Left Panel ──── */}
      <div style={{
        flex: '0 0 50%',
        background: 'linear-gradient(160deg, var(--primary-700) 0%, var(--primary-900) 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '3rem',
        position: 'relative',
        overflow: 'hidden',
      }} className="hide-mobile">
        {/* Decorative circles */}
        <div style={{
          position: 'absolute', top: '-80px', right: '-80px',
          width: '300px', height: '300px', borderRadius: '50%',
          background: 'rgb(255 255 255 / 0.05)',
        }} />
        <div style={{
          position: 'absolute', bottom: '-100px', left: '-60px',
          width: '400px', height: '400px', borderRadius: '50%',
          background: 'rgb(255 255 255 / 0.04)',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: 'rgb(255 255 255 / 0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <GraduationCap size={26} color="#fff" />
            </div>
            <div>
              <div style={{ color: '#fff', fontWeight: 700, fontSize: '1.1rem', lineHeight: 1.2 }}>Credit Tracker</div>
              <div style={{ color: 'rgb(255 255 255 / 0.6)', fontSize: '0.8rem' }}>Saveetha Engineering College</div>
            </div>
          </div>

          <h1 style={{ color: '#fff', fontSize: '2.2rem', fontWeight: 800, lineHeight: 1.2, marginBottom: '1rem' }}>
            Track Your Academic<br />Journey Effortlessly
          </h1>
          <p style={{ color: 'rgb(255 255 255 / 0.7)', fontSize: '1rem', lineHeight: 1.7, marginBottom: '1.5rem' }}>
            Monitor curriculum completion, upload result PDFs, and stay on top of your credit requirements — all in one place.
          </p>

          {/* Last Updated Notice */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: 12,
            padding: '1rem 1.25rem',
            marginBottom: '2rem',
            color: '#fff',
            fontSize: '0.85rem',
            lineHeight: '1.5',
            backdropFilter: 'blur(4px)',
          }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📅 Record Notice (Last Updated: 8.5.26)
            </div>
            <div style={{ color: 'rgba(255, 255, 255, 0.85)' }}>
              Current course completion records were last updated on <strong>8.5.26</strong>. After results are published, you can upload your result PDF to automatically update the tracker.
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <div key={title} style={{
                display: 'flex', alignItems: 'flex-start', gap: '1rem',
                background: 'rgb(255 255 255 / 0.07)',
                borderRadius: 12, padding: '0.875rem 1rem',
                border: '1px solid rgb(255 255 255 / 0.1)',
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 8,
                  background: 'rgb(255 255 255 / 0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                }}>
                  <Icon size={18} color="#93c5fd" />
                </div>
                <div>
                  <div style={{ color: '#fff', fontWeight: 600, fontSize: '0.9rem' }}>{title}</div>
                  <div style={{ color: 'rgb(255 255 255 / 0.6)', fontSize: '0.8rem' }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ─── Right Panel (Form) ──── */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
      }}>
        <div style={{ width: '100%', maxWidth: 420 }}>

          {/* Mobile logo */}
          <div className="hide-desktop" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', justifyContent: 'center' }}>
            <GraduationCap size={28} color="var(--primary-600)" />
            <span style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--primary-800)' }}>Credit Tracker</span>
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ color: 'var(--neutral-900)', marginBottom: '0.375rem' }}>Student Login</h2>
            <p style={{ color: 'var(--neutral-500)', fontSize: '0.9rem' }}>Enter your register number to continue</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

            <div className="input-group">
              <label className="input-label" htmlFor="reg-number">Register Number</label>
              <input
                id="reg-number"
                className={`input-field ${error ? 'error' : ''}`}
                type="text"
                placeholder="e.g. 212224100042"
                value={regNo}
                onChange={e => { setRegNo(e.target.value.replace(/\D/g, '')); setError(''); }}
                maxLength={12}
                autoFocus
                style={{ fontSize: '1.05rem', letterSpacing: '0.05em', fontFamily: 'monospace, Inter, sans-serif' }}
              />
              {/* Live parse preview */}
              {regNo.length >= 8 && (
                <div style={{
                  display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.25rem',
                }}>
                  <span style={{ fontSize: '0.75rem', padding: '2px 8px', background: 'var(--primary-50)', color: 'var(--primary-700)', borderRadius: 99, border: '1px solid var(--primary-100)' }}>
                    📅 Batch {yearJoining}
                  </span>
                  <span style={{ fontSize: '0.75rem', padding: '2px 8px', background: SUPPORTED_DEPTS[deptCode] ? 'var(--success-50)' : '#fee2e2', color: SUPPORTED_DEPTS[deptCode] ? 'var(--success-600)' : '#dc2626', borderRadius: 99, border: `1px solid ${SUPPORTED_DEPTS[deptCode] ? 'var(--success-500)' : '#fca5a5'}` }}>
                    🏛 {SUPPORTED_DEPTS[deptCode] ? SUPPORTED_DEPTS[deptCode] : `Dept ${deptCode} (unsupported)`}
                  </span>
                </div>
              )}
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="student-name">
                Your Name <span style={{ color: 'var(--neutral-400)', fontWeight: 400 }}>(optional)</span>
              </label>
              <input
                id="student-name"
                className="input-field"
                type="text"
                placeholder="e.g. Praisy Nishitha J"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>

            {error && (
              <div style={{
                padding: '0.75rem 1rem',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: 8,
                color: '#dc2626',
                fontSize: '0.875rem',
                display: 'flex', alignItems: 'center', gap: '0.5rem',
              }}>
                ⚠️ {error}
              </div>
            )}

            <button
              type="submit"
              id="login-btn"
              className="btn btn-primary btn-lg"
              disabled={loading || regNo.length < 12}
              style={{ marginTop: '0.5rem' }}
            >
              {loading ? <span className="spin">⟳</span> : <ArrowRight size={18} />}
              {loading ? 'Signing in…' : 'Enter Dashboard'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.8rem', color: 'var(--neutral-400)' }}>
            BATCH 2024–2028 · R2024 Regulation
          </p>
        </div>
      </div>
    </div>
  );
}
