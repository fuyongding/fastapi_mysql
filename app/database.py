from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Task

DATABASE_URL = "mysql+pymysql://root:password@mysql-db/task_db" # task_db is the database we want to connect to
engine = create_engine(DATABASE_URL)

# Create the tables based on the models
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()