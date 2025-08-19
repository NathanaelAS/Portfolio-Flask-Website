from db import db
import datetime

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return '<Task %r>' % self.id
    
class ScheduleEventList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    start = db.Column(db.DateTime, nullable = False)
    end = db.Column(db.DateTime, nullable = True)
    all_day = db.Column(db.Boolean, nullable = False, default = False)
    description = db.Column(db.String(500), nullable = True)
    url = db.Column(db.String(200), nullable = True)
    color = db.Column(db.String(7), default = "#007bff")
    class_name = db.Column(db.String(50), nullable = True)

    def __repr__(self):
        return f"<Event {self.id}: {self.title}"