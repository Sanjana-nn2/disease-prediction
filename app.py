from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json, os, joblib, numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# ---------------- USER FUNCTIONS ---------------- #

def load_users():
    file_path = 'users.json'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

USER_CREDENTIALS = load_users()

def add_user(username, password):
    users = load_users()
    if username in users:
        return False  # already exists
    users[username] = password
    save_users(users)
    return True

# ---------------- MODEL LOADING ---------------- #
model = joblib.load('model/model.pkl')
with open('model/cols.json') as f:
    cols = json.load(f)
with open('model/label_map.json') as f:
    labels = json.load(f)['classes']

# ---------------- ROUTES ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if add_user(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error="Username already exists!")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    symptoms = data.get('symptoms', {})
    age = int(data.get('age', 30))
    gender = data.get('gender', 'M')

    x = [0]*len(cols)
    for i, c in enumerate(cols):
        if c == 'age':
            x[i] = age
        elif c == 'gender_male':
            x[i] = 1 if gender == 'M' else 0
        else:
            x[i] = int(symptoms.get(c, 0))

    x = np.array(x).reshape(1, -1)
    pred_idx = model.predict(x)[0]
    pred_label = labels[int(pred_idx)]

    probs = None
    try:
        probs = model.predict_proba(x).tolist()[0]
    except Exception:
        probs = None

    return jsonify({'prediction': pred_label, 'probabilities': probs})

if __name__ == '__main__':
    app.run(debug=True)
