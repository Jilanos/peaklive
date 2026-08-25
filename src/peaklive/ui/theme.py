"""Instrument-panel design tokens shared by every workspace panel.

Keeping the palette here rather than inline in the main window means a panel can
be styled, tested, and reviewed on its own, and the visual system stays one
source of truth instead of a string that grows with each UX wave.
"""

from __future__ import annotations

from typing import Final

BACKGROUND: Final = "#0b1018"
SURFACE: Final = "#141c27"
SURFACE_DEEP: Final = "#0f1722"
PLOT_BACKGROUND: Final = "#080d13"
BORDER: Final = "#263448"
BORDER_SUBTLE: Final = "#293748"

TEXT: Final = "#e6edf7"
TEXT_MUTED: Final = "#94a3b8"
TEXT_BODY: Final = "#cbd5e1"
HEADING: Final = "#f59e0b"
ACCENT: Final = "#1f6feb"
ACCENT_SOFT: Final = "#93c5fd"

CURVE: Final = "#38bdf8"
CURSOR_A: Final = "#f59e0b"
CURSOR_B: Final = "#a78bfa"

STATE_IDLE: Final = "#64748b"
STATE_BUSY: Final = "#38bdf8"
STATE_RUNNING: Final = "#22c55e"
STATE_WARNING: Final = "#f59e0b"
STATE_ERROR: Final = "#ef4444"

#: Bus-state marker colours keyed by the state names used by the acquisition bar.
BUS_STATE_COLORS: Final[dict[str, str]] = {
    "idle": STATE_IDLE,
    "connecting": STATE_BUSY,
    "running": STATE_RUNNING,
    "reconnecting": STATE_WARNING,
    "bus_error": STATE_ERROR,
    "bus_off": STATE_ERROR,
    "stopped": STATE_IDLE,
}

APP_STYLE: Final = f"""
QMainWindow {{ background: {BACKGROUND}; color: {TEXT}; }}
QDialog {{ background: {BACKGROUND}; color: {TEXT}; }}
QLabel {{ color: {TEXT_BODY}; }}
QLabel#panelHeading {{ color: {HEADING}; font-weight: 800; letter-spacing: 0.08em; }}
QLabel#statusPill {{ background: {SURFACE_DEEP}; border: 1px solid #334155; border-radius: 999px;
                    color: {ACCENT_SOFT}; padding: 5px 10px; }}
QLabel#stateNote {{ color: {TEXT_MUTED}; font-style: italic; }}
QLabel#errorNote {{ background: #2a1214; border: 1px solid {STATE_ERROR}; border-radius: 5px;
                    color: #fecaca; padding: 5px 8px; }}
QLabel#warningNote {{ background: #2a2210; border: 1px solid {STATE_WARNING}; border-radius: 5px;
                      color: #fde68a; padding: 5px 8px; }}
QFrame#instrument {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#busState {{ background: {SURFACE_DEEP}; border: 1px solid #334155; border-radius: 999px; }}
QPushButton, QToolButton {{ background: {ACCENT}; border: none; border-radius: 5px; color: white;
                           font-weight: 700; min-height: 28px; padding: 0 10px; }}
QToolButton#collapseButton {{ background: #202b3a; color: {TEXT_BODY}; min-width: 24px; }}
QToolButton[navButton="true"] {{ background: #202b3a; color: {TEXT_BODY}; min-width: 30px; }}
QPushButton#chipButton {{ background: #1d2a3b; border: 1px solid {BORDER}; color: {ACCENT_SOFT};
                          font-weight: 600; min-height: 22px; padding: 0 8px; }}
QPushButton:disabled, QToolButton:disabled {{ background: #334155; color: {TEXT_MUTED}; }}
QComboBox, QListWidget, QTableWidget, QTreeWidget, QLineEdit, QSpinBox, QPlainTextEdit {{
    background: {SURFACE_DEEP}; border: 1px solid {BORDER_SUBTLE}; border-radius: 5px;
    color: {TEXT}; selection-background-color: {ACCENT}; min-height: 26px;
}}
QCheckBox {{ color: {TEXT_BODY}; spacing: 8px; }}
QHeaderView::section {{ background: #17202b; color: {TEXT_MUTED}; border: none; padding: 5px; }}
QProgressBar {{ background: {SURFACE_DEEP}; border: 1px solid {BORDER_SUBTLE}; border-radius: 5px;
                color: {TEXT}; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QStatusBar {{ background: {PLOT_BACKGROUND}; color: {TEXT_MUTED}; }}
QMenuBar {{ background: {PLOT_BACKGROUND}; color: {TEXT_BODY}; }}
QMenuBar::item:selected {{ background: {ACCENT}; color: white; }}
QMenu {{ background: {SURFACE}; border: 1px solid {BORDER}; color: {TEXT_BODY}; }}
QMenu::item:selected {{ background: {ACCENT}; color: white; }}
"""
