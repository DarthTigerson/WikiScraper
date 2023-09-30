from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Dictionary
import zlib

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

@router.get('/get_wiki_page/{name}')
async def get_wiki_page(name, db: Session = Depends(get_db)):
    print(f'Loading: {name}')
    db_data = db.query(Dictionary).filter(Dictionary.title == name).first()
    page = zlib.decompress(db_data.page_content)
    page = page.decode('utf-8').replace('\n', '')
    if db_data is not None:
        return page
    else:
        return None
    
@router.get('/get_wiki_page_list/')
async def get_wiki_page_list(db: Session = Depends(get_db)):
    db_data = db.query(Dictionary).filter(Dictionary.searched == True).all()
    if db_data is not None:
        return [data.title for data in db_data]
    else:
        return None
    
@router.get('/return_unscraped_wiki_pages/')
async def return_unscraped_wiki_pages(db: Session = Depends(get_db)):
    db_data = db.query(Dictionary).filter(Dictionary.searched == False).all()
    if db_data is not None:
        return [data.title for data in db_data]
    else:
        return None
    
@router.get('/return_wiki_url_list/')
async def return_wiki_url_list(db: Session = Depends(get_db)):
    db_data = db.query(Dictionary).all()
    if db_data is not None:
        return [{'name': data.title, 'url': f'https://wiki.example.com/{data.title}', 'searched': data.searched} for data in db_data]
    else:
        return None
