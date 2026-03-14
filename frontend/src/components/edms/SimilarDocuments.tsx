// =============================================================================
// FILE: frontend/src/components/edms/SimilarDocuments.tsx
// SPRINT 2 — Feature #8: "More Like This" Similarity Search
// PURPOSE : Sidebar card on Document detail page showing top similar documents
//           returned by the pg_trgm similarity endpoint.
// ENDPOINT: GET /api/edms/documents/{id}/similar/?limit=5
// =============================================================================
import React from 'react';
import { useSimilarDocuments } from '../../hooks/useSimilarDocuments';

interface Props {
  documentId: number;
  onNavigate?: (id: number) => void; // callback so parent can navigate to doc
}

export const SimilarDocuments: React.FC<Props> = ({ documentId, onNavigate }) => {
  const { results, loading, sourceTitle } = useSimilarDocuments(documentId, 5);

  if (loading) {
    return (
      <div className="similar-docs">
        <h4 className="similar-docs__heading">Related Documents</h4>
        <p className="similar-docs__loading">Finding similar documents…</p>
      </div>
    );
  }

  if (results.length === 0) return null;

  return (
    <div className="similar-docs">
      <h4 className="similar-docs__heading">Related Documents</h4>
      <ul className="similar-docs__list">
        {results.map(doc => (
          <li key={doc.id} className="similar-docs__item">
            <button
              className="similar-docs__link"
              onClick={() => onNavigate?.(doc.id)}
              title={`Similarity: ${(doc.similarity_score * 100).toFixed(1)}%`}
            >
              <span className="similar-docs__number">{doc.document_number}</span>
              <span className="similar-docs__title">{doc.title}</span>
            </button>
            <span
              className="similar-docs__score"
              title="Trigram similarity score"
            >
              {Math.round(doc.similarity_score * 100)}%
            </span>

            {/* Status pill */}
            <span className={`similar-docs__status similar-docs__status--${doc.status.toLowerCase()}`}>
              {doc.status}
            </span>

            {/* Category / type breadcrumb */}
            {doc.category_name && (
              <span className="similar-docs__category">{doc.category_name}</span>
            )}
          </li>
        ))}
      </ul>
      <p className="similar-docs__hint">
        Similarity to “{sourceTitle}” based on title and keywords.
      </p>
    </div>
  );
};
