import pytest
import reconciliation.engine as engine
import synthetic.generate_dataset as generate_dataset
import ingestion.csv_reader as csv_reader
import ingestion.json_reader as json_reader


def test_data_generation_and_ingestion():
    generate_dataset.main()
    feed_df = csv_reader.parse_csv(csv_reader.read_csv())
    ledger_df = json_reader.parse_json(json_reader.read_json())
    breaks = engine.reconcile_trades(feed_df, ledger_df)
    print(breaks)
    assert not breaks.empty
    assert "trade_id" in breaks.columns
