from flask import current_app as app
from flask_pymongo import PyMongo
from api.config import DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASS

class Mongo:
    __connection = None

    @classmethod
    def db(cls):
        if cls.__connection is None:
            app.config["MONGO_DBNAME"] = DB_NAME
            app.config["MONGO_PORT"] = DB_PORT
            app.config["MONGO_HOST"] = DB_HOST
            app.config["MONGO_USERNAME"] = DB_USER
            app.config["MONGO_PASSWORD"] = DB_PASS

            cls.__connection = PyMongo(app, config_prefix='MONGO').db

        return cls.__connection
