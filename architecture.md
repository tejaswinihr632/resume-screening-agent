cat > architecture.md <<'MD'
flowchart TD
  U[User (Browser)] -->|Upload resumes / Paste JD| UI[Streamlit App]
  UI --> Parser[Resume Parser (pdfplumber/docx/tika + spaCy)]
  Parser --> Parsed[Parsed Resumes (text + metadata)]
  UI --> Screening[Screening Module]
  Parsed --> Screening
  Screening --> Embeddings[OpenAI Embeddings]
  Embeddings --> Scoring[Scoring & Ranking (similarity, keyword, skills, exp)]
  Scoring --> LLM[LLM Explanation (OpenAI Chat)]
  LLM --> UI
  Scoring --> Outputs[CSV / downloadable]
MD
