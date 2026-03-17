"""Add an audit-log immutability trigger on PostgreSQL only."""
from django.db import migrations


SQL_CREATE = """
CREATE OR REPLACE FUNCTION audit_log_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log rows are immutable: % on audit_log is not allowed', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_log_immutable
BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();
"""

SQL_DROP = """
DROP TRIGGER IF EXISTS trg_audit_log_immutable ON audit_log;
DROP FUNCTION IF EXISTS audit_log_immutable();
"""


def create_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SQL_CREATE)


def drop_trigger(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute(SQL_DROP)


class Migration(migrations.Migration):
    dependencies = [('audit', '0001_initial')]
    operations = [
        migrations.RunPython(create_trigger, reverse_code=drop_trigger),
    ]
