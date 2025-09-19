from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .schemas import EntryCreate
from . import crud

app = FastAPI(title="Personal Journal")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def index(request: Request, sentiment: Optional[str] = None, page: int = 1, db: Session = Depends(get_db)):
    page = max(page, 1)
    limit = 10
    offset = (page - 1) * limit
    entries = crud.list_entries(db, sentiment=sentiment, offset=offset, limit=limit)
    topics = crud.keyword_frequencies(db, top_k=10)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "entries": entries, "sentiment": sentiment, "page": page, "topics": topics}
    )

@app.post("/entries")
def create_entry(content: str = Form(...), db: Session = Depends(get_db)):
    content = content.strip()
    data = EntryCreate(content=content)
    crud.create_entry(db, data)
    return RedirectResponse(url="/", status_code=303)

@app.get("/entries/{entry_id}")
def entry_detail(entry_id: int, request: Request, db: Session = Depends(get_db)):
    entry = crud.get_entry(db, entry_id)
    if not entry:
        return RedirectResponse(url="/", status_code=303)
    kws = [k for k in entry.keywords.split(",") if k]
    return templates.TemplateResponse("detail.html", {"request": request, "entry": entry, "keywords": kws})
