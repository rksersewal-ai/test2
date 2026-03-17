# =============================================================================
# FILE: apps/work_ledger/reports.py
# Monthly Work Report PDF generator for the active Work Ledger models.
# =============================================================================
import io
from datetime import date

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ImportError:  # pragma: no cover - optional dependency
    REPORTLAB_AVAILABLE = False
else:
    REPORTLAB_AVAILABLE = True
    PLW_NAVY = colors.HexColor('#003366')
    PLW_GOLD = colors.HexColor('#CC9900')
    PLW_LIGHT = colors.HexColor('#EEF2F7')


MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]


def _display_name(user) -> str:
    return (
        getattr(user, 'full_name', '')
        or getattr(user, 'get_full_name', lambda: '')()
        or str(user)
    )


def _display_section(user) -> str:
    section = getattr(user, 'section', None)
    if section is None:
        return ''
    return getattr(section, 'name', '') or str(section)


def _get_entries(user, year: int, month: int):
    from apps.work_ledger.models import WorkEntry

    return list(
        WorkEntry.objects.filter(
            user=user,
            work_date__year=year,
            work_date__month=month,
        )
        .order_by('work_date', 'created_at')
        .select_related('category')
        .prefetch_related('verifications')
    )


def _entry_effort(entry) -> str:
    if entry.effort_value is None:
        return ''
    return f'{entry.effort_value} {entry.get_effort_unit_display()}'


def generate_monthly_work_report(user, year: int, month: int) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise ImportError('ReportLab is required for PDF generation. Run: pip install reportlab')

    entries = _get_entries(user, year, month)

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'PLWTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=PLW_NAVY,
        alignment=1,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        'PLWBody',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
    )

    full_name = _display_name(user)
    designation = getattr(user, 'designation', '') or ''
    section = _display_section(user)
    employee_id = getattr(user, 'employee_id', '') or ''
    month_label = f'{MONTH_NAMES[month]} {year}'

    story = [
        Paragraph('PATIALA LOCOMOTIVE WORKS - LOCO DRAWING OFFICE', title_style),
        Paragraph('MONTHLY WORK REPORT', title_style),
        HRFlowable(width='100%', thickness=1.5, color=PLW_GOLD, spaceAfter=6),
    ]

    info_rows = [
        ['Staff Name:', full_name, 'Employee ID:', employee_id],
        ['Designation:', designation, 'Section:', section],
        ['Report Month:', month_label, 'Generated On:', date.today().strftime('%d-%b-%Y')],
    ]
    info_table = Table(info_rows, colWidths=[3.2 * cm, 7.6 * cm, 3.2 * cm, 7.0 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 0), (0, -1), PLW_NAVY),
                ('TEXTCOLOR', (2, 0), (2, -1), PLW_NAVY),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.extend([info_table, Spacer(1, 0.3 * cm)])

    table_rows = [[
        'Sr',
        'Date',
        'Work Type',
        'Category',
        'Description',
        'Reference',
        'Effort',
        'Status',
    ]]
    total_effort = 0.0
    work_type_summary: dict[str, int] = {}

    for index, entry in enumerate(entries, start=1):
        effort_value = float(entry.effort_value or 0)
        total_effort += effort_value
        work_type_label = entry.get_work_type_display()
        work_type_summary[work_type_label] = work_type_summary.get(work_type_label, 0) + 1

        table_rows.append(
            [
                str(index),
                entry.work_date.strftime('%d-%b-%Y') if entry.work_date else '',
                work_type_label,
                entry.category.name if entry.category else '',
                Paragraph(entry.description[:240], body_style),
                entry.reference_number or '',
                _entry_effort(entry),
                entry.get_status_display(),
            ]
        )

    if len(table_rows) == 1:
        table_rows.append(['', 'No entries found for this period.', '', '', '', '', '', ''])

    entries_table = Table(
        table_rows,
        colWidths=[0.8 * cm, 2.0 * cm, 4.0 * cm, 3.2 * cm, 10.4 * cm, 3.6 * cm, 3.0 * cm, 2.8 * cm],
        repeatRows=1,
    )
    entries_table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), PLW_NAVY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PLW_LIGHT]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (7, 1), (7, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ]
        )
    )
    story.extend([entries_table, Spacer(1, 0.5 * cm)])

    summary_rows = [['Work Type', 'Entry Count']]
    for work_type_label, count in sorted(work_type_summary.items(), key=lambda item: (-item[1], item[0])):
        summary_rows.append([work_type_label, str(count)])
    summary_rows.append(['TOTAL ENTRIES', str(len(entries))])
    summary_rows.append(['TOTAL EFFORT', f'{total_effort:.2f}'])

    summary_table = Table(summary_rows, colWidths=[9.5 * cm, 3.5 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), PLW_NAVY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -2), (-1, -1), PLW_GOLD),
                ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(summary_table)

    document.build(story)
    return buffer.getvalue()
