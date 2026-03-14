import csv
import io
from typing import List, Dict


def build_csv_response(rows: List[Dict], fields: List[str]) -> str:
    """Return CSV string for the given rows and field list."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


ACTIVITY_REPORT_FIELDS = [
    "work_code",
    "received_date",
    "closed_date",
    "section",
    "engineer_id",
    "officer_id",
    "work_category_label",
    "pl_number",
    "drawing_number",
    "tender_number",
    "status",
    "remarks",
]

KPI_REPORT_FIELDS = [
    "work_category_code",
    "work_category_label",
    "work_count",
]
