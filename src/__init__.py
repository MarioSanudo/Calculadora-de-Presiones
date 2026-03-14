from flask import Flask
from .utils.extensions import db,migrate
from dotenv import load_dotenv
from ..config import DeveopmentConfig



def app_creation():

    load_dotenv()

    app=Flask(__name__)
    app.config.from_object(DeveopmentConfig)

    db.init_app(app)
    migrate.init_app(app)

    return app