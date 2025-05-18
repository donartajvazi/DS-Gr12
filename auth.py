from flask import Flask, request, jsonify, render_template
import pyotp
import json
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

DATABASE_FILE = 'users.txt'
users = []
def save_users():
    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def find_user(email):
    for user in users:
        if user['email'] == email:
            return user
    return None

if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'r') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []

@app.route('/')
@app.route('/user_access')
def user_access():
    return render_template('user_access.html')

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
        'totp_secret': totp.secret
    }

    users.append(new_user)
    save_users()

    return jsonify({
        "message": "Registration successful",
        "totp_secret": totp.secret
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

@app.route('/send_email_code', methods=['POST'])
def send_email_code():
    email = request.form['email']
    user = find_user(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    verification_code = str(random.randint(100000, 999999))

    if send_verification_code(email, verification_code):
        user['pending_code'] = verification_code
        return jsonify({"message": "Code sent"})
    else:
        return jsonify({"message": "Failed to send email code"}), 500

def send_verification_code(to_email, code):
    EMAIL_ADDRESS = "dion.haradinaj@student.uni-pr.edu"
    EMAIL_PASSWORD = "geus ezmz ihmd bime"

    msg = EmailMessage()
    msg['Subject'] = 'Kodi juaj i verifikimit'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f'Kodi juaj i verifikimit është: {code}')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email u dërgua me sukses!")
        return True
    except Exception as e:
        print(f'Dështoi dërgimi i emailit: {e}')
        return False

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

    elif method == 'email':
        if 'pending_code' in user and code == user['pending_code']:
            del user['pending_code']
            save_users()
            return jsonify({"message": "2FA verified successfully via email"})
        else:
            return jsonify({"message": "Invalid email verification code"}), 400

    return jsonify({"message": "Invalid 2FA method"}), 400

@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)