from flask import current_app as app
from flask_mongoalchemy import MongoAlchemy
from werkzeug.local import LocalProxy

from api.config import DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASS
from flask import g


def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        app.config['MONGOALCHEMY_DATABASE'] = DB_NAME
        app.config['MONGOALCHEMY_SERVER_AUTH'] = False
        app.config["MONGOALCHEMY_PORT"] = DB_PORT
        app.config["MONGOALCHEMY_SERVER"] = DB_HOST
        app.config["MONGOALCHEMY_USER"] = DB_USER
        app.config["MONGOALCHEMY_PASSWORD"] = DB_PASS

        db = MongoAlchemy(app)

    return db

#
# db = LocalProxy(get_db)