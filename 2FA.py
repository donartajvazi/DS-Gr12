from flask import Flask, request, jsonify, render_template
import pyotp
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE_FILE = 'users.json'
users = []

# Funksion ndihmës për gjetjen e userit sipas email
def find_user(email):
    for user in users:
        if user['email'] == email:
            return user
    return None

# Lexo userat ekzistues nga skedari
if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'r') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []

@app.route('/')
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

    new_user = {
        'email': email,
        'password': hashed_password,
        'totp_secret': totp.secret,
        'hardware_token': None  # fillimi pa hardware token
    }

    users.append(new_user)

    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"message": "Registration successful", "totp_secret": totp.secret})

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
    method = request.form['method']  # 'totp' ose 'hardware'

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
        # Hardware token thjesht kontrollon nese kodi eshte i barabarte me token-in e ruajtur
        if user['hardware_token'] and code == user['hardware_token']:
            return jsonify({"message": "2FA verified successfully"})
        else:
            return jsonify({"message": "Invalid hardware token code"}), 400

    else:
        return jsonify({"message": "Invalid 2FA method"}), 400

@app.route('/register_hardware_token', methods=['POST'])
def register_hardware_token():
    email = request.form['email']
    hardware_token = request.form['hardware_token']

    user = find_user(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    user['hardware_token'] = hardware_token

    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"message": "Hardware token registered successfully"})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
