from flask import Flask, request, jsonify, render_template
import pyotp
import json
import os

app = Flask(__name__)

DATABASE_FILE = 'users.json'
users = []

# Lexo userat ekzistues nga skedari
if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'r') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []


@app.route('/')
def index():
    return render_template('index1.html')  # Sigurohu që index.html është në /templates/


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    # Kontrollo nëse user ekziston
    for user in users:
        if user['email'] == email:
            return jsonify({"message": "User already exists"}), 400

    # Gjenero TOTP sekretin
    totp = pyotp.TOTP(pyotp.random_base32())
    new_user = {
        'email': email,
        'password': password,
        'totp_secret': totp.secret
    }

    users.append(new_user)

    # Ruaj në skedar
    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"message": "Registration successful", "totp_secret": totp.secret})


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    for user in users:
        if user['email'] == email and user['password'] == password:
            # Return login success, but require TOTP verification
            return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401


@app.route('/setup_totp', methods=['POST'])
def setup_totp():
    email = request.form['email']

    for user in users:
        if user['email'] == email:
            totp = pyotp.TOTP(user['totp_secret'])
            qr_url = totp.provisioning_uri(name=email, issuer_name="MyApp")
            return jsonify({"qr_url": qr_url})

    return jsonify({"message": "User not found"}), 404


@app.route('/verify_totp', methods=['POST'])
def verify_totp():
    email = request.form['email']
    code = request.form['code']

    for user in users:
        if user['email'] == email:
            totp = pyotp.TOTP(user['totp_secret'])
            if totp.verify(code):
                return jsonify({"message": "TOTP verified successfully"})
            else:
                return jsonify({"message": "Invalid TOTP code"}), 400

    return jsonify({"message": "User not found"}), 404


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # Sigurohu që dashboard.html është në /templates/

if __name__ == '__main__':
    app.run(debug=True)
