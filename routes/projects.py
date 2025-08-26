from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from db import db
from models import TodoList, ScheduleEventList
from datetime import datetime, timedelta, time

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

        start_datetime_obj = datetime.combine(start_date_obj, formatted_start_time)
        end_datetime_obj = datetime.combine(end_date_obj, formatted_end_time)

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

@projects_bp.route('schedulingCalendar/update-event/<int:event_id>', methods = ['PUT'])
def update_event(event_id):
    event = ScheduleEventList.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)

    db.session.commit()

    return jsonify({'message': 'Event updated successfully'})

@projects_bp.route('schedulingCalendar/delete-event/<int:event_id>', methods = ['DELETE'])
def delete_event(event_id):
    event = ScheduleEventList.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event deleted successfully'})