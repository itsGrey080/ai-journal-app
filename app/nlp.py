from transformers import pipeline
from rake_nltk import Rake
import nltk
import os


# Ensure required NLTK resources exist at import time. This prevents LookupError
# in production when the app is started by a process that doesn't have the
# nltk_data preinstalled. We prefer to download into the project's venv
# nltk_data directory if available so the files are local to the project.
def _ensure_nltk_resources(resources: list[str], download_dir: str | None = None) -> None:
    # Add download_dir to search path so find() will succeed after download
    if download_dir:
        nltk.data.path.insert(0, download_dir)
    for res in resources:
        try:
            nltk.data.find(res)
        except LookupError:
            nltk.download(res.split('/')[-1], download_dir=download_dir)

# Prefer project-local venv nltk_data if it exists
_proj_venv_nltk = None
try:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    venv_candidate = os.path.join(root, '.venv', 'nltk_data')
    # also support top-level .venv path (project root .venv used previously)
    if os.path.isdir(venv_candidate) or not os.path.exists(venv_candidate):
        _proj_venv_nltk = venv_candidate
except Exception:
    _proj_venv_nltk = None

_ensure_nltk_resources(['corpora/stopwords', 'tokenizers/punkt', 'tokenizers/punkt_tab'], download_dir=_proj_venv_nltk)

# Load once at startup
_sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")  # type: ignore

# RAKE keyword extractor (uses NLTK stopwords)
_rake = Rake()  # default english

def analyze_sentiment(text: str) -> str:
    result = _sentiment(text[:4000])[0]  # keep short for speed
    label = result["label"].lower()
    if label == "positive":
        return "positive"
    if label == "negative":
        return "negative"
    return "neutral"

def extract_keywords(text: str, top_k: int = 8) -> list[str]:
    _rake.extract_keywords_from_text(text)
    ranked = _rake.get_ranked_phrases()[:top_k]
    cleaned = [k.lower().strip() for k in ranked if len(k.split()) <= 4]
    # Deduplicate but keep order
    seen = set()
    uniq = []
    for k in cleaned:
        if k not in seen:
            uniq.append(k)
            seen.add(k)
    return uniq
