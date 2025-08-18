from flask import Flask, render_template
from routes.pages import pages_bp
from routes.projects import projects_bp

app = Flask(__name__)

app.register_blueprint(pages_bp)
app.register_blueprint(projects_bp)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)