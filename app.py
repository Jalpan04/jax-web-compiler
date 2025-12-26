import subprocess
import sys
import os
import uuid
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder=os.getcwd(), static_folder='assets')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.form.get('code')
    if not code:
        return jsonify({'output': '', 'error': 'No code provided!'})

    # Use a unique filename for each request to allow concurrency
    unique_id = str(uuid.uuid4())
    filename = f"temp_code_{unique_id}.py"
    
    try:
        with open(filename, 'w') as file:
            file.write(code)

        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True, text=True, timeout=5
        )

        output = result.stdout
        error = result.stderr if result.returncode != 0 else None
        
        # If there was a timeout, subprocess.run raises TimeoutExpired, catch it below
        
    except subprocess.TimeoutExpired:
        output = ""
        error = "Error: Timeout exceeded (5s limit)."
    except Exception as e:
        output = ""
        error = f"System Error: {str(e)}"
    finally:
        if os.path.exists(filename):
            os.remove(filename)

    return jsonify({'output': output, 'error': error})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
