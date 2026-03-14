# =============================================================================
# FILE: apps/work_ledger/reports_excel.py
#
# Monthly Work Report — Excel (.xlsx) export using openpyxl.
#
# OUTPUT:
#   Sheet 1 — Work Entries  (full table with formatting)
#   Sheet 2 — Summary       (work type breakdown + totals)
#   Sheet 3 — Targets vs Actual (if WorkTarget exists for the month)
# =============================================================================
import io
from datetime import date

try:
    import openpyxl
    from openpyxl.styles import (
        PatternFill, Font, Alignment, Border, Side, numbers
    )
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# PLW palette
NAVY_HEX  = '003366'
GOLD_HEX  = 'CC9900'
LIGHT_HEX = 'EEF2F7'
WHITE     = 'FFFFFF'
GREY_BORDER = '999999'


def _fill(hex_color):
    return PatternFill(fill_type='solid', fgColor=hex_color)


def _font(bold=False, color='000000', size=10):
    return Font(bold=bold, color=color, size=size, name='Calibri')


def _border():
    thin = Side(style='thin', color=GREY_BORDER)
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def _center():
    return Alignment(horizontal='center', vertical='center', wrap_text=True)


def _left():
    return Alignment(horizontal='left', vertical='top', wrap_text=True)


def generate_monthly_work_report_excel(user, year: int, month: int) -> bytes:
    """
    Generate a monthly work report as .xlsx for `user`.
    Returns bytes.
    Raises ImportError if openpyxl is not installed.
    """
    if not OPENPYXL_AVAILABLE:
        raise ImportError(
            'openpyxl is required for Excel export. Run: pip install openpyxl'
        )

    from apps.work_ledger.models import WorkEntry, WorkTarget

    entries = (
        WorkEntry.objects
        .filter(created_by=user, work_date__year=year, work_date__month=month)
        .order_by('work_date', 'created_at')
        .select_related('category', 'verified_by')
    )
    month_str   = f'{MONTH_NAMES[month]} {year}'
    full_name   = getattr(user, 'get_full_name', lambda: str(user))()
    designation = getattr(user, 'designation', '') or ''
    section     = getattr(user, 'section', '') or ''
    employee_id = getattr(user, 'employee_id', '') or ''

    wb = openpyxl.Workbook()

    # ===========================================================
    # Sheet 1: Work Entries
    # ===========================================================
    ws1 = wb.active
    ws1.title = 'Work Entries'
    ws1.sheet_view.showGridLines = False

    # --- Title rows ---
    ws1.merge_cells('A1:J1')
    ws1['A1'] = 'PATIALA LOCOMOTIVE WORKS — LOCO DRAWING OFFICE'
    ws1['A1'].font      = _font(bold=True, color=WHITE, size=13)
    ws1['A1'].fill      = _fill(NAVY_HEX)
    ws1['A1'].alignment = _center()
    ws1.row_dimensions[1].height = 22

    ws1.merge_cells('A2:J2')
    ws1['A2'] = f'MONTHLY WORK REPORT — {month_str.upper()}'
    ws1['A2'].font      = _font(bold=True, color=WHITE, size=11)
    ws1['A2'].fill      = _fill(NAVY_HEX)
    ws1['A2'].alignment = _center()
    ws1.row_dimensions[2].height = 18

    # --- Staff info block ---
    info = [
        ('Staff Name', full_name,   'Employee ID',    employee_id),
        ('Designation', designation, 'Section',        section),
        ('Report Month', month_str, 'Generated On',   date.today().strftime('%d-%b-%Y')),
    ]
    for r_idx, (l1, v1, l2, v2) in enumerate(info, start=3):
        ws1.cell(r_idx, 1, l1).font = _font(bold=True, color=NAVY_HEX)
        ws1.cell(r_idx, 2, v1)
        ws1.cell(r_idx, 5, l2).font = _font(bold=True, color=NAVY_HEX)
        ws1.cell(r_idx, 6, v2)
    ws1.row_dimensions[6].height = 6  # spacer

    # --- Table header ---
    headers = [
        'Sr', 'Date', 'Work Type', 'Category',
        'Subject / Description', 'Reference No.',
        'Hours', 'e-Office File No.', 'Status', 'Verified By'
    ]
    col_widths = [5, 13, 18, 16, 40, 18, 8, 20, 14, 20]
    HDR_ROW = 7

    for col_idx, (hdr, width) in enumerate(zip(headers, col_widths), start=1):
        cell = ws1.cell(HDR_ROW, col_idx, hdr)
        cell.font      = _font(bold=True, color=WHITE)
        cell.fill      = _fill(NAVY_HEX)
        cell.alignment = _center()
        cell.border    = _border()
        ws1.column_dimensions[get_column_letter(col_idx)].width = width
    ws1.row_dimensions[HDR_ROW].height = 20

    # --- Data rows ---
    total_hours = 0
    work_type_summary = {}

    for idx, entry in enumerate(entries, start=1):
        row = HDR_ROW + idx
        hours = float(entry.hours_spent or 0)
        total_hours += hours
        wtype = entry.get_work_type_display()
        work_type_summary[wtype] = work_type_summary.get(wtype, 0) + hours

        verified_name = ''
        if entry.verified_by:
            verified_name = getattr(entry.verified_by, 'get_full_name', lambda: '')() or ''

        row_fill = _fill(LIGHT_HEX) if idx % 2 == 0 else _fill(WHITE)
        values   = [
            idx,
            entry.work_date.strftime('%d-%b-%Y') if entry.work_date else '',
            wtype,
            entry.category.category_name if entry.category else '',
            str(entry.work_description)[:300],
            entry.reference_number or '',
            hours,
            entry.eoffice_file_no or '',
            entry.get_status_display(),
            verified_name,
        ]
        for c, val in enumerate(values, start=1):
            cell            = ws1.cell(row, c, val)
            cell.fill       = row_fill
            cell.border     = _border()
            cell.alignment  = _center() if c in (1, 7) else _left()
            cell.font       = _font(size=9)
        ws1.row_dimensions[row].height = 15

    # --- Total row ---
    total_row = HDR_ROW + len(list(entries)) + 1
    ws1.merge_cells(f'A{total_row}:F{total_row}')
    tc = ws1.cell(total_row, 1, 'TOTAL HOURS')
    tc.font = _font(bold=True, color=WHITE)
    tc.fill = _fill(GOLD_HEX)
    tc.alignment = _center()
    for c in range(1, 7):
        ws1.cell(total_row, c).fill = _fill(GOLD_HEX)
    th = ws1.cell(total_row, 7, round(total_hours, 1))
    th.font = _font(bold=True)
    th.fill = _fill(GOLD_HEX)
    th.alignment = _center()

    ws1.freeze_panes = f'A{HDR_ROW + 1}'

    # ===========================================================
    # Sheet 2: Summary
    # ===========================================================
    ws2 = wb.create_sheet('Summary')
    ws2.sheet_view.showGridLines = False
    ws2.column_dimensions['A'].width = 30
    ws2.column_dimensions['B'].width = 14
    ws2.column_dimensions['C'].width = 14

    ws2.merge_cells('A1:C1')
    ws2['A1'] = f'Work Type Summary — {month_str}'
    ws2['A1'].font      = _font(bold=True, color=WHITE, size=12)
    ws2['A1'].fill      = _fill(NAVY_HEX)
    ws2['A1'].alignment = _center()

    hdr_row = ['Work Type', 'Hours', '% of Total']
    for c, h in enumerate(hdr_row, 1):
        cell = ws2.cell(2, c, h)
        cell.font = _font(bold=True, color=WHITE)
        cell.fill = _fill(NAVY_HEX)
        cell.alignment = _center()
        cell.border = _border()

    for r, (wtype, hrs) in enumerate(sorted(work_type_summary.items(), key=lambda x: -x[1]), start=3):
        pct = round(hrs / total_hours * 100, 1) if total_hours else 0
        row_fill = _fill(LIGHT_HEX) if r % 2 == 0 else _fill(WHITE)
        for c, val in enumerate([wtype, round(hrs, 1), f'{pct}%'], start=1):
            cell = ws2.cell(r, c, val)
            cell.fill = row_fill
            cell.border = _border()
            cell.alignment = _center()
            cell.font = _font(size=9)

    total_r = 3 + len(work_type_summary)
    for c, val in enumerate(['TOTAL', round(total_hours, 1), '100%'], start=1):
        cell = ws2.cell(total_r, c, val)
        cell.font = _font(bold=True)
        cell.fill = _fill(GOLD_HEX)
        cell.alignment = _center()
        cell.border = _border()

    # ===========================================================
    # Sheet 3: Targets vs Actual
    # ===========================================================
    ws3 = wb.create_sheet('Targets vs Actual')
    ws3.sheet_view.showGridLines = False
    ws3.column_dimensions['A'].width = 30
    ws3.column_dimensions['B'].width = 14
    ws3.column_dimensions['C'].width = 14
    ws3.column_dimensions['D'].width = 18

    ws3.merge_cells('A1:D1')
    ws3['A1'] = f'Targets vs Actual — {month_str}'
    ws3['A1'].font      = _font(bold=True, color=WHITE, size=12)
    ws3['A1'].fill      = _fill(NAVY_HEX)
    ws3['A1'].alignment = _center()

    for c, h in enumerate(['Work Type', 'Target Hours', 'Actual Hours', 'Achievement'], start=1):
        cell = ws3.cell(2, c, h)
        cell.font = _font(bold=True, color=WHITE)
        cell.fill = _fill(NAVY_HEX)
        cell.alignment = _center()
        cell.border = _border()

    from apps.work_ledger.models import WorkTarget
    targets = WorkTarget.objects.filter(
        user=user, year=year, month=month
    )
    r = 3
    for tgt in targets:
        actual = work_type_summary.get(tgt.get_work_type_display(), 0)
        target = float(tgt.target_hours or 0)
        achv   = f'{round(actual/target*100, 1)}%' if target else 'N/A'
        for c, val in enumerate(
            [tgt.get_work_type_display(), round(target, 1), round(actual, 1), achv],
            start=1
        ):
            cell = ws3.cell(r, c, val)
            cell.border = _border()
            cell.alignment = _center()
            cell.font = _font(size=9)
        r += 1

    if targets.count() == 0:
        ws3.merge_cells('A3:D3')
        ws3['A3'] = 'No targets set for this period.'
        ws3['A3'].alignment = _center()
        ws3['A3'].font = _font(size=9, color='888888')

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
