# -AI-Powered-Journaling-Companion
A local-first AI goal journaling app built with Streamlit and Ollama. Track goals, log daily progress, and get private AI feedback — all data stays on your machine.

# 🎯 Goalbot — Local AI Goal Journal (Llama 3.1)

Goalbot is a **local-first goal journaling app** built with Streamlit and Ollama.  
You can track goals, log daily updates, view history, and ask an AI companion questions — all **stored locally in JSON** and powered by **Llama 3.1** running on your machine.

---

## 🚀 Features
- Add / delete goals (active or inactive)
- Daily goal updates
- AI feedback after each update
- Ask Goalbot questions using your history
- Generate progress summaries
- Full timeline (user updates + AI responses)
- 100% local (no cloud, no database)

---

## 🧠 Tech Stack
- **UI:** Streamlit
- **LLM:** Ollama (`llama3.1`)
- **Backend:** Python
- **Storage:** Local JSON file

---

## 📁 Project Structure

main.py main Streamlit app

requirements.txt Python dependencies

data/goalbot.json local data file (auto-created if missing)


##Setup Instructions
---

Clone the repository
git clone <your-repo-url>
cd goalbot

Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

Install dependencies
pip install -r requirements.txt

Install Ollama
Download from:
https://ollama.com/download

Pull the model:
ollama pull llama3.1

Start Ollama:
ollama serve

(Optional test)
ollama run llama3.1

Run the app
streamlit run main.py

Open in browser:
http://localhost:8501

Data Storage
All user data is stored locally on your machine in:
data/goalbot.json

This includes goals, daily updates, and AI responses.
If the file or folder does not exist, the app will create it automatically.
No external database or cloud storage is used.

Privacy
Goalbot is private by design.

Ollama runs entirely on your local machine, and the Llama model processes all prompts locally.
No user data, prompts, or AI responses are sent to external servers or third parties.

All goal data stays on your device.

## Project Structure
--
flowchart TB
    %% =====================
    %% User Interface
    %% =====================
    User((User))
    UI[Streamlit UI<br/>hello.py]

    %% =====================
    %% Pages
    %% =====================
    GoalsPage[Goals Page<br/>Daily updates<br/>Add / Remove goals]
    HistoryPage[History Page<br/>Timeline of updates<br/>+ AI responses]
    AskPage[Ask Goalbot Page<br/>Questions + Progress Summary]

    %% =====================
    %% State & Storage
    %% =====================
    Session[Streamlit Session State]
    Storage[storage.py<br/>JSON persistence<br/>data.json]

    %% =====================
    %% Data Objects
    %% =====================
    Goals[(Goals)]
    Updates[(User Updates)]
    AIEvents[(AI Events<br/>daily_feedback<br/>ask_answer<br/>progress_summary)]

    %% =====================
    %% AI Layer
    %% =====================
    Ollama[Ollama Local LLM<br/>llama3.1]
    PromptBuilder[Prompt Builder<br/>Context + Instructions]

    %% =====================
    %% User Flow
    %% =====================
    User --> UI
    UI --> GoalsPage
    UI --> HistoryPage
    UI --> AskPage

    %% =====================
    %% Goals Page Flow
    %% =====================
    GoalsPage -->|Add / Update| Session
    GoalsPage -->|Save Update| Storage
    GoalsPage --> PromptBuilder
    PromptBuilder --> Ollama
    Ollama -->|AI Feedback| Storage
    Ollama -->|AI Feedback| Session

    %% =====================
    %% Ask Goalbot Flow
    %% =====================
    AskPage -->|Question| PromptBuilder
    Storage -->|Load Updates| PromptBuilder
    PromptBuilder --> Ollama
    Ollama -->|Answer| Storage
    Ollama -->|Answer| UI

    %% =====================
    %% History Flow
    %% =====================
    Storage --> HistoryPage
    HistoryPage --> UI

    %% =====================
    %% Storage Breakdown
    %% =====================
    Storage --> Goals
    Storage --> Updates
    Storage --> AIEvents
