from flask import Flask, request, jsonify, render_template
from workflow import plant_care_workflow
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
        
    try:
        schedule = plant_care_workflow(user_input, session_id)
        return jsonify({
            "response": schedule,
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
