from sqlalchemy.orm import Session
from typing import List, Optional
from .database import JournalEntry
from .schemas import EntryCreate
from . import nlp
import re


def _clean_keyword(tok: str) -> str:
    """Normalize a keyword: strip, remove punctuation, lowercase."""
    tok = tok or ""
    # remove punctuation except word chars, whitespace and hyphen
    tok = re.sub(r"[^\w\s-]", "", tok)
    return tok.strip().lower()


def _normalize_keywords_list(kws: list[str]) -> list[str]:
    """Normalize keywords and preserve order while deduplicating."""
    seen = set()
    out: list[str] = []
    for k in kws:
        nk = _clean_keyword(k)
        if not nk:
            continue
        if nk in seen:
            continue
        seen.add(nk)
        out.append(nk)
    return out

def create_entry(db: Session, entry: EntryCreate) -> JournalEntry:
    sentiment = nlp.analyze_sentiment(entry.content)
    kw = nlp.extract_keywords(entry.content)
    # normalize and deduplicate keywords before saving
    norm_kw = _normalize_keywords_list(kw)
    record = JournalEntry(
        content=entry.content,
        sentiment=sentiment,
        keywords=",".join(norm_kw),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def list_entries(db: Session, sentiment: Optional[str] = None, offset: int = 0, limit: int = 20) -> List[JournalEntry]:
    q = db.query(JournalEntry).order_by(JournalEntry.created_at.desc())
    if sentiment in {"positive", "neutral", "negative"}:
        q = q.filter(JournalEntry.sentiment == sentiment)
    return q.offset(offset).limit(limit).all()

def get_entry(db: Session, entry_id: int) -> Optional[JournalEntry]:
    return db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()

def keyword_frequencies(db: Session, top_k: int = 10) -> list[tuple[str, int]]:
    from collections import Counter
    all_kws = []
    for e in db.query(JournalEntry).all():
        # normalize and deduplicate per entry to count presence across entries
        kws = [k for k in (k.strip() for k in e.keywords.split(",")) if k]
        kws = _normalize_keywords_list(kws)
        all_kws.extend(kws)
    freq = Counter(all_kws)
    return freq.most_common(top_k)
