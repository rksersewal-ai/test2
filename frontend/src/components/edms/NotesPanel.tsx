// =============================================================================
// FILE: frontend/src/components/edms/NotesPanel.tsx
// SPRINT 1 — Feature #12: Document Notes & Annotations
// PURPOSE : Collapsible notes thread per document/revision.
//           Append-only — no edit/delete buttons shown.
//           Engineers can add notes; Section Heads can resolve them.
// ENDPOINTS:
//   GET   /api/edms/notes/?document={id}&revision={id}  → list notes
//   POST  /api/edms/notes/                              → create note
//   PATCH /api/edms/notes/{id}/resolve/                  → resolve note
// =============================================================================
import React, { useEffect, useState, useCallback } from 'react';

interface Note {
  id: number;
  note_type: string;
  note_text: string;
  is_resolved: boolean;
  resolved_by_name: string;
  resolved_at: string | null;
  resolution_note: string;
  created_by_name: string;
  created_at: string;
  revision: number | null;
}

const NOTE_TYPES = [
  { value: 'OBSERVATION',     label: 'Observation'    },
  { value: 'REVIEW',          label: 'Review Comment' },
  { value: 'QUERY',           label: 'Query'          },
  { value: 'INFO',            label: 'Information'    },
  { value: 'ACTION_REQUIRED', label: 'Action Required'},
];

const TYPE_COLOURS: Record<string, string> = {
  REVIEW:          '#2563eb',
  QUERY:           '#d97706',
  OBSERVATION:     '#6b7280',
  INFO:            '#0891b2',
  ACTION_REQUIRED: '#dc2626',
};

interface Props {
  documentId: number;
  revisionId?: number;    // if set, shows only notes for that revision
  canResolve?: boolean;   // Section Head / Admin
}

export const NotesPanel: React.FC<Props> = ({ documentId, revisionId, canResolve = false }) => {
  const [notes,       setNotes]       = useState<Note[]>([]);
  const [loading,     setLoading]     = useState(true);
  const [newText,     setNewText]     = useState('');
  const [newType,     setNewType]     = useState('OBSERVATION');
  const [saving,      setSaving]      = useState(false);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [resNote,     setResNote]     = useState('');
  const [collapsed,   setCollapsed]   = useState(false);

  const loadNotes = useCallback(() => {
    setLoading(true);
    let url = `/api/edms/notes/?document=${documentId}`;
    if (revisionId) url += `&revision=${revisionId}`;
    fetch(url, { credentials: 'include' })
      .then(r => r.json())
      .then(setNotes)
      .finally(() => setLoading(false));
  }, [documentId, revisionId]);

  useEffect(() => { loadNotes(); }, [loadNotes]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newText.trim()) return;
    setSaving(true);
    try {
      await fetch('/api/edms/notes/', {
        method:      'POST',
        credentials: 'include',
        headers:     { 'Content-Type': 'application/json' },
        body:        JSON.stringify({
          document:  documentId,
          revision:  revisionId ?? null,
          note_type: newType,
          note_text: newText.trim(),
        }),
      });
      setNewText(''); loadNotes();
    } finally { setSaving(false); }
  };

  const handleResolve = async (noteId: number) => {
    await fetch(`/api/edms/notes/${noteId}/resolve/`, {
      method:      'PATCH',
      credentials: 'include',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify({ resolution_note: resNote }),
    });
    setResolvingId(null); setResNote(''); loadNotes();
  };

  const unresolved = notes.filter(n => !n.is_resolved).length;

  return (
    <div className="notes-panel">
      <button className="notes-panel__toggle" onClick={() => setCollapsed(c => !c)}>
        Notes {unresolved > 0 && <span className="notes-badge">{unresolved} open</span>}
        <span>{collapsed ? '▼' : '▲'}</span>
      </button>

      {!collapsed && (
        <>
          {/* Add note form */}
          <form className="notes-add-form" onSubmit={handleAddNote}>
            <select value={newType} onChange={e => setNewType(e.target.value)}
              className="notes-type-select">
              {NOTE_TYPES.map(nt => (
                <option key={nt.value} value={nt.value}>{nt.label}</option>
              ))}
            </select>
            <textarea
              className="notes-textarea"
              rows={3}
              placeholder="Add a note, query, or observation..."
              value={newText}
              onChange={e => setNewText(e.target.value)}
            />
            <button type="submit" className="edms-btn edms-btn--primary" disabled={saving || !newText.trim()}>
              {saving ? 'Adding...' : 'Add Note'}
            </button>
          </form>

          {/* Notes thread */}
          {loading ? (
            <p className="notes-loading">Loading notes...</p>
          ) : notes.length === 0 ? (
            <p className="notes-empty">No notes yet.</p>
          ) : (
            <ul className="notes-list">
              {notes.map(note => (
                <li key={note.id}
                    className={`notes-item ${note.is_resolved ? 'notes-item--resolved' : ''}`}>
                  <div className="notes-item__header">
                    <span className="notes-type-badge"
                          style={{ backgroundColor: TYPE_COLOURS[note.note_type] ?? '#6b7280' }}>
                      {note.note_type.replace('_', ' ')}
                    </span>
                    <span className="notes-author">{note.created_by_name}</span>
                    <span className="notes-date">
                      {new Date(note.created_at).toLocaleDateString('en-IN')}
                    </span>
                    {note.is_resolved && (
                      <span className="notes-resolved-badge">✓ Resolved</span>
                    )}
                  </div>

                  <p className="notes-text">{note.note_text}</p>

                  {note.is_resolved && note.resolution_note && (
                    <p className="notes-resolution">
                      <strong>Resolution:</strong> {note.resolution_note}
                      <span className="notes-resolver"> — {note.resolved_by_name},
                        {note.resolved_at && new Date(note.resolved_at).toLocaleDateString('en-IN')}
                      </span>
                    </p>
                  )}

                  {!note.is_resolved && canResolve && (
                    resolvingId === note.id ? (
                      <div className="notes-resolve-form">
                        <input type="text" placeholder="Resolution note (optional)"
                          value={resNote} onChange={e => setResNote(e.target.value)}
                          className="notes-res-input" />
                        <button className="edms-btn edms-btn--sm edms-btn--success"
                          onClick={() => handleResolve(note.id)}>Confirm Resolve</button>
                        <button className="edms-btn edms-btn--sm"
                          onClick={() => setResolvingId(null)}>Cancel</button>
                      </div>
                    ) : (
                      <button className="notes-resolve-btn"
                        onClick={() => setResolvingId(note.id)}>Mark Resolved</button>
                    )
                  )}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
};
