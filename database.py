# database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Using local SQLite for the starter implementation
DATABASE_URL = "sqlite:///./transactions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()
