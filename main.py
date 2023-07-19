from flask import render_template, send_file, request, redirect, session, make_response, flash
from flask import Flask, jsonify
from flask import abort
from flask import url_for
from flask_jwt_extended import create_access_token, jwt_required, decode_token
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_autoindex import AutoIndex
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz
import io
import os
import re
import time
import signal
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

def signal_handler(signal, frame):
    print("QUIT Signal Recived.")
    print("Closing Database")
    try:
      conn.close()  
    except:
      print(Fore.RED + "Cannot close database. Database is probably already closed." + Fore.RESET)
    sys.exit(0)

# Register the signal_handler function to be called only on SIGINT (Ctrl+C)
for sig in signal.Signals:
    try:
        signal.signal(sig, signal_handler)
    except (OSError, RuntimeError):
        pass

#Required Init

#Set timezone
vancouver_tz = pytz.timezone('America/Vancouver')
now = datetime.now(vancouver_tz)


# Reqire Generate

def generate_random_string(length):
    characters = string.ascii_letters + string.digits + "_"
    print(characters)
    random_string = ''.join(random.choice(characters) for _ in range(length))
    while random_string.startswith('_') or random_string.endswith('_'):
        random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

# init

app = Flask('app')
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '1QGz0JZvqsNJg0Mp2o'  # Change this!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'Token'
app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'CSRF-TOKEN'
app.config['JWT_ACCESS_CSRF_FIELD_NAME'] = 'csrf_token'
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_IN_COOKIES'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
jwt = JWTManager(app)

db = SQLAlchemy(app)

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

print(Fore.GREEN + "Flask Initialized." + Fore.RESET)

DATABASE_NAME = 'users.db'

requests_left = 'Infinity'

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
        return render_template('keynotfound.html')

    # Get the user ID from the session
    c.execute('SELECT userid FROM keys WHERE key = ?', (random_key,))
    user_id = c.fetchone()[0]  # Extract the value from the tuple

# Update the requests column for the user
    c.execute('UPDATE requests SET count = (SELECT COALESCE(count, 0) + 1 FROM requests WHERE userid = ?) WHERE userid = ?', (user_id, user_id))
    conn.commit()

# Require Define Functions:

def get_scratch_data(url):
    proxy_url = 'https://jungle-strengthened-aardvark.glitch.me/get/'
    proxied_url = proxy_url + url
    response = requests.get(proxied_url)
    response.raise_for_status()

    try:
        return json.loads(response.text)
    except ValueError:
        try:
            return int(response.text)
        except ValueError:
            return response.text

def get_scratch_data_nojson(url):
    proxy_url = 'https://jungle-strengthened-aardvark.glitch.me/get/'
    proxied_url = proxy_url + url
    response = requests.get(proxied_url)
    response.raise_for_status()

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
   
if app == '__main__':
   app.run()

@app.route('/settings')
def settings():
    # Logic for the settings page
    return render_template('settings.html')

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

@app.route("/get/follower-count/<username>/")
def count(username):
    try:
        response = requests.get(f"http://jungle-strengthened-aardvark.glitch.me/followers/{username}")
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
        response = requests.get(f"http://jungle-strengthened-aardvark.glitch.me/following/{username}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if isinstance(data, int):
                return str(data)
            else:
                abort(404)
                return "Invalid response"
        elif response.status_code == 404:
            abort(404)
            return "User does not exist"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/wiwo/<username>/")
def wiwo(username):
    try:
        response = requests.get(
            f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/users/{username}"
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            profile = data.get("profile", {})
            work = profile.get("status", "")
            return work.replace("\n", " ")
        else:
            abort(404)
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        abort(404)
        return f"An error occurred: {str(e)}"


@app.route("/get/aboutme/<username>/")
def about_me(username):
    try:
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/users/{username}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.text:
            try:
                data = json.loads(response.text)
                if "code" in data and data["code"] == "NotFound":
                    abort(404)
                    return "User does not exist"
                elif "username" in data and "profile" in data:
                    about_me = data["profile"].get("bio", "")
                    return about_me
                else:
                    return "Invalid response structure"
            except json.decoder.JSONDecodeError:
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
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "author" in data and "username" in data["author"]:
                creator = data["author"]["username"]
                return creator
            else:
                return "Project creator not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/name/<project_id>/")
def project_name(project_id):
    try:
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "title" in data:
                name = data["title"]
                return name
            else:
                return "Project name not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/notes_and_credits/<project_id>/")
def project_notes_and_credits(project_id):
    try:
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "description" in data:
                description = data["description"]
                return description.strip()  # Return the description as-is
            else:
                return "Project description not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@app.route("/get/project/instructions/<project_id>/")
def project_instructions(project_id):
    try:
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/projects/{project_id}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            data = json.loads(response.text)
            if "instructions" in data:
                instructions = data["instructions"]
                return instructions.strip()  # Return the instructions as-is
            else:
                return "Project instructions not found"
        elif response.status_code == 404:
            abort(404)
            return "Project not found"
        else:
            return "Invalid response"
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
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/studios/{studioid}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if "title" in data:
                title = data["title"]
                return title
            else:
                return "Studio title not found"
        elif response.status_code == 404:
            abort(404)
            return "Studio not found"
        else:
            return "Invalid response"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route("/get/studio/description/<studioid>/")
def studio_description(studioid):
    try:
        response = requests.get(f"https://jungle-strengthened-aardvark.glitch.me/get/https://api.scratch.mit.edu/studios/{studioid}")
        if response.status_code == 200:
            data = json.loads(response.text)
            if "description" in data:
                description = data["description"]
                return description
            else:
                return "Studio description not found"
        elif response.status_code == 404:
            return "Studio not found"
        else:
            return "Invalid response"
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

#Testing use

@app.route("/get/ip/", methods=["GET", "POST"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200



@app.route("/internal/auth-only", methods=["GET", "POST", "KOKOAUTH"])
def auth_only():
    auth = request.authorization
    if not auth or auth.username != 'example' or auth.password != os.environ['internal_secret']:
        abort(401)
    return "Authenticated successfully"

#Admin page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
                session['token'] = 'token_' + secrets.token_hex(8)
                flash('You have successfully logged in')
            
            # Insert a new row into the strings table
                now = datetime.utcnow()

                now_str = now.strftime('%Y-%m-%d %H:%M:%S')

                print("Time: " + now_str)
              
                c.execute('INSERT INTO strings (userid, string, created) VALUES (?, ?, ?)', (session['user_id'], session['token'], now_str))
                conn.commit()
                print('userid: ' + str(session['user_id']) + ' string: ' + session['token'])
            
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
                session['username'] = 'admin'
                session['token'] = 'token_' + secrets.token_hex(8)
                flash('You have successfully logged in')
          
            
            # Insert a new row into the strings table
                now = datetime.utcnow()

                print("Time: " + now)
              
                c.execute('INSERT INTO strings (userid, string, created) VALUES (?, ?, ?)', (session['user_id'], session['token'], now))
            
                return redirect(url_for('admin'))
            else:
                flash('Invalid username or password')
                print('Invalid username or password')
            conn.close()  
        
    return render_template('login.html')

@app.route('/serverstats')
def server_status():
    status_message = "All systems are operational"
    last_updated = "July 18, 2023, 8:23 PM"
    description = "This is the status page for the scratch-getdar"
    server_version = "1.0.0"
    server_status = "Online"
    now = datetime.utcnow()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    server_time = now_str
    return render_template('serverstats.html', status_message=status_message, last_updated=last_updated, description=description, server_version=server_version, server_status=server_status, server_time=server_time)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Generate a password hash
        password_hash = generate_password_hash(password)
        
        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Check if the username already exists in the database
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        
        if result:
            flash('Username already exists')
        else:
            # Insert the new user into the database
            c.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)', (username, password_hash, email))
            user_id = c.lastrowid
            conn.commit()
            
            # Generate a random 6-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # Insert the user ID and verification code into the "verifycode" table
            c.execute('INSERT INTO verifycode (userid, code) VALUES (?, ?)', (user_id, verification_code))
            conn.commit()
            
            # Generate a random key for the user
            key = secrets.token_hex(16)
            
            # Insert the key into the database
            c.execute('INSERT INTO keys (userid, key) VALUES (?, ?)', (user_id, key))
            c.execute('INSERT INTO requests (userid, count) VALUES (?, ?)', (user_id, '0'))
            conn.commit()
            
            
            flash('User created successfully')
            sendemailtorec(email, verification_code)
        
        # Close the database connection
        conn.close()
        
        # Redirect to the login page
        return redirect(url_for('email_verification'))
    
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
    

@app.route('/dashboard')
def dashboard():
    try:
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
                    return render_template('dashboard.html', username=user[0], result=api_key, requests_left=requests_left,requests_sent=norequests)
                  else:
                     return redirect(url_for('email_verification'))
                else:
                    flash('User not found')
                    return redirect(url_for('login'))
                conn.close()  
            else:
                flash('Invalid authentication')
            # Close the database connection
            conn.close()
            return redirect(url_for('login'))
        else:
          return redirect(url_for('login'))
    except Exception as e:
        print(e)
        return redirect(url_for('login'))
  
@app.route('/admin')
def admin():
    if 'user_id' in session and 'username' in session and 'token' in session:
        user_id = session['user_id']
        username = session['username']
        auth_string = session['token']
      
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute('SELECT userid FROM strings WHERE string = ?', (auth_string,))
        result = c.fetchone()

        conn.close()

        if result and str(result[0]) == str(user_id):

            print(f'session username: {session["username"]}')
            return render_template('admin.html')
        else:
            print('redirecting to login')
            # Store the URL of the current page in the session
            session['previous_page'] = request.url
            # Redirect the user to the login page with the afterlogin URL parameter
            return redirect(url_for('login', afterlogin='/admin'))
    else:
        print('redirecting to login')
        # Store the URL of the current page in the session
        session['previous_page'] = request.url
        # Redirect the user to the login page with the afterlogin URL parameter
        return redirect(url_for('login', afterlogin='/admin'))

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
                    return redirect(url_for('login'))
            else:
                return redirect(url_for('login'))
    else:
          return redirect(url_for('login'))            
    # Add your logic here to handle the settings page

@app.route('/logout')
def logout():
    # Remove the token and user ID from the Strings table
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM Strings WHERE string = ? AND userid = ?', (session['token'], session['user_id']))
    conn.commit()
    conn.close()

    # Clear the session data and redirect to the home page
    session.clear()
    return redirect(url_for('home'))

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

#Other things and error handlers

@app.route("/keep-alive/")
def keep_alive():
    return '{"Status": "Up"}'

@app.before_request
def set_server_header():
    request.environ['werkzeug.server'] = 'Cloudflare'
  
@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='favicon.png')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html'), 400

@app.errorhandler(405)
def page_not_found(e):
    return render_template('405.html'), 400


app.run(host='0.0.0.0', port=8080)

print(Fore.GREEN + "Flask Ready." + Fore.RESET)

print(Fore.GREEN + "Flask Webserver started" + Fore.RESET)