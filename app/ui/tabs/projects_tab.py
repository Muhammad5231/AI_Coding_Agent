"""
Project Manager Tab Component.
Lists generated projects, offers search filtering, folder opening, renaming, and deletion.
"""

import os
import subprocess
import platform
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, 
    QHeaderView, QInputDialog
)
from app.database.db_manager import DatabaseManager


class ProjectsTab(QWidget):
    """UI view for managing saved project records."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__()
        self.db = db_manager
        self._init_ui()
        self.refresh_projects()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header Search Bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Projects:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type project name or description...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_projects)
        search_layout.addWidget(btn_refresh)

        layout.addLayout(search_layout)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Project Name", "Description", "Path", "Created At"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Bottom Action Bar
        action_layout = QHBoxLayout()

        btn_open_folder = QPushButton("Open Folder")
        btn_open_folder.setObjectName("primary_button")
        btn_open_folder.clicked.connect(self._open_project_folder)

        btn_rename = QPushButton("Rename Project")
        btn_rename.clicked.connect(self._rename_project)

        btn_delete = QPushButton("Delete Record")
        btn_delete.setObjectName("danger_button")
        btn_delete.clicked.connect(self._delete_project)

        action_layout.addWidget(btn_open_folder)
        action_layout.addWidget(btn_rename)
        action_layout.addWidget(btn_delete)
        action_layout.addStretch()

        layout.addLayout(action_layout)

    def refresh_projects(self) -> None:
        """Fetch and populate project rows in the table."""
        query = self.search_input.text().strip()
        projects = self.db.get_all_projects(query)

        self.table.setRowCount(0)
        for row_idx, proj in enumerate(projects):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(proj["id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(proj["name"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(proj["description"])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(proj["root_path"])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(proj["created_at"])))

    def _on_search_changed(self) -> None:
        self.refresh_projects()

    def _get_selected_project_row(self) -> tuple[int, int, str, str]:
        """Returns tuple of (selected_row_index, project_id, project_name, path_str)."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return -1, -1, "", ""
        
        row = selected_items[0].row()
        proj_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        path_str = self.table.item(row, 3).text()
        return row, proj_id, name, path_str

    def _open_project_folder(self) -> None:
        _, _, _, path_str = self._get_selected_project_row()
        if not path_str:
            QMessageBox.warning(self, "Selection Required", "Please select a project row.")
            return

        path = Path(path_str)
        if not path.exists():
            QMessageBox.warning(self, "Path Not Found", f"Directory does not exist:\n{path_str}")
            return

        # OS Agnostic Folder Opening
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open directory: {e}")

    def _rename_project(self) -> None:
        _, proj_id, old_name, _ = self._get_selected_project_row()
        if proj_id == -1:
            QMessageBox.warning(self, "Selection Required", "Please select a project to rename.")
            return

        new_name, ok = QInputDialog.getText(self, "Rename Project", "New project name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if self.db.rename_project(proj_id, new_name.strip()):
                self.refresh_projects()
                QMessageBox.information(self, "Success", "Project record renamed successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to rename project record.")

    def _delete_project(self) -> None:
        _, proj_id, proj_name, _ = self._get_selected_project_row()
        if proj_id == -1:
            QMessageBox.warning(self, "Selection Required", "Please select a project row to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove project entry '{proj_name}' from the database?\n(Note: Files on disk will remain intact)",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_project(proj_id)
            self.refresh_projects()