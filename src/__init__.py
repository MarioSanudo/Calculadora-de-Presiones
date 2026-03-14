from flask import Flask
from .utils.extensions import db,migrate
from dotenv import load_dotenv



def app_creation():

    load_dotenv()

    app=Flask(__name__)
    app.config.from_object()

    db.init_app(app)
    migrate.init_app(app)

    return app