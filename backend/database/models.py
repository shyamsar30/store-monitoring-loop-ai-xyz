from sqlalchemy import BigInteger, Column, DateTime, Enum, Integer, String, Time

from backend.database.connector import Base, db_engine
from backend.database.datatypes import StoreStatusTypes

class StoreStatus(Base):
    __tablename__ = "store_status"

    id = Column(Integer, autoincrement=True, primary_key=True)
    store_id = Column(BigInteger, nullable=False)
    status = Column(Enum(*StoreStatusTypes.all(), name='store_status_types'), nullable=False)
    timestamp_utc = Column(DateTime)


class MenuHours(Base):
    __tablename__ = "menu_hours"

    id = Column(Integer, autoincrement=True, primary_key=True)
    store_id = Column(BigInteger, nullable=False)
    day = Column(Integer, nullable=False)
    start_time_local = Column(Time, nullable=False)
    end_time_local = Column(Time, nullable=False)


class LocalTimeZones(Base):
    __tablename__ = 'local_time_zones'

    id = Column(Integer, autoincrement=True, primary_key=True)
    store_id = Column(BigInteger, nullable=False)
    timezone_str = Column(String(50), nullable=False)


# Create all the tables in database
if __name__ == "__main__":
    Base.metadata.create_all(db_engine)