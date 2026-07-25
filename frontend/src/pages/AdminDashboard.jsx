import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Search, ArrowLeft, GraduationCap, Users } from 'lucide-react';
import api from '../api';
import { useToast } from '../components/ToastProvider';
import '../index.css';

export default function AdminDashboard() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Upload states
  const [uploadDept, setUploadDept] = useState('AIDS');
  const [uploadYear, setUploadYear] = useState('2024');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadingCurriculum, setUploadingCurriculum] = useState(false);
  
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleUploadCurriculum = async () => {
    if (!uploadFile) return;
    setUploadingCurriculum(true);
    try {
      const form = new FormData();
      form.append('department', uploadDept);
      form.append('curriculum_year', uploadYear);
      form.append('file', uploadFile);
      
      const { data } = await api.post('/admin/curriculum/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      toast(data.message, 'success');
      setUploadFile(null); // Reset file
      fetchStudents(); // Refresh students to pick up new tables
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to upload curriculum', 'error');
    } finally {
      setUploadingCurriculum(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const { data } = await api.get('/admin/students');
      setStudents(data);
    } catch (err) {
      toast('Failed to load students data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filteredStudents = students.filter(
    (student) =>
      student.register_number.includes(searchTerm) ||
      (student.name && student.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (student.dept_name && student.dept_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', display: 'flex', flexDirection: 'column' }}>
      {/* Navbar */}
      <nav style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        padding: '1rem 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => navigate(-1)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              color: 'var(--neutral-500)', padding: '0.5rem'
            }}
          >
            <ArrowLeft size={20} />
            <span style={{ fontWeight: 500 }}>Back</span>
          </button>
          <div style={{ width: '1px', height: '24px', backgroundColor: '#e2e8f0' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: 'linear-gradient(135deg, var(--primary-600) 0%, var(--primary-800) 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Shield size={22} color="#ffffff" />
            </div>
            <div>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--neutral-900)' }}>Admin Portal</h1>
              <div style={{ fontSize: '0.8rem', color: 'var(--neutral-500)' }}>Overview of all students</div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '999px',
              padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
              width: '300px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
            }}>
              <Search size={18} color="var(--neutral-400)" />
              <input
                type="text"
                placeholder="Search students..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ border: 'none', outline: 'none', width: '100%', fontSize: '0.95rem' }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '0.5rem 1rem' }}>
              <select 
                value={uploadDept} 
                onChange={e => setUploadDept(e.target.value)}
                style={{ border: 'none', outline: 'none', background: 'transparent', fontSize: '0.9rem', fontWeight: 500 }}
              >
                <option value="AGRI">AGRI</option>
                <option value="AIDS">AIDS</option>
                <option value="AIML">AIML</option>
                <option value="BME">BME</option>
                <option value="CHEM">CHEM</option>
                <option value="CIVIL">CIVIL</option>
                <option value="CSE">CSE</option>
                <option value="CSECS">CSECS</option>
                <option value="CSEIOT">CSEIOT</option>
                <option value="ECE">ECE</option>
                <option value="EEE">EEE</option>
                <option value="IT">IT</option>
                <option value="MECH">MECH</option>
              </select>
              <div style={{ width: 1, height: 16, background: '#e2e8f0' }} />
              <input 
                type="text" 
                value={uploadYear} 
                onChange={e => setUploadYear(e.target.value)}
                placeholder="Year (e.g. 2024)"
                style={{ border: 'none', outline: 'none', width: '100px', fontSize: '0.9rem' }}
              />
              <div style={{ width: 1, height: 16, background: '#e2e8f0' }} />
              <input 
                key={uploadFile ? uploadFile.name : 'empty'}
                type="file" 
                accept=".json,.pdf"
                onChange={e => setUploadFile(e.target.files[0])}
                style={{ width: '180px', fontSize: '0.8rem' }}
              />
              <button 
                className="btn btn-primary" 
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                onClick={handleUploadCurriculum}
                disabled={uploadingCurriculum || !uploadFile}
              >
                {uploadingCurriculum ? 'Uploading...' : 'Upload Curriculum'}
              </button>
            </div>
            
            <div style={{
              background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px',
              padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '1rem',
              boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%', background: 'var(--primary-50)',
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                <Users size={18} color="var(--primary-600)" />
              </div>
              <div>
                <div style={{ fontSize: '0.8rem', color: 'var(--neutral-500)', fontWeight: 500 }}>Total Students</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--neutral-900)' }}>{students.length}</div>
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0' }}>
            <div className="spin" style={{ fontSize: '2rem', color: 'var(--primary-600)' }}>⟳</div>
          </div>
        ) : (
          <div style={{
            background: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '16px',
            overflow: 'hidden',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)'
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.85rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Student</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.85rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Register No</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.85rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Department</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.85rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Batch</th>
                  <th style={{ padding: '1rem', textAlign: 'right', fontSize: '0.85rem', fontWeight: 600, color: 'var(--neutral-500)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Credits Completed</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.length > 0 ? (
                  filteredStudents.map((student) => (
                    <tr key={student.id} style={{ borderBottom: '1px solid #f1f5f9', transition: 'background-color 0.2s' }} className="hover-row">
                      <td style={{ padding: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{
                            width: 32, height: 32, borderRadius: '50%', background: 'var(--primary-100)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            color: 'var(--primary-700)', fontWeight: 600, fontSize: '0.85rem'
                          }}>
                            {student.name ? student.name.charAt(0).toUpperCase() : <GraduationCap size={16} />}
                          </div>
                          <span style={{ fontWeight: 500, color: 'var(--neutral-900)' }}>
                            {student.name || 'Unknown'}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '1rem', color: 'var(--neutral-600)', fontFamily: 'monospace', fontSize: '0.95rem' }}>
                        {student.register_number}
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          borderRadius: '999px',
                          fontSize: '0.8rem',
                          fontWeight: 500,
                          background: 'var(--primary-50)',
                          color: 'var(--primary-700)',
                          border: '1px solid var(--primary-100)'
                        }}>
                          {student.dept_name || `Dept ${student.dept_code}`}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', color: 'var(--neutral-600)' }}>
                        {student.year_of_joining ? `20${String(student.year_of_joining).slice(-2)}` : 'N/A'}
                      </td>
                      <td style={{ padding: '1rem', textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                          <span style={{ fontWeight: 700, color: student.total_completed_credits >= 169 ? 'var(--success-600)' : 'var(--neutral-800)', fontSize: '1.1rem' }}>
                            {student.total_completed_credits}
                          </span>
                          <span style={{ color: 'var(--neutral-400)', fontSize: '0.85rem' }}>/ 169</span>
                        </div>
                        {/* Mini progress bar */}
                        <div style={{ width: '80px', height: '4px', background: '#f1f5f9', borderRadius: '2px', marginLeft: 'auto', marginTop: '0.25rem', overflow: 'hidden' }}>
                          <div style={{
                            height: '100%',
                            width: `${Math.min(100, (student.total_completed_credits / 169) * 100)}%`,
                            background: student.total_completed_credits >= 169 ? 'var(--success-500)' : 'var(--primary-500)'
                          }} />
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} style={{ padding: '3rem', textAlign: 'center', color: 'var(--neutral-500)' }}>
                      No students found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
      <style>{`
        .hover-row:hover {
          background-color: #f8fafc;
        }
      `}</style>
    </div>
  );
}
