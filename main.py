"""
AI Coding Agent Studio - Main Entry Point.
Initializes logging, configuration, SQLite database, PySide6 GUI, and execution loop.
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from app.config.settings import Config
from app.database.db_manager import DatabaseManager
from app.ui.styles import DARK_THEME_QSS
from app.ui.main_window import MainWindow


def configure_logging(db_manager: DatabaseManager) -> None:
    """Sets up standard Python file and console logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File Handler
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)


def main() -> None:
    """Main execution function."""
    # Initialize storage directories
    Config.initialize_directories()

    # Initialize Database
    db_manager = DatabaseManager()

    # Configure Logging
    configure_logging(db_manager)
    logging.info("Starting AI Coding Agent Studio v1.0")

    # Launch PySide6 Application
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()