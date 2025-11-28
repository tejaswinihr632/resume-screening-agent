# app/streamlit_app.py
import os
import sys

# Ensure project root is on sys.path so 'src' package is importable when running via Streamlit
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
from src.parse_resumes import parse_multiple_resumes
from src.screening import screen_candidates

# Optional export placeholders (should accept demo_mode parameter)
from src.google_sheets_utils import export_to_google_sheets
from src.notion_db_utils import save_to_notion

st.set_page_config(page_title="AI Resume Screening Agent", layout="wide")

# Title
st.title("📄 AI Resume Screening Agent")
st.write("Upload resumes + paste Job Description → Get ranking, similarity scores, and results.")

# Sidebar
st.sidebar.header("Settings")
required_years = st.sidebar.number_input(
    "Required Experience (years)",
    min_value=0, max_value=50, value=2
)

# Demo mode toggle (important when free tiers are exhausted)
demo_mode = st.sidebar.checkbox("Demo mode (use local mocks & local exports)", value=True)

use_openai = st.sidebar.checkbox(
    "Use real OpenAI explanations (requires OPENAI_API_KEY)", value=False
)

# Warn if user checked OpenAI but key is missing or demo mode on
_openai_key = os.getenv("OPENAI_API_KEY")
if use_openai and demo_mode:
    st.sidebar.warning("Demo mode is ON — OpenAI calls will be mocked (no external API calls). Turn off demo mode to call OpenAI.")
elif use_openai and not _openai_key:
    st.sidebar.warning("OPENAI_API_KEY not found in environment. OpenAI explanations will not run until you set the key.")

st.sidebar.write("---")
st.sidebar.write("Upload multiple resumes on the main page.")

# Input Section
st.header("1️⃣ Upload Candidate Resumes")
uploaded_files = st.file_uploader(
    "Upload PDF or DOCX resumes", type=["pdf", "docx"], accept_multiple_files=True
)

st.header("2️⃣ Paste Job Description (JD)")
jd_text = st.text_area("Paste JD here", height=200)

process_btn = st.button("🚀 Process Resumes")

# Initialize session_state placeholders if they don't exist
if "parsed_resumes" not in st.session_state:
    st.session_state["parsed_resumes"] = None
if "results" not in st.session_state:
    st.session_state["results"] = None
if "results_df" not in st.session_state:
    st.session_state["results_df"] = None
if "jd_keywords" not in st.session_state:
    st.session_state["jd_keywords"] = None

# Processing block: run when user clicks Process Resumes
if process_btn:
    if not uploaded_files:
        st.error("❌ Please upload resumes.")
    elif not jd_text.strip():
        st.error("❌ Please paste the Job Description.")
    else:
        with st.spinner("Processing resumes..."):
            parsed_resumes = parse_multiple_resumes(uploaded_files)

            results, jd_keywords = screen_candidates(
                parsed_resumes,
                jd_text,
                required_exp=required_years,
                use_openai=use_openai,
                cache_enabled=True,
                demo_mode=demo_mode  # pass demo_mode so explanations are mocked when demo_mode=True
            )

        # Save processed outputs into session_state so export buttons won't force re-processing
        st.session_state["parsed_resumes"] = parsed_resumes
        st.session_state["results"] = results
        st.session_state["jd_keywords"] = jd_keywords

        # Build DataFrame for CSV export and UI table (include explanation column only if present)
        df_rows = []
        for i, c in enumerate(results, start=1):
            row = {
                "rank": i,
                "filename": c.get("filename"),
                "final_score": c.get("final_score"),
                "match_percentage": c.get("match_percentage"),
                "similarity": c.get("similarity"),
                "keyword_matches": c.get("keyword_matches")
            }

            if c.get("explanation") is not None:
                row["explanation"] = c.get("explanation")
            df_rows.append(row)

        df = pd.DataFrame(df_rows)
        st.session_state["results_df"] = df

        st.success("✔️ Screening completed!")

# If we have processed results in session_state, show them and export buttons
if st.session_state.get("results") is not None:
    results = st.session_state["results"]
    jd_keywords = st.session_state.get("jd_keywords", [])

    st.subheader("🔍 Extracted JD Keywords")
    try:
        st.write(", ".join(jd_keywords))
    except Exception:
        st.write(jd_keywords)

    df = st.session_state.get("results_df", pd.DataFrame())

    # CSV download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download results as CSV",
        data=csv,
        file_name="resume_screening_results.csv",
        mime="text/csv"
    )

    # --- Export callbacks (operate on session_state) ---
    def _export_google():
        df_local = st.session_state.get("results_df")
        # pass demo_mode to exporter so it writes local CSV when demo_mode=True
        msg = export_to_google_sheets(df_local, demo_mode=demo_mode)
        st.session_state["_last_export_msg"] = msg

    def _save_notion():
        df_local = st.session_state.get("results_df")
        msg = save_to_notion(df_local.to_dict(orient="records"), demo_mode=demo_mode)
        st.session_state["_last_notion_msg"] = msg

    # Buttons that call callbacks (on_click avoids needing process_btn)
    st.button("📤 Export to Google Sheets", on_click=_export_google, key="export_sheets_btn")
    st.button("🗂 Save results to Notion DB", on_click=_save_notion, key="save_notion_btn")

    # Show messages from last export (if any)
    if st.session_state.get("_last_export_msg"):
        st.info(st.session_state.get("_last_export_msg"))

    if st.session_state.get("_last_notion_msg"):
        st.info(st.session_state.get("_last_notion_msg"))

    # Ranked candidates display
    st.subheader("🏆 Ranked Candidates")
    if df.empty:
        st.info("No candidates found.")

    parsed_resumes = st.session_state.get("parsed_resumes", [])
    for idx, candidate in enumerate(results, start=1):
        title = candidate.get("filename") or candidate.get("name") or f"Candidate {idx}"
        final_score = candidate.get("final_score", "N/A")
        similarity = candidate.get("similarity", "N/A")
        keyword_matches = candidate.get("keyword_matches", 0)

        with st.expander(f"{idx}. {title} — Score: {final_score}"):

            st.markdown(f"**Filename / Name:** {title}")
            st.markdown(f"**Match:** {candidate.get('match_percentage', 'N/A')}%  —  **Score:** {final_score}")
            st.markdown(f"**Similarity:** {similarity}")
            st.markdown(f"**Keyword matches:** {keyword_matches}")

            parsed_info = next((p for p in parsed_resumes if (p.get("path") or p.get("name") or "").lower() in title.lower()), None)
            if parsed_info:
                st.write(f"**Email(s):** {parsed_info.get('emails')}")
                st.write(f"**Phone(s):** {parsed_info.get('phones')}")
                st.write(f"**Skills:** {parsed_info.get('skills')}")
                st.write(f"**Years Experience:** {parsed_info.get('years_experience')}")

            # Show explanation if available (either local deterministic or OpenAI/Gemini result)
            explanation_text = candidate.get("explanation")
            if explanation_text:
                st.write("### Explanation (AI / local)")
                st.write(explanation_text)

            # RAW RESUME ONLY
            st.write("### Raw Resume Extract (preview)")
            st.code((candidate.get("resume_text") or "")[:1500])
else:
    st.info("Upload resumes and paste JD, then click 'Process Resumes' to see results.")
