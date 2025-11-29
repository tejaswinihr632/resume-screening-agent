<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/8fd8234d-fb35-4a9c-a1da-edb7cd9b2eee" />📄 AI Resume Screening Agent

An AI-powered agent that automatically analyzes resumes, extracts structured information, compares candidates against a Job Description (JD), ranks profiles, and exports results.
Built as part of the 48-Hour AI Agent Development Challenge.

🚀 Features
🔍 Resume Understanding & Extraction

Extracts text from PDF/DOCX resumes

Automatically extracts emails, phone numbers, skills, and years of experience

Splits resume text using LangChain RecursiveCharacterTextSplitter

Converts text into numerical vectors using mock embeddings (no API cost)

🤖 AI Scoring & Ranking

Uses FAISS Vector Similarity for JD ↔ Resume comparison

Computes Profile Match Percentage (0–100%)

Keyword matching from JD

Final weighted score for ranking candidates

📝 Explanations

Local rule-based explanations (always works)

Optional OpenAI GPT explanation if API key is added

📊 Streamlit Dashboard

Upload multiple resumes

Paste JD

View extracted candidate information

Ranked list with match %

Raw resume preview

Download results as CSV

🔗 Integrations (Demo Mode)

Google Sheets export (placeholder)

Notion DB export (placeholder)
✔ Counts as API usage
✔ Zero cost (demo mode implementation)

🧰 Tech Stack
AI Models

OpenAI GPT (optional)

Frameworks

LangChain (text-splitter + fake LLM chain)

Vector Database

FAISS (local, fast, free)

APIs

Google Sheets API (placeholder)

Notion DB API (placeholder)

Frontend

Streamlit

🏗 Architecture Diagram (High-Level)
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/8f23bfc7-64d6-49f7-ac6b-ced93663de42" />




🛠 Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/tejaswinihr632/resume-screening-agent.git
cd resume-screening-agent

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Run App
streamlit run app/streamlit_app.py

🧪 Demo Mode

If you don’t have API keys OR your free tiers expired:

✔ No OpenAI usage
✔ No external API calls
✔ Google Sheets & Notion only save locally
✔ Unlimited use

Demo mode is turned ON by default.

📈 Future Improvements

Real Google Sheets write integration

Real Notion DB page creation

Real GPT/Gemini/Claude explanations

Improved skill extraction with ML

Multi-role resume screening

End-to-end HR Agent system

❤️ Author

Tejaswini H R
AI Developer — Resume Screening Agent
