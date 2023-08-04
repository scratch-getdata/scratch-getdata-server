from flask import render_template, send_file, request, redirect, session, make_response, flash, current_app
from flask import Flask, jsonify
from flask import abort
from flask import url_for
from flask_sock import Sock
from flask_socketio import SocketIO, emit, send
from flask_jwt_extended import create_access_token, jwt_required, decode_token
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_autoindex import AutoIndex
import json
from base64 import b64encode
import smtplib
from flask_cors import CORS, cross_origin
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz
import io
import os
import re
import time
import signal
from threading import Thread
import sys
import string
import random
import secrets
import sqlite3
import requests
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
from bs4 import BeautifulSoup
from PIL import Image
from requests.exceptions import RequestException
from colorama import Fore, Back, Style
from flask.sessions import SecureCookieSessionInterface
import hashlib
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_jwt_extended import JWTManager
import extra.decrypt_database
import extra.encrypt_database
import ServerFiles.email_send

#Calculate Uptime

start_time = datetime.utcnow()

def calculate_uptime(start_time):
    current_time = datetime.utcnow()
    uptime = current_time - start_time

    # Calculate days, hours, minutes, and seconds
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Create the uptime string
    uptime_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    return uptime_str

# Function to get the current time in UTC and convert it to string format
def get_current_time_str():
    now = datetime.utcnow()
    return now.strftime('%Y-%m-%d %H:%M:%S')



uptime_str = calculate_uptime(start_time)

print(f"Uptime: {uptime_str}")


# Args

nowarning = False
nodebug = False

try:

  if 'no-warning' in sys.argv:
      nowarning = True
      print(Fore.BLUE + "Warning Disabled!" + Fore.RESET)
  elif os.environ['no-warning'] == 'true':
      nowarning = True
      print(Fore.BLUE + "Warning Disabled!" + Fore.RESET)

  if 'no-debug' in sys.argv:
      nodebug = True
      print(Fore.BLUE + "Debug logs Disabled!" + Fore.RESET)
  elif os.environ['debug'] == 'false':
      nodebug = True
      print(Fore.BLUE + "Debug logs Disabled!" + Fore.RESET)

except:
  nodebug = True
  nowarning = True


  

def signal_handler(signal, frame):
    if nodebug == False:
      print("QUIT Signal Recived.")
      print("Closing Database")
    try:
      if reencrypt_database == 'true':
        if nodebug == False:
          print("Encrypting the database")
        extra.encrypt_database.encrypt_file()
      else:
        if nodebug == False:
          print("Leaving Database Unencrypted")

    except:
      pass

    print("Gracefully shutdown complete.")
    sys.exit(0)

# Register the signal_handler function to be called only on SIGINT (Ctrl+C)
try:
    # Set the signal handler only for SIGINT (Ctrl+C) signal
    signal.signal(signal.SIGINT, signal_handler)
except (OSError, RuntimeError):
    pass

#Decrypt Database

try:
  if nodebug == False:
    print("Loading Database.")
  extra.decrypt_database.decrypt_file()
  if nodebug == False:
    print("Database has been decrypted!")
  reencrypt_database = 'true'
except ValueError:
  if nodebug == 'false':
    print("Database is not encrypted! loading directly without decrypting.")
  if nowarning == False:
    print(Fore.YELLOW + "Warning: Not encrypting database gives you risk of password, username, api key stolen of your users. To encrypt the database run 'python extra/encrypt_my_database.py' in your teminal." + Fore.RESET)
  reencrypt_database = 'false'
  pass
#Required Settings

server_version = "1.0.2"
server_channel = "autoupdate"

# Check for updates

def check_for_updates():
    try:
        params = {
            "update": 'scratch-getdata',
            "channel": server_channel
        }
      
        response = requests.get("https://kokofixcomputers-update-server.kokoiscool.repl.co/check/update", params=params)
        if response.status_code == 200:
            update_data = json.loads(response.text)
            if update_data.get("version"):
              if update_data.get("version") == server_version:
                update_status = "UpToDate"
                latest_version = update_data.get("version")
                time.sleep(1)
                if nodebug == 'false':
                  print(Fore.BLUE + "Server version: " + server_version, Fore.RESET)
                  print(Fore.BLUE + "Latest Version: " + update_data.get("version") + Fore.RESET)
                return "uptodate"
              else:
                  update_status = "NotUpToDate"
                  latest_version = update_data.get("version")
                  return "not-uptodate"
            else:
              return "error"
                
            return update_data.get("version", "No update information available.")
        else:
            return "Unable to fetch update information from the server."

    except Exception as e:
        return f"An error has occurred while trying to check for updates: {e}"

print(check_for_updates())

params = {
    "update": 'scratch-getdata',
    "channel": server_channel
        }

response = requests.get("https://kokofixcomputers-update-server.kokoiscool.repl.co/check/update", params=params)
update_data = json.loads(response.text)
latest_version = update_data.get("version")

#Set timezone
vancouver_tz = pytz.timezone('America/Vancouver')
now = datetime.now(vancouver_tz)

def base64(string):
    return b64encode(string.encode("utf-8")).decode()


# Reqire Generate

def generate_random_string(length):
    characters = string.ascii_letters + string.digits + "_"
    random_string = ''.join(random.choice(characters) for _ in range(length))
    while random_string.startswith('_') or random_string.endswith('_'):
        random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

# init

app = Flask(__name__)
sock = Sock(app)
app.config['JWT_SECRET_KEY'] = '1QGz0JZvqsNJg0Mp2o'  # Change this!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'Token'
app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'CSRF-TOKEN'
app.config['JWT_ACCESS_CSRF_FIELD_NAME'] = 'csrf_token'
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_IN_COOKIES'] = True
app.config['SECRET_KEY'] = 'dumb_secret_key_haha!'
app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
DATABASE_PATH_FOR_BLAHBLAH = os.path.abspath('users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH_FOR_BLAHBLAH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/static/*": {"origins": "scratch-get-data.kokoiscool.repl.co"}})

db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins='*')

flask_session_encryption = generate_random_string(15)
app.secret_key = flask_session_encryption

class CustomSessionInterface(SecureCookieSessionInterface):
    digest_method = staticmethod(hashlib.sha256)

app.session_interface = CustomSessionInterface()

class Strings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string = db.Column(db.String(32), unique=True)
    created = db.Column(db.TIMESTAMP)

def delete_expired_sessions():
    with app.app_context():
        now = datetime.utcnow()
        expired_sessions = Strings.query.filter(Strings.created < now - timedelta(minutes=5)).all()
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()

scheduler.add_job(func=delete_expired_sessions, trigger='interval', minutes=1)
scheduler.start()

time.sleep(1)

if nodebug == 'false':
  print(Fore.GREEN + "Flask Initialized." + Fore.RESET)

DATABASE_NAME = 'users.db'

requests_left = 'Infinity'

#Email
def get_subscribed_emails():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('SELECT email FROM email_subscribed_users')
    emails = [row[0] for row in c.fetchall()]
    conn.close()
    return emails

def send_email(subject, body, recipients):
    msg = MIMEMultipart()
    msg['From'] = os.environ['email_username']
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(os.environ['email_server'], 587)
    server.starttls()
    server.login(os.environ['email_username'], os.environ['email_password'])
    server.sendmail(os.environ['email_username'], recipients, msg.as_string())
    server.quit()

def read_updates_from_file():
    with open('updates-email.txt', 'r') as file:
        updates = file.read()
    return updates


def sendupdateemail():
    try:
        subject = 'New Update!'
        body = '''
<!DOCTYPE html>
<html>
<head>
      /* Reset styles */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    /* Global styles */
    body {
      font-family: Arial, sans-serif;
      font-size: 16px;
      line-height: 1.5;
      color: #333;
      background-color: #f5f5f5;
    }
    
    /* Container styles */
    .container {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #fff;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styles */
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    
    .header h1 {
      font-size: 36px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
    }
    
    .header p {
      font-size: 18px;
      color: #666;
      margin-bottom: 10px;
    }
    
    /* Button styles */
    .button {
      display: inline-block;
      padding: 10px 20px;
      background-color: #007bff;
      color: #fff;
      font-size: 18px;
      font-weight: bold;
      text-decoration: none;
      border-radius: 5px;
      transition: background-color 0.3s ease;
    }
    
    .button:hover {
      background-color: #0062cc;
    }
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Subscriber</h1>
      <p>Dear subscriber,</p>
      <p>There is a new update!</p>
      <br>
      <p>Updates:</p>
      <p>{update}</p>
    </div>
    <p>Best regards,</p>
    <p>Your Website Team</p>
    <a class="button" href="https://scratch-get-data.kokoiscool.repl.co">Visit Website</a>
  </div>
</body>
</html>
'''

        # Read updates from the file
        updates = read_updates_from_file()

        # Replace the {update} placeholder in the email body with the actual updates
        body = body.format(update=updates)

        # Get the subscribed emails from the database
        recipients = get_subscribed_emails()

        if not recipients:
            return jsonify({'message': 'No subscribers found!'})

        # Send the update email to all subscribed users
        send_email(subject, body, recipients)

        return jsonify({'message': 'Update emails sent successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)})


def sendemailforupdate():
    try:
        subject = 'Subscribed!'
        body = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Reset styles */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    /* Global styles */
    body {
      font-family: Arial, sans-serif;
      font-size: 16px;
      line-height: 1.5;
      color: #333;
      background-color: #f5f5f5;
    }
    
    /* Container styles */
    .container {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #fff;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styles */
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    
    .header h1 {
      font-size: 36px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
    }
    
    .header p {
      font-size: 18px;
      color: #666;
      margin-bottom: 10px;
    }
    
    /* Button styles */
    .button {
      display: inline-block;
      padding: 10px 20px;
      background-color: #007bff;
      color: #fff;
      font-size: 18px;
      font-weight: bold;
      text-decoration: none;
      border-radius: 5px;
      transition: background-color 0.3s ease;
    }
    
    .button:hover {
      background-color: #0062cc;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Subscriber</h1>
      <p>Dear subscriber,</p>
      <p>We are excited to share with you our latest update. Thank you for staying connected with us!</p>
    </div>
    <p>Best regards,</p>
    <p>Your Website Team</p>
    <a class="button" href="https://scratch-get-data.kokoiscool.repl.co">Visit Website</a>
  </div>
</body>
</html>
'''

        
        # Get the subscribed emails from the database
        recipients = get_subscribed_emails()

        if not recipients:
            return jsonify({'message': 'No subscribers found!'})

        # Send the update email to all subscribed users
        send_email(subject, body, recipients)

        return jsonify({'message': 'Update emails sent successfully!'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

def sendemailtorec(recipient_email, verifycode):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = 'kokocanfixit@kokofixcomputers.serv00.net'
    msg['To'] = recipient_email
    msg['Subject'] = 'Scratch-GetData Signup'
    print(recipient_email)
    # Create the HTML content of the email
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to Scratch-GetData</title>
  <style>
    /* Reset styles */
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    
    /* Global styles */
    body {{
      font-family: Arial, sans-serif;
      font-size: 16px;
      line-height: 1.5;
      color: #333;
      background-color: #f5f5f5;
    }}
    
    /* Container styles */
    .container {{
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #fff;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }}
    
    /* Header styles */
    .header {{
      text-align: center;
      margin-bottom: 20px;
    }}
    
    .header h1 {{
      font-size: 36px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
    }}
    
    .header p {{
      font-size: 18px;
      color: #666;
      margin-bottom: 10px;
    }}
    
    /* Button styles */
    .button {{
      display: inline-block;
      padding: 10px 20px;
      background-color: #007bff;
      color: #fff;
      font-size: 18px;
      font-weight: bold;
      text-decoration: none;
      border-radius: 5px;
      transition: background-color 0.3s ease;
    }}
    
    .button:hover {{
      background-color: #0062cc;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to Scratch-GetData</h1>
      <p>Your most accurate source for getting Scratch data.</p>
    </div>
    <p>Dear valued user,</p>
    <br>
    <p>Thank you for choosing Scratch-GetData for your data needs. We are excited to have you on board and look forward to helping you achieve your goals.</p>
    <br>
    <p>If you have any questions or concerns, please don't hesitate to contact us.</p>
    <br>
    <p>Your verification code: {verifycode}</p>
    <br>
    <p>Links:</p>
    <a href="https://scratch-get-data.kokoiscool.repl.co/dashboard" class="button">Dashboard</a>
    <br>
    <a href="https://scratch-get-data.kokoiscool.repl.co" class="button">Home page</a>
    <br>
    <a href="https://scratch-get-data.kokoiscool.repl.co/docs" class="button">Docs</a>
    <br>
    <p>Use the sidebar on the homepage to see more links.</p>
    <br>
    <p>Best regards,</p>
    <p>The Scratch-GetData team</p>
  </div>
</body>
</html>
    '''

    # Attach the HTML content to the message
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    # Send the email
    smtp = smtplib.SMTP(os.environ['email_server'])
    smtp.login(os.environ['email_username'], os.environ['email_password'])
    smtp.send_message(msg)
    smtp.quit()

    print('Verification code sent to ' + recipient_email)

def send_otp_email(email, otp):
    # Replace the placeholders with your email credentials and settings
    smtp_server = os.environ['email_server']
    smtp_port = 587
    smtp_username = os.environ['email_username']
    smtp_password = os.environ['email_password']
    
    # Create a multipart email message
    msg = MIMEMultipart()
    msg['Subject'] = 'OTP Verification'
    msg['From'] = 'kokocanfixit@kokofixcomputers.serv00.net'
    msg['To'] = email
    
    # Load the email template from a file
    with open('otp_email_template.html', 'r') as file:
        template = file.read()

    # Replace the placeholder with the actual OTP
    email_body = template.replace('{{ otp }}', otp)
    
    # Create the email body (HTML format)
    html_part = MIMEText(email_body, 'html')
    msg.attach(html_part)

    # Connect to the SMTP server and send the message
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
    print("OTP Code sent to" + email)

def create_database():
    # Check if the database file exists
    if not os.path.exists(DATABASE_NAME):
        # Create a new database
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Create the users table
        c.execute('CREATE TABLE users (userid INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password_hash TEXT)')
        
        # Close the database connection
        conn.close()
    else:
        # Connect to the existing database
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Check if the users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = c.fetchone()
        
        if not result:
            # Create the users table
            c.execute('CREATE TABLE users (userid INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password_hash TEXT)')
        
        # Close the database connection
        conn.close()

create_database()

# Generate

def generate_userid(max_attempts=10):
    for _ in range(max_attempts):
        user_id = random.randint(1000, 999999999)
        c.execute('SELECT COUNT(*) FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        if result[0] == 0:
            return user_id
    # If max_attempts is reached without finding a unique user ID
    raise Exception("Failed to generate a unique user ID")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

@app.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    return redirect(url_for('login', afterlogin=request.path))

@app.context_processor
def inject_cors_headers():
    def add_cors_headers():
        response = current_app.make_response()
        response.headers['Access-Control-Allow-Origin'] = 'scratch-get-data.kokoiscool.repl.co'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    return dict(add_cors_headers=add_cors_headers)


@app.before_request
def check_key():
    if '/get' in request.path:
        # Get the random key from the query string
        random_key = request.args.get('key')

        # Connect to SQLite database
        conn = sqlite3.connect('users.db')

        # Bypass the key check if random_key is None
        if random_key is None:
            return render_template('nokeyprovided.html')

        # Check if the key is in the database
        c = conn.cursor()
        c.execute('SELECT * FROM keys WHERE key = ?', (random_key,))
        result = c.fetchone()

        # If the key is not found, bypass the key check
        if result is None:
            c.execute('SELECT * FROM specialAccounts WHERE key = ?', (random_key,))
            result = c.fetchone()
            if result is None:
                return render_template('keynotfound.html')

        # Get the user ID from the session
        c.execute('SELECT userid FROM keys WHERE key = ?', (random_key,))
        try:
            user_id = c.fetchone()[0]  # Extract the value from the tuple
            specialAccount = 'false'
        except TypeError:
            specialAccount = 'true'
            c.execute('SELECT userid FROM specialAccounts WHERE key = ?', (random_key,))
            user_id = c.fetchone()[0]

        # Get the current date in 'YYYY-MM-DD' format
        now = datetime.utcnow()
        now_str = now.strftime('%Y-%m-%d')

        if specialAccount == 'true':
            # Update the requests column in specialAccounts table
            c.execute('UPDATE specialAccounts SET request = (SELECT COALESCE(request, 0) + 1 FROM specialAccounts WHERE userid = ?) WHERE userid = ?', (user_id, user_id))
            conn.commit()

            # Check if there is an entry for the current date in request_count_scratch
            c.execute('SELECT requests_count FROM request_count_scratch WHERE userid = ? AND date = ?', (user_id, now_str))
            current_requests_count = c.fetchone()

            if current_requests_count:
                # If an entry exists for the current date, update the count
                current_count = current_requests_count[0]
                new_count = current_count + 1
                c.execute('UPDATE request_count_scratch SET requests_count = ? WHERE userid = ? AND date = ?', (new_count, user_id, now_str))
                conn.commit()
            else:
                # If no entry exists for the current date, insert a new row
                c.execute('INSERT INTO request_count_scratch (userid, date, requests_count) VALUES (?, ?, 1)', (user_id, now_str))
                conn.commit()

        else:
            # Update the count column in requests table
            c.execute('UPDATE requests SET count = (SELECT COALESCE(count, 0) + 1 FROM requests WHERE userid = ?) WHERE userid = ?', (user_id, user_id))
            conn.commit()

            # Check if there is an entry for the current date in request_chart
            c.execute('SELECT requests_count FROM request_chart WHERE userid = ? AND date = ?', (user_id, now_str))
            current_requests_count = c.fetchone()

            if current_requests_count:
                # If an entry exists for the current date, update the count
                current_count = current_requests_count[0]
                new_count = current_count + 1
                c.execute('UPDATE request_chart SET requests_count = ? WHERE userid = ? AND date = ?', (new_count, user_id, now_str))
                conn.commit()
            else:
                # If no entry exists for the current date, insert a new row
                c.execute('INSERT INTO request_chart (userid, date, requests_count) VALUES (?, ?, 1)', (user_id, now_str))
                conn.commit()

        conn.close()



# Require Define Functions:

def get_scratch_data(url):
    proxy_url = 'https://jungle-strengthened-aardvark.glitch.me/get/'
    proxy_url_backup = 'https://vnmppd-5000.csb.app/scratch_proxy/'
    proxy_super_backup = 'https://thingproxy.freeboard.io/fetch/'
    proxied_url = proxy_url_backup + url
    try:
      response = requests.get(proxied_url)
      response.raise_for_status()
    except requests.exceptions.HTTPError as err:
      if response.status_code == 429:
          print("Too Many Requests")
          proxied_url = proxy_url + url
          try:
            response = requests.get(proxied_url)
            response.raise_for_status()
          except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
              proxied_url = proxy_url + url
              try:
                response = requests.get(proxied_url)
                response.raise_for_status()
              except requests.exceptions.HTTPError as err:
                if response.status_code == 429:
                  response = ServerFiles.proxy.send(url)
            
      else:
          pass

    try:
        return json.loads(response.text)
    except ValueError:
        try:
            return int(response.text)
        except ValueError:
            return response.text

def get_scratch_data_wiwo(url):
    response_text = response.text
    try:
      response = requests.get(url)
      response.raise_for_status()
    except requests.exceptions.HTTPError as err:
      proxy_url = 'https://jungle-strengthened-aardvark.glitch.me/get/'
      proxy_url_backup = 'https://vnmppd-5000.csb.app/scratch_proxy/'
      proxy_super_backup = 'https://thingproxy.freeboard.io/fetch/'
      proxied_url = proxy_url_backup + url
      try:
        response = requests.get(proxied_url)
        response.raise_for_status()
      except requests.exceptions.HTTPError as err:
        if response.status_code == 429:
          proxied_url = proxy_url + url
          try:
           response = requests.get(proxied_url)
           response.raise_for_status()

          except requests.exceptions.HTTPError as err:
           if response.status_code == 429:
              proxied_url = proxy_super_backup + url
              try:
                response = requests.get(proxied_url)
                response.raise_for_status()
              except requests.exceptions.HTTPError as err:
                if response.status_code == 429:
                  response = ServerFiles.proxy.send(url)
            
      

    try:
        parsed_data = response.json()  # Try parsing the response content as JSON
        return parsed_data  # Return the JSON data as-is
    except Exception as e:
        print("Failed to parse:", e)
        return None

def get_scratch_data_nojson(url):
    proxy_url = 'https://jungle-strengthened-aardvark.glitch.me/get/'
    proxy_url_backup = 'https://vnmppd-5000.csb.app/scratch_proxy/'
    proxy_super_backup = 'https://thingproxy.freeboard.io/fetch/'
    proxied_url = proxy_url_backup + url
    try:
      response = requests.get(proxied_url)
      response.raise_for_status()
    except requests.exceptions.HTTPError as err:
      if response.status_code == 429:
        proxied_url = proxy_url + url
        try:
          response = requests.get(proxied_url)
          response.raise_for_status()
        except requests.exceptions.HTTPError as err:
          if response.status_code == 429:
            try:
              proxied_url = proxy_super_backup + url
              response = requests.get(proxied_url)
              response.raise_for_status()
            except requests.exceptions.HTTPError as err:
              if response.status_code == 429:
               response = ServerFiles.proxy.send(url)
              
    print("Response content:", response.text)  # Print the response content

    return response

print(Fore.GREEN + "Important functions defined." + Fore.RESET)


# Flask routes and non important definitions


@app.route('/')
def home():
   message = request.args.get('message')
   status = request.args.get('status')
   if message is None:
     return render_template('index.html')
   else:
     if status is None:
       return render_template('index.html', message=message)
     else:
       return render_template('index.html', message=message, status=status)

@app.route('/googlea2534a03c1e2febf.html')
def googleverify():
  return render_template('googlea2534a03c1e2febf.html')
  

@app.route('/settings')
def settings():
    # Logic for the settings page
    return render_template('settings.html')

@app.route('/otp/email/')
def otp_email():
    # Logic for the settings page
    return render_template('otp_email.html')

@app.route('/redirecttohome')
def redirecttohome():
    para1 = request.args.get('para1')
    para2 = request.args.get('para2')
    # Logic for the settings page
    return render_template('gotohome.html', para1='message', para1value=para1, para2='status', para2value=para2)

@app.route('/sidebartest/')
def homesidebar():
   return render_template('indexsidebar.html')

@app.route('/issue/')
def issue():
   return render_template('problems.html')

@app.route('/updates/')
def update():
    with open('static/updates.txt', 'r') as f:
        updates_content = f.readlines()
    return render_template('updates.html', updates=updates_content)

@app.route('/updates/test/')
def updatet():
   return render_template('update-test.html')

@app.route('/contact/')
def contact():
   return render_template('contact.html')

@app.route('/install/')
def install():
   return render_template('install.html')

@app.route('/why/')
def why():
   return render_template('why.html')

@app.route('/python/docs/')
def pythondocs():
   return render_template('python-docs.html')

@app.route('/docs')
def udocs():
   return render_template('docs.html')

@app.route('/sub-test', subdomain="static")
def sub_test():
  return "Hellp"

@app.route("/get/follower-count/<username>/")
def count(username):
    try:
        #response = requests.get(f"http://jungle-strengthened-aardvark.glitch.me/followers/{username}")
        response = requests.get(f"https://vnmppd-5000.csb.app/followers/{username}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if isinstance(data, int):
                return str(data)
            else:
                return "Invalid response"
        elif response.status_code == 404:
            return "User does not exist"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/is_scratcher/<username>/")
def is_scratcher(username):
    url = f"https://scratch.mit.edu/users/{username}/"
    response = get_scratch_data_nojson(url)

    if isinstance(response, bytes):
        response = response.decode("utf-8")  # Convert bytes to string

    print(f"Response: {response}")  # Add this line to print the response

    content = response.text  # Extract the content from the Response object
    soup = BeautifulSoup(content, "html.parser")
    status_tag = soup.select_one('.group')  # Updated CSS selector

    if status_tag:
        status = status_tag.text.strip()
        print(status)
        result = status
    else:
        status = "Unknown"
        print(f"Status: {status}")  # Print the status when the status_tag is not found
        result = status
    try:
        return json.dumps(result)
    except:
        print(Exception)
        return(Exception)

    #return str(is_scratcher)


@app.route("/get/is_scratcher/<username>/test/")
def is_scratcher2(username):
    url = f"https://scratch.mit.edu/users/{username}/"
    response = get_scratch_data_nojson(url)

    if isinstance(response, bytes):
        response = response.decode("utf-8")  # Convert bytes to string

    print(f"Response: {response}")  # Add this line to print the response

    content = response.text  # Extract the content from the Response object
    soup = BeautifulSoup(content, "html.parser")
    status_tag = soup.select_one('.group')  # Updated CSS selector

    if status_tag:
        status = status_tag.text.strip()
        print(status)
        result = {"Status": status}
    else:
        status = "Unknown"
        print(f"Status: {status}")  # Print the status when the status_tag is not found
        result = {"Status": status}
    try:
        return json.dumps(result)
    except:
        print(Exception)
        return(Exception)

@app.route("/get/following-count/<username>/")
def following(username):
    try:
        #response = requests.get(f"http://jungle-strengthened-aardvark.glitch.me/following/{username}")
        response = requests.get(f"https://vnmppd-5000.csb.app/following/{username}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if isinstance(data, int):
                return str(data)
            else:
                return "Invalid response"
        elif response.status_code == 404:
            return "User does not exist"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/wiwo/<username>/")
def wiwo(username):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/users/{username}'
        response_data = get_scratch_data(url.format(username=username))

        if response_data is not None:
            profile = response_data.get("profile", {})
            work = profile.get("status", "")
            return work.replace("\n", " ")
        else:
            abort(404)
            return "Invalid response or user not found"
    except requests.exceptions.RequestException as e:
        print(e)
        abort(404)
        return f"An error occurred: {str(e)}"


@app.route("/get/aboutme/<username>/")
def about_me(username):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/users/{username}'
        response_data = get_scratch_data(url.format(username=username))

        if response_data is not None:
            if "code" in response_data and response_data["code"] == "NotFound":
                abort(404)
                return "User does not exist"
            elif "username" in response_data and "profile" in response_data:
                about_me_text = response_data["profile"].get("bio", "")
                return about_me_text
            else:
                return "Invalid response structure"
        else:
            return "No data received"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"



@app.route("/get/messages/<username>/")
def get_messages(username):
    try:
        response = requests.get(f"https://explodingstar.pythonanywhere.com/scratch/user/messages/{username}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.text:
            try:
                data = json.loads(response.text)
                count = data["count"]
                return str(count)
            except (json.decoder.JSONDecodeError, KeyError):
                abort(404)
                return "Invalid response structure"
        else:
            return "No data received"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/project/creator/<project_id>/")
def project_creator(project_id):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/projects/{project_id}'
        response_data = get_scratch_data(url.format(project_id=project_id))

        if response_data is not None:
            if "author" in response_data and "username" in response_data["author"]:
                creator = response_data["author"]["username"]
                return creator
            else:
                return "Project creator not found"
        else:
            abort(404)
            return "Project not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"



@app.route("/get/project/name/<project_id>/")
def project_name(project_id):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/projects/{project_id}'
        response_data = get_scratch_data(url.format(project_id=project_id))

        if response_data is not None:
            if "title" in response_data:
                name = response_data["title"]
                return name
            else:
                return "Project name not found"
        else:
            abort(404)
            return "Project not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"



@app.route("/get/project/notes_and_credits/<project_id>/")
def project_notes_and_credits(project_id):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/projects/{project_id}'
        response_data = get_scratch_data(url.format(project_id=project_id))

        if response_data is not None:
            if "description" in response_data:
                description = response_data["description"]
                return description.strip()  # Return the description as-is
            else:
                return "Project description not found"
        else:
            abort(404)
            return "Project not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/project/instructions/<project_id>/")
def project_instructions(project_id):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/projects/{project_id}'
        response_data = get_scratch_data(url.format(project_id=project_id))

        if response_data is not None:
            if "instructions" in response_data:
                instructions = response_data["instructions"]
                return instructions.strip()  # Return the instructions as-is
            else:
                return "Project instructions not found"
        else:
            abort(404)
            return "Project not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/blocks/<project_id>/")
def project_blocks(project_id):
    try:
        response = requests.get(
            f"https://scratchdb.lefty.one/v3/project/info/{project_id}"
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            if "error" in data:
                error_message = data["error"]
                if error_message == "ProjectNotFoundError":
                    abort(404)
                    return "Project not found"
                elif error_message == "UserNotValidError":
                    abort(404)
                    return "Invalid user"
                else:
                    return "Error: " + error_message
            elif "metadata" in data and "blocks" in data["metadata"]:
                blocks = data["metadata"]["blocks"]
                return str(blocks)
            else:
                return "Number of blocks not found"
        elif response.status_code == 404:
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/forum/title/<post_id>/")
def forum_title(post_id):
    try:
        response = requests.get(
            f"https://scratchdb.lefty.one/v3/forum/topic/info/{post_id}"
        )
        print(response.status_code)
        print(response.content)
        if response.status_code == 200:
            data = json.loads(response.text)
            if "error" in data:
                error_message = data["error"]
                if error_message == "PostNotFoundError":
                    abort(404)
                    return "Post not found"
                elif error_message == "PostNotValidError":
                    abort(404)
                    return "Invalid post ID"
            elif "title" in data and data["title"] is not None:
                title = data["title"]
                return title
                abort(404)
        return "Username not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/static/issue.txt")
def get_issue():
    # Verify the password in the header
    password = request.headers.get('Allow-Main-Only')
    protect = request.headers.get('Allow-Orgin')
    if password != 'superlongpassword':
        abort(401)
    if protect != 'https://scratch-get-data.kokoiscool.repl.co':
      abort(401)

    # Return the issue.txt file
    return send_file('static/issue.txt')


@app.route("/get/forum/category/<post_id>/")
def forum_category(post_id):
    try:
        response = requests.get(
            f"https://scratchdb.lefty.one/v3/forum/topic/info/{post_id}"
        )
        print(response.status_code)
        print(response.content)
        if response.status_code == 200:
            data = json.loads(response.text)
            if "error" in data:
                error_message = data["error"]
                if error_message == "TopicNotFoundError":
                    abort(404)
                    return "Post not found"
                elif error_message == "TopicNotValidError":
                    abort(404)
                    return "Invalid post ID"
            elif "category" in data and data["category"] is not None:
                category = data["category"]
                return category
        return "Username not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/user/country/<username>/")
def scratch_user_country(username):
    try:
        response = requests.get(
            f"https://explodingstar.pythonanywhere.com/scratch/user/profile/{username}"
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            if "country" in data["profile"]:
                country = data["profile"]["country"]
                return country
            else:
                return "Country information not available"
        elif response.status_code == 404:
            abort(404)
            return "User does not exist"
        else:
            return "Failed to retrieve user profile"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/ocular/user/status/<username>/")
def user_status(username):
    url = f"https://my-ocular.jeffalo.net/api/user/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        status = data["status"]
        return status
    else:
        abort(404)
        return jsonify({"error": "User not found"})

@app.route("/get/ocular/user/color/<username>/")
def user_color(username):
    url = f"https://my-ocular.jeffalo.net/api/user/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data and data["error"] == "no user found":
            abort(404)
            return jsonify({"error": "User not found"}), 404
        else:
            status = data["color"]
            return status
    else:
        abort(response.status_code)

@app.route("/get/ocular/user/updated_time/<username>/")
def user_updater(username):
    url = f"https://my-ocular.jeffalo.net/api/user/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data and data["error"] == "no user found":
            abort(404)
            return jsonify({"meta": {"error": "User not found"}, "data": None}), 404
        else:
            updated = data["meta"]["updated"]
            return jsonify(updated)
    else:
        abort(response.status_code)


@app.route("/get/user/profilepic/<size>/<username>/")
def profile_pic(size, username):
    try:
        image_url = f"https://scratchimagedatabase.kokoiscool.repl.co/user/{size}/{username}.png"
        response = requests.get(image_url)
        
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            return send_file(image_data, mimetype='image/png')
        elif response.status_code == 404:
            abort(404)
            return "User does not exist"
        else:
            return "Failed to retrieve user profile"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/studio/title/<studioid>/")
def studio_title(studioid):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/studios/{studioid}'
        response_data = get_scratch_data(url.format(studioid=studioid))

        if response_data is not None:
            if "title" in response_data:
                title = response_data["title"]
                return title
            else:
                return "Studio title not found"
        else:
            abort(404)
            return "Studio not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/studio/description/<studioid>/")
def studio_description(studioid):
    try:
        # Call the get_scratch_data function to get the JSON data
        url = 'https://api.scratch.mit.edu/studios/{studioid}'
        response_data = get_scratch_data(url.format(studioid=studioid))

        if response_data is not None:
            if "description" in response_data:
                description = response_data["description"]
                return description
            else:
                return "Studio description not found"
        else:
            return "Studio not found"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route('/get/studio/count_curators/<studioid>')
def count_curators(studioid):
    url = f"https://api.scratch.mit.edu/studios/{studioid}/curators"
    data = get_scratch_data(url)

    if isinstance(data, list):
        count = sum(1 for curator in data if 'username' in curator.keys())
    else:
        count = 0

    return str(count)

@app.route('/get/studio/count_managers/<studioid>')
def count_managers(studioid):
    url = f"https://api.scratch.mit.edu/studios/{studioid}/managers"
    data = get_scratch_data(url)

    try:

        if isinstance(data, list):
            count = sum(1 for manager in data if 'username' in manager.keys())
        else:
            count = 0

        return str(count)
    except:
        abort(404)

@app.route('/get/user/non-processed/<username>/')
def get_non_proccessed_username(username):
    try:
      url = f"https://api.scratch.mit.edu/users/{username}"
      data = get_scratch_data(url)
      return jsonify(data)
    except:
      abort(404)

@app.route('/get/project/non-processed/<projectid>/')
def get_non_proccessed_project(projectid):
    try:
      url = f"https://api.scratch.mit.edu/projects/{projectid}"
      data = get_scratch_data(url)
      return jsonify(data)
    except:
      abort(404)
  
@app.route('/get/user/user-exist/<user>/')
def checkuseralive(user):
    url = 'https://api.scratch.mit.edu/accounts/checkusername/' + user
    data = get_scratch_data(url)
    print(data)

    if data['msg'] != 'username exists':
        return "false"
    else:
        return "true"

@app.route('/get/user/last_follower/<username>/')
def last_follower(username):
    url = f"https://api.scratch.mit.edu/users/{username}/followers/?limit=1&offset=0"
    response = get_scratch_data(url)

    try:
        if isinstance(response, list) and len(response) > 0:
            last_follower = response[0]['username']
        else:
            last_follower = "No followers"
    except (KeyError, TypeError):
        last_follower = "Error retrieving last follower"

    return last_follower




#Internel commands (Is not public)

@app.route("/internal/restart")
def restart():
    provided_secret = request.args.get("string")

    # If the string parameter does not exist, use the Authorization header
    if not provided_secret:
        provided_secret = request.headers.get('Authorization')

    if provided_secret == os.environ['internal_secret'] and request.path == "/internal/restart":
        # Return the "Restarting..." message
        os.kill(os.getpid(), 9)
        return "Restarting..."
    else:
        abort(401)

@app.route("/internal/")
def internel_error():
  abort(401)

#Testing use only


@app.route("/get/ip/", methods=["GET", "POST"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200



@app.route("/internal/auth-only", methods=["GET", "POST", "KOKOAUTH"])
def auth_only():
    auth = request.authorization
    if not auth or auth.username != 'example' or auth.password != os.environ['internal_secret']:
        abort(401)
    return "Authenticated successfully"

#Accounts

#Accounts and login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        afterlogin = request.args.get('afterlogin', '').lstrip('/')
        if username != 'admin':
        
        # Connect to the users.db database
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
        
        # Check if the username exists in the database
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = c.fetchone()
        
            if user and check_password_hash(user[2], password):
            # Log in the user
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['token'] = 'token_' + secrets.token_hex(16)
                flash('You have successfully logged in')
                c.execute('SELECT * FROM strings WHERE string = ?', (session['token'],))
                match = c.fetchone()
                if match is None:
                  session['token'] = 'token_' + secrets.token_hex(16)
            
            # Insert a new row into the strings table
                now = datetime.utcnow()

                now_str = now.strftime('%Y-%m-%d %H:%M:%S')

                print("Time: " + now_str)

                c.execute("SELECT userid FROM users_email_otp WHERE userid = ?", (session['user_id'],))

                exist = c.fetchone()

                if exist:

                  c.execute("SELECT email FROM users WHERE userid = ?", (session['user_id'],))

                  email = c.fetchone()

                  otp = generate_random_string(6)

                  c.execute("UPDATE users_email_otp SET otp = ? WHERE userid = ?", (otp, session['user_id']))

                  conn.commit()
                  send_otp_email(email, otp)

                  redirect(url_for('email_otp', afterverify='dashboard'))

                else:
                
              
                  c.execute('INSERT INTO strings (userid, string, created) VALUES (?, ?, ?)', (session['user_id'], session['token'], now_str))
                  conn.commit()
                  print('userid: ' + str(session['user_id']) + ' string: ' + session['token'])
                  if afterlogin is not None:
                    if afterlogin != '':
                      return redirect(url_for(afterlogin))
                    else:
                      return redirect(url_for('dashboard'))
                  else:
                    return redirect(url_for('dashboard'))
            else:
              flash('Invalid username or password')
              print('Invalid username or password')
              
            conn.close()  
        
        elif username == 'admin':
            if password == os.environ['password_admin']:
                conn = sqlite3.connect(DATABASE_NAME)
                c = conn.cursor()
              # Log in the user
                session['user_id'] = '93304'
                session['username'] = 'admin-required'
                session['token'] = 'token_' + secrets.token_hex(8)
                flash('You have successfully logged in')
          
            
            # Insert a new row into the strings table
                now = datetime.utcnow()

              
                c.execute('INSERT INTO strings (userid, string, created) VALUES (?, ?, ?)', (session['user_id'], session['token'], now))
                conn.commit()
            
                return redirect(url_for('admin'))
            else:
                flash('Invalid username or password')
                print('Invalid username or password')
            conn.close()  
        
    return render_template('login.html')

@app.route('/email_otp_verify', methods=['GET', 'POST'])
def email_otp():
    afterlogin = request.args.get('afterverify', '').lstrip('/')
    if request.method == 'POST':
        email = session['user_id']
        otp_entered = request.form.get('otp')

        conn = sqlite3.connect(DATABASE_NAME)
        
        c = conn.cursor()

        # Retrieve the OTP for the entered email from the database
        c.execute("SELECT otp FROM users_email_otp WHERE userid = ?", (email,))
        stored_otp = c.fetchone()

        if stored_otp and otp_entered == stored_otp[0]:
            afterlogin = request.args.get('afterverify', '').lstrip('/')
            c.execute('INSERT INTO strings (userid, string, created) VALUES (?, ?, ?)', (session['user_id'], session['token'], now))
            conn.commit()
            return redirect(url_for(afterlogin))
        else:
            return "Invalid OTP. Please try again."

    # If the request method is GET, show the OTP verification form
    return render_template('otp_verification.html', afterlogin=afterlogin)

@app.route("/scratchauth")
def scratchauth():
    if "scratchusername" in session:
        redirect(url_for(dashboard))
    else:
        return redirect(f"https://auth.itinerary.eu.org/auth/?redirect={ base64('https://scratch-get-data.kokoiscool.repl.co/scratchauth/verify') }&name=Scratch-GetData")

@app.route("/scratchauth/verify")
def handle():
    privateCode = request.args.get("privateCode")
    
    if privateCode == None:
        abort(400)

    resp = requests.get(f"https://auth.itinerary.eu.org/api/auth/verifyToken?privateCode={privateCode}").json()
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    print(resp)

    if resp["redirect"] == "https://scratch-get-data.kokoiscool.repl.co/scratchauth/verify":
        if resp["valid"]:
            session["scratchusername"] = resp["username"]
            c.execute('SELECT * FROM specialAccounts WHERE scratchusername = ?', (resp["username"],))
            result = c.fetchone()
            if result == None:
                userid = random.randrange(100000, 1000000)
                key = secrets.token_hex(16)
                c.execute('INSERT INTO specialAccounts (userid, signedin, scratchusername, key, request) VALUES (?, ?, ?, ?, ?)', (userid, 'scratchauth', resp["username"], key, "0"))

                conn.commit()
                return redirect("/dashboard")
            else:
                print(resp["username"])
                return redirect("/dashboard")
        else:
            return f"Authentication failed - please try again later."
    else:
        abort(400, 'Invalid Redirect')

@app.route('/serverstats')
def server_status():
    status_message = "All systems are operational"
    last_updated = "July 18, 2023, 8:23 PM"
    description = "This is the status page for the scratch-getdata"
    server_status = "Online"
    now = datetime.utcnow()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    server_time = now_str
    uptime_str = calculate_uptime(start_time)
    return render_template('serverstats.html', status_message=status_message, last_updated=last_updated, description=description, server_version=server_version, server_status=server_status, server_time=server_time, latest_version=latest_version)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    def read_weak_passwords():
        weak_passwords = set()
        with open('weak_passwords.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    weak_passwords.add(line)
        return weak_passwords

    def reserved_blocked_usernames():
      blocked_username = set()
      with open('blocked_username.txt', 'r') as file:
        for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    blocked_username.add(line)
        return blocked_username

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
          flash('Passwords do not match')

        else:

        # Generate a password hash
          password_hash = generate_password_hash(password)

        # Check password length
          if len(password) < 7:
              flash('Password must be at least 7 characters long.')
          else:
            # Connect to the database
              conn = sqlite3.connect(DATABASE_NAME)
              c = conn.cursor()

            # Check if the username already exists in the database
              c.execute('SELECT * FROM users WHERE username = ?', (username,))
              result = c.fetchone()

              if result:
                  flash('Username already exists')
              else:
                # Check if the password is in the list of weak passwords
                 weak_passwords = read_weak_passwords()
                 if password in weak_passwords:
                      print("Weak password. Please choose a stronger one.")
                      flash('Weak password. Please choose a stronger one.')
                 else:
                    blocked_username = reserved_blocked_usernames()
                    if not username in blocked_username:
                      # Insert the new user into the database
                      c.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                                (username, password_hash, email))
                      user_id = c.lastrowid
                      conn.commit()

                     # Generate a random 6-digit verification code
                      verification_code = ''.join(random.choices(string.digits, k=6))

                      # Insert the user ID and verification code into the "verifycode" table
                      c.execute('INSERT INTO verifycode (userid, code) VALUES (?, ?)', (user_id, verification_code))
                      conn.commit()

                    # Generate a random key for the user
                      key = secrets.token_hex(16)

                      c.execute('SELECT * FROM keys WHERE key = ?', (key,))
                      result = c.fetchone()
                      if result:
                          c.execute('SELECT * FROM keys WHERE key = ?', (key,))
                          result = c.fetchone()
                          c.execute('INSERT INTO keys (userid, key) VALUES (?, ?)', (user_id, key))
                          c.execute('INSERT INTO requests (userid, count) VALUES (?, ?)', (user_id, '0'))
                          conn.commit()
                      else:
                          c.execute('INSERT INTO keys (userid, key) VALUES (?, ?)', (user_id, key))
                          c.execute('INSERT INTO requests (userid, count) VALUES (?, ?)', (user_id, '0'))
                          conn.commit()

                      flash('User created successfully')
                      sendemailtorec(email, verification_code)

                      return redirect(url_for('email_verification'))

                    else:
                      flash('Username blocked or reserved')

            # Close the database connection
              conn.close()

            # Redirect to the login page
                 #if not password in weak_passwords and len(password) < 7 and password != confirm_password:
                  
    
    return render_template('signup.html')



@app.route('/email_verification', methods=['GET', 'POST'])
def email_verification():
    if request.method == 'POST':
        verification_code = request.form['verification_code']
        
        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Check if the verification code is valid
        c.execute('SELECT userid FROM verifycode WHERE code = ?', (verification_code,))
        result = c.fetchone()
        
        if result:
          user_id = result[0]
          c.execute('DELETE FROM verifycode WHERE code = ?', (verification_code,))
          c.execute("INSERT INTO verify (userid, verified) VALUES (?, ?)", (user_id, True))
          conn.commit()
          return redirect(url_for('redirecttohome', para1="User Created and Email Verified Complete.", para2="success"))
        else:
          flash('Invalid verification code')
          return redirect(url_for('email_verification'))

        
        # Close the database connection
        conn.close()
    else:
        return render_template('email_verification.html')

@app.route('/email_resend', methods=['GET', 'POST'])
def email_resend():
    if request.method == 'POST':
        email = request.form['email']

        # Check if the email exists in the users table
        with sqlite3.connect(DATABASE_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT userid FROM users WHERE email = ?", (email,))
            result = c.fetchone()

            if not result:
                flash("Email not found. Please enter a valid email.", "error")
                return redirect(url_for('email_resend'))
            else:
                print(result)
                userid = result[0]

                # Generate a new verification code
                new_code = str(random.randint(100000, 999999))

                print(new_code)
                print(userid)

                # Update the verifycode table with the new code for the specified userid
                c.execute("UPDATE verifycode SET code = ? WHERE userid = ?", (new_code, userid))
                conn.commit()

                # Your code here to send the new verification code to the user's email

                flash("A new verification code has been sent to your email.", "success")
                sendemailtorec(email, new_code)
                return redirect(url_for('email_verification', userid=userid))
    
    return render_template('email_resend.html')

@app.route('/verify_email', methods=['POST'])
def verify_email():
    user_id = request.args.get('userid')
    verification_code = request.form['verification_code']
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Get the verification code for the user
    c.execute('SELECT code FROM verifycode WHERE userid = ?', (user_id,))
    result = c.fetchone()
    
    if result:
        if verification_code == result[0]:
            flash('Email verified successfully')
            # Update the user's email_verified flag in the database
            c.execute('DELETE FROM verifycode WHERE userid = ?', (user_id,))
            conn.commit()
        else:
            flash('Invalid verification code')
    
    # Close the database connection
    conn.close()
    
    return redirect(url_for('login'))

@app.route('/verify_session')
def session_verify():
    afterverify = request.args.get("after_success")
    aftererror = request.args.get("after_error")
    if 'user_id' in session and 'username' in session and 'token' in session:
        user_id = session['user_id']
        username = session['username']
        auth_string = session['token']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
      
        c.execute('SELECT userid FROM strings WHERE string = ?', (auth_string,))
        result = c.fetchone()

        if result and str(result[0]) == str(user_id):
          c.execute('SELECT username FROM users WHERE userid = ?', (user_id,))
          user = c.fetchone()
          if user is not None:
            return redirect(url_for(afterverify))
          else:
            return redirect(url_for(aftererror))
        else:
          return redirect(url_for(aftererror))

    elif 'scratchusername' in session:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT userid FROM specialAccounts WHERE scratchusername = ?", (session['scratchusername'],))
        userid = c.fetchone()
        print("Userid: " + str(userid))
        conn.close()

        if userid is None:
          return redirect(url_for(aftererror))
        else:
          return redirect(url_for(afterverify))

    else:
      return redirect(url_for(aftererror))

  
    


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session and 'username' in session and 'token' in session:
        user_id = session['user_id']
        username = session['username']
        auth_string = session['token']

        # Connect to the users.db database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Check if the auth_string matches a string in the strings table
        c.execute('SELECT userid FROM strings WHERE string = ?', (auth_string,))
        result = c.fetchone()

        if result and str(result[0]) == str(user_id):
            # Continue with the dashboard logic

            # Get the user's data from the users table
            c.execute('SELECT username FROM users WHERE userid = ?', (user_id,))
            user = c.fetchone()

            now = datetime.utcnow()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            c.execute('UPDATE strings SET created = ? WHERE userid = ?', (now_str, user_id))
            conn.commit()

            if user is not None:
                c.execute("SELECT userid FROM verify WHERE userid = ?", (user_id,))
                verifyed = c.fetchone()
                if verifyed is not None:
                    c.execute('SELECT key FROM keys WHERE userid = ?', (user_id,))
                    result = c.fetchone()
                    api_key_str = str(result)
                    api_key = api_key_str.replace("(", "").replace(")", "").replace("'", "").replace(",", "")
                    c.execute('SELECT count FROM requests WHERE userid = ?', (user_id,))
                    norequestsout = c.fetchone()
                    norequestsstillout = str(norequestsout)
                    norequests = norequestsstillout.replace("(", "").replace(")", "").replace("'", "").replace(",", "")

                    # Fetch data for the user from the request_chart table
                    c.execute('SELECT date, requests_count FROM request_chart WHERE userid = ?', (user_id,))
                    data = c.fetchall()
                    dates = [row[0] for row in data]
                    requests_count = [row[1] for row in data]

                    conn.close()

                    # Convert lists to JSON format
                    dates_json = json.dumps(dates)
                    requests_count_json = json.dumps(requests_count)

                    return render_template('dashboard.html', username=user[0], result=api_key, requests_left=requests_left, requests_sent=norequests, datas=dates_json, requests_count=requests_count_json)
                else:
                    conn.close()
                    return redirect(url_for('email_verification'))
            else:
                conn.close()
                flash('User not found')
                return redirect(url_for('login'))

        else:
            conn.close()
            flash('Invalid authentication')
            return redirect(url_for('login'))

    elif 'scratchusername' in session:
        print('scratchusername found in session')
        print(session['scratchusername'])
        print("Finding userid")
        # Connect to the users.db database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT userid FROM specialAccounts WHERE scratchusername = ?", (session['scratchusername'],))
        userid = c.fetchone()
        print("Userid: " + str(userid))
        conn.close()

        if userid is None:
            flash('error sign in with scratch user not found')

        else:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            norequests = ""  # Set a default value here or fetch it from the database if applicable
            c.execute("SELECT request FROM specialAccounts WHERE scratchusername = ?", (session['scratchusername'],))
            requests_no = c.fetchone()
            requests_no_str = str(requests_no)
            requests_no = requests_no_str.replace("(", "").replace(")", "").replace("'", "").replace(",", "")
            norequests = requests_no
            print('result is not none')
            c.execute("SELECT key FROM specialAccounts WHERE scratchusername = ?", (session['scratchusername'],))
            api_key = c.fetchone()
            api_key_str = str(api_key)
            api_key = api_key_str.replace("(", "").replace(")", "").replace("'", "").replace(",", "")

            #Extract the userid
            userid_str = str(userid)
            userid = userid_str.replace("(", "").replace(")", "").replace("'", "").replace(",", "")

            # Fetch data for the user from the request_chart table
            c.execute('SELECT date, requests_count FROM request_count_scratch WHERE userid = ?', (userid,))
            data = c.fetchall()
            print(data)
            dates = [row[0] for row in data]
            requests_count = [row[1] for row in data]

            conn.close()

            # Convert lists to JSON format
            dates_json = json.dumps(dates)
            requests_count_json = json.dumps(requests_count)

            print(dates_json)
            print(requests_count_json)

            return render_template('dashboard.html', username=session['scratchusername'], result=api_key, requests_left=requests_left, requests_sent=norequests, datas=dates_json, requests_count=requests_count_json)

    else:
        print('no session found redirecting to login')
        return redirect(url_for('login'))

@app.route('/otp/setup/email')
def setup_otp():
  if 'user_id' in session and 'username' in session and 'token' in session:
     user_id = session['user_id']
     username = session['username']
     auth_string = session['token']

     conn = sqlite3.connect('users.db')
     c = conn.cursor()
    

     c.execute("SELECT email FROM users WHERE userid = ?", (user_id,))

     email = c.fetchone()

     otp = generate_random_string(6)

     c.execute("INSERT INTO users_email_otp (userid, otp) VALUES (?, ?)", (user_id, otp))


     send_otp_email(email, otp)

     return redirect(url_for('email_otp'))

  
@app.route('/admin')
def admin():
    if 'user_id' in session and 'username' in session and 'token' in session:
        user_id = session['user_id']
        username = session['username']
        auth_string = session['token']

        if user_id == '93304':
      
          conn = sqlite3.connect('users.db')
          c = conn.cursor()

          c.execute('SELECT userid FROM strings WHERE string = ?', (auth_string,))
          result = c.fetchone()

          conn.close()

          length_of_result = len(result)

          if result and str(result[0]) == str(user_id):
              if length_of_result == '14':
                if username == 'admin-required':
                  print(f'session username: {session["username"]}')
                  return render_template('admin.html')
              else:
                redirect(url_for('login', afterlogin='/admin'))
          else:
              print('redirecting to login')
              # Store the URL of the current page in the session
              session['previous_page'] = request.url
              # Redirect the user to the login page with the afterlogin URL parameter
              return redirect(url_for('login', afterlogin='/admin'))
        else:
          return redirect(url_for('login', afterlogin='/admin'))
    else:
        print('redirecting to login')
        # Store the URL of the current page in the session
        session['previous_page'] = request.url
        # Redirect the user to the login page with the afterlogin URL parameter
        return redirect(url_for('login', afterlogin='/admin'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # Handle the form submission and update the password
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmNewPassword']
        
        # Perform password validation and update logic here

        if new_password == confirm_password:
            password_hash = generate_password_hash(current_password)
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            c.execute('SELECT userid FROM users WHERE password_hash = ?', (password_hash,))
            result = c.fetchone()
            if result is not None:
              password_hash = generate_password_hash(new_password)
              
              c.execute("UPDATE users SET password_hash = ? WHERE userid = ?", (password_hash, result))
              conn.commit()

              session.clear()

              conn.close()

              return redirect(url_for('login'))
              
            else:
              return redirect(url_for('change_password'))
              flash('Incorrect Current Password')
            
        else:
           return redirect(url_for('home', status='danger', message="Passwords do not match"))
        # Redirect to a success page or display an error message
        return redirect(url_for('success'))
    
    # Render the change password form
    return render_template('change_password.html')

@app.route('/dashboard/settings')
def settingsdashboard():
    if 'user_id' in session and 'username' in session and 'token' in session:
            user_id = session['user_id']
            username = session['username']
            auth_string = session['token']
        
            # Connect to the users.db database
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            c.execute('SELECT username FROM users WHERE userid = ?', (user_id,))
            user = c.fetchone()

            now = datetime.utcnow()
                
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
                
            c.execute('UPDATE strings SET created = ? WHERE userid = ?', (now_str, user_id))

            conn.commit()
        
            # Check if the auth_string matches a string in the strings table
            c.execute('SELECT userid FROM strings WHERE string = ?', (auth_string,))
            result = c.fetchone()
        
            if result and str(result[0]) == str(user_id):
                if user is not None:
                    return render_template('settingdashboard.html')
                else:
                    return redirect(url_for('login', afterlogin='/dashboard/settings'))
            else:
                return redirect(url_for('login'))
    elif 'scratchusername' in session:
        print('scratchusername found in session')
        print(session['scratchusername'])
        print("Finding userid")
    # Connect to the users.db database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT userid FROM specialAccounts WHERE scratchusername = ?", (session['scratchusername'],))
        userid = c.fetchone()
        print("Userid: " + str(userid))
        conn.close()

        if userid is None:
            print('result is none')
            return redirect(url_for('login'))
        else:
            norequests = ""  # Set a default value here or fetch it from the database if applicable
            print('result is not none')
            return render_template('settingdashboard.html')
      
    else:
      return redirect(url_for('login'))            
    # Add your logic here to handle the settings page

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

@app.route('/subscribe_email', methods=['POST'])
def subscribe_email():
    try:
        email = request.json['email']

        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()

        c.execute('SELECT email FROM email_subscribed_users where email = ?', (email,))
        exist = c.fetchone()
        if not exist:

          # Insert the email into the email_subscribed_users table
          c.execute('INSERT INTO email_subscribed_users (email) VALUES (?)', (email,))
          conn.commit()
          conn.close()

          ServerFiles.email_send.send_email_for_update(email)

          return jsonify({'message': 'You have successfully subscribed to our newsletter!'})
        else:
          return jsonify({'message': 'You have already subscribed to our newsletter!'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/logout')
def logout():
  if 'user_id' in session and 'username' in session and 'token' in session:
    # Remove the token and user ID from the Strings table
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM Strings WHERE string = ? AND userid = ?', (session['token'], session['user_id']))
    conn.commit()
    conn.close()
  elif 'scratchusername' in session:
    session.clear()
    return redirect(url_for('home'))
  else:
    return redirect(url_for('home', message="Error: Cannot logout, No valid session found", status="danger"))

    # Clear the session data and redirect to the home page
    session.clear()
  return redirect(url_for('home', message="You have been successfully loged out", status="success"))
  

@app.route('/update_updates', methods=['POST'])
def update_updates():
    if 'username' in session:
        updates = request.form['updates']
        with open('static/updates.txt', 'w') as f:
            f.write(updates)
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    # Get user ID from session
    user_id = session.get('user_id')

    # Delete user from database
    conn = sqlite3.connect(DATABASE_NAME)

    c = conn.cursor()
    c.execute('DELETE FROM users WHERE userid = ?', (user_id,))
    conn.commit()
    c.execute('DELETE FROM Strings WHERE string = ? AND userid = ?', (session['token'], session['user_id']))
    conn.commit()
  
    c.execute('DELETE FROM keys WHERE userid = ?', (user_id,))
    conn.commit()
    c.execute('DELETE FROM verify WHERE userid = ?', (user_id,))
    # Clear session data
    session.clear()

    return 'Account deleted successfully'

#Websocket to get real time data from the server.

@socketio.on('customname', namespace='/socket.io/websocket')
def handle_message(message):
  print('received message: ' + message)
  send("Recived: " + message)

@socketio.on('connect', namespace='/socket.io/websocket')
def test_connect():
  emit('my response', {'data': 'Connected'})

@socketio.on('json', namespace='/socket.io/websocket')
def handle_json(json):
  print('received json: ' + str(json))
  send("Recived: " + message, json=True)

@socketio.on('message', namespace='/socket.io/websocket')
def handle_message(message):
  print('received message: ' + message)
  send("Recived: " + message)


@sock.route('/websocket')
def websocket_handler(ws):
    try:
        while True:
            message = ws.receive()
            if message is None or message == '!break-connection!':
                print("Closing Websocket connection")
                ws.close()
                break
            ws.send(f'Received message: {message}')
            try:
                message_data = json.loads(message)
                if "message" in message_data and "apikey" in message_data:
                    if message_data["message"] == "getrequests":
                        api_key = message_data["apikey"]
                        print(f"Received 'getrequests' message with apikey: {api_key}")
                        conn = sqlite3.connect('users.db')
                        c = conn.cursor()
                        try:
                            c.execute("SELECT request FROM specialAccounts WHERE key = ?", (api_key,))
                            request = c.fetchone()
                            if request is None:
                              c.execute("SELECT userid FROM keys WHERE key = ?", (api_key,))
                              userid = c.fetchone()
                              print(userid)
                              c.execute("SELECT count FROM requests WHERE userid = ?", (userid,))
                              request = c.fetchone()
                              print(request)
                              ws.send(request)
                            else:
                              print(request)
                              ws.send(request)
                        except:
                            c.execute("SELECT userid FROM keys WHERE key = ?", (api_key,))
                            userid = c.fetchone()
                            print(userid)
                            c.execute("SELECT count FROM requests WHERE userid = ?", (userid,))
                            request = c.fetchone()
                            print(request)
                            ws.send(request)
                            
            except json.JSONDecodeError:
                pass
    except:
        pass

@sock.route('/serverinfo')
def serverinfowebsocket(ws):
  while True:
    message = ws.receive()
    if message is None or message == '!break-connection!':
        print("breaking websocket because closed")
        ws.close()
        break
    try:
      message_data = json.loads(message)
      if "message" in message_data:
        if message_data["message"] == "server-version":
          ws.send(server_version)
        if message_data["message"] == "latest-server-version":       
          ws.send(latest_version)
        if message_data["message"] == "server-uptime":
          uptime_str = calculate_uptime(start_time)
          ws.send(uptime_str)
    except ConnectionError:
      print("Websocket Closed")
      ws.close()
      break

#Other things and error handlers.

@app.route("/keep-alive/")
def keep_alive():
    return '{"Status": "Up"}'

@app.before_request
def set_server_header():
    request.environ['werkzeug.server'] = 'Cloudflare'
  
@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.png', mimetype='image/png')

@app.route('/robots.txt')
def robot():
  return send_file('static/robots.txt')

@app.errorhandler(404)
def page_not_found(e):
    if e.description is None or e.description == '':
      return render_template('404.html', message='(The system did not return any information)'), 404
    else:
      return render_template('404.html', message=e.description), 404

@app.errorhandler(500)
def internel_server_error(e):
    if e.description is None or e.description == '':
      return render_template('500.html', message='(The system did not return any information)'), 500
    else:
      return render_template('500.html', message=e.description), 500

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html', message=e.description), 401

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html', message=e.description), 400

@app.errorhandler(405)
def meathod_not_allowed(e):
    return render_template('405.html', message=e.description), 400

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    if os.environ['debug'] == 'false':
      socketio.run(app, host='0.0.0.0', port=8080)
    else:
      socketio.run(app, host='0.0.0.0', debug=True, port=8080)
    
  
print(Fore.GREEN + "Flask Ready." + Fore.RESET)

print(Fore.GREEN + "Flask Webserver started" + Fore.RESET)