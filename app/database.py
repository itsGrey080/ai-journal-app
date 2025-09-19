from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./journal.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sentiment = Column(String(16), index=True, nullable=False)
    keywords = Column(Text, nullable=False)  # comma-separated
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 