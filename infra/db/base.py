from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

engine: Engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        print("Closing DB")
        db.close()


Base = declarative_base()
