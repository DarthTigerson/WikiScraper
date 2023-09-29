from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Dictionary
from bs4 import BeautifulSoup
from time import sleep
import requests, time, zlib

router = APIRouter(
    prefix="/wiki",
    tags=["wiki"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/load_wiki_page/{name}')
async def load_wiki_page(name, db: Session = Depends(get_db)):
    print(f'Loading: {name}')
    db_data = db.query(Dictionary).filter(Dictionary.title == name).first()
    if db_data:
        return db_data
    else:
        return None