from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime

app = FastAPI()

DATABASE_URL = "mysql+mysqlconnector://root:Sqljg#12@localhost/newsdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

Base.metadata.create_all(bind=engine)

class NewsCreate(BaseModel):
    title: str
    content: str

class NewsResponse(NewsCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

@app.post("/news/", response_model=NewsResponse)
def create_news(news: NewsCreate):
    with SessionLocal() as db:
        db_news = News(title=news.title, content=news.content)
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        return db_news

@app.get("/news/", response_model=List[NewsResponse])
def read_news():
    with SessionLocal() as db:
        news_items = db.query(News).all()
        return news_items

@app.get("/news/{news_id}", response_model=NewsResponse)
def read_news_item(news_id: int):
    with SessionLocal() as db:
        news_item = db.query(News).filter(News.id == news_id).first()
        if news_item is None:
            raise HTTPException(status_code=404, detail="News not found")
        return news_item

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI News API!"}



