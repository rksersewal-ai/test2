# =============================================================================
# FILE: apps/work_ledger/reports.py
#
# Monthly Work Report PDF generator.
# Uses ReportLab (pip install reportlab).
#
# OUTPUT FORMAT:
#   PLW Loco Drawing Office — Monthly Work Report
#   Staff Name | Month | Year | Section
#   Table: Sr | Date | Work Type | Subject | Reference | Hours | Status
#   Summary: Total entries, total hours, breakdown by work type
#   Supervisor verification block (signature line)
# =============================================================================
import io
from datetime import date

try:
    from reportlab.lib              import colors
    from reportlab.lib.pagesizes    import A4, landscape
    from reportlab.lib.styles       import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units        import cm
    from reportlab.platypus         import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# PLW brand colours
PLW_NAVY  = colors.HexColor('#003366')
PLW_GOLD  = colors.HexColor('#CC9900')
PLW_LIGHT = colors.HexColor('#EEF2F7')

MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]


def generate_monthly_work_report(user, year: int, month: int) -> bytes:
    """
    Generate a monthly work report PDF for `user` for the given year/month.
    Returns PDF bytes.
    Raises ImportError if reportlab is not installed.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            'ReportLab is required for PDF generation. '
            'Run: pip install reportlab'
        )

    from apps.work_ledger.models import WorkEntry

    entries = (
        WorkEntry.objects
        .filter(
            created_by=user,
            work_date__year=year,
            work_date__month=month,
        )
        .order_by('work_date', 'created_at')
        .select_related('category', 'verified_by')
    )

    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm,
    )
    styles = getSampleStyleSheet()
    story  = []

    # --- Header ------------------------------------------------------------
    title_style = ParagraphStyle(
        'PLWTitle',
        parent=styles['Heading1'],
        fontSize=13, textColor=PLW_NAVY, spaceAfter=2,
        fontName='Helvetica-Bold', alignment=1,
    )
    sub_style = ParagraphStyle(
        'PLWSub',
        parent=styles['Normal'],
        fontSize=9, textColor=PLW_NAVY, alignment=1, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'PLWBody', parent=styles['Normal'],
        fontSize=8.5, leading=12,
    )

    story.append(Paragraph('PATIALA LOCOMOTIVE WORKS — LOCO DRAWING OFFICE', title_style))
    story.append(Paragraph('MONTHLY WORK REPORT', title_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=PLW_GOLD, spaceAfter=6))

    # --- Staff details -----------------------------------------------------
    full_name   = getattr(user, 'get_full_name', lambda: str(user))()
    designation = getattr(user, 'designation', '') or ''
    section     = getattr(user, 'section', '') or ''
    employee_id = getattr(user, 'employee_id', '') or ''
    month_str   = f'{MONTH_NAMES[month]} {year}'

    info_data = [
        ['Staff Name:', full_name,      'Employee ID:', employee_id],
        ['Designation:', designation,   'Section:',     section],
        ['Report Month:', month_str,    'Generated On:', date.today().strftime('%d-%b-%Y')],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8.5),
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), PLW_NAVY),
        ('TEXTCOLOR', (2,0), (2,-1), PLW_NAVY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=PLW_LIGHT, spaceAfter=6))

    # --- Work entries table ------------------------------------------------
    col_headers = [
        'Sr', 'Date', 'Work Type', 'Category',
        'Subject / Description', 'Reference No.',
        'Hours', 'e-Office\nFile No.', 'Status', 'Verified By'
    ]
    col_widths  = [
        0.8*cm, 2.2*cm, 3*cm, 2.5*cm,
        8.5*cm, 3*cm,
        1.3*cm, 3.5*cm, 2*cm, 3*cm
    ]

    table_data = [col_headers]
    total_hours = 0
    work_type_summary = {}

    for idx, entry in enumerate(entries, start=1):
        hours = float(entry.hours_spent or 0)
        total_hours += hours
        wtype = entry.get_work_type_display()
        work_type_summary[wtype] = work_type_summary.get(wtype, 0) + hours

        verified_by_name = ''
        if entry.verified_by:
            verified_by_name = getattr(entry.verified_by, 'get_full_name', lambda: '')() or ''

        subject_para = Paragraph(
            str(entry.work_description)[:200],
            ParagraphStyle('cell', fontSize=7.5, leading=10)
        )

        table_data.append([
            str(idx),
            entry.work_date.strftime('%d-%b-%Y') if entry.work_date else '',
            wtype,
            entry.category.category_name if entry.category else '',
            subject_para,
            entry.reference_number or '',
            f'{hours:.1f}',
            entry.eoffice_file_no or '',
            entry.get_status_display(),
            verified_by_name,
        ])

    if not entries:
        table_data.append(['', 'No entries found for this period.', '', '', '', '', '', '', '', ''])

    entries_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    entries_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND',    (0,0), (-1,0), PLW_NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 8),
        ('ALIGN',         (0,0), (-1,0), 'CENTER'),
        ('VALIGN',        (0,0), (-1,0), 'MIDDLE'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, PLW_LIGHT]),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 7.5),
        ('VALIGN',        (0,1), (-1,-1), 'TOP'),
        ('ALIGN',         (0,1), (0,-1), 'CENTER'),   # Sr
        ('ALIGN',         (6,1), (6,-1), 'CENTER'),   # Hours
        ('ALIGN',         (8,1), (8,-1), 'CENTER'),   # Status
        ('GRID',          (0,0), (-1,-1), 0.4, colors.grey),
        ('TOPPADDING',    (0,1), (-1,-1), 3),
        ('BOTTOMPADDING', (0,1), (-1,-1), 3),
    ]))
    story.append(entries_table)
    story.append(Spacer(1, 0.5*cm))

    # --- Summary block -----------------------------------------------------
    story.append(Paragraph('<b>WORK SUMMARY</b>', ParagraphStyle(
        'SumHead', parent=styles['Normal'],
        fontSize=9, textColor=PLW_NAVY, fontName='Helvetica-Bold', spaceAfter=4
    )))

    summary_rows = [['Work Type', 'Hours Spent', '% of Total']]
    for wtype, hrs in sorted(work_type_summary.items(), key=lambda x: -x[1]):
        pct = (hrs / total_hours * 100) if total_hours else 0
        summary_rows.append([wtype, f'{hrs:.1f}', f'{pct:.1f}%'])
    summary_rows.append(['TOTAL', f'{total_hours:.1f}', '100%'])

    sum_table = Table(summary_rows, colWidths=[7*cm, 3.5*cm, 3.5*cm])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), PLW_NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('BACKGROUND',    (0,-1), (-1,-1), PLW_GOLD),
        ('FONTNAME',      (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID',          (0,0), (-1,-1), 0.4, colors.grey),
        ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 0.8*cm))

    # --- Signature block ---------------------------------------------------
    sig_data = [
        ['Prepared By', 'Verified By (SSE/JE)', 'Approved By (WM/Officer)'],
        ['\n\n\n\n', '\n\n\n\n', '\n\n\n\n'],
        [full_name, '________________________', '________________________'],
        [designation, '', ''],
        [month_str, 'Date:', 'Date:'],
    ]
    sig_table = Table(sig_data, colWidths=[9*cm, 9*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'BOTTOM'),
        ('BOX',        (0,0), (0,-1), 0.5, PLW_NAVY),
        ('BOX',        (1,0), (1,-1), 0.5, PLW_NAVY),
        ('BOX',        (2,0), (2,-1), 0.5, PLW_NAVY),
        ('BACKGROUND', (0,0), (-1,0), PLW_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buf.getvalue()
