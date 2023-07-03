from .env import Environment

class Config:
    DB_URL = Environment.DB_URL

    APP_NAME = "Store Monitoring"
    SWAGGER_UI_URL = "/wherearemyapis"


    CURRENT_TIME_UTC = "2023-01-25 18:13:22.479"