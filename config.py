import os
from secrets import token_hex

class Config:

    SECRET_KEY= os.environ.get("SECRET_KEY") or token_hex(32)
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    

class DeveopmentConfig(Config):

    SQLALCHEMY_DATABASE_URI= os.getenv("DATABASE_URL_DEVELOPMENT")


    
    