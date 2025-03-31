from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

# Use a more flexible path approach
data_dir = os.environ.get("DATA_DIR", "/app/data")
os.makedirs(data_dir, exist_ok=True)

engine = create_engine(f"sqlite:///{os.path.join(data_dir, 'files.db')}")
SessionLocal = sessionmaker(bind=engine)

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    size = Column(Integer)
    timestamp = Column(Float)

def init_db():
    try:
        Base.metadata.create_all(engine, checkfirst=True)
    except Exception as e:
        print(f"Database initialization note: {e}")

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()