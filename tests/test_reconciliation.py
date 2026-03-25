import pytest
import pandas as pd
import reconciliation.engine as engine


@pytest.fixture
def feed_df() -> pd.DataFrame:
    """Deterministic feed trades exercising all mismatch branches."""
    settlement = pd.Timestamp("2026-03-01")
    return pd.DataFrame(
        [
            {
                "trade_id": "t_rate",
                "rate": 1.2000,
                "notional": 1000.00,
                "settlement_date": settlement,
                "status": "OPEN",
            },
            {
                "trade_id": "t_notional",
                "rate": 1.2000,
                "notional": 1000.00,
                "settlement_date": settlement,
                "status": "OPEN",
            },
            {
                "trade_id": "t_timing",
                "rate": 1.2000,
                "notional": 1000.00,
                "settlement_date": settlement,
                "status": "OPEN",
            },
            {
                "trade_id": "t_status",
                "rate": 1.2000,
                "notional": 1000.00,
                "settlement_date": settlement,
                "status": "OPEN",
            },
        ]
    )

@pytest.fixture
def ledger_df() -> pd.DataFrame:
    """Deterministic ledger trades with known mismatches."""
    settlement = pd.Timestamp("2026-03-01")
    return pd.DataFrame(
        [
            # RATE_MISMATCH: exceed RATE_TOLERANCE (0.0001)
            {
                "trade_id": "t_rate",
                "rate": 1.2002,
                "notional": 1000.00,
                "settlement_date": settlement,
                "status": "OPEN",
            },
            # NOTIONAL_MISMATCH: exceed NOTIONAL_TOLERANCE (0.01)
            {
                "trade_id": "t_notional",
                "rate": 1.2000,
                "notional": 1000.02,
                "settlement_date": settlement,
                "status": "OPEN",
            },
            # TIMING_DIFFERENCE
            {
                "trade_id": "t_timing",
                "rate": 1.2000,
                "notional": 1000.00,
                "settlement_date": pd.Timestamp("2026-03-02"),
                "status": "OPEN",
            },
            # STATUS_MISMATCH
            {
                "trade_id": "t_status",
                "rate": 1.2000,
                "notional": 1000.00,
                "settlement_date": settlement,
                "status": "SETTLED",
            },
        ]
    )

@pytest.fixture
def breaks(feed_df: pd.DataFrame, ledger_df: pd.DataFrame) -> pd.DataFrame:
    """Reconciliation output for deterministic inputs."""
    return engine.reconcile_trades(feed_df, ledger_df)


def test_reconciliation_returns_expected_trade_ids(breaks: pd.DataFrame) -> None:
    assert set(breaks["trade_id"]) == {
        "t_rate",
        "t_notional",
        "t_timing",
        "t_status",
    }


@pytest.mark.parametrize(
    ("trade_id", "expected_break_type"),
    [
        ("t_rate", "RATE_MISMATCH"),
        ("t_notional", "NOTIONAL_MISMATCH"),
        ("t_timing", "TIMING_DIFFERENCE"),
        ("t_status", "STATUS_MISMATCH"),
    ],
)
def test_reconciliation_break_types(
    breaks: pd.DataFrame, trade_id: str, expected_break_type: str
) -> None:
    by_trade_id = breaks.set_index("trade_id")["break_type"].to_dict()
    assert by_trade_id[trade_id] == expected_break_type