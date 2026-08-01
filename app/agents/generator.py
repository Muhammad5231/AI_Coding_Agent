"""
Background Worker Threads for Generation and LLM tasks.
Prevents GUI blocking during stream consumption and API calls.
"""

from PySide6.QtCore import QThread, Signal
from typing import Dict, Any
from app.llm.llm_client import LLMClient
from app.database.db_manager import DatabaseManager


class LLMTestWorker(QThread):
    """Background worker for testing API connectivity."""
    finished_signal = Signal(bool, str)

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self.config = config

    def run(self) -> None:
        client = LLMClient(self.config)
        success, message = client.test_connection()
        self.finished_signal.emit(success, message)


class GenerationWorker(QThread):
    """Background thread to stream LLM outputs continuously to the UI."""
    chunk_received = Signal(str)
    generation_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, prompt: str, settings: Dict[str, Any], db_manager: DatabaseManager) -> None:
        super().__init__()
        self.prompt = prompt
        self.settings = settings
        self.db = db_manager
        self.is_cancelled = False

    def cancel() -> None:
        """Flag cancellation request."""
        self.is_cancelled = True

    def run(self) -> None:
        full_response = []
        try:
            client = LLMClient(self.settings)
            system_prompt = self.settings.get("system_prompt", "")
            
            self.db.add_log("INFO", "GenerationWorker", f"Starting LLM generation for model: {client.model_name}")

            stream = client.stream_generation(self.prompt, system_prompt)
            for chunk in stream:
                if self.is_cancelled:
                    self.db.add_log("WARNING", "GenerationWorker", "Generation cancelled by user.")
                    break
                full_response.append(chunk)
                self.chunk_received.emit(chunk)

            complete_text = "".join(full_response)
            self.generation_finished.emit(complete_text)
            self.db.add_log("INFO", "GenerationWorker", "Generation completed successfully.")

        except Exception as e:
            error_msg = f"Generation worker error: {str(e)}"
            self.db.add_log("ERROR", "GenerationWorker", error_msg)
            self.error_occurred.emit(error_msg)