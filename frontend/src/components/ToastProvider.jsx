import { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

let toastId = 0;

export function useToast() {
  return useContext(ToastContext);
}

export default function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = ++toastId;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const icons = {
    success: <CheckCircle size={16} color="var(--success-500)" />,
    error: <XCircle size={16} color="#ef4444" />,
    info: <Info size={16} color="var(--primary-500)" />,
  };

  return (
    <ToastContext.Provider value={addToast}>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            {icons[t.type]}
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => removeToast(t.id)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0 0 0 4px', display: 'flex' }}
            >
              <X size={14} color="var(--neutral-400)" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
