"""
Project Exporter Engine.
Parses multi-file markdown/text structure outputted by the LLM and creates real files on the disk.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from app.config.settings import Config

logger = logging.getLogger("ProjectExporter")


class ProjectExporter:
    """Parses raw LLM text generation and saves project structure to disk."""

    @staticmethod
    def parse_llm_output(raw_text: str) -> Dict[str, str]:
        """
        Parses multi-file patterns from LLM output.
        Supported delimiter formats:
        1) ### File: path/to/file.ext
        2) File: path/to/file.ext
        3) ```language path/to/file.ext
        """
        files: Dict[str, str] = {}
        
        # Regex matching headers: ### File: filepath OR File: filepath followed by optional code blocks
        pattern = r'(?:###\s*File:\s*|File:\s*)([^\n\r]+)[\r\n]+```(?:\w+)?[\r\n]+([\s\S]*?)```'
        matches = re.findall(pattern, raw_text, re.MULTILINE)

        if matches:
            for filepath_str, code_content in matches:
                clean_path = filepath_str.strip().strip("`").strip("'").strip('"')
                files[clean_path] = code_content.rstrip() + "\n"
        else:
            # Fallback regex search for filenames in code block top comment lines
            fallback_pattern = r'```(?:\w+)?\s*[\r\n]+(?://|#)\s*([a-zA-Z0-9_\-/\.\\]+\.[a-zA-Z0-9]+)[\r\n]+([\s\S]*?)```'
            fallback_matches = re.findall(fallback_pattern, raw_text, re.MULTILINE)
            if fallback_matches:
                for filepath_str, code_content in fallback_matches:
                    files[filepath_str.strip()] = code_content.rstrip() + "\n"

        # Direct fallback if format parsing yields no distinct files
        if not files and raw_text.strip():
            files["main_output.txt"] = raw_text

        return files

    @classmethod
    def export_project(cls, project_name: str, raw_llm_output: str) -> Tuple[bool, Path, List[str]]:
        """
        Exports extracted project files to `storage/projects/<project_name>`.
        Returns success status, absolute target path, and list of written relative file paths.
        """
        try:
            # Normalize directory name
            safe_name = re.sub(r'[^\w\-_]', '_', project_name)
            target_dir = Config.PROJECTS_DIR / safe_name
            target_dir.mkdir(parents=True, exist_ok=True)

            parsed_files = cls.parse_llm_output(raw_llm_output)
            written_files: List[str] = []

            for rel_path_str, content in parsed_files.items():
                file_path = target_dir / rel_path_str
                # Ensure child subdirectories exist
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                written_files.append(rel_path_str)

            logger.info(f"Successfully exported project '{safe_name}' to {target_dir}")
            return True, target_dir, written_files
        except Exception as e:
            logger.error(f"Failed to export project files: {e}")
            return False, Config.PROJECTS_DIR, []