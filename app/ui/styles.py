"""
UI Stylesheet Module.
Provides a modern, polished dark QSS theme for PySide6 desktop widgets.
"""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

/* Sidebar Navigation */
QFrame#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
}

QPushButton#nav_button {
    background-color: transparent;
    color: #a6adc8;
    border: none;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
}

QPushButton#nav_button:hover {
    background-color: #313244;
    color: #cdd6f4;
}

QPushButton#nav_button:checked {
    background-color: #89b4fa;
    color: #11111b;
}

/* Input Controls */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #585b70;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}

/* Buttons */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#primary_button {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
}

QPushButton#primary_button:hover {
    background-color: #b4befe;
}

QPushButton#danger_button {
    background-color: #f38ba8;
    color: #11111b;
    border: none;
}

QPushButton#danger_button:hover {
    background-color: #eba0ac;
}

/* Tables and Lists */
QTableWidget, QListWidget {
    background-color: #181825;
    border: 1px solid #313244;
    gridline-color: #313244;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #11111b;
    color: #cdd6f4;
    padding: 6px;
    border: 1px solid #313244;
    font-weight: bold;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 6px;
}

QTabBar::tab {
    background: #181825;
    color: #a6adc8;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #313244;
    color: #89b4fa;
    font-weight: bold;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    background-color: #181825;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}

/* Status Bar */
QStatusBar {
    background-color: #11111b;
    color: #a6adc8;
    border-top: 1px solid #313244;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #89b4fa;
}
"""