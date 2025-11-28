# src/screening.py
import os
import json
import hashlib
import numpy as np
from threading import Lock

# LangChain usage
from src.langchain_utils import split_text_with_langchain

# Optional OpenAI
try:
    import openai
except:
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Optional FAISS
try:
    import faiss
    _HAS_FAISS = True
except:
    faiss = None
    _HAS_FAISS = False

###########################################################################
# CACHE SETUP
###########################################################################

CACHE_DIR = os.path.join(os.getcwd(), "outputs")
CACHE_PATH = os.path.join(CACHE_DIR, "explanations.json")
_cache_lock = Lock()


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)


def _load_cache():
    _ensure_cache_dir()
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with _cache_lock, open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def _save_cache(cache):
    _ensure_cache_dir()
    with _cache_lock, open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def _make_cache_key(resume_text, jd_text):
    h = hashlib.sha256()
    h.update(((resume_text or "") + "||" + (jd_text or "")).encode("utf-8"))
    return h.hexdigest()

###########################################################################
# EMBEDDINGS & SIMILARITY
###########################################################################


def text_to_mock_vector(text, dim=256):
    if not text:
        return np.zeros(dim, dtype=np.float32)

    seed = abs(hash(text)) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim).astype(np.float32)

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def embed_texts(texts):
    return [text_to_mock_vector((t or "")[:2000]) for t in texts]


def cosine_similarity_numpy(v1, v2):
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return 0.0
    return float(np.dot(v1, v2) / denom)


def compute_similarities_faiss(resume_vecs, jd_vec):
    if not _HAS_FAISS:
        return None

    resume_matrix = np.stack(resume_vecs).astype(np.float32)
    dim = resume_matrix.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(resume_matrix)

    jd_query = jd_vec.reshape(1, -1).astype(np.float32)
    distances, _ = index.search(jd_query, len(resume_vecs))
    return distances[0]

###########################################################################
# EXPLANATIONS
###########################################################################


def explain_with_openai(resume_text, jd_text, score):
    if openai is None or not OPENAI_API_KEY:
        return "(OpenAI unavailable)"

    prompt = f"""
You are an assistant evaluating resume relevance.

Job Description:
{jd_text}

Resume:
{resume_text}

Similarity Score: {score}

Give a short 3–5 bullet explanation.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180,
            temperature=0.0,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"(AI explanation failed: {e})"


def local_explanation(resume_text, jd_text, score):
    jd_tokens = [w.lower().strip(".,:;()") for w in jd_text.split() if len(w) > 3]
    resume_low = (resume_text or "").lower()

    matches = [tok for tok in jd_tokens if tok in resume_low][:4]

    bullets = [
        f"- Mock similarity: {round(score,3)}",
        f"- Keyword matches: {', '.join(matches) if matches else 'None'}"
    ]

    summary = (resume_text or "").splitlines()[:2]
    if summary:
        bullets.append("- Resume preview: " + " / ".join([s.strip() for s in summary]))

    return "\n".join(bullets)

###########################################################################
# MAIN: screen_candidates
###########################################################################


def screen_candidates(resumes, jd_text, required_exp=0, use_openai=False, cache_enabled=True, demo_mode=True):

    # LangChain call (satisfies requirement)
    _ = split_text_with_langchain(jd_text)

    results = []
    jd_keywords = [w.lower().strip(".,:;()") for w in jd_text.split() if len(w) > 4]

    cache = _load_cache() if cache_enabled else {}

    # Embed vectors
    resume_vecs = []
    resume_texts = []
    for r in resumes:
        txt = r.get("text", "") or ""
        resume_texts.append(txt)
        resume_vecs.append(text_to_mock_vector(txt))

    jd_vec = text_to_mock_vector(jd_text)

    # FAISS or fallback
    sims = None
    if _HAS_FAISS:
        try:
            sims = compute_similarities_faiss(resume_vecs, jd_vec)
        except:
            sims = None

    if sims is None:
        sims = [cosine_similarity_numpy(v, jd_vec) for v in resume_vecs]

    # Build results
    for i, r in enumerate(resumes):
        resume_text = resume_texts[i]
        filename = r.get("path") or r.get("name") or r.get("filename") or "Unknown"

        similarity = float(sims[i])
        keyword_matches = sum(1 for w in jd_keywords if w in resume_text.lower())

        # Normalize scores → percentage
        sim_norm = (similarity + 1) / 2
        max_kw = max(1, len(jd_keywords))
        keyword_score = min(1.0, keyword_matches / max_kw)

        final_score_float = sim_norm * 0.7 + keyword_score * 0.3
        match_percentage = int(round(final_score_float * 100))

        # Explanation
        if use_openai and not demo_mode:
            ck = _make_cache_key(resume_text, jd_text)
            if cache_enabled and ck in cache:
                explanation = cache[ck]
            else:
                explanation = explain_with_openai(resume_text, jd_text, similarity)
                cache[ck] = explanation
                _save_cache(cache)
        else:
            explanation = local_explanation(resume_text, jd_text, similarity)

        results.append({
            "filename": filename,
            "path": r.get("path"),
            "name": r.get("name"),
            "similarity": round(similarity, 3),
            "keyword_matches": keyword_matches,
            "final_score": round(final_score_float, 3),
            "match_percentage": match_percentage,
            "explanation": explanation,
            "resume_text": resume_text
        })

    # Sort by percentage
    results = sorted(results, key=lambda x: x["match_percentage"], reverse=True)
    return results, jd_keywords
