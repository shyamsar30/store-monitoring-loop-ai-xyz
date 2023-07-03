from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from backend.config import Config

db_engine = create_engine(Config.DB_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db_engine))

Base = declarative_base()
