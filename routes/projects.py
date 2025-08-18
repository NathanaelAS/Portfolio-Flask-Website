from flask import Blueprint, render_template

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projectOverview')
def projectOverview_page():
    return render_template('projects/projectOverview.html', active_page = 'projectOverview')

@projects_bp.route('/project1')
def project1_page():
    return render_template('projects/project1.html', active_page = 'project1')