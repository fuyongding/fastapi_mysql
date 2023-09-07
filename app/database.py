"""
Module to define database configurations
"""
# pylint: disable=invalid-name
# pylint: disable=trailing-whitespace
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

# Load environment variables from .env file
load_dotenv()

# Get environment variables
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE = os.getenv("DATABASE")
DATABASE_HOST = os.getenv("DATABASE_HOST")

# task_db is the database we want to connect to
DATABASE_URL = f'mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE}'
engine = create_engine(DATABASE_URL)

# Create the tables based on the models 
models.Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """gets a local session of database

    Yields:
        db: local session of database
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
