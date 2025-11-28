# src/parse_resumes.py
# Robust resume parsing helpers for the Streamlit app.
# Supports uploaded file-like objects from Streamlit (with .name and .read()).

import io
import re
import pdfplumber
import docx
from email_validator import validate_email, EmailNotValidError
import phonenumbers

def extract_text_pdf_bytes(file_bytes):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    except Exception:
        # fallback: try decode plain text (rare)
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
    return text

def extract_text_docx_bytes(file_bytes):
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""

def extract_emails(text):
    emails = []
    for match in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        try:
            valid = validate_email(match)
            emails.append(valid.email)
        except Exception:
            continue
    return list(dict.fromkeys(emails))

def extract_phone_numbers(text, region="IN"):
    phones = []
    try:
        for m in phonenumbers.PhoneNumberMatcher(text, region):
            phones.append(phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    except Exception:
        pass
    return list(dict.fromkeys(phones))

def extract_skills(text):
    # small default skill lexicon — extend as needed
    skill_keywords = [
        "python","java","c++","c#","javascript","react","node","django","flask",
        "sql","mysql","postgresql","mongodb","docker","kubernetes","aws","azure","gcp",
        "machine learning","nlp","deep learning","pandas","numpy","scikit-learn",
        "tensorflow","pytorch","excel","tableau","power bi","git","github"
    ]
    s = (text or "").lower()
    found = [k for k in skill_keywords if k in s]
    return list(dict.fromkeys(found))

def extract_years_of_experience(text):
    # try "X years" and date ranges
    if not text:
        return None
    m = re.search(r"(\d{1,2})\+?\s+years", text.lower())
    if m:
        try:
            return int(m.group(1))
        except:
            pass
    ranges = re.findall(r"(\b19\d{2}|\b20\d{2})\s*[-to]{1,3}\s*(\b19\d{2}|\b20\d{2})", text)
    if ranges:
        diffs = []
        for s,e in ranges:
            try:
                diffs.append(abs(int(e)-int(s)))
            except:
                pass
        if diffs:
            return max(diffs)
    return None

def parse_resume(uploaded_file):
    """
    uploaded_file: Streamlit UploadedFile (has .name and .read())
    returns dict with keys: path, text, name, emails, phones, skills, years_experience
    """
    name = getattr(uploaded_file, "name", "unknown")
    try:
        data = uploaded_file.read()
    except Exception:
        # if it's already bytes-like
        data = uploaded_file

    text = ""
    lower = name.lower()
    if lower.endswith(".pdf"):
        text = extract_text_pdf_bytes(data)
    elif lower.endswith(".docx"):
        text = extract_text_docx_bytes(data)
    else:
        # try decoding as text
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    emails = extract_emails(text)
    phones = extract_phone_numbers(text)
    skills = extract_skills(text)
    years = extract_years_of_experience(text)

    return {
        "path": name,
        "text": text,
        "name": name.rsplit(".", 1)[0],
        "emails": emails,
        "phones": phones,
        "skills": skills,
        "years_experience": years
    }

def parse_multiple_resumes(uploaded_files):
    """
    uploaded_files: list of uploaded file objects (Streamlit's uploader returns such)
    returns list of parsed resume dicts
    """
    parsed = []
    for f in uploaded_files:
        try:
            parsed.append(parse_resume(f))
        except Exception as e:
            # continue but include an entry with minimal info
            parsed.append({
                "path": getattr(f, "name", "unknown"),
                "text": "",
                "name": getattr(f, "name", "unknown"),
                "emails": [],
                "phones": [],
                "skills": [],
                "years_experience": None,
                "error": str(e)
            })
    return parsed
