from flask import Flask, render_template, request, jsonify
from data_manager import add_task, toggle_task, get_tasks_by_type, load_tasks
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

# Strict System Instruction
SYSTEM_INSTRUCTION = """
You are a strict, professional AI Task Assistant. 
Your ONLY purpose is to help the user manage their tasks based on the provided JSON data.
You must REFUSE nicely but firmly to answer any questions unrelated to the user's tasks or task management.
If the user asks "Tell me a joke", "What is the weather", or generates code unrelated to this app, you must say:
"I am sorry, I can only assist you with your tasks and productivity."
When analyzing tasks, be concise, direct, and professional.
"""

@app.route('/')
def index():
    tasks = get_tasks_by_type()
    return render_template('index.html', upcoming=tasks['upcoming'], previous=tasks['previous'])

@app.route('/completed')
def completed():
    tasks = get_tasks_by_type()
    return render_template('completed.html', completed=tasks['completed'])

@app.route('/api/add_task', methods=['POST'])
def api_add_task():
    data = request.json
    add_task(data['title'], data.get('description', ''), data['due_date'])
    return jsonify({'success': True})

@app.route('/api/toggle_task', methods=['POST'])
def api_toggle_task():
    data = request.json
    toggle_task(data['id'])
    return jsonify({'success': True})

@app.route('/api/ai_chat', methods=['POST'])
def api_ai_chat():
    if not model:
        return jsonify({'response': "AI functionality is not available (Missing API Key)."})
    
    user_message = request.json.get('message', '')
    tasks = load_tasks()
    
    # Construct context
    context = f"{SYSTEM_INSTRUCTION}\n\nCurrent Tasks Context:\n{tasks}\n\nUser Question: {user_message}"
    
    try:
        response = model.generate_content(context)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': f"AI Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
