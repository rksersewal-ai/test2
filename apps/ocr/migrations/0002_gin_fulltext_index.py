"""Add PostgreSQL GIN index on ocr_result.full_text for fast full-text search."""
from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

# Uses pg_trgm for ILIKE-friendly trigram index (no need for tsvector config).
# Requires PostgreSQL extension pg_trgm (available by default on PG 12+).
SQL_CREATE = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS ocr_result_fulltext_trgm_idx
    ON ocr_result USING GIN (full_text gin_trgm_ops);
"""
SQL_DROP = "DROP INDEX IF EXISTS ocr_result_fulltext_trgm_idx;"


class Migration(migrations.Migration):
    dependencies = [('ocr', '0001_initial')]
    operations  = [
        TrigramExtension(),
        migrations.RunSQL(sql=SQL_CREATE, reverse_sql=SQL_DROP),
    ]
