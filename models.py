from db import db
from datetime import datetime, timezone

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return '<Task %r>' % self.id
    
class ScheduleEventList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = True)
    start_time = db.Column(db.Time, nullable = True)
    end_time = db.Column(db.Time, nullable = True)
    all_day = db.Column(db.Boolean, nullable = False, default = False)
    description = db.Column(db.String(500), nullable = True)
    url = db.Column(db.String(200), nullable = True)
    color = db.Column(db.String(7), default = "#007bff")
    class_name = db.Column(db.String(50), nullable = True)

    def __repr__(self):
        return f"<Event {self.id}: {self.title}"
    
class BlogUser(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    hashedPassword = db.Column(db.String(128), nullable = False)
    posts = db.relationship('BlogPost', backref = 'author', lazy = True)

    def __repr__(self):
        return f"<User {self.id}: {self.username}"
    
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

    def __repr__(self):
        return f"<Post {self.id}: {self.title}"