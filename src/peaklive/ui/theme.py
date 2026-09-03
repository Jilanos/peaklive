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

#: Deterministic, colour-blind-considered palette for simultaneously shown
#: curves (item_053 AC1). Assigned by each signal's position in the sorted
#: shown-signal list, never by identity alone, so it stays stable across a
#: live refresh but never needs a persisted per-signal mapping. Every entry is
#: legible against PLOT_BACKGROUND and distinguishable under common colour-
#: vision deficiencies (kept far apart in hue and paired with varying
#: lightness rather than relying on hue alone).
TRACE_PALETTE: Final[list[str]] = [
    "#38bdf8",  # sky
    "#fb923c",  # orange
    "#4ade80",  # green
    "#f472b6",  # pink
    "#facc15",  # yellow
    "#c084fc",  # violet
    "#2dd4bf",  # teal
    "#f87171",  # red
]

#: Control-state contract shared by every interactive Qt control (item_027).
#: Each state pairs a foreground with a background so no control inherits an
#: ambient colour, and focus adds a thicker outline so the state never depends
#: on hue alone.
CONTROL_SURFACE: Final = "#101a26"
CONTROL_BORDER: Final = "#3a4c66"
CONTROL_HOVER: Final = "#1c2a3b"
POPUP_SURFACE: Final = "#16202d"
SELECTION_BACKGROUND: Final = ACCENT
SELECTION_TEXT: Final = "#ffffff"
DISABLED_BACKGROUND: Final = "#1a2230"
DISABLED_TEXT: Final = "#7c8ba1"
FOCUS_RING: Final = "#7cb0ff"
FOCUS_RING_WIDTH: Final = "2px"
INDICATOR_SIZE: Final = "12px"
INDICATOR_BACKGROUND: Final = "#0a121c"
INDICATOR_BORDER: Final = "#7f92ad"
INDICATOR_CHECKED: Final = "#38bdf8"
INDICATOR_CHECKED_BORDER: Final = "#bae6fd"

#: Eye/star row-action pictograms (item_054 AC3): filled/accent when the
#: signal is shown or favorited, muted-but-still-visible otherwise so an
#: unselected action never reads as absent.
ROW_ACTION_ACTIVE: Final = "#38bdf8"
ROW_ACTION_MUTED: Final = "#7f92ad"

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
    "stopping": STATE_BUSY,
    "degraded": STATE_WARNING,
    "stopped": STATE_IDLE,
}

BASE_STYLE: Final = f"""
QMainWindow {{ background: {BACKGROUND}; color: {TEXT}; }}
QDialog {{ background: {BACKGROUND}; color: {TEXT}; }}
QLabel {{ color: {TEXT_BODY}; }}
QLabel#panelHeading {{ color: {HEADING}; font-weight: 800; letter-spacing: 0.08em; }}
QLabel#statusPill {{ background: {SURFACE_DEEP}; border: 1px solid #334155; border-radius: 999px;
                    color: {ACCENT_SOFT}; padding: 5px 10px; }}
QLabel#panelRail {{ color: {HEADING}; font-weight: 800; letter-spacing: 0.12em; }}
QLabel#controlGroupLabel {{ color: {TEXT_MUTED}; font-weight: 700; letter-spacing: 0.08em; }}
QLabel#stateNote {{ color: {TEXT_MUTED}; font-style: italic; }}
/* Readable, never prominent: it must not compete with CAN analysis. */
QLabel#buildIdentifier {{ color: {TEXT_MUTED}; font-size: 11px;
    letter-spacing: 0.04em; padding: 0 8px 0 4px; }}
QLabel#errorNote {{ background: #2a1214; border: 1px solid {STATE_ERROR}; border-radius: 5px;
                    color: #fecaca; padding: 5px 8px; }}
QLabel#warningNote {{ background: #2a2210; border: 1px solid {STATE_WARNING}; border-radius: 5px;
                      color: #fde68a; padding: 5px 8px; }}
QFrame#instrument {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#busState {{ background: {SURFACE_DEEP}; border: 1px solid #334155; border-radius: 999px; }}
QPushButton, QToolButton {{ background: {ACCENT}; border: none; border-radius: 5px; color: white;
                           font-weight: 700; min-height: 28px; padding: 0 10px; }}
QToolButton#collapseButton {{ background: #202b3a; color: {TEXT_BODY}; min-width: 24px; }}
QToolButton#collapseButton[collapsed="true"] {{ min-width: 18px; min-height: 18px; padding: 0; }}
QToolButton[navButton="true"] {{ background: #202b3a; color: {TEXT_BODY};
                                min-width: 26px; padding: 0 4px; }}
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

#: Explicit foreground/background pairs for every interactive control state
#: (item_027). Qt only styles what a rule names: a popup view, a menu item, or
#: a checkbox indicator left unnamed falls back to the platform palette and
#: renders dark-on-dark inside the instrument theme.
CONTROL_STYLE: Final = f"""
QComboBox {{ background: {CONTROL_SURFACE}; color: {TEXT}; }}
QComboBox:hover {{ background: {CONTROL_HOVER}; border-color: {CONTROL_BORDER}; }}
QComboBox:disabled {{ background: {DISABLED_BACKGROUND}; color: {DISABLED_TEXT}; }}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox::down-arrow {{
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_BODY}; height: 0; width: 0;
}}
QComboBox::down-arrow:disabled {{ border-top-color: {DISABLED_TEXT}; }}
QComboBox::down-arrow:hover {{ border-top-color: {FOCUS_RING}; }}
QComboBox QAbstractItemView {{
    background: {POPUP_SURFACE}; border: 1px solid {CONTROL_BORDER}; color: {TEXT};
    outline: none; selection-background-color: {SELECTION_BACKGROUND};
    selection-color: {SELECTION_TEXT};
}}
QComboBox QAbstractItemView::item {{ background: {POPUP_SURFACE}; color: {TEXT};
                                     min-height: 24px; padding: 2px 8px; }}
QComboBox QAbstractItemView::item:hover {{ background: {CONTROL_HOVER}; color: {TEXT}; }}
QComboBox QAbstractItemView::item:selected {{ background: {SELECTION_BACKGROUND};
                                              color: {SELECTION_TEXT}; }}
QComboBox QAbstractItemView::item:disabled {{ background: {POPUP_SURFACE};
                                              color: {DISABLED_TEXT}; }}
QAbstractItemView {{ background: {SURFACE_DEEP}; color: {TEXT}; outline: none;
                     selection-background-color: {SELECTION_BACKGROUND};
                     selection-color: {SELECTION_TEXT}; }}
QAbstractItemView::item {{ color: {TEXT}; }}
QAbstractItemView::item:hover {{ background: {CONTROL_HOVER}; color: {TEXT}; }}
QAbstractItemView::item:selected {{ background: {SELECTION_BACKGROUND};
                                    color: {SELECTION_TEXT}; }}
QAbstractItemView::item:selected:!active {{ background: {SELECTION_BACKGROUND};
                                            color: {SELECTION_TEXT}; }}
QAbstractItemView::item:disabled {{ color: {DISABLED_TEXT}; }}
QTreeView::branch {{ background: transparent; }}
QMenu::item {{ background: transparent; color: {TEXT_BODY}; padding: 4px 20px; }}
QMenu::item:selected {{ background: {SELECTION_BACKGROUND}; color: {SELECTION_TEXT}; }}
QMenu::item:disabled {{ color: {DISABLED_TEXT}; }}
QMenu::separator {{ background: {BORDER}; height: 1px; margin: 4px 8px; }}
QMenuBar::item:disabled {{ color: {DISABLED_TEXT}; }}
QCheckBox::indicator, QTreeView::indicator, QListView::indicator, QTableView::indicator {{
    background: {INDICATOR_BACKGROUND}; border: 2px solid {INDICATOR_BORDER};
    border-radius: 3px; height: {INDICATOR_SIZE}; width: {INDICATOR_SIZE};
}}
QCheckBox::indicator:unchecked, QTreeView::indicator:unchecked,
QListView::indicator:unchecked, QTableView::indicator:unchecked {{
    background: {INDICATOR_BACKGROUND}; border: 2px solid {INDICATOR_BORDER};
}}
QCheckBox::indicator:checked, QTreeView::indicator:checked,
QListView::indicator:checked, QTableView::indicator:checked {{
    background: {INDICATOR_CHECKED}; border: 2px solid {INDICATOR_CHECKED_BORDER};
}}
QCheckBox::indicator:hover, QTreeView::indicator:hover,
QListView::indicator:hover, QTableView::indicator:hover {{
    border-color: {FOCUS_RING};
}}
QCheckBox::indicator:focus, QTreeView::indicator:focus {{
    border: {FOCUS_RING_WIDTH} solid {FOCUS_RING};
}}
QCheckBox::indicator:disabled, QTreeView::indicator:disabled,
QListView::indicator:disabled, QTableView::indicator:disabled {{
    background: {DISABLED_BACKGROUND}; border: 1px dashed {DISABLED_TEXT};
}}
QCheckBox:disabled {{ color: {DISABLED_TEXT}; }}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QPlainTextEdit:focus,
QTreeWidget:focus, QListWidget:focus, QTableWidget:focus, QAbstractItemView:focus {{
    border: {FOCUS_RING_WIDTH} solid {FOCUS_RING};
}}
QPushButton:focus, QToolButton:focus {{ border: {FOCUS_RING_WIDTH} solid {FOCUS_RING}; }}
QLineEdit:disabled, QSpinBox:disabled, QPlainTextEdit:disabled {{
    background: {DISABLED_BACKGROUND}; color: {DISABLED_TEXT};
}}
QToolTip {{ background: {POPUP_SURFACE}; border: 1px solid {CONTROL_BORDER}; color: {TEXT};
            padding: 3px 6px; }}
QScrollBar:vertical {{ background: {SURFACE_DEEP}; width: 10px; margin: 0; }}
QScrollBar:horizontal {{ background: {SURFACE_DEEP}; height: 10px; margin: 0; }}
QScrollBar::handle {{ background: {CONTROL_BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::handle:hover {{ background: {ACCENT_SOFT}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QSplitter::handle {{ background: {BORDER}; }}
QSplitter::handle:hover {{ background: {ACCENT}; }}
"""

#: The one stylesheet the workspace installs: base chrome plus the explicit
#: control-state contract.
APP_STYLE: Final = BASE_STYLE + CONTROL_STYLE
