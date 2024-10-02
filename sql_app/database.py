from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_PASS = os.getenv("SUPABASE_PASS")
SUPABASE_DBNAME = os.getenv("SUPABASE_DBNAME")
DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASS}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DBNAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
