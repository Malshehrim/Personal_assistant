from flask import Flask, render_template, request, redirect, url_for
from data_manager import add_task, toggle_task, get_tasks_by_type, load_tasks
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================
# 🚀 APP SETUP
# ==========================================

# 1. Load secret variables (like API keys) from .env file
load_dotenv()

# 2. Initialize Flask App
app = Flask(__name__)

# --- AI Configuration (Gemini) ---
api_key = os.getenv("GEMINI_API_KEY")
model = None

# Check if API Key exists
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("⚠️ WARNING: Gemini API Key not found. AI features will not work.")

# This is the 'System Instruction' - The brain of our AI
SYSTEM_INSTRUCTION = """
You are a helpful and strict Task Assistant.
Your job is to manage the user's tasks.
Only answer questions about the tasks provided in the context.
If asked about off-topic things (jokes, weather, etc.), politely refuse.
Keep answers short and clear.
"""

# ==========================================
# 🌐 ROUTES (Pages)
# ==========================================

@app.route('/')
def index():
    """
    The Home Page (Dashboard).
    Displays Upcoming and Previous tasks.
    """
    # Get sorted tasks
    all_tasks = get_tasks_by_type()
    
    # Check if there is an AI answer to show
    ai_response = request.args.get('ai_response') 
    
    # Send data to HTML template
    return render_template('index.html', 
                         upcoming=all_tasks['upcoming'], 
                         previous=all_tasks['previous'],
                         ai_response=ai_response)

@app.route('/completed')
def completed():
    """
    The Completed Tasks Page.
    """
    all_tasks = get_tasks_by_type()
    return render_template('completed.html', completed=all_tasks['completed'])

# ==========================================
# ⚡ ACTIONS (Form Handling)
# ==========================================

@app.route('/add_task', methods=['POST'])
def handle_add_task():
    """
    Handles adding a new task from the form.
    """
    # Get data from HTML form inputs
    title = request.form.get('title')
    due_date = request.form.get('due_date')
    
    # Add to database (JSON file)
    if title and due_date:
        add_task(title, "", due_date)
        
    # Redirect back to home page
    return redirect(url_for('index'))

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def handle_toggle_task(task_id):
    """
    Marks a task as complete or incomplete.
    """
    toggle_task(task_id)
    
    # Return user to the page they came from
    referrer = request.referrer
    if referrer and 'completed' in referrer:
        return redirect(url_for('completed'))
    
    return redirect(url_for('index'))

@app.route('/ask_ai', methods=['POST'])
def handle_ask_ai():
    """
    Sends the user's question to Gemini AI.
    """
    if not model:
        return redirect(url_for('index', ai_response="Error: AI Key missing."))
        
    user_question = request.form.get('question')
    
    # 1. Get current tasks
    current_tasks = load_tasks()
    
    # 2. Build the full prompt (Instructions + Data + Question)
    full_prompt = f"""
    {SYSTEM_INSTRUCTION}
    
    Current User Tasks (JSON):
    {current_tasks}
    
    User Question: {user_question}
    """
    
    try:
        # 3. Generate response
        response = model.generate_content(full_prompt)
        answer = response.text
    except Exception as e:
        answer = "Sorry, I couldn't reach the AI server."

    # 4. Reload page with the answer
    return redirect(url_for('index', ai_response=answer))

# ==========================================
# ▶️ RUN THE APP
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
