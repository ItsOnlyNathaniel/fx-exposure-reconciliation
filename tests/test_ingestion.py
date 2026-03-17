import pytest
import reconciliation.engine as engine
import synthetic.generate_dataset as generate_dataset
import ingestion.file_reader as file_reader


def test_data_generation_and_ingestion():
    generate_dataset.main()
    feed_df = file_reader.parse(file_reader.read_csv())
    ledger_df = file_reader.parse(file_reader.read_json())
    breaks = engine.reconcile_trades(feed_df, ledger_df)
    
    assert not breaks.empty
    assert "trade_id" in breaks.columns
