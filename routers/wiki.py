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
    
@router.get('/get_wiki_page_list/{searched}')
async def get_wiki_page_list(searched: bool, db: Session = Depends(get_db)):
    db_data = db.query(Dictionary).filter(Dictionary.searched == searched).all()
    if db_data is not None:
        return [data.title for data in db_data]
    else:
        return None