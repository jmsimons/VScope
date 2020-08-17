#!/usr/bin/python3.5

import sys, os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message


# Load config #
config = {}
try:
    with open("vscope.conf") as f:
        items = [i for i in f.read().split('\n') if i != '']
        for item in items:
            k, v = item.split(':')
            if v == "False": v = False
            elif v == "True": v = True
            else:
                try: v = int(v)
                except: pass
            config[k] = v
except:
    print('Unable to load vscope.conf')


# Initialize Flask App #
if getattr(sys, 'frozen', False):
    root = sys._MEIPASS
    template_folder = os.path.join(root, 'webapp', 'templates')
    app = Flask(__name__, template_folder=template_folder)
    database_filepath = os.path.join(root, 'webapp', 'assets', 'webapp.db')
else:
    app = Flask(__name__)
    database_filepath = 'assets/webapp.db'

app.config['SECRET_KEY'] = 'cf808b01eca1b48b52ac925de441a16c'
if 'LOGIN_DISABLED' in config:
    app.config['LOGIN_DISABLED'] = config['LOGIN_DISABLED']
else:
    app.config['LOGIN_DISABLED'] = True


# Initialize User Database #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(database_filepath)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.googleemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

try:
    with open('email.creds') as f:
        data = f.read().split('\n')
        app.config['MAIL_USERNAME'] = data[0]
        app.config['MAIL_PASSWORD'] = data[1]
        print('Email Credentials Found')
except: print('No Email Credentials Found')


# User-management functions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_reset_email(user):
    token = user.get_reset_token()
    message = Message('Password Reset Request', sender = 'noreply@lcsc.edu', recipients = [user.email])
    body = 'To reset your password, visit the following link:\n{}\n\nIf you did not make this request then simply ignore this email and no change will be made.\n'
    message.body = body.format(url_for('reset_token', token = token, _external = True))
    mail.send(message)
    

# Imports that import objects from this script #
from webapp.routes import *
from webapp.models import User, Project
