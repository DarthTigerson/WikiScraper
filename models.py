from database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey

class Dictionary(Base):
    __tablename__ = 'dictionary'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String)
    searched = Column(Boolean, default=False)
    page_content = Column(String)