from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def home_page():
    return render_template('index.html', active_page = 'home')

@pages_bp.route('/contact')
def contact_page():
    return render_template('contact.html', active_page = 'contact')

@pages_bp.route('/about')
def about_page():
    return render_template('about.html', active_page = 'about')