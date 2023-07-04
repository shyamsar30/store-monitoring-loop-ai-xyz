from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from backend.database.models import LocalTimeZones, MenuHours, StoreStatus

class StoreStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = StoreStatus
        include_fk = True
        include_relationships = True
        load_instance = True

class MenuHoursSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MenuHours
        include_fk = True
        include_relationships = True
        load_instance = True

class LocalTimeZonesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LocalTimeZones
        include_fk = True
        include_relationships = True
        load_instance = True