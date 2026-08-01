"""
Logs and Console Viewer Tab Component.
Displays execution logs from SQLite database with search and clear functionality.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView
)
from app.database.db_manager import DatabaseManager


class LogsTab(QWidget):
    """UI view for reviewing application log traces."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__()
        self.db = db_manager
        self._init_ui()
        self.refresh_logs()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("<b>Application Logs Audit Trail</b>"))
        ctrl_layout.addStretch()

        btn_refresh = QPushButton("Refresh Logs")
        btn_refresh.clicked.connect(self.refresh_logs)

        btn_clear = QPushButton("Clear Logs")
        btn_clear.setObjectName("danger_button")
        btn_clear.clicked.connect(self._clear_logs)

        ctrl_layout.addWidget(btn_refresh)
        ctrl_layout.addWidget(btn_clear)

        layout.addLayout(ctrl_layout)

        # Logs Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Level", "Source", "Message", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh_logs(self) -> None:
        """Fetch latest database logs into the table view."""
        logs = self.db.get_recent_logs(limit=300)
        self.table.setRowCount(0)

        for row_idx, log in enumerate(logs):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(log["id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(log["level"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(log["source"])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(log["message"])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(log["timestamp"])))

    def _clear_logs(self) -> None:
        self.db.clear_logs()
        self.refresh_logs()