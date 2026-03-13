from django.db import connection
from django.utils.dateparse import parse_date
from typing import Optional
import datetime


def generate_work_code(year: int, sequence: int) -> str:
    return f"WL-{year}-{sequence:06d}"


def next_work_code() -> str:
    year = datetime.date.today().year
    with connection.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM work_ledger WHERE EXTRACT(YEAR FROM received_date) = %s",
            [year],
        )
        count = cur.fetchone()[0]
    return generate_work_code(year, count + 1)


def get_activity_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    section: Optional[str] = None,
    engineer_id: Optional[int] = None,
    officer_id: Optional[int] = None,
    category_code: Optional[str] = None,
    pl_number: Optional[str] = None,
    status: Optional[str] = None,
) -> list:
    filters = []
    params = []

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

    sql = f"""
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
    """
    with connection.cursor() as cur:
        cur.execute(sql, params)
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_monthly_kpi(
    year: int,
    month: int,
    section: Optional[str] = None,
) -> list:
    filters = ["EXTRACT(YEAR FROM wl.received_date) = %s",
               "EXTRACT(MONTH FROM wl.received_date) = %s"]
    params = [year, month]
    if section:
        filters.append("wl.section = %s")
        params.append(section)

    where_clause = "WHERE " + " AND ".join(filters)
    sql = f"""
        SELECT
            wl.work_category_code,
            wcm.label   AS work_category_label,
            COUNT(*)    AS work_count
        FROM work_ledger wl
        JOIN work_category_master wcm ON wcm.code = wl.work_category_code
        {where_clause}
        GROUP BY wl.work_category_code, wcm.label, wcm.sort_order
        ORDER BY wcm.sort_order
    """
    with connection.cursor() as cur:
        cur.execute(sql, params)
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_dashboard_monthly_summary(year: int, month: int) -> dict:
    rows = get_monthly_kpi(year, month)
    total = sum(r["work_count"] for r in rows)
    return {"month": f"{year}-{month:02d}", "total": total, "by_category": rows}
