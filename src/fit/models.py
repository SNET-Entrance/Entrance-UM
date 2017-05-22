from bootstrap import db
from bootstrap.models import Ext
import datetime

class FitFile(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    path = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activityDateTime = db.Column(db.Text, nullable=False)

    def __init__(self, name, path, user_id, activityDateTime):
        self.name = name
        self.path = path
        self.created = datetime.datetime.now()
        self.user_id = user_id
        self.activityDateTime = activityDateTime