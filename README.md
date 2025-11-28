📄 AI Resume Screening Agent

An AI-powered agent that automatically analyzes resumes, extracts candidate details, compares them with a job description, ranks candidates, and exports results.

This project was built for the 48-hour AI Agent Development Challenge.

🚀 Features
🔍 Resume Analysis

Extracts text from PDF/DOCX

Extracts emails, phones, skills, experience

Splits text using LangChain

Embeds text and JD using mock embeddings

🤖 AI Scoring

Uses FAISS vector similarity

Profile Match % (0–100)

Keyword Matching

Final Composite Score

📝 Explanations (AI / Local)

Local AI-generated explanations

OpenAI GPT support (optional, if API key available)

📊 Ranking Dashboard (Streamlit UI)

Displays ranked candidates

Show resume preview

Show extracted details

Download results as CSV

🔗 Integrations (Mock / Optional)

Google Sheets API (demo mode)

Notion DB API (demo mode)

🧰 Tech Stack
AI Models

OpenAI GPT (optional, supports but not required)

Frameworks

LangChain (text splitter + fake LLM chain)

Vector DB

FAISS (local similarity search)

Databases / APIs

Google Sheets API (placeholder)

Notion DB API (placeholder)

Frontend / UI

Streamlit

🛠 Installation
1️⃣ Clone Repository
git clone https://github.com/tejaswinihr632/resume-screening-agent.git
cd resume-screening-agent

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Requirements
pip install -r requirements.txt

▶️ Running the App
streamlit run app/streamlit_app.py

📦 Project Structure
resume-screening-agent/
│── app/
│   └── streamlit_app.py
│── src/
│   ├── screening.py
│   ├── parse_resumes.py
│   ├── langchain_utils.py
│   ├── google_sheets_utils.py
│   ├── notion_db_utils.py
│── outputs/
│── sample_docs/
│── README.md
│── requirements.txt

📘 Architecture Diagram (High-Level)

User → Streamlit UI

Resume → Parser → FAISS Similarity → Final Score

LangChain Text Splitter → Chunking

AI / Local Explanation Engine

Export: Google Sheets / Notion

🧪 Demo Mode

If free API tiers are expired, enable demo mode:

✔ No OpenAI calls
✔ No external APIs
✔ Local exports only

📈 Future Improvements

Real Google Sheets + Notion integration

Real GPT / Gemini / Claude LLM explanations

PDF text cleaning improvements

Multi-role interview agent extension

❤️ Author

Tejaswini H R
AI Developer — Resume Screening Agent Project