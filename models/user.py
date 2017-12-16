from api.index import db


class UserModel(db.Document):
    name = db.StringField()
    email = db.StringField()
    password = db.StringField()
