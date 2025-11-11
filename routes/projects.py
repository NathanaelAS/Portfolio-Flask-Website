from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from db import db
from models import TodoList, ScheduleEventList, BlogUser, BlogPost
from datetime import datetime, timedelta, time, timezone
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

@projects_bp.route('/projectOverview')
def projectOverview_page():
    return render_template('projects/projectOverview.html', active_page = 'projectOverview')

@projects_bp.route('/contact/verify-captcha', methods=['POST'])
def verify_captcha():
    try:
        data = request.get_json()
        token = data.get('recaptcha_token')
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
    
    if not token:
        return jsonify({'success': False, 'error': 'No token provided'}), 400
    
    payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': token,
        'remoteip': request.remote_addr
    }

    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Google API Request failed: {e}")
        return jsonify({'success': False, 'error': 'Google API communication failed'}), 500
    
    if result.get('success'):
        return jsonify({'success': True}), 200
    else:
        print(f"reCAPTCHA verification failed. Error codes: {result.get('error-codes')}")
        return jsonify({'success': False, 'error': 'reCAPTCHA failed'}), 200
    

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
        event_data = request.get_json()

        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')

        if not start_time and not end_time:
            is_all_day = True
            formatted_start_time = time(0, 0, 0)
            formatted_end_time = time(0, 0, 0)
        elif start_time and not end_time:
            is_all_day = False
            formatted_start_time = datetime.strptime(start_time, '%I:%M %p').time()
            formatted_end_time = time(23,59,59)
        else:
            is_all_day = False

            if start_time:
                formatted_start_time = datetime.strptime(start_time, '%I:%M %p').time()
            else:
                formatted_start_time = time(0, 0, 0)
            
            if end_time:
                formatted_end_time = datetime.strptime(end_time, '%I:%M %p').time()
            else:
                if start_time:
                    formatted_end_time = time(23,59,59)
                else:
                    formatted_end_time = time(0, 0, 0)
        
        start_date_obj = datetime.strptime(event_data.get('start_date'), '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(event_data.get('end_date'), '%Y-%m-%d').date()


        new_event = ScheduleEventList(
            title = event_data.get('title'),
            start_date = start_date_obj,
            end_date = end_date_obj,
            start_time = formatted_start_time,
            end_time = formatted_end_time,
            all_day = is_all_day,
            description = event_data.get('description'),
            url = event_data.get('url'),
            color = event_data.get('color')
        )

        db.session.add(new_event)
        db.session.commit()

        return jsonify({'message': 'Event added successfully'}), 201

    else:
        return render_template('projects/schedulerproject/scheduler.html', active_page = 'schedulingCalendar')
    
@projects_bp.route('/schedulingCalendar/eventViewer', methods = ['GET'])
def eventViewer_Page():
    events = ScheduleEventList.query.all()
    return render_template('projects/schedulerproject/eventViewer.html', active_page = 'schedulingCalendar', events = events)
    
@projects_bp.route('/schedulingCalendar/events', methods = ['GET'])
def get_all_events():

    start_str = request.args.get('start')
    end_str = request.args.get('end')

    start_date = datetime.fromisoformat(start_str)
    end_date = datetime.fromisoformat(end_str)

    events = ScheduleEventList.query.filter(
        (ScheduleEventList.start_date >= start_date) &
        (ScheduleEventList.end_date <= end_date)
    ).all()

    events_list = []

    for event in events:

        formatted_start_time = time(0,0,0)
        formatted_end_time = time(0,0,0)

        if event.start_time:
            formatted_start_time = event.start_time
        if event.end_time:
            formatted_end_time = event.end_time

        if event.all_day:
            start_datetime_obj = datetime.combine(event.start_date, formatted_start_time)
            end_date_exclusive_for_calendar = event.end_date + timedelta(days=1)
            end_datetime_obj = datetime.combine(end_date_exclusive_for_calendar, formatted_end_time)
        else:
            start_datetime_obj = datetime.combine(event.start_date, formatted_start_time)
            end_datetime_obj = datetime.combine(event.end_date, formatted_end_time)

        

        event_dict = {
            'id': event.id,
            'title': event.title,
            'start': start_datetime_obj.isoformat(),
            'end': end_datetime_obj.isoformat(),
            'allDay': bool(event.all_day),
            'url': event.url,
            'color': event.color,
            'extendedProps':{
                'description': event.description
            }
        }
        events_list.append(event_dict)

    return jsonify(events_list)

@projects_bp.route('/schedulingCalendar/update-event/<int:event_id>', methods = ['PUT'])
def update_event(event_id):
    event = ScheduleEventList.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    event.color = data.get('color', event.color)

    if data.get('start_date'):
        pythonStartDate = datetime.strptime((data.get('start_date')), '%Y-%m-%d').date()
    else:
        pythonStartDate = event.start_date

    if data.get('end_date'):
        if event.all_day:
            pythonEndDate = datetime.strptime((data.get('end_date')), '%Y-%m-%d').date() - timedelta(days=1)
        else:
            pythonEndDate = datetime.strptime((data.get('end_date')), '%Y-%m-%d').date()
    else:
        pythonEndDate = event.end_date
    
    event.start_date = pythonStartDate
    event.end_date = pythonEndDate

    db.session.commit()

    return jsonify({'message': 'Event updated successfully'})

@projects_bp.route('/schedulingCalendar/delete-event/<int:event_id>', methods = ['DELETE'])
def delete_event(event_id):
    event = ScheduleEventList.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event deleted successfully'})

@projects_bp.route('/schedulingCalendar/calendar-drag-event/<int:event_id>', methods = ['POST'])
def calendar_drag_event(event_id):
    event = ScheduleEventList.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    if event.all_day:
        durationInHours = data.get('event_duration_hours')
        pythonStartDate = datetime.strptime((data.get('start_date')), '%Y-%m-%dT%H:%M:%S.%fZ').date()
        if durationInHours > 24:
            duration = timedelta(hours=durationInHours)
            pythonEndDate = pythonStartDate + duration - timedelta(days=1)

            event.start_date = pythonStartDate
            event.end_date = pythonEndDate
        else:
            event.start_date = pythonStartDate
            event.end_date = pythonStartDate
    else:
        pythonStartDate = datetime.strptime((data.get('start_date')), '%Y-%m-%dT%H:%M:%S.%fZ')
        pythonEndDate = datetime.strptime((data.get('end_date')), '%Y-%m-%dT%H:%M:%S.%fZ')

        event.start_date = pythonStartDate.date()
        event.start_time = pythonStartDate.time()
        event.end_date = pythonEndDate.date()
        event.end_time = pythonEndDate.time()

    db.session.commit()

    return jsonify({'message': 'Event updated successfully'})

@projects_bp.route('/schedulingCalendar/calendar-resize-event/<int:event_id>', methods = ['POST'])
def calendar_resize_event(event_id):
    event = ScheduleEventList.query.get(event_id)

    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    pythonStartDate = datetime.strptime((data.get('start_date')), '%Y-%m-%dT%H:%M:%S.%fZ').date()
    pythonEndDate = datetime.strptime((data.get('end_date')), '%Y-%m-%dT%H:%M:%S.%fZ').date()

    event.start_date = pythonStartDate
    event.end_date = pythonEndDate - timedelta(days=1)

    db.session.commit()

    return jsonify({'message': 'Event updated successfully'})

@projects_bp.route('/blog', methods = ['GET', 'POST'])
def blog_page():
    return render_template('projects/blogProject/blogHome.html', active_page = 'blog')

@projects_bp.route('/blog/login', methods = ['GET','POST'])
def blog_login_page():
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        plainTextPassword = data.get('password')

        if not username or not plainTextPassword:
            return jsonify({'error': 'All fields are required'}), 400
        
        user = BlogUser.query.filter_by(username = username).first()

        if user:
            # If the user exists, compare the submitted password to the stored hash
            if check_password_hash(user.hashedPassword, plainTextPassword):
                login_user(user)
                return redirect(url_for('projects.blog_page')), 302
            else:
                return jsonify({'error': 'Invalid username or password.'}), 401
        else:
            # The user exists, but the password was incorrect
            return jsonify({'error': 'Invalid username or password.'}), 401
    else:
        # No user with that username was found
        return render_template('projects/blogProject/blogLogin.html', active_page = 'blog')
    
@projects_bp.route('/blog/logout', methods = ['POST'])
@login_required
def blog_logout():
    logout_user()

    return redirect(url_for('projects.blog_login_page'))

    
@projects_bp.route('/blog/register', methods = ['GET','POST'])
def blog_register_page():
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username')
        plainTextPassword = data.get('password')

        if not username or not plainTextPassword:
            return jsonify({'error': 'All fields are required'}), 400

        user = BlogUser.query.filter_by(username = username).first()

        if user:
            return jsonify({'error': 'Username is already taken.'}), 409
        
        hashed_password = generate_password_hash(plainTextPassword, method='pbkdf2:sha256', salt_length=16)

        new_user = BlogUser(
            username = username,
            hashedPassword = hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('projects.blog_page'))

    else:
        return render_template('projects/blogProject/blogRegister.html', active_page = 'blog')
    
@projects_bp.route('/blog/register/check_username', methods = ['GET'])
def check_username():
    username = request.args.get('username')

    user = BlogUser.query.filter_by(username = username).first()

    if user:
        is_available = False
    else:
        is_available = True

    return jsonify({'is_available': is_available})

@projects_bp.route('/blog/get_posts', methods = ['GET'])
def get_posts():
    all_posts = BlogPost.query.all()

    posts_list = []

    for post in all_posts:
        post_dict = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.strftime("%m/%d/%Y %I:%M %p"),
            'author': post.author.username
        }
        posts_list.append(post_dict)

    return jsonify(posts_list)

@projects_bp.route('/blog/create_post', methods = ['POST'])
@login_required
def create_post():
    data = request.get_json()

    if not data:
            return jsonify({'error': 'No data provided'}), 400
    
    postTitle = data.get('postTitle')
    postContent = data.get('postContent')

    if not postTitle or not postContent:
            return jsonify({'error': 'Post Title and Content are required'}), 400
    
    new_post = BlogPost(
        title = postTitle,
        content = postContent,
        author = current_user,
        created_at = datetime.now(timezone.utc)
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Pot created successfully'}), 201

@projects_bp.route('/blog/account', methods = ['GET'])
@login_required
def blog_account_page():
    return render_template('projects/blogProject/blogAccount.html', active_page = 'blog')

@projects_bp.route('/blog/account/get_user_data_and_posts', methods = ['GET'])
@login_required
def get_user_data_and_posts():
    user = current_user

    userPosts = BlogPost.query.filter_by(author = user).order_by(BlogPost.created_at.desc()).all()

    userPostsList = []

    for post in userPosts:
        userPostsList.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.strftime("%m/%d/%Y %I:%M %p")
        })
    
    userDetailsDict = {
        'id': user.id,
        'username': user.username
    }

    combinedData = {
        'user': userDetailsDict,
        'posts': userPostsList
    }
    return jsonify(combinedData), 200

