from sqlalchemy.orm import Session
from typing import List, Optional
from .database import JournalEntry
from .schemas import EntryCreate
from . import nlp

def create_entry(db: Session, entry: EntryCreate) -> JournalEntry:
    sentiment = nlp.analyze_sentiment(entry.content)
    kw = nlp.extract_keywords(entry.content)
    record = JournalEntry(
        content=entry.content,
        sentiment=sentiment,
        keywords=",".join(kw),
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
        all_kws.extend([k.strip() for k in e.keywords.split(",") if k.strip()])
    freq = Counter(all_kws)
    return freq.most_common(top_k)
