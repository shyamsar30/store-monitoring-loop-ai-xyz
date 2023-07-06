import json
import traceback

from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect
from flask_restx import Api

from backend.celery.config import celery_init_app
from backend.config import Config
from backend.database.connector import db_session
from backend.api.endpoints import namespace

class ExtendedApi(Api):
    @property
    def specs_url(self):
        return f"{Config.SWAGGER_UI_URL}/swagger.json"

    def init_app(self, app, *args, **kwargs):
        app.route(f"{Config.SWAGGER_UI_URL}/swagger.json")(lambda: json.dumps(self.__schema__))
        super().init_app(app, *args, **kwargs)


# Setup API Endpoints
def configure_endpoints(app):
    restx_api = ExtendedApi(
        title="Store Monitoring APIs",
        version="1.0",
        description="API Documentation for store monitoring apis",
        prefix="/api",
        doc=Config.SWAGGER_UI_URL
    )

    restx_api.add_namespace(namespace)

    restx_api.init_app(app)

    return app


# Setup Database Connection
def configure_database(app):

    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DB_URL

    try:
        db_session.execute(text("SELECT 1;"))
    except Exception as e:
        traceback.print_exc()
        raise e

def configure_celery(app):

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            broker_connection_retry_on_startup=True
        ),
    )

    app.config.from_prefixed_env()
    celery_init_app(app)


# Setup Flask APP
def init_app():
    app = Flask(Config.APP_NAME)

    configure_endpoints(app)
    configure_database(app)

    configure_celery(app)

    @app.route('/')
    def home():
        return redirect(Config.SWAGGER_UI_URL)
    
    return app


# if __name__ == "__main__":
app = init_app()

db_session = SQLAlchemy(app)

celery_app = app.extensions["celery"]