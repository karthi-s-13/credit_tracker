import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ToastProvider from './components/ToastProvider';

function PrivateRoute({ children }) {
  const student = localStorage.getItem('student');
  return student ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}
