from flask import Blueprint, render_template, request, redirect, url_for
from db import db
from models import TodoList

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/projectOverview')
def projectOverview_page():
    return render_template('projects/projectOverview.html', active_page = 'projectOverview')

@projects_bp.route('/project1', methods = ['POST', 'GET'])
def project1_page():
    if request.method == 'POST':
        task_content = request.form["content"]
        new_task = TodoList(content = task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('projects.project1_page'))
        except:
            return "There was an issue adding your task"
        

    else:
        tasks = TodoList.query.order_by(TodoList.date_created).all()
        return render_template('projects/project1.html', active_page = 'project1', tasks = tasks)

    