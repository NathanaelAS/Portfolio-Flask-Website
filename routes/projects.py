from flask import Blueprint, render_template, request, redirect, url_for
from db import db
from models import TodoList

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/projectOverview')
def projectOverview_page():
    return render_template('projects/projectOverview.html', active_page = 'projectOverview')

@projects_bp.route('/taskManager', methods = ['POST', 'GET'])
def taskManager_page():
    if request.method == 'POST':
        task_content = request.form["content"]
        new_task = TodoList(content = task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('projects.taskManager_page'))
        except:
            return "There was an issue adding your task"
        

    else:
        tasks = TodoList.query.order_by(TodoList.date_created).all()
        return render_template('projects/taskManager/taskManager.html', active_page = 'taskManager', tasks = tasks)
    
@projects_bp.route('/taskManager/delete/<int:id>')
def delete(id):
    task_to_delete = TodoList.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('projects.taskManager_page'))
    except:
        return 'There was a problem deleting that task'
    
@projects_bp.route('/taskManager/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = TodoList.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect(url_for('projects.taskManager_page'))
        except:
            return "There was an issue updating your task"
        
    else:
        return render_template('projects/taskManager/update.html', active_page = 'taskManager', task=task)
    
@projects_bp.route('/schedulingCalendar', methods = ['POST', 'GET'])
def schedulingCalendar_page():
    if request.method == 'POST':
        pass
    else:
        return render_template('projects/schedulerproject/scheduler.html', active_page = 'schedulingCalendar')