from transformers import pipeline
from rake_nltk import Rake
import nltk


# Ensure stopwords are available on first run
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")
    nltk.download("punkt")

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
