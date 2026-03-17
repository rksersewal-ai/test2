"""Add a PostgreSQL trigram index for OCR full-text search only on PostgreSQL."""
from django.db import migrations


SQL_CREATE = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS ocr_result_fulltext_trgm_idx
    ON ocr_result USING GIN (full_text gin_trgm_ops);
"""

SQL_DROP = "DROP INDEX IF EXISTS ocr_result_fulltext_trgm_idx;"


def create_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SQL_CREATE)


def drop_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SQL_DROP)


class Migration(migrations.Migration):
    dependencies = [('ocr', '0001_initial')]
    operations = [
        migrations.RunPython(create_index, reverse_code=drop_index),
    ]
