"""
Project Generator Tab Component.
Primary UI workspace for sending prompts to local LLM, reviewing streaming responses, and exporting projects.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QLineEdit, QPushButton, QMessageBox, QSplitter, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from app.database.db_manager import DatabaseManager
from app.agents.generator import GenerationWorker
from app.core.project_exporter import ProjectExporter


class GeneratorTab(QWidget):
    """UI tab for entering project specifications and processing generation stream."""
    generation_started_signal = Signal()
    generation_finished_signal = Signal()

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__()
        self.db = db_manager
        self.worker = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Vertical)

        # Upper Area - Prompt Entry & Controls
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        top_layout.addWidget(QLabel("<b>Project Specification Prompt</b>"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Describe the project you want to create (e.g. 'Create a Python CLI tool for image resizing')..."
        )
        top_layout.addWidget(self.prompt_input)

        # Config Row
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Project Name:"))
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("MyGeneratedProject")
        controls_layout.addWidget(self.project_name_input)

        self.btn_generate = QPushButton("Generate Project")
        self.btn_generate.setObjectName("primary_button")
        self.btn_generate.clicked.connect(self._start_generation)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_generation)

        controls_layout.addWidget(self.btn_generate)
        controls_layout.addWidget(self.btn_cancel)

        top_layout.addLayout(controls_layout)

        # Lower Area - Streaming LLM Output View
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        bottom_layout.addWidget(QLabel("<b>LLM Response Stream & Output</b>"))
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        bottom_layout.addWidget(self.output_console)

        # Export Controls
        export_layout = QHBoxLayout()
        self.btn_save_project = QPushButton("Save / Export Generated Files")
        self.btn_save_project.setObjectName("primary_button")
        self.btn_save_project.setEnabled(False)
        self.btn_save_project.clicked.connect(self._export_project)

        export_layout.addStretch()
        export_layout.addWidget(self.btn_save_project)

        bottom_layout.addLayout(export_layout)

        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

    def set_prompt_text(self, text: str) -> None:
        """Set prompt input programmatically from another tab."""
        self.prompt_input.setText(text)

    def _start_generation(self) -> None:
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Missing Prompt", "Please enter a prompt before generating.")
            return

        settings = self.db.get_settings()
        self.output_console.clear()
        self.btn_generate.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_save_project.setEnabled(False)

        self.generation_started_signal.emit()

        self.worker = GenerationWorker(prompt, settings, self.db)
        self.worker.chunk_received.connect(self._on_chunk_received)
        self.worker.generation_finished.connect(self._on_generation_finished)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _cancel_generation(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.btn_cancel.setEnabled(False)

    def _on_chunk_received(self, chunk: str) -> None:
        self.output_console.insertPlainText(chunk)
        self.output_console.ensureCursorVisible()

    def _on_generation_finished(self, full_text: str) -> None:
        self.btn_generate.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_save_project.setEnabled(True)
        self.generation_finished_signal.emit()
        QMessageBox.information(self, "Generation Complete", "LLM response stream complete. You can now save/export the project.")

    def _on_error(self, error_msg: str) -> None:
        self.btn_generate.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.generation_finished_signal.emit()
        QMessageBox.critical(self, "Generation Error", error_msg)

    def _export_project(self) -> None:
        project_name = self.project_name_input.text().strip() or "Untitled_Project"
        raw_output = self.output_console.toPlainText()
        prompt = self.prompt_input.toPlainText().strip()

        if not raw_output:
            QMessageBox.warning(self, "Empty Output", "No content available to export.")
            return

        success, root_path, files = ProjectExporter.export_project(project_name, raw_output)

        if success:
            # Register in SQLite DB
            desc = f"Generated project containing {len(files)} file(s)"
            self.db.add_project(project_name, desc, str(root_path), prompt)
            
            QMessageBox.information(
                self, 
                "Project Saved", 
                f"Project exported successfully!\n\nLocation: {root_path}\nFiles Created: {len(files)}"
            )
        else:
            QMessageBox.critical(self, "Export Failed", "An error occurred while saving the project files.")