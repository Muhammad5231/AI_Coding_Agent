# AI Coding Agent Studio (Version 1)

AI Coding Agent Studio is a lightweight, local-first desktop application designed to generate complete code projects using local Large Language Models (via Ollama or OpenAI-compatible local APIs). 

It is optimized for CPU-bound systems (Intel i5, 8GB RAM, Windows 10/11) without external cloud dependencies or heavy frameworks.

## Features
- **Modern PySide6 GUI**: Dark-themed, responsive dashboard interface.
- **Local LLM Integration**: Connects seamlessly with Ollama (`/api/generate`) or OpenAI-compatible APIs (`/v1/chat/completions`).
- **Prompt Workspace**: Draft, save, load, and manage system prompts.
- **Project Generator**: Real-time non-blocking response streaming with automatic structured multi-file code parsing and project export.
- **Project Manager**: Browse, search, open, rename, and delete generated local projects.
- **Built-in Logging & SQLite DB**: Audit log trace, persistent settings, prompt history, and project index.

## Installation

1. Prerequisites: Python 3.12+ installed on Windows 10/11.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt