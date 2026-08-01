"""
Settings Configuration Tab Component.
Provides controls to modify and validate Ollama / OpenAI local API connection settings.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QGroupBox
)
from app.database.db_manager import DatabaseManager
from app.agents.generator import LLMTestWorker


class SettingsTab(QWidget):
    """UI widget to configure local LLM parameters."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__()
        self.db = db_manager
        self.test_worker = None
        self._init_ui()
        self.load_settings()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        group = QGroupBox("Local LLM Configuration")
        form_layout = QVBoxLayout(group)

        # Provider Type
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("API Type:"))
        self.combo_api_type = QComboBox()
        self.combo_api_type.addItems(["ollama", "openai"])
        row1.addWidget(self.combo_api_type)
        form_layout.addLayout(row1)

        # Endpoint URL
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Base URL:"))
        self.input_url = QLineEdit()
        row2.addWidget(self.input_url)
        form_layout.addLayout(row2)

        # Model Name
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Model Name:"))
        self.input_model = QLineEdit()
        row3.addWidget(self.input_model)
        form_layout.addLayout(row3)

        # Temperature
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Temperature:"))
        self.spin_temp = QDoubleSpinBox()
        self.spin_temp.setRange(0.0, 1.0)
        self.spin_temp.setSingleStep(0.05)
        row4.addWidget(self.spin_temp)
        form_layout.addLayout(row4)

        # Max Tokens
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Max Tokens:"))
        self.spin_tokens = QSpinBox()
        self.spin_tokens.setRange(256, 32768)
        self.spin_tokens.setSingleStep(256)
        row5.addWidget(self.spin_tokens)
        form_layout.addLayout(row5)

        # Timeout
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Timeout (seconds):"))
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(10, 600)
        row6.addWidget(self.spin_timeout)
        form_layout.addLayout(row6)

        layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_test = QPushButton("Test Connection")
        self.btn_test.clicked.connect(self._test_connection)

        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setObjectName("primary_button")
        self.btn_save.clicked.connect(self.save_settings)

        btn_layout.addWidget(self.btn_test)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addStretch()

    def load_settings(self) -> None:
        """Populate settings controls from SQLite storage."""
        s = self.db.get_settings()
        self.combo_api_type.setCurrentText(s.get("api_type", "ollama"))
        self.input_url.setText(s.get("api_url", "http://localhost:11434"))
        self.input_model.setText(s.get("model_name", "llama3:8b"))
        self.spin_temp.setValue(float(s.get("temperature", 0.2)))
        self.spin_tokens.setValue(int(s.get("max_tokens", 4096)))
        self.spin_timeout.setValue(int(s.get("timeout", 120)))

    def save_settings(self) -> None:
        """Save settings controls to SQLite storage."""
        data = {
            "api_type": self.combo_api_type.currentText(),
            "api_url": self.input_url.text().strip(),
            "model_name": self.input_model.text().strip(),
            "temperature": self.spin_temp.value(),
            "max_tokens": self.spin_tokens.value(),
            "timeout": self.spin_timeout.value()
        }
        if self.db.save_settings(data):
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings.")

    def _test_connection(self) -> None:
        config = {
            "api_type": self.combo_api_type.currentText(),
            "api_url": self.input_url.text().strip(),
            "model_name": self.input_model.text().strip()
        }
        self.btn_test.setEnabled(False)
        self.test_worker = LLMTestWorker(config)
        self.test_worker.finished_signal.connect(self._on_test_finished)
        self.test_worker.start()

    def _on_test_finished(self, success: bool, message: str) -> None:
        self.btn_test.setEnabled(True)
        if success:
            QMessageBox.information(self, "Connection Test", message)
        else:
            QMessageBox.warning(self, "Connection Test", message)