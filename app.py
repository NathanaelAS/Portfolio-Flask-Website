from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from routes.pages import pages_bp
from routes.projects import projects_bp
from db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project1.db'

db.init_app(app)


app.register_blueprint(pages_bp)
app.register_blueprint(projects_bp)


# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)