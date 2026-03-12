"""Add PostgreSQL trigger that blocks UPDATE and DELETE on audit_log."""
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


class Migration(migrations.Migration):
    dependencies = [('audit', '0001_initial')]
    operations  = [
        migrations.RunSQL(sql=SQL_CREATE, reverse_sql=SQL_DROP),
    ]
