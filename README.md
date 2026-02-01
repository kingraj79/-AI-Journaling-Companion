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


Setup Instructions
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
--
All user data is stored locally on your machine in:
data/goalbot.json

This includes goals, daily updates, and AI responses.
If the file or folder does not exist, the app will create it automatically.
No external database or cloud storage is used.

Privacy
--
Goalbot is private by design.

Ollama runs entirely on your local machine, and the Llama model processes all prompts locally.
No user data, prompts, or AI responses are sent to external servers or third parties.

All goal data stays on your device.

