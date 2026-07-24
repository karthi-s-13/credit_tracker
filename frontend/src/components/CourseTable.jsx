import { useState, useMemo } from 'react';
import { Search, ChevronUp, ChevronDown, CheckCircle2, Clock } from 'lucide-react';

const CATEGORY_LABELS = {
  HS: 'Humanities & Science', BS: 'Basic Science', ES: 'Engineering Science',
  PC: 'Professional Core', PE: 'Professional Electives', OE: 'Open Electives',
  EEC: 'Employability Enhancement', MC: 'Mandatory Courses',
};

export default function CourseTable({ courses, completedIds, onToggle }) {
  const [search, setSearch] = useState('');
  const [filterCat, setFilterCat] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [sortKey, setSortKey] = useState('sno');
  const [sortDir, setSortDir] = useState('asc');

  const categories = useMemo(() => {
    const cats = [...new Set(courses.map(c => c.category).filter(Boolean))].sort();
    return ['ALL', ...cats];
  }, [courses]);

  const filtered = useMemo(() => {
    let data = courses.filter(c => {
      const isCompleted = completedIds.has(c.id);
      const matchSearch = !search ||
        c.course_title?.toLowerCase().includes(search.toLowerCase()) ||
        c.course_code_r2024?.toLowerCase().includes(search.toLowerCase());
      const matchCat = filterCat === 'ALL' || c.category === filterCat;
      const matchStatus =
        filterStatus === 'ALL' ? true :
        filterStatus === 'completed' ? isCompleted : !isCompleted;
      return matchSearch && matchCat && matchStatus;
    });

    data.sort((a, b) => {
      let av = a[sortKey], bv = b[sortKey];
      if (sortKey === 'sno' || sortKey === 'total_credits') {
        av = Number(av); bv = Number(bv);
      } else {
        av = (av || '').toString().toLowerCase();
        bv = (bv || '').toString().toLowerCase();
      }
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return data;
  }, [courses, search, filterCat, filterStatus, sortKey, sortDir, completedIds]);

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('asc'); }
  };

  const SortIcon = ({ k }) => (
    <span style={{ opacity: sortKey === k ? 1 : 0.3, marginLeft: 3 }}>
      {sortKey === k && sortDir === 'asc' ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
    </span>
  );

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      {/* Filters bar */}
      <div style={{
        padding: '1rem 1.25rem',
        borderBottom: '1px solid var(--neutral-100)',
        display: 'flex',
        gap: '0.75rem',
        flexWrap: 'wrap',
        alignItems: 'center',
      }}>
        {/* Search */}
        <div style={{ position: 'relative', flex: '1', minWidth: 180 }}>
          <Search size={15} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--neutral-400)' }} />
          <input
            className="input-field"
            placeholder="Search courses…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: '2rem', padding: '0.5rem 0.75rem 0.5rem 2rem', fontSize: '0.85rem' }}
            id="course-search"
          />
        </div>

        {/* Category filter */}
        <select
          className="input-field"
          value={filterCat}
          onChange={e => setFilterCat(e.target.value)}
          style={{ width: 'auto', padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
          id="filter-category"
        >
          {categories.map(c => (
            <option key={c} value={c}>{c === 'ALL' ? 'All Categories' : `${c} – ${CATEGORY_LABELS[c] || c}`}</option>
          ))}
        </select>

        {/* Status filter */}
        <select
          className="input-field"
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
          style={{ width: 'auto', padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
          id="filter-status"
        >
          <option value="ALL">All Status</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
        </select>

        <span style={{ fontSize: '0.8rem', color: 'var(--neutral-500)', whiteSpace: 'nowrap' }}>
          {filtered.length} courses
        </span>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th style={{ cursor: 'pointer', userSelect: 'none' }} onClick={() => toggleSort('sno')}>
                # <SortIcon k="sno" />
              </th>
              <th style={{ cursor: 'pointer', userSelect: 'none' }} onClick={() => toggleSort('course_code_r2024')}>
                Code <SortIcon k="course_code_r2024" />
              </th>
              <th style={{ cursor: 'pointer', userSelect: 'none', minWidth: 220 }} onClick={() => toggleSort('course_title')}>
                Course Title <SortIcon k="course_title" />
              </th>
              <th style={{ cursor: 'pointer', userSelect: 'none' }} onClick={() => toggleSort('category')}>
                Category <SortIcon k="category" />
              </th>
              <th style={{ cursor: 'pointer', userSelect: 'none', textAlign: 'center' }} onClick={() => toggleSort('total_credits')}>
                Credits <SortIcon k="total_credits" />
              </th>
              <th style={{ textAlign: 'center' }}>Type</th>
              <th style={{ textAlign: 'center' }}>Status</th>
              <th style={{ textAlign: 'center' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: 'var(--neutral-400)' }}>
                  No courses match your filters
                </td>
              </tr>
            ) : filtered.map(course => {
              const isCompleted = completedIds.has(course.id);
              return (
                <tr key={course.id}>
                  <td style={{ color: 'var(--neutral-400)', fontSize: '0.8rem' }}>{course.sno}</td>
                  <td>
                    <code style={{
                      fontSize: '0.78rem', fontWeight: 600,
                      background: 'var(--primary-50)', color: 'var(--primary-700)',
                      padding: '2px 6px', borderRadius: 4,
                    }}>
                      {course.course_code_r2024 || '—'}
                    </code>
                  </td>
                  <td style={{ maxWidth: 260 }}>
                    <div style={{ fontWeight: 500, color: 'var(--neutral-800)', fontSize: '0.85rem', lineHeight: 1.4 }}>
                      {course.course_title}
                    </div>
                    {course.cgpa_type && (
                      <span style={{ fontSize: '0.7rem', color: 'var(--neutral-400)' }}>{course.cgpa_type}</span>
                    )}
                  </td>
                  <td>
                    <span className="badge badge-category" style={{ fontSize: '0.7rem' }}>
                      {course.category || '—'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center', fontWeight: 700, color: 'var(--primary-700)' }}>
                    {course.total_credits}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span style={{ fontSize: '0.72rem', color: 'var(--neutral-500)' }}>
                      {course.course_type?.split('(')[0]?.trim() || '—'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {isCompleted
                      ? <span className="badge badge-completed"><CheckCircle2 size={11} /> Done</span>
                      : <span className="badge badge-pending"><Clock size={11} /> Pending</span>
                    }
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      id={`toggle-course-${course.id}`}
                      className={`btn btn-sm ${isCompleted ? 'btn-outline' : 'btn-success'}`}
                      onClick={() => onToggle(course, !isCompleted)}
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.75rem' }}
                    >
                      {isCompleted ? 'Undo' : '✓ Mark Done'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
