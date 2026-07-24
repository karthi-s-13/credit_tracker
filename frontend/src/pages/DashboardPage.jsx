import { useState, useEffect, useCallback } from 'react';
import { Upload } from 'lucide-react';
import Navbar from '../components/Navbar';
import CategoryCard from '../components/CategoryCard';
import CourseTable from '../components/CourseTable';
import UploadModal from '../components/UploadModal';
import api from '../api';
import { useToast } from '../components/ToastProvider';

export default function DashboardPage() {
  const [student, setStudent] = useState(null);
  const [curriculum, setCurriculum] = useState([]);
  const [meta, setMeta] = useState(null);
  const [completedIds, setCompletedIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const toast = useToast();

  const loadData = useCallback(async () => {
    try {
      const stored = localStorage.getItem('student');
      if (!stored) return;
      const parsedStudent = JSON.parse(stored);
      setStudent(parsedStudent);

      // Load curriculum & meta
      const dept = parsedStudent.dept_name || 'AIDS';
      const [currRes, metaRes, progRes] = await Promise.all([
        api.get(`/curriculum/${dept}`),
        api.get(`/curriculum/${dept}/meta?is_lateral_entry=${parsedStudent.is_lateral_entry}`),
        api.get(`/progress/${parsedStudent.register_number}`),
      ]);

      setCurriculum(currRes.data);
      setMeta(metaRes.data);
      
      const ids = new Set(
        progRes.data
          .filter(p => p.status === 'completed')
          .map(p => p.course_id)
      );
      setCompletedIds(ids);
    } catch (err) {
      toast('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleToggle = async (course, willComplete) => {
    try {
      await api.post('/progress/toggle', {
        register_number: student.register_number,
        course_id: course.id,
        status: willComplete ? 'completed' : 'pending',
        source: 'manual',
      });
      
      setCompletedIds(prev => {
        const next = new Set(prev);
        willComplete ? next.add(course.id) : next.delete(course.id);
        return next;
      });
      
      toast(`${course.course_code_r2024 || 'Course'} marked as ${willComplete ? 'completed' : 'pending'}`, 'success');
    } catch (err) {
      toast('Failed to update course status', 'error');
    }
  };

  const handleUploadSaved = () => {
    toast('OCR results saved successfully!', 'success');
    loadData();
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spin" style={{ fontSize: '2rem' }}>⟳</div>
      </div>
    );
  }

  // Calculate earned credits per category
  const earnedByCategory = {};
  let totalEarned = 0;
  
  if (meta) {
    meta.categories.forEach(c => {
      earnedByCategory[c.code] = 0;
    });
    
    curriculum.forEach(c => {
      if (completedIds.has(c.id) && c.category) {
        const credits = c.total_credits || 0;
        earnedByCategory[c.category] = (earnedByCategory[c.category] || 0) + credits;
        totalEarned += credits;
      }
    });
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar student={student} />
      
      <main style={{ flex: 1, padding: '2rem 1.5rem', maxWidth: 1200, margin: '0 auto', width: '100%' }}>
        {/* Header Section */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ color: 'var(--neutral-900)', marginBottom: '0.25rem' }}>Your Curriculum Progress</h1>
            <p style={{ color: 'var(--neutral-500)', fontSize: '0.9rem', margin: 0 }}>
              Track your {meta?.total_required} required credits for graduation.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              id="upload-pdf-btn"
              className="btn btn-primary"
              onClick={() => setShowUploadModal(true)}
            >
              <Upload size={16} /> Upload Result PDF
            </button>
          </div>
        </div>

        {/* Global Progress Bar */}
        {meta && (
          <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--neutral-900)' }}>
                  Total Credits: {totalEarned} <span style={{ color: 'var(--neutral-400)', fontSize: '0.9rem', fontWeight: 600 }}>/ {meta.total_required}</span>
                </div>
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary-600)' }}>
                {Math.min(Math.round((totalEarned / meta.total_required) * 100), 100)}%
              </div>
            </div>
            
            <div style={{ height: 12, background: 'var(--neutral-100)', borderRadius: 99, overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${Math.min((totalEarned / meta.total_required) * 100, 100)}%`,
                background: 'linear-gradient(90deg, var(--primary-500), var(--primary-700))',
                borderRadius: 99,
                transition: 'width 0.8s ease',
              }} />
            </div>
          </div>
        )}

        {/* Category Grid */}
        {meta && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
            gap: '1rem',
            marginBottom: '2.5rem',
          }}>
            {meta.categories.map(cat => (
              <CategoryCard
                key={cat.code}
                category={cat}
                earned={earnedByCategory[cat.code] || 0}
                required={cat.required_credits}
              />
            ))}
          </div>
        )}

        {/* Course List */}
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Course Checklist</h2>
        <CourseTable
          courses={curriculum}
          completedIds={completedIds}
          onToggle={handleToggle}
        />
      </main>

      {showUploadModal && (
        <UploadModal
          student={student}
          onClose={() => setShowUploadModal(false)}
          onSaved={handleUploadSaved}
        />
      )}
    </div>
  );
}
