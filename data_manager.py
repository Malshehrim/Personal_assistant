import json
import os
from datetime import datetime

DATA_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def add_task(title, description, due_date):
    tasks = load_tasks()
    new_task = {
        'id': len(tasks) + 1,
        'title': title,
        'description': description,
        'due_date': due_date,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

def toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == int(task_id):
            if task['status'] == 'pending':
                task['status'] = 'completed'
            else:
                task['status'] = 'pending'
            break
    save_tasks(tasks)

def get_tasks_by_type():
    tasks = load_tasks()
    upcoming = []
    previous = []
    completed = []
    
    today = datetime.now().date()
    
    for task in tasks:
        if task['status'] == 'completed':
            completed.append(task)
            continue
            
        # Parse due date (assuming YYYY-MM-DD)
        try:
            task_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            if task_date < today:
                previous.append(task)
            else:
                upcoming.append(task)
        except ValueError:
            # If date is invalid or missing, put in upcoming by default or handle as error
            upcoming.append(task)
            
    # Sort tasks
    upcoming.sort(key=lambda x: x['due_date'])
    previous.sort(key=lambda x: x['due_date'], reverse=True) # Newest overdue first
    
    return {
        'upcoming': upcoming,
        'previous': previous,
        'completed': completed
    }
