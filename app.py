from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from routes.pages import pages_bp
from routes.projects import projects_bp
from db import db
from models import BlogUser

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return BlogUser.query.get(int(user_id))

@app.context_processor
def inject_user():
    return {'current_user': current_user}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project1.db'

app.config['SECRET_KEY'] = 'my-super-secret-and-unique-key'

db.init_app(app)


app.register_blueprint(pages_bp)
app.register_blueprint(projects_bp)


# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)