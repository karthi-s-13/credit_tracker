import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { X, Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import api from '../api';

export default function UploadModal({ student, onClose, onSaved }) {
  const [step, setStep] = useState('upload'); // 'upload' | 'review' | 'saving'
  const [ocrResult, setOcrResult] = useState(null);
  const [selected, setSelected] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fileName, setFileName] = useState('');

  const onDrop = useCallback(async (files) => {
    const file = files[0];
    if (!file) return;
    setFileName(file.name);
    setLoading(true);
    setError('');
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('department', student.dept_name || 'AIDS');
      const { data } = await api.post('/ocr/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setOcrResult(data);
      // Pre-select all matches with Pass status
      const passIds = new Set(
        data.matches
          .filter(m => !m.result_status || m.result_status?.toLowerCase().includes('pass'))
          .map(m => m.course_id)
      );
      setSelected(passIds);
      setStep('review');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [student]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'] }, multiple: false,
  });

  const toggleSelect = (courseId) => {
    setSelected(prev => {
      const next = new Set(prev);
      next.has(courseId) ? next.delete(courseId) : next.add(courseId);
      return next;
    });
  };

  const handleSave = async () => {
    if (selected.size === 0) return;
    setStep('saving');
    const entries = ocrResult.matches
      .filter(m => selected.has(m.course_id))
      .map(m => ({
        course_id: m.course_id,
        status: 'completed',
        source: 'ocr',
        grade: m.grade,
        grade_point: m.grade_point,
      }));
    try {
      await api.post('/progress/bulk', {
        register_number: student.register_number,
        entries,
      });
      onSaved(entries.map(e => e.course_id));
      onClose();
    } catch (err) {
      setError('Failed to save. Please try again.');
      setStep('review');
    }
  };

  return (
    <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'var(--primary-50)', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <Upload size={18} color="var(--primary-600)" />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', color: 'var(--neutral-900)' }}>Upload Result PDF</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--neutral-500)', margin: 0 }}>
                OCR will extract your courses automatically
              </p>
            </div>
          </div>
          <button className="btn btn-ghost btn-icon" onClick={onClose} id="close-upload-modal">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {step === 'upload' && (
            <>
              <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
                <input {...getInputProps()} id="pdf-file-input" />
                {loading ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
                    <Loader2 size={36} className="spin" color="var(--primary-500)" />
                    <p style={{ margin: 0, color: 'var(--primary-600)', fontWeight: 500 }}>Processing PDF with OCR…</p>
                    <p style={{ margin: 0, fontSize: '0.8rem' }}>This may take 10–30 seconds</p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
                    <FileText size={40} color="var(--primary-400)" />
                    <div>
                      <p style={{ margin: 0, fontWeight: 600, color: 'var(--neutral-700)' }}>
                        {isDragActive ? 'Drop your PDF here' : 'Drag & drop your result PDF'}
                      </p>
                      <p style={{ margin: '0.25rem 0 0', fontSize: '0.82rem', color: 'var(--neutral-400)' }}>
                        or <span style={{ color: 'var(--primary-600)', fontWeight: 600 }}>click to browse</span>
                      </p>
                    </div>
                    <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--neutral-400)' }}>PDF files only · Max 10MB</p>
                  </div>
                )}
              </div>
              {error && (
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '1rem', color: '#dc2626', fontSize: '0.875rem' }}>
                  <AlertCircle size={15} /> {error}
                </div>
              )}
            </>
          )}

          {(step === 'review' || step === 'saving') && ocrResult && (
            <div>
              {/* File name */}
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.625rem 0.875rem', background: 'var(--primary-50)',
                borderRadius: 8, marginBottom: '1rem',
              }}>
                <FileText size={15} color="var(--primary-600)" />
                <span style={{ fontSize: '0.85rem', color: 'var(--primary-700)', fontWeight: 500 }}>{fileName}</span>
                <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--neutral-500)' }}>
                  {ocrResult.matches.length} courses detected
                </span>
              </div>

              {/* Matches list */}
              {ocrResult.matches.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: 340, overflowY: 'auto' }}>
                  {ocrResult.matches.map(m => {
                    const isSelected = selected.has(m.course_id);
                    const passed = !m.result_status || m.result_status?.toLowerCase().includes('pass');
                    return (
                      <label key={m.course_id} style={{
                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                        padding: '0.75rem 0.875rem',
                        borderRadius: 8, cursor: 'pointer',
                        border: `1.5px solid ${isSelected ? 'var(--primary-300)' : 'var(--neutral-200)'}`,
                        background: isSelected ? 'var(--primary-50)' : '#fff',
                        transition: 'all 0.15s',
                      }}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleSelect(m.course_id)}
                          style={{ width: 16, height: 16, accentColor: 'var(--primary-600)' }}
                        />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--neutral-800)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {m.course_title}
                          </div>
                          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.2rem', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.7rem', color: 'var(--primary-600)', fontFamily: 'monospace' }}>{m.course_code}</span>
                            {m.grade && <span style={{ fontSize: '0.7rem', color: 'var(--neutral-500)' }}>Grade: <b>{m.grade}</b></span>}
                            {m.grade_point && <span style={{ fontSize: '0.7rem', color: 'var(--neutral-500)' }}>GP: <b>{m.grade_point}</b></span>}
                          </div>
                        </div>
                        <div style={{ textAlign: 'right', flexShrink: 0 }}>
                          <span className={passed ? 'badge badge-completed' : 'badge badge-pending'} style={{ fontSize: '0.7rem' }}>
                            {m.result_status || 'Pass'}
                          </span>
                          <div style={{ fontSize: '0.65rem', color: 'var(--neutral-400)', marginTop: 2 }}>
                            {m.total_credits} cr · {Math.round(m.confidence)}% match
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--neutral-400)' }}>
                  <AlertCircle size={32} style={{ marginBottom: '0.5rem' }} />
                  <p style={{ margin: 0 }}>No courses could be matched from the PDF</p>
                </div>
              )}

              {/* Unmatched */}
              {ocrResult.unmatched.length > 0 && (
                <div style={{ marginTop: '0.875rem', padding: '0.75rem', background: '#fffbeb', borderRadius: 8, border: '1px solid #fde68a' }}>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#92400e', fontWeight: 600, marginBottom: '0.25rem' }}>
                    ⚠ {ocrResult.unmatched.length} code(s) not matched (manual review needed):
                  </p>
                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#78350f', fontFamily: 'monospace' }}>
                    {ocrResult.unmatched.join(', ')}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {(step === 'review' || step === 'saving') && (
          <div className="modal-footer">
            <button className="btn btn-outline" onClick={() => setStep('upload')} disabled={step === 'saving'}>
              ← Upload Another
            </button>
            <button
              id="save-ocr-results"
              className="btn btn-primary"
              onClick={handleSave}
              disabled={selected.size === 0 || step === 'saving'}
            >
              {step === 'saving' ? <><Loader2 size={15} className="spin" /> Saving…</> : `Save ${selected.size} Course${selected.size !== 1 ? 's' : ''}`}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
