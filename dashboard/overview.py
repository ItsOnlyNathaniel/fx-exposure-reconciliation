import streamlit as sl
import pandas as pd


sl.title("Title - FX Reconciliation & Monitoring Dashboard")
sl.header("Header - Automating daily FX trade reconciliation and risk oversight")

pg = sl.navigation([sl.Page("breaks.py",title="Reconcilaiation Breaks"), sl.Page("exposure.py",title="Exposure Monitor"), sl.Page("audit.py,",title="Audit Log")])
sl.set_page_config(page_title="Dashboard")#, page_icon=":material/edit":)
sl.markdown (
    """
    # FX Exposure Reconciliation & Monitoring Dashboard

    **Python tool that automates FX trade reconciliation, flags breaks, calculates real-time mark-to-market exposure, triggers margin alerts, and provides audit-ready reporting — built to mirror daily workflows in FX/payments operations.**

    Live demo: [https://your-streamlit-app-url.streamlit.app](https://your-streamlit-app-url.streamlit.app) ← **add this as soon as deployed!**

    ## Problem it solves
    Small/mid-size FX firms deal with mismatched trade feeds from banks, internal systems, and counterparties. Manual reconciliation is slow, error-prone, and misses margin/credit risks. This project automates:
    - Ingestion from multiple formats (CSV/JSON simulated feeds)
    - Matching & break detection (missing, value mismatch, timing, duplicates)
    - Live FX rate enrichment (via frankfurter.app)
    - Counterparty exposure monitoring & margin call flagging
    - Audit logging + professional reports (Excel + PDF)

    Directly relevant to roles in FX operations, payments reconciliation, risk control.

    ## Key Features
    - Dual-feed reconciliation with configurable break classification
    - Real-time mark-to-market using live exchange rates
    - Margin breach detection with severity levels (warning/breach)
    - Persistent audit trail (SQLite)
    - Interactive Streamlit dashboard: overview KPIs, break explorer, exposure by pair, run history
    - Unit tests on core logic (pytest)
    - Clean report outputs (OpenPyXL + ReportLab)

    *** README used as placeholder text - think Lorem Ipsum 

    """
)
pg.run()

with sl.sidebar:
    sl.sidebar.header(("Sidebar Header - This should appear at the top."))
    with sl.echo():
        sl.write("Overview")
        sl.write("Reconciliation Breaks")
        sl.write("Exposure Monitor")
        sl.write("Audit Log")
