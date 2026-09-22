"""Render README screenshots from a private ASC file using the actual Qt widgets.

Display titles are adapted and sensitive fields are redacted in the widgets
before capture. Source frames, DBCs, decoded values and timestamps are unchanged.
No CAN connection is opened and no private input is copied into the repository.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QHeaderView

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.dbc import signal_display_title
from peaklive.analysis.replay import iter_trace
from peaklive.app import apply_application_identity, apply_application_theme
from peaklive.domain import CanFrame
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileStore
from peaklive.services.ui_settings import UiSettingsStore
from peaklive.ui import MainWindow
from peaklive.ui.dialogs.recording import RecordingSettingsDialog
from peaklive.ui.panels.trace_view import RECORD_INDEX_ROLE

SOURCES = {
    "Motor_Current": ("transparent_signals.dbc", "Courant moteur"),
    "Vehicle_Speed": ("transparent_signals.dbc", "Vitesse"),
    "High_Voltage": ("transparent_signals.dbc", "Tension haute"),
}


def redact_widgets(window: MainWindow) -> None:
    """Redact actual widget text, so sensitive pixels never enter the PNG."""
    tree = window.explorer_panel.tree
    tree.blockSignals(True)
    for index in range(tree.topLevelItemCount()):
        database = tree.topLevelItem(index)
        database.setText(0, "Base de démonstration")
        for child in range(database.childCount()):
            message = database.child(child)
            message.setText(0, f"Message {child + 1} · ID masqué")
            for row in range(message.childCount()):
                signal = message.child(row)
                for source, (_, label) in SOURCES.items():
                    if signal.text(0).startswith(source):
                        signal.setText(0, signal.text(0).replace(source, label, 1))
    tree.blockSignals(False)
    for column, spec in enumerate(c for c in window.trace_panel.columns if c.visible):
        if spec.key in {"id", "data", "message"}:
            for row in range(window.trace_table.rowCount()):
                window.trace_table.item(row, column).setText("Masqué")
    body = window.inspector.body.text()
    for key in ("arbitration_id", "payload", "payload_bytes", "database", "message"):
        label = translate(f"inspector.{key}")
        body = re.sub(rf"(?m)^{re.escape(label)}:.*$", f"{label}: Masqué", body)
    window.inspector.body.setText(body)
    report = window.report_panel.view.toPlainText()
    report = re.sub(r"0x[0-9A-Fa-f]+x?", "[ID masqué]", report)
    report = re.sub(r"latest=.*? count=", "latest=[octets masqués] count=", report)
    for summary in window._dbc_summaries():
        report = report.replace(summary.name, "Base de démonstration")
        report = report.replace(summary.short_hash, "empreinte masquée")
        assert summary.name not in report and summary.short_hash not in report
    assert not re.search(r"0x[0-9A-Fa-f]+", report)
    assert not re.search(r"latest=(?!\[octets masqués\])", report)
    window.report_panel.view.setPlainText(report)
    window.report_panel.view.moveCursor(window.report_panel.view.textCursor().MoveOperation.Start)


def pump(app: QApplication, seconds: float = 0.5) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("dbc_directory", type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/images"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    apply_application_theme(app)
    apply_application_identity(app)
    with TemporaryDirectory(prefix="peaklive-readme-") as directory, ExitStack() as stack:
        ui_settings = UiSettingsStore(Path(directory))
        ui_settings.save_locale("fr")
        window = MainWindow(
            ProfileStore(Path(directory)), adapter_factory=FakeCanAdapter,
            ui_settings=ui_settings,
        )
        try:
            for filename in sorted({source[0] for source in SOURCES.values()}):
                window._load_dbc_path(args.dbc_directory / filename)
            references = {
                ref.signal_key: ref
                for ref in window._catalog.signal_references()
                if ref.signal_name in SOURCES
            }
            if len(references) != 3:
                raise RuntimeError(f"Expected exactly three source signals, got {references}")
            aliases = {key: SOURCES[ref.signal_name][1] for key, ref in references.items()}

            def title(name: str) -> str:
                return aliases.get(name, signal_display_title(name))

            for module in ("graph_lane_header", "signal_summary"):
                stack.enter_context(patch(
                    f"peaklive.ui.panels.{module}.signal_display_title", side_effect=title
                ))
            window._selected_signal_names = set(references)
            window._favorite_signal_names = set(references)
            window.explorer_panel.refresh(
                window._catalog.signal_references(), set(references), set(references)
            )
            window._sync_graphs()
            # A cropped extract must retain the original acquisition clock,
            # rather than rebasing its first sample to zero.
            window._series._origin = 0.0
            window._facts.source = "Capture de démonstration · 370–530 s"
            window.resize(1680, 1050)
            window.show()
            # Keep the source timestamps and values; order the excerpt for the
            # bisect-based cursor calculations even if ASC lines arrive late.
            frames = sorted(
                (record for record in iter_trace(args.capture)
                 if isinstance(record, CanFrame) and 370 <= record.timestamp <= 530),
                key=lambda record: record.timestamp,
            )
            count = len(frames)
            batch = []
            for record in frames:
                batch.append(record)
                if len(batch) >= 1000:
                    window._ingest_frames(batch, coalesce=True)
                    batch = []
                    app.processEvents()
            if batch:
                window._ingest_frames(batch, coalesce=True)
            deadline = time.monotonic() + 60
            while window._history_batches_settled < window._history_batches_submitted:
                pump(app, 0.05)
                if time.monotonic() > deadline or window._history_failed:
                    raise RuntimeError("History did not settle")
            window._settle_presentation()
            for key in references:
                series = window._series.series(key)
                if series is None or not len(series):
                    raise RuntimeError(f"Missing samples: {key}")
                print(f"{title(key)}: {len(series)} samples, {series.bounds}", flush=True)
            window.acquisition_bar.set_bus_state("disconnected")
            window.status.showMessage("Démonstration · 370–530 s · identifiants et octets masqués")
            window.inspector_panel.set_hidden(True)
            window.workspace.setSizes([330, 1350, 0])
            graph = window.graph_panel
            graph.set_follow_live(False)
            graph.place_cursor("a", 400.0)
            graph.place_cursor("b", 480.0)
            window._sync_graphs()
            graph.fit_y()
            next(iter(graph.plots.values())).setXRange(370, 530, padding=0)
            window.signal_summary_panel.refresh(window._series, set(references))
            window.signal_summary_panel.tree.header().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            window.explorer_panel.shown_only.setChecked(True)
            pump(app)
            window.explorer_panel.tree.expandAll()
            graph.measurement.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            graph.measurement.table.setWordWrap(False)
            graph.measurement.table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )

            def capture(name: str, widget=window) -> None:
                pump(app)
                if name in {"graphs.png", "workspace.png"}:
                    next(iter(graph.plots.values())).setXRange(370, 530, padding=0)
                    pump(app)
                    low, high = graph.visible_window()
                    assert abs(low - 370) < 0.01 and abs(high - 530) < 0.01
                    for key in references:
                        series = window._series.series(key)
                        assert 370 <= series.bounds[0] <= series.bounds[1] <= 530
                    for row in range(graph.measurement.table.rowCount()):
                        assert int(graph.measurement.table.item(row, 4).text()) > 0
                redact_widgets(window)
                if not widget.grab().save(str(args.output / name)):
                    raise RuntimeError(f"Could not save {name}")
                print(f"Saved {name}", flush=True)

            def mode(value: str) -> None:
                selector = window.workspace_mode_selector
                selector.setCurrentIndex(selector.findData(value))

            mode("graphs")
            window.signals_panel.set_hidden(True)
            capture("graphs.png")
            window.signals_panel.set_hidden(False)
            mode("combo")
            window.center_divider.setSizes([600, 250, 0])
            capture("workspace.png")
            mode("trace")
            window.inspector_panel.set_hidden(False)
            window.workspace.setSizes([280, 1000, 400])
            for row in range(window.trace_table.rowCount()):
                item = window.trace_table.item(row, 0)
                record = window._trace.record(item.data(RECORD_INDEX_ROLE))
                if record is not None and record.message_name == "Motor_Status":
                    window.trace_table.setCurrentCell(row, 0)
                    break
            else:
                window.trace_table.setCurrentCell(0, 0)
            capture("trace.png")
            window.inspector_panel.set_hidden(True)
            window.signals_panel.set_hidden(True)
            mode("report")
            window._refresh_report()
            capture("report.png")
            window.selected_profile.name = "Démonstration"
            window.selected_profile.recording.directory = "C:/Captures"
            window.selected_profile.recording.text = "essai"
            dialog = RecordingSettingsDialog(window.selected_profile, parent=window)
            dialog.resize(850, 450)
            dialog.show()
            capture("recording.png", dialog)
            dialog.close()
            manifest = {
                "source": args.capture.name,
                "range_seconds": [370, 530],
                "frames_in_range": count,
                "cursor_seconds": [400, 480],
                "signals": [
                    {"source": ref.display_name, "label": aliases[key],
                     "dbc": SOURCES[ref.signal_name][0], "unit": ref.unit,
                     "samples": len(window._series.series(key))}
                    for key, ref in references.items()
                ],
            }
            print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
        finally:
            window.close()
            pump(app)


if __name__ == "__main__":
    main()
