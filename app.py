from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html', active_page='home')

@app.route('/projects')
def projectOverview_page():
    return render_template('projects.html', active_page='projects')
    
@app.route('/project1')
def projectPDFReader_page():
    return render_template('project1.html', active_page='project1')

@app.route('/contact')
def contact_page():
    return render_template('contact.html', active_page='contact')

@app.route('/about')
def about_page():
    return render_template('about.html', active_page='about')





# Run the application
if __name__ == '__main__':
    app.run(debug=True)