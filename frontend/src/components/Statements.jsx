import { useState, useEffect, useRef } from 'react';
import { getStatements, uploadStatement, deleteStatement, savePassword, getPassword } from '../api';

function generatePassword(firstName, dob) {
  // Password = first 4 letters of first name in CAPS + MMYY of DOB
  const namePart = firstName.trim().substring(0, 4).toUpperCase();
  const dobDate = new Date(dob);
  const mm = String(dobDate.getMonth() + 1).padStart(2, '0');
  const yy = String(dobDate.getFullYear()).slice(-2);
  return namePart + mm + yy;
}

export default function Statements() {
  const [statements, setStatements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState('');
  const [firstName, setFirstName] = useState('');
  const [dob, setDob] = useState('');
  const [passwordReady, setPasswordReady] = useState(false);
  const [savedPassword, setSavedPassword] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadStatements();
    loadSavedPassword();
  }, []);

  const loadSavedPassword = async () => {
    try {
      const res = await getPassword();
      if (res.data.saved) {
        setSavedPassword(res.data.password);
        setPasswordReady(true);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadStatements = async () => {
    try {
      const res = await getStatements();
      setStatements(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSetPassword = async () => {
    if (firstName.trim().length < 4) {
      setMessage('Error: First name must be at least 4 characters.');
      return;
    }
    if (!dob) {
      setMessage('Error: Please enter your date of birth.');
      return;
    }
    const password = generatePassword(firstName, dob);
    try {
      await savePassword(password);
      setSavedPassword(password);
      setPasswordReady(true);
      setMessage('');
    } catch (err) {
      setMessage('Error: Failed to save password.');
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!savedPassword) {
      setMessage('Error: Please save a password first.');
      return;
    }

    setIngesting(true);
    setMessage('');
    try {
      const res = await uploadStatement(file, savedPassword);
      const { ingested, skipped, errors } = res.data;
      setMessage(
        `Upload - Ingested: ${ingested}, Skipped: ${skipped}${errors.length > 0 ? `, Errors: ${errors.join('; ')}` : ''}`
      );
      loadStatements();
    } catch (err) {
      setMessage('Upload error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIngesting(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this statement and all its transactions?')) return;
    try {
      await deleteStatement(id);
      loadStatements();
      setMessage('Statement deleted.');
    } catch (err) {
      setMessage('Delete error: ' + err.message);
    }
  };

  return (
    <div>
      {/* Password Setup Card */}
      <div className="card">
        <h2>PDF Statement Password</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.9rem' }}>
          Your PDF statements are password protected. Enter your details below to generate the unlock password.
          <br />
          <span style={{ fontSize: '0.8rem' }}>
            (Password format: First 4 letters of name in CAPS + MMYY of date of birth)
          </span>
        </p>

        <div className="filter-bar">
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
              First Name
            </label>
            <input
              type="text"
              placeholder="e.g. Rahul"
              value={firstName}
              onChange={(e) => { setFirstName(e.target.value); setPasswordReady(false); }}
              style={{ minWidth: '180px' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
              Date of Birth
            </label>
            <input
              type="date"
              value={dob}
              onChange={(e) => { setDob(e.target.value); setPasswordReady(false); }}
              style={{ minWidth: '180px' }}
            />
          </div>
          <div style={{ alignSelf: 'flex-end' }}>
            <button className="btn btn-primary" onClick={handleSetPassword}>
              Set Password
            </button>
          </div>
        </div>

        {passwordReady && savedPassword && (
          <p style={{
            padding: '0.5rem 0.75rem',
            borderRadius: '8px',
            background: '#f0fdf4',
            color: 'var(--success)',
            fontSize: '0.85rem',
            marginTop: '0.75rem'
          }}>
            Password configured: <code style={{ fontWeight: 600 }}>{savedPassword}</code> — Ready to ingest PDFs.
          </p>
        )}

        {!savedPassword && (
          <p style={{
            padding: '0.5rem 0.75rem',
            borderRadius: '8px',
            background: '#fef2f2',
            color: 'var(--danger)',
            fontSize: '0.85rem',
            marginTop: '0.75rem'
          }}>
            No password saved. Ingestion is disabled until you configure a password.
          </p>
        )}
      </div>

      {/* Ingestion Card */}
      <div className="card">
        <h2>Manage Statements</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.9rem' }}>
          Upload your credit card statement PDFs below.
          The bank is auto-detected from the PDF content. Supported: HDFC, ICICI, SBI, Axis.
        </p>

        <div className="filter-bar">
          <div className="upload-area" onClick={() => savedPassword && fileInputRef.current?.click()} style={{ opacity: savedPassword ? 1 : 0.5, cursor: savedPassword ? 'pointer' : 'not-allowed' }}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleUpload}
            />
            <p>Click to upload a statement (PDF)</p>
          </div>
        </div>

        {/* Ingestion Loader */}
        {ingesting && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '1rem',
            marginTop: '1rem',
            borderRadius: '8px',
            background: 'var(--bg)',
            border: '1px solid var(--border)'
          }}>
            <div className="spinner"></div>
            <div>
              <p style={{ fontWeight: 500, color: 'var(--text)', margin: 0, fontSize: '0.8125rem' }}>Processing statements...</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                Parsing, extracting transactions, and categorizing.
              </p>
            </div>
          </div>
        )}

        {message && !ingesting && (
          <p style={{
            padding: '0.75rem',
            borderRadius: '8px',
            background: message.includes('Error') ? '#fef2f2' : '#f0fdf4',
            color: message.includes('Error') ? 'var(--danger)' : 'var(--success)',
            fontSize: '0.85rem',
            marginTop: '0.5rem'
          }}>
            {message}
          </p>
        )}
      </div>

      <div className="card">
        <h2>Imported Statements ({statements.length})</h2>
        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : statements.length === 0 ? (
          <div className="empty-state">
            <p>No statements imported yet.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Bank</th>
                  <th>Month</th>
                  <th>Card Type</th>
                  <th>Filename</th>
                  <th>Imported</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {statements.map((stmt) => (
                  <tr key={stmt.id}>
                    <td><strong>{stmt.bank}</strong></td>
                    <td>{stmt.statement_month}</td>
                    <td>{stmt.card_type || '-'}</td>
                    <td style={{ fontSize: '0.8rem' }}>{stmt.filename}</td>
                    <td style={{ fontSize: '0.8rem' }}>{stmt.imported_at ? new Date(stmt.imported_at).toLocaleDateString() : '-'}</td>
                    <td>
                      <button className="btn btn-danger" onClick={() => handleDelete(stmt.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
