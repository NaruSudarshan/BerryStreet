from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. The Database URL (SQLite creates a local file named berry_street.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./berry_street.db"

# 2. The Engine (The actual connection to the database)
# check_same_thread=False is a specific requirement for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. The Session Factory (Creates temporary conversations with the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base Class (All our future database tables will inherit from this)
Base = declarative_base()

# 5. Dependency Injection (We will use this in our routers later)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()