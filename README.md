# Mini AI Operating System Core

A voice-enabled AI assistant that understands requests, generates action plans, and executes tasks upon approval.

## 🏗 Architecture
- **Backend**: FastAPI (Python)
- **AI Planner**: Ollama with Gemma
- **Execution Engine**: Custom pluggable tool system
- **Frontend**: React with local STT/TTS

## 🚀 Getting Started

### 1. Prerequisites
- **Ollama**: [Download and Install](https://ollama.com/)
- **Model**: Run `ollama run gemma` to pull the required model.
- **Python**: 3.9+
- **Node.js**: 18+

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source .venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend will run at `http://localhost:8000`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will run at `http://localhost:5173`.

## 🛠 Key Features
- **Voice Interface**: Click the microphone icon to speak commands.
- **Approval System**: The AI cannot execute high-risk commands (like shell scripts) without your clicking "Approve".
- **Structured Planning**: User requests are decomposed into JSON-based steps.
- **Extensible Tools**: Add new tools in `backend/app/tools/implementations.py`.

## 🛡 Security
- **Command Allowlist**: Only safe commands like `ls`, `git status`, etc., are allowed by default.
- **Sandbox Directory**: File creation is restricted to the `/sandbox` folder.
- **No Secret Exposure**: The system prompt ensures it doesn't leak internal tool logic.

## 🧩 Initial Tools
- `create_file(name, content)`
- `run_command(cmd)`
- `deploy_app()` (stub)
- `post_instagram(caption)` (stub)
