"""
SQLite Database Manager.
Handles persistent storage for settings, prompt history, projects, and application logs.
"""

import sqlite3
import logging
from typing import Dict, List, Tuple, Any, Optional
from app.config.settings import Config

logger = logging.getLogger("DatabaseManager")


class DatabaseManager:
    """Manages SQLite connections and thread-safe database interactions."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = str(db_path) if db_path else str(Config.DB_FILE)
        self._initialize_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection with Row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_tables(self) -> None:
        """Create database tables if they do not exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Settings Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)

                # Prompt History Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        prompt TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Projects Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        root_path TEXT NOT NULL,
                        prompt TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Logs Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level TEXT NOT NULL,
                        source TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                self._seed_default_settings(cursor)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database tables: {e}")

    def _seed_default_settings(self, cursor: sqlite3.Cursor) -> None:
        """Seed default configuration key-value pairs if not set."""
        for key, value in Config.DEFAULT_SETTINGS.items():
            cursor.execute("SELECT key FROM settings WHERE key = ?", (key,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    # --- Settings Methods ---

    def get_settings(self) -> Dict[str, str]:
        """Retrieve all configuration settings as a key-value dictionary."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save configuration dictionary into the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for key, val in settings.items():
                    cursor.execute(
                        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, str(val))
                    )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving settings: {e}")
            return False

    # --- Prompt History Methods ---

    def add_prompt(self, title: str, prompt: str) -> int:
        """Save a new prompt to history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO prompt_history (title, prompt) VALUES (?, ?)", (title, prompt))
            conn.commit()
            return cursor.lastrowid

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """Fetch all prompts ordered by creation time descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompt_history ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_prompt(self, prompt_id: int) -> bool:
        """Delete a prompt entry from history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prompt_history WHERE id = ?", (prompt_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Project Methods ---

    def add_project(self, name: str, description: str, root_path: str, prompt: str) -> int:
        """Record a generated project into the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description, root_path, prompt) VALUES (?, ?, ?, ?)",
                (name, description, root_path, prompt)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_projects(self, search_query: str = "") -> List[Dict[str, Any]]:
        """Retrieve projects, optionally filtering by search term."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                query = "SELECT * FROM projects WHERE name LIKE ? OR description LIKE ? ORDER BY created_at DESC"
                pattern = f"%{search_query}%"
                cursor.execute(query, (pattern, pattern))
            else:
                cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def rename_project(self, project_id: int, new_name: str) -> bool:
        """Rename an existing project record."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE projects SET name = ? WHERE id = ?", (new_name, project_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error renaming project {project_id}: {e}")
            return False

    def delete_project(self, project_id: int) -> bool:
        """Delete a project entry from database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Log Storage Methods ---

    def add_log(self, level: str, source: str, message: str) -> None:
        """Record an application log event to SQLite."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO logs (level, source, message) VALUES (?, ?, ?)", (level, source, message))
                conn.commit()
        except sqlite3.Error:
            pass  # Avoid recursive failure during logging errors

    def get_recent_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch recent logs up to the specified limit."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def clear_logs(self) -> None:
        """Truncate application logs database table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs")
            conn.commit()