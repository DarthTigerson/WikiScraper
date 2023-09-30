from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi_utils.tasks import repeat_every
from models import Dictionary
from bs4 import BeautifulSoup
from time import sleep
import requests, zlib

router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/scrape_wiki_page/{url}')
async def get_wikipedia_page_soup(url):
    url = f"https://en.wikipedia.org/wiki/{url}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

async def get_wikipedia_page_name(url, db: Session = Depends(get_db)):
    soup = await get_wikipedia_page_soup(url)
    name = soup.find(id="firstHeading").text

    db_url = db.query(Dictionary).filter(Dictionary.url == url).first()
    
    if db_url:
        db_url.title = name
        db.add(db_url)
        db.commit()
        return url
    else:
        return url

async def scrape_urls_from_soup(url, db: Session = Depends(get_db)):
    soup = await get_wikipedia_page_soup(url)

    for link in soup.find_all("a"):
        url = link.get("href")
        if url != None and url != "/wiki/Main_Page":
            if url.startswith("/wiki/") and not ":" in url and not "#" in url:
                url = url.replace("/wiki/", "")
                await add_new_url_to_dictionary(url, db)

async def add_new_url_to_dictionary(url, db: Session = Depends(get_db)):

    db_url = db.query(Dictionary).filter(Dictionary.url == url).first()

    if db_url == None:
        print(f'Adding: {url}')
        dictionary = Dictionary(url=url)
        db.add(dictionary)
        db.commit()
        return dictionary

async def save_soup_to_database(url, db: Session = Depends(get_db)):
    print(f'Saving soup to database: {url}')
    soup = await get_wikipedia_page_soup(url)

    db_url = db.query(Dictionary).filter(Dictionary.url == url).first()
    db_url.page_content = zlib.compress(str(await html_soup_data_cleaner(soup)).encode())
    db_url.searched = True
    db.add(db_url)
    db.commit()
    return db_url

@router.get('wiki_soup_data_cleaner/{soup}')
async def html_soup_data_cleaner(soup):
    key1 = '<div class="noprint" id="siteSub">'
    key2 = '<h2><span class="mw-headline" id="References">References</span>'

    soup = str(soup)
    soup = soup[soup.find(key1):]
    soup = soup[:soup.find(key2)]

    return soup

@router.get('/main_scraper/{url}')
async def main_scraper(url, db: Session = Depends(get_db)):
    print(f'Running main scraper on: {url}')
    try:
        await get_wikipedia_page_name(url, db=db)
        await scrape_urls_from_soup(url, db=db)
        await save_soup_to_database(url, db=db)
        return True
    except:
        print('Error, waiting 15 seconds')
        sleep(15)
        return False

async def main(db: Session = Depends(get_db)):
    url_entry = db.query(Dictionary).order_by(Dictionary.id.asc()).filter(Dictionary.searched == False).first()
    if url_entry:
        await main_scraper(url_entry.url, db=db)

@router.on_event("startup")
@repeat_every(seconds=10)
async def startup_event():
    print('Hello there')
    await add_new_url_to_dictionary("Space", db=SessionLocal())
    await main(db=SessionLocal())