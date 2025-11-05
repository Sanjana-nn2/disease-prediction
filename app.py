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

def add_user(username, password):
    users = load_users()
    if username in users:
        return False
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
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return render_template('dashboard.html', username=username)
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


@app.route('/tips/<disease>')
def health_tips(disease):
    if 'user' not in session:
        return redirect(url_for('login'))

    tips_dict = {
        'flu': ["Drink plenty of fluids.", "Get enough rest.", "Avoid contact with others.", "Take antiviral medications if prescribed.", "Maintain proper hygiene like frequent handwashing."],
        'malaria': ["Use mosquito nets while sleeping.", "Take prescribed antimalarial medications on time.", "Avoid mosquito-prone areas and stagnant water.", "Stay hydrated and rest adequately.", "Wear full-sleeved clothing to prevent mosquito bites."],
        'dengue': ["Avoid mosquito bites using nets, repellents, and long clothing.", "Stay hydrated and drink ORS if needed.", "Rest as much as possible.", "Monitor platelet counts regularly.", "Avoid self-medicating with painkillers like aspirin."],
        'typhoid': ["Drink safe, boiled, or filtered water.", "Maintain proper hand hygiene before eating.", "Eat freshly cooked, clean food.", "Take prescribed antibiotics completely.", "Avoid street food or unhygienic restaurants."],
        'urinary tract infection': ["Drink plenty of water to flush out bacteria.", "Urinate frequently and do not hold it for long.", "Maintain proper genital hygiene.", "Wear loose cotton clothing.", "Take prescribed antibiotics as directed by your doctor."],
        'viral fever': ["Take adequate rest and avoid stress.", "Drink fluids regularly.", "Use paracetamol if fever is high (as prescribed).", "Avoid cold drinks and heavy food.", "Consult a doctor if symptoms persist beyond a few days."],
        'common cold': ["Drink warm fluids like tea and soup.", "Rest and sleep well.", "Use saline nasal drops to relieve congestion.", "Avoid cold exposure and maintain room humidity.", "Wash hands frequently to prevent spreading infection."],
        'default': ["Maintain a balanced diet.", "Exercise regularly.", "Keep hygiene habits.", "Consult a doctor if symptoms worsen."]
    }

    tips = tips_dict.get(disease.lower(), tips_dict['default'])
    return render_template('health_tips.html', disease=disease, tips=tips)


@app.route('/index')
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

    x = [0] * len(cols)
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

    try:
        probs = model.predict_proba(x).tolist()[0]
    except Exception:
        probs = None

    return jsonify({'prediction': pred_label, 'probabilities': probs})

if __name__ == '__main__':
    app.run(debug=True)
