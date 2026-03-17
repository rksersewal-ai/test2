"""Migration #19 — Add PostgreSQL GIN tsvector index on OCRResult.full_text.

Why:
  The existing 0002 migration created a trigram (gin_trgm_ops) index which
  supports ILIKE / similarity() searches. This migration adds a *separate*
  tsvector GIN index that powers fast SearchVector / SearchQuery lookups via
  Django's postgres full-text search framework (to_tsvector).

  Together the two indexes cover:
    - Fuzzy / partial matches  → trigram index  (0002)
    - Ranked full-word search  → tsvector index (0003, this file)

Note:
  Uses CONCURRENTLY so the index build does not lock the table.
  CONCURRENTLY cannot run inside a transaction, so atomic=False is set.
"""
from django.db import migrations

SQL_CREATE = """
CREATE INDEX CONCURRENTLY IF NOT EXISTS ocr_result_fulltext_tsv_idx
    ON ocr_ocrresult
    USING GIN (to_tsvector('english', COALESCE(full_text, '')));
"""

SQL_DROP = "DROP INDEX CONCURRENTLY IF EXISTS ocr_result_fulltext_tsv_idx;"


def create_tsvector_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SQL_CREATE)


def drop_tsvector_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SQL_DROP)


class Migration(migrations.Migration):
    # CONCURRENTLY requires no wrapping transaction
    atomic = False

    dependencies = [('ocr', '0002_gin_fulltext_index')]

    operations = [
        migrations.RunPython(
            create_tsvector_index,
            reverse_code=drop_tsvector_index,
        ),
    ]
