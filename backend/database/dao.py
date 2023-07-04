from backend.database.models import LocalTimeZones, MenuHours, StoreStatus
from backend.database.schemas import LocalTimeZonesSchema, MenuHoursSchema, StoreStatusSchema


class StoreStatusDao():
    model = StoreStatus
    schema = StoreStatusSchema

class MenuHoursDao():
    model = MenuHours
    schema = MenuHoursSchema

class LocalTimeZonesDao():
    model = LocalTimeZones
    schema = LocalTimeZonesSchema

store_status_dao = StoreStatusDao()
menu_hours_dao = MenuHoursDao()
local_time_zone_dao = LocalTimeZonesDao()
