from datetime import datetime, timedelta
from flask import g
from sqlalchemy import func, text
from backend.config import Config
from backend.database.models import LocalTimeZones, MenuHours, StoreStatus
from backend.database.schemas import LocalTimeZonesSchema, MenuHoursSchema, StoreStatusSchema
from backend.app import db_session

class StoreStatusDao():
    model = StoreStatus
    schema = StoreStatusSchema

    def get_store_status(self, timestamp, store_id):
        return db_session.query(
            self.model
        ).filter(
            self.model.store_id == store_id,
            self.model.timestamp_utc.isnot(None),
            func.date(self.model.timestamp_utc) > datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").date() - timedelta(days=7)
        ).order_by(
            self.model.timestamp_utc
        ).with_entities(
            self.model.timestamp_utc,
            self.model.status
        ).all()
    
    def get_all_ids(self):
        return db_session.query(
            self.model.store_id
        ).distinct().all()

class MenuHoursDao():
    model = MenuHours
    schema = MenuHoursSchema

    def get_start_end_time_utc_by_store_id(self, store_id):
        return db_session.query(
            self.model
        ).outerjoin(
            LocalTimeZones, self.model.store_id == LocalTimeZones.store_id
        ).outerjoin(
            func.pg_timezone_names().alias('pg'), LocalTimeZones.timezone_str == text('pg.name')
        ).filter(
            self.model.store_id == store_id
        ).with_entities(
            self.model.store_id,
            self.model.day,
            (self.model.start_time_local - text('pg.utc_offset')).label('start_time'),
            (self.model.end_time_local - text('pg.utc_offset')).label('end_time')
        ).all()
    
    def get_null_menu_hours(self, store_id):
        return db_session.query(
            self.model
        ).filter(
            self.model.store_id == store_id
        ).with_entities(
            self.model.store_id,
            self.model.day,
            (self.model.start_time_local + text("interval '5 hours'")).label('start_time'),
            (self.model.end_time_local + text("interval '5 hours'")).label("end_time")
        ).all()

class LocalTimeZonesDao():
    model = LocalTimeZones
    schema = LocalTimeZonesSchema

store_status_dao = StoreStatusDao()
menu_hours_dao = MenuHoursDao()
local_time_zone_dao = LocalTimeZonesDao()
