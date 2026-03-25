# src/reporting/pdf_report.py
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas


def generate_pdf_summary_report(
    run_metadata: dict,
    breaks_df: pd.DataFrame,
    exposure_df: pd.DataFrame,
    output_dir: str = "reports"
) -> str:
    """
    Generates a clean one-page (or two-page) executive PDF summary.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filename = f"FX_Recon_Summary_{run_metadata['run_date'].strftime('%Y%m%d_%H%M')}.pdf"
    filepath = Path(output_dir) / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  # center
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10
    )
    normal_style = styles['Normal']

    elements = []

    # ==================== HEADER ====================
    elements.append(Paragraph("FX Reconciliation & Exposure Monitor", title_style))
    elements.append(Paragraph(
        f"Daily Executive Summary — {run_metadata['run_date'].strftime('%d %B %Y %H:%M')}",
        styles['Heading2']
    ))
    elements.append(Spacer(1, 20))

    # ==================== SUMMARY SECTION ====================
    elements.append(Paragraph("Summary", heading_style))

    summary_data = [
        ["Metric", "Value"],
        ["Total Trades Processed", str(run_metadata.get("total_trades", "N/A"))],
        ["Breaks Detected", str(run_metadata.get("breaks_found", len(breaks_df)))],
        ["Margin Breaches / Warnings", str(run_metadata.get("breaches_found", 0))],
        ["Feed Rows", str(run_metadata.get("feed_rows", "N/A"))],
        ["Ledger Rows", str(run_metadata.get("ledger_rows", "N/A"))],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # ==================== BREAKS SUMMARY ====================
    elements.append(Paragraph("Reconciliation Breaks", heading_style))

    if breaks_df.empty:
        elements.append(Paragraph("✅ No breaks detected — all trades reconciled cleanly.", normal_style))
    else:
        break_summary = breaks_df['break_type'].value_counts().reset_index()
        break_summary.columns = ['Break Type', 'Count']

        break_data = [["Break Type", "Count"]] + break_summary.values.tolist()

        break_table = Table(break_data, colWidths=[4*inch, 2*inch])
        break_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(break_table)

    elements.append(Spacer(1, 20))

    # ==================== EXPOSURE SUMMARY ====================
    elements.append(Paragraph("Counterparty Exposure & Margin Status", heading_style))

    if exposure_df.empty:
        elements.append(Paragraph("No open positions.", normal_style))
    else:
        # Select key columns (adjust to match your exposure_df)
        display_cols = ['counterparty', 'current_exposure', 'limit_quote_ccy', 'utilisation_pct', 'status']
        display_df = exposure_df[display_cols].copy() if all(c in exposure_df.columns for c in display_cols) else exposure_df

        # Round for nicer display
        if 'utilisation_pct' in display_df.columns:
            display_df['utilisation_pct'] = display_df['utilisation_pct'].round(1)

        exposure_data = [display_df.columns.tolist()] + display_df.values.tolist()

        exp_table = Table(exposure_data, colWidths=[2.2*inch, 1.4*inch, 1.4*inch, 1.2*inch, 1*inch])
        exp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ]))

        # Colour rows based on status
        for i, row in enumerate(exposure_df.itertuples(), 1):
            status = getattr(row, 'status', '')
            if status == "BREACH":
                exp_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.red)]))
            elif status == "WARNING":
                exp_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.orange)]))

        elements.append(exp_table)

    elements.append(Spacer(1, 30))
    elements.append(Paragraph("End of Daily Summary Report", styles['Normal']))

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF Summary Report saved: {filepath}")
    return str(filepath)


# ====================== QUICK TEST CALL ======================
if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime

    test_meta = {
        "run_date": datetime.now(),
        "total_trades": 245,
        "breaks_found": 7,
        "breaches_found": 2,
        "feed_rows": 120,
        "ledger_rows": 130,
    }

    # Dummy data - replace with your real DataFrames
    test_breaks = pd.DataFrame({
        "break_type": ["NOTIONAL_MISMATCH", "RATE_MISMATCH", "TIMING_DIFFERENCE"] * 2 + ["NOTIONAL_MISMATCH"]
    })

    test_exposure = pd.DataFrame({
        "counterparty": ["CounterpartyA", "CounterpartyB", "CounterpartyC"],
        "current_exposure": [850000, 620000, 120000],
        "limit_quote_ccy": [1000000, 500000, 300000],
        "utilisation_pct": [85.0, 124.0, 40.0],
        "status": ["WARNING", "BREACH", "OK"]
    })

    generate_pdf_summary_report(test_meta, test_breaks, test_exposure)