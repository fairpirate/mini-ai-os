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

## 💡 Example Usage

The AI OS can plan and execute various tasks using its available tools. Here are examples of what you can ask it to do:

### 1. File Creation & Execution
- **You:** *"Create a Python script that prints 'Hello AI OS' and run it."*
- **Plan:** 
  1. `create_file` (name: `hello.py`, content: `print("Hello AI OS")`)
  2. `run_command` (cmd: `python hello.py`)

### 2. System Inspection
- **You:** *"List the files in my directory and check my python version."*
- **Plan:**
  1. `list_directory` ()
  2. `run_command` (cmd: `python --version`)

### 3. File Reading
- **You:** *"Read the contents of hello.py."*
- **Plan:**
  1. `read_file` (name: `hello.py`)

### 4. Web Research (Mocked)
- **You:** *"Search the web for the latest news on AI."*
- **Plan:** 
  1. `search_web` (query: `latest news on AI`)

### 5. Social Media (Stubbed)
- **You:** *"Post a photo to Instagram with the caption 'Working on my AI OS'."*
- **Plan:**
  1. `post_instagram` (caption: `Working on my AI OS`)

### 6. Real-World Information (Mocked)
- **You:** *"What is the weather like in New York?"*
- **Plan:**
  1. `get_weather` (location: `New York`)

### How to run an example:
1. Open your browser to `http://localhost:5173`.
2. Click the microphone icon or type one of the requests above.
3. The AI Planner generates the action plan.
4. The system pauses for your approval (especially for high-risk actions like `run_command`).
5. Click **Approve** on the proposed plan.
6. The system executes the steps and displays the final output.

## 🛠 Key Features
- **Voice Interface**: Click the microphone icon to speak commands.
- **Approval System**: The AI cannot execute high-risk commands (like shell scripts) without your clicking "Approve".
- **Structured Planning**: User requests are decomposed into JSON-based steps.
- **Extensible Tools**: Add new tools in `backend/app/tools/implementations.py`.

## 🛡 Security
- **Command Allowlist**: Only safe commands like `ls`, `git status`, etc., are allowed by default.
- **Sandbox Directory**: File creation is restricted to the `/sandbox` folder.
- **No Secret Exposure**: The system prompt ensures it doesn't leak internal tool logic.

## 🧩 Available Capabilities (Tools)
The AI is equipped with the following tools (some are stubs/mocked for demonstration):
- `create_file(name, content)`: Creates a file in the sandbox directory.
- `read_file(name)`: Reads a file from the sandbox directory.
- `list_directory()`: Lists files in the sandbox directory.
- `run_command(cmd)`: Runs allowlisted shell commands (e.g., `ls`, `pwd`, `git status`, `python --version`).
- `search_web(query)`: Searches the web (Mocked).
- `get_weather(location)`: Gets current weather (Mocked).
- `deploy_app()`: Initiates a mock cloud deployment.
- `post_instagram(caption)`: Creates a mock Instagram post.
