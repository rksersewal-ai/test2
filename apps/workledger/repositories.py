# =============================================================================
# FILE: apps/workledger/repositories.py
# FIX (#6): Pagination added to get_activity_report and get_monthly_kpi.
# FIX (#7): next_work_code() replaced COUNT(*) race with PostgreSQL SEQUENCE
#           (wl_work_code_seq). Concurrent inserts now always get unique codes.
# =============================================================================
from django.db import connection
from typing import Optional
import datetime

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE     = 500


def generate_work_code(year: int, sequence: int) -> str:
    return f"WL-{year}-{sequence:06d}"


def next_work_code() -> str:
    """FIX (#7): Use a PostgreSQL per-year sequence to guarantee uniqueness
    under concurrent inserts. Sequence is auto-created if not present.
    The sequence name encodes the current year so codes reset each year.
    """
    year = datetime.date.today().year
    seq_name = f'wl_work_code_{year}_seq'
    with connection.cursor() as cur:
        # Create sequence for this year if it doesn't exist yet
        cur.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_sequences WHERE sequencename = '{seq_name}'
                ) THEN
                    CREATE SEQUENCE {seq_name} START 1 INCREMENT 1 NO CYCLE;
                END IF;
            END
            $$;
        """)
        cur.execute(f"SELECT nextval('{seq_name}')")
        seq_val = cur.fetchone()[0]
    return generate_work_code(year, seq_val)


def get_activity_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    section: Optional[str] = None,
    engineer_id: Optional[int] = None,
    officer_id: Optional[int] = None,
    category_code: Optional[str] = None,
    pl_number: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict:
    """FIX (#6): Returns paginated dict with {results, total_count, page, page_size}."""
    page_size = min(max(int(page_size), 1), MAX_PAGE_SIZE)
    page      = max(int(page), 1)
    offset    = (page - 1) * page_size

    filters = []
    params  = []

    if from_date:
        filters.append("wl.received_date >= %s")
        params.append(from_date)
    if to_date:
        filters.append("wl.received_date <= %s")
        params.append(to_date)
    if section:
        filters.append("wl.section = %s")
        params.append(section)
    if engineer_id:
        filters.append("wl.engineer_id = %s")
        params.append(engineer_id)
    if officer_id:
        filters.append("wl.officer_id = %s")
        params.append(officer_id)
    if category_code:
        filters.append("wl.work_category_code = %s")
        params.append(category_code)
    if pl_number:
        filters.append("wl.pl_number = %s")
        params.append(pl_number)
    if status:
        filters.append("wl.status = %s")
        params.append(status)

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    count_sql = f"""
        SELECT COUNT(*)
        FROM work_ledger wl
        JOIN work_category_master wcm ON wcm.code = wl.work_category_code
        {where_clause}
    """
    data_sql = f"""
        SELECT
            wl.work_id,
            wl.work_code,
            wl.received_date,
            wl.closed_date,
            wl.section,
            wl.status,
            wcm.label            AS work_category_label,
            wl.pl_number,
            wl.drawing_number,
            wl.tender_number,
            wl.remarks,
            wl.engineer_id,
            wl.officer_id
        FROM work_ledger wl
        JOIN work_category_master wcm ON wcm.code = wl.work_category_code
        {where_clause}
        ORDER BY wl.received_date DESC, wl.work_id DESC
        LIMIT %s OFFSET %s
    """
    with connection.cursor() as cur:
        cur.execute(count_sql, params)
        total_count = cur.fetchone()[0]

        cur.execute(data_sql, params + [page_size, offset])
        columns = [col[0] for col in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]

    return {
        'results':     results,
        'total_count': total_count,
        'page':        page,
        'page_size':   page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
    }


def get_monthly_kpi(
    year: int,
    month: int,
    section: Optional[str] = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict:
    """FIX (#6): Paginated monthly KPI summary."""
    page_size = min(max(int(page_size), 1), MAX_PAGE_SIZE)
    page      = max(int(page), 1)
    offset    = (page - 1) * page_size

    filters = [
        "EXTRACT(YEAR  FROM wl.received_date) = %s",
        "EXTRACT(MONTH FROM wl.received_date) = %s",
    ]
    params = [year, month]
    if section:
        filters.append("wl.section = %s")
        params.append(section)

    where_clause = "WHERE " + " AND ".join(filters)

    count_sql = f"""
        SELECT COUNT(DISTINCT wl.work_category_code)
        FROM work_ledger wl
        JOIN work_category_master wcm ON wcm.code = wl.work_category_code
        {where_clause}
    """
    data_sql = f"""
        SELECT
            wl.work_category_code,
            wcm.label   AS work_category_label,
            COUNT(*)    AS work_count
        FROM work_ledger wl
        JOIN work_category_master wcm ON wcm.code = wl.work_category_code
        {where_clause}
        GROUP BY wl.work_category_code, wcm.label, wcm.sort_order
        ORDER BY wcm.sort_order
        LIMIT %s OFFSET %s
    """
    with connection.cursor() as cur:
        cur.execute(count_sql, params)
        total_count = cur.fetchone()[0]

        cur.execute(data_sql, params + [page_size, offset])
        columns = [col[0] for col in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]

    return {
        'results':     results,
        'total_count': total_count,
        'page':        page,
        'page_size':   page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
    }


def get_dashboard_monthly_summary(year: int, month: int) -> dict:
    kpi = get_monthly_kpi(year, month, page_size=MAX_PAGE_SIZE)
    total = sum(r['work_count'] for r in kpi['results'])
    return {
        'month':       f'{year}-{month:02d}',
        'total':       total,
        'by_category': kpi['results'],
    }
