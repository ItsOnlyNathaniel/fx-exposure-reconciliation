# FX Exposure Reconciliation & Monitoring Dashboard

**Python tool that automates FX trade reconciliation, flags breaks, calculates real-time mark-to-market exposure, triggers margin alerts, and provides audit-ready reporting — built to mirror daily workflows in FX/payments operations.**

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

## Tech Stack
- Python 3.10+
- Pandas (data wrangling)
- SQLAlchemy + SQLite (persistence & audit)
- Streamlit (dashboard)
- Requests (FX API)
- OpenPyXL & ReportLab (reports)
- Pytest (testing)

## Quick Start
```bash
# Clone & install
git clone https://github.com/ItsOnlyNathaniel/fx-exposure-reconciliation.git
cd fx-exposure-reconciliation
pip install -r requirements.txt

# Run reconciliation pipeline (CLI mode)
python src/main.py  # or wherever your entry point is

# Launch dashboard
streamlit run src/dashboard/app.py  # adjust path if needed
