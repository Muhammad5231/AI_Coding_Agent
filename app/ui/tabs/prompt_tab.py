"""
Prompt Workspace Tab Component.
Allows drafting, loading, saving, and removing system or user prompts.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QListWidget, QPushButton, QInputDialog, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt
from app.database.db_manager import DatabaseManager


class PromptTab(QWidget):
    """Prompt workspace with side list for loading saved templates."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__()
        self.db = db_manager
        self._init_ui()
        self.load_history()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal)

        # Left Container - Saved Prompts List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel("<b>Saved Prompt History / Templates</b>"))
        self.prompt_list = QListWidget()
        self.prompt_list.itemClicked.connect(self._on_prompt_selected)
        left_layout.addWidget(self.prompt_list)

        btn_load = QPushButton("Load Selected")
        btn_load.clicked.connect(self._load_selected_prompt)
        btn_delete = QPushButton("Delete Selected")
        btn_delete.setObjectName("danger_button")
        btn_delete.clicked.connect(self._delete_selected_prompt)

        left_btn_box = QHBoxLayout()
        left_btn_box.addWidget(btn_load)
        left_btn_box.addWidget(btn_delete)
        left_layout.addLayout(left_btn_box)

        # Right Container - Prompt Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addWidget(QLabel("<b>Prompt Editor</b>"))
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlaceholderText("Write or modify your architectural or project prompt here...")
        right_layout.addWidget(self.prompt_editor)

        # Action Buttons
        action_layout = QHBoxLayout()
        btn_save = QPushButton("Save to History")
        btn_save.setObjectName("primary_button")
        btn_save.clicked.connect(self._save_prompt)

        btn_clear = QPushButton("Clear Editor")
        btn_clear.clicked.connect(self.prompt_editor.clear)

        action_layout.addWidget(btn_save)
        action_layout.addWidget(btn_clear)
        action_layout.addStretch()

        right_layout.addLayout(action_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)

    def load_history(self) -> None:
        """Reload prompts list from database."""
        self.prompt_list.clear()
        prompts = self.db.get_all_prompts()
        for p in prompts:
            title = f"{p['title']} ({p['created_at'][:10]})"
            self.prompt_list.addItem(f"{p['id']}: {title}")

    def _on_prompt_selected(self) -> None:
        pass

    def _load_selected_prompt(self) -> None:
        selected_items = self.prompt_list.selectedItems()
        if not selected_items:
            return
        
        prompt_id = int(selected_items[0].text().split(":")[0])
        prompts = self.db.get_all_prompts()
        for p in prompts:
            if p["id"] == prompt_id:
                self.prompt_editor.setText(p["prompt"])
                break

    def _save_prompt(self) -> None:
        text = self.prompt_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty Prompt", "Cannot save an empty prompt.")
            return

        title, ok = QInputDialog.getText(self, "Save Prompt", "Enter a title/label for this prompt:")
        if ok and title:
            self.db.add_prompt(title.strip(), text)
            self.load_history()
            QMessageBox.information(self, "Saved", "Prompt successfully saved to history.")

    def _delete_selected_prompt(self) -> None:
        selected_items = self.prompt_list.selectedItems()
        if not selected_items:
            return

        prompt_id = int(selected_items[0].text().split(":")[0])
        if QMessageBox.question(self, "Confirm Delete", "Delete this prompt entry?") == QMessageBox.Yes:
            self.db.delete_prompt(prompt_id)
            self.load_history()

    def get_current_prompt(self) -> str:
        """Return text currently in editor."""
        return self.prompt_editor.toPlainText()