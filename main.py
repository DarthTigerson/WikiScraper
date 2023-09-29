from fastapi import FastAPI
from routers import scraper
from database import engine
import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


app.include_router(scraper.router)