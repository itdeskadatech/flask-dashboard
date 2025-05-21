from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this!

UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'data/agents.json'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('upload'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_excel(filepath)
            required_columns = ['First Name', 'University Name', 'Incentive Amount']
            if all(col in df.columns for col in required_columns):
                data = df[required_columns].to_dict(orient='records')
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f)
                return redirect(url_for('dashboard'))
            else:
                error = f"Excel file must contain columns: {', '.join(required_columns)}"
                return render_template('upload.html', error=error)
        else:
            return render_template('upload.html', error="Please upload a valid Excel file (.xls or .xlsx).")

    return render_template('upload.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
 
@app.route('/data')
def get_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
