from flask import Flask, request, jsonify, render_template
import pyotp
import json
import os
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE_FILE = 'users.txt'
users = []

def find_user(email):
    for user in users:
        if user['email'] == email:
            return user
    return None

# Load existing users
if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'r') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []

# 🔐 Funksion për gjenerimin e një hardware token (rastësor)
def generate_hardware_token(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/')
@app.route('/index1')
def index():
    return render_template('index1.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    if find_user(email):
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    totp = pyotp.TOTP(pyotp.random_base32())
    hardware_token = generate_hardware_token()

    new_user = {
        'email': email,
        'password': hashed_password,
        'totp_secret': totp.secret,
        'hardware_token': hardware_token
    }

    users.append(new_user)

    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({
        "message": "Registration successful",
        "totp_secret": totp.secret,
        "hardware_token": hardware_token  # opsionale, vetëm për shfaqje/testim
    })

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = find_user(email)
    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/setup_totp', methods=['POST'])
def setup_totp():
    email = request.form['email']
    user = find_user(email)
    if user:
        totp = pyotp.TOTP(user['totp_secret'])
        qr_url = totp.provisioning_uri(name=email, issuer_name="MyApp")
        return jsonify({"qr_url": qr_url})
    return jsonify({"message": "User not found"}), 404

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    email = request.form['email']
    code = request.form['code']
    method = request.form['method']

    user = find_user(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if method == 'totp':
        totp = pyotp.TOTP(user['totp_secret'])
        if totp.verify(code):
            return jsonify({"message": "2FA verified successfully"})
        else:
            return jsonify({"message": "Invalid TOTP code"}), 400

    elif method == 'hardware':
        if code == user['hardware_token']:
            return jsonify({"message": "2FA verified successfully"})
        else:
            return jsonify({"message": "Invalid hardware token code"}), 400

    return jsonify({"message": "Invalid 2FA method"}), 400

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
