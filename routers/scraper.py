from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi_utils.tasks import repeat_every
from models import Dictionary
from bs4 import BeautifulSoup
from time import sleep
import requests, zlib, asyncio

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
        #sleep(1)
        return True
    except Exception as e:
        # print error that occurred
        print(f'Error: {e}. Waiting 15 seconds.')
        sleep(15)
        return False

async def main(db: Session = Depends(get_db)):
    while True:
        try:
            url_entry = db.query(Dictionary).order_by(Dictionary.id.asc()).filter(Dictionary.searched == False).first()
            if url_entry:
                await main_scraper(url_entry.url, db=db)
        except:
            print('Error, waiting 15 seconds')
            sleep(15)
            db.rollback()
            db.close()
            db = SessionLocal()

async def main_concurrent(db: Session = Depends(get_db)):
    while True:
        try:
            tasks = []
            url_entries = db.query(Dictionary).order_by(Dictionary.id.asc()).filter(Dictionary.searched == False).limit(10).all()
            if url_entries:
                for url_entry in url_entries:
                    tasks.append(main_scraper(url_entry.url, db))
                await asyncio.gather(*tasks)
        except:
            print('Error, waiting 15 seconds')
            sleep(15)
            db.rollback()
            db.close()
            db = SessionLocal()

@router.on_event("startup")
async def startup_event():
    print('Hello there')
    await add_new_url_to_dictionary("Space", db=SessionLocal())
    await main_concurrent(db=SessionLocal())