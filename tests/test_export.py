import pyarrow.parquet as pq

from peaklive.analysis import ExportRow, export_csv, export_parquet


def _rows():
    yield ExportRow(0.0, "VehicleStatus", "Speed", 12.3, "km/h")
    yield ExportRow(0.1, "VehicleStatus", "Speed", 12.4, "km/h")


def test_streams_csv_and_parquet_exports(tmp_path):
    csv_path = tmp_path / "signals.csv"
    parquet_path = tmp_path / "signals.parquet"

    assert export_csv(csv_path, _rows()) == 2
    assert export_parquet(parquet_path, _rows(), batch_size=1) == 2

    assert "VehicleStatus" in csv_path.read_text(encoding="utf-8")
    assert pq.read_table(parquet_path).to_pylist()[1]["value"] == "12.4"
