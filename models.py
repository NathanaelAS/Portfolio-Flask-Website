from db import db
import datetime

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return '<Task %r>' % self.id