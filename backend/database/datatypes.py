class DataType:
    @classmethod
    def all(cls):
        return [getattr(cls, k) for k in dir(cls) if k.isupper()]

class StoreStatusTypes(DataType):
    ACTIVE = 'active'
    INACTIVE = 'inactive'