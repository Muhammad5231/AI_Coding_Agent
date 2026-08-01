"""
Main Dashboard Window.
Combines left sidebar navigation, top status toolbar, central tabs, and global progress bar.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QPushButton, QTabWidget, QStatusBar, QProgressBar, QLabel, QToolBar
)
from PySide6.QtCore import Qt, QSize
from app.database.db_manager import DatabaseManager
from app.ui.tabs.prompt_tab import PromptTab
from app.ui.tabs.generator_tab import GeneratorTab
from app.ui.tabs.projects_tab import ProjectsTab
from app.ui.tabs.settings_tab import SettingsTab
from app.ui.tabs.logs_tab import LogsTab


class MainWindow(QMainWindow):
    """Primary application main window."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("AI Coding Agent Studio v1.0")
        self.resize(1200, 800)

        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Sidebar Navigation
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        app_title = QLabel("AI Coding Agent\n<b>STUDIO</b>")
        app_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(20)

        # Navigation Buttons
        self.btn_tab_generator = QPushButton("🚀 Project Generator")
        self.btn_tab_generator.setObjectName("nav_button")
        self.btn_tab_generator.setCheckable(True)

        self.btn_tab_prompts = QPushButton("📝 Prompt Workspace")
        self.btn_tab_prompts.setObjectName("nav_button")
        self.btn_tab_prompts.setCheckable(True)

        self.btn_tab_projects = QPushButton("📁 Project Manager")
        self.btn_tab_projects.setObjectName("nav_button")
        self.btn_tab_projects.setCheckable(True)

        self.btn_tab_settings = QPushButton("⚙️ Local LLM Settings")
        self.btn_tab_settings.setObjectName("nav_button")
        self.btn_tab_settings.setCheckable(True)

        self.btn_tab_logs = QPushButton("📊 Audit Logs")
        self.btn_tab_logs.setObjectName("nav_button")
        self.btn_tab_logs.setCheckable(True)

        self.nav_buttons = [
            self.btn_tab_generator,
            self.btn_tab_prompts,
            self.btn_tab_projects,
            self.btn_tab_settings,
            self.btn_tab_logs
        ]

        for btn in self.nav_buttons:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Right Main Display Area
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(10, 10, 10, 10)

        # Central Tab Stack
        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()  # Driven by sidebar navigation

        self.tab_generator = GeneratorTab(self.db)
        self.tab_prompts = PromptTab(self.db)
        self.tab_projects = ProjectsTab(self.db)
        self.tab_settings = SettingsTab(self.db)
        self.tab_logs = LogsTab(self.db)

        self.tabs.addTab(self.tab_generator, "Generator")
        self.tabs.addTab(self.tab_prompts, "Prompts")
        self.tabs.addTab(self.tab_projects, "Projects")
        self.tabs.addTab(self.tab_settings, "Settings")
        self.tabs.addTab(self.tab_logs, "Logs")

        right_layout.addWidget(self.tabs)
        main_layout.addWidget(right_container)

        # Signal Wiring
        self.btn_tab_generator.clicked.connect(lambda: self._switch_tab(0))
        self.btn_tab_prompts.clicked.connect(lambda: self._switch_tab(1))
        self.btn_tab_projects.clicked.connect(lambda: self._switch_tab(2))
        self.btn_tab_settings.clicked.connect(lambda: self._switch_tab(3))
        self.btn_tab_logs.clicked.connect(lambda: self._switch_tab(4))

        # Generator Signals
        self.tab_generator.generation_started_signal.connect(self._on_gen_started)
        self.tab_generator.generation_finished_signal.connect(self._on_gen_finished)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.showMessage("Ready - Standby for prompt request")

        # Default Active Tab
        self._switch_tab(0)

    def _switch_tab(self, index: int) -> None:
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # Auto refresh tabs when opened
        if index == 2:
            self.tab_projects.refresh_projects()
        elif index == 4:
            self.tab_logs.refresh_logs()

    def _on_gen_started(self) -> None:
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate state
        self.status_bar.showMessage("Streaming LLM output...")

    def _on_gen_finished(self) -> None:
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Generation complete.")