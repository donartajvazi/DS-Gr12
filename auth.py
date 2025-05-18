from flask import Flask, request, jsonify, render_template
import pyotp
import json
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

def save_users():
    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

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

@app.route('/send_email_code', methods=['POST'])
def send_email_code():
    email = request.form['email']
    user = find_user(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

