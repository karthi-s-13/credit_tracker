import { GraduationCap, LogOut, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ student }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('student');
    navigate('/');
  };

  const initials = student?.name
    ? student.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : student?.register_number?.slice(-2) || 'ST';

  return (
    <nav style={{
      background: '#fff',
      borderBottom: '1px solid var(--neutral-200)',
      padding: '0 1.5rem',
      height: 64,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 4px rgb(0 0 0 / 0.05)',
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: 'linear-gradient(135deg, var(--primary-600), var(--primary-800))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <GraduationCap size={20} color="#fff" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--neutral-900)', lineHeight: 1.2 }}>Credit Tracker</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--neutral-500)' }}>Saveetha Engineering College</div>
        </div>
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Student info */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          padding: '0.375rem 0.875rem',
          background: 'var(--primary-50)',
          borderRadius: 99,
          border: '1px solid var(--primary-100)',
        }}>
          <div style={{
            width: 28, height: 28, borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--primary-500), var(--primary-700))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#fff', fontSize: '0.7rem', fontWeight: 700,
          }}>
            {initials}
          </div>
          <div style={{ lineHeight: 1.2 }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--neutral-800)' }}>
              {student?.name || 'Student'}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--neutral-500)', fontFamily: 'monospace' }}>
              {student?.register_number}
            </div>
          </div>
        </div>

        <button
          id="logout-btn"
          className="btn btn-ghost btn-sm"
          onClick={handleLogout}
          title="Logout"
        >
          <LogOut size={16} />
          <span className="hide-mobile">Logout</span>
        </button>
      </div>
    </nav>
  );
}
