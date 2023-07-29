import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask import jsonify, Flask

app = Flask(__name__)

DATABASE_NAME = os.path.abspath('users.db')

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

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(os.environ['email_server'], 587)
    server.starttls()
    server.login(os.environ['email_username'], os.environ['email_password'])
    server.sendmail(os.environ['email_username'], recipients, msg.as_string())
    server.quit()

def read_updates_from_file():
    with open(os.path.abspath('updates-email.txt'), 'r') as file:
        updates = file.read()
    return updates

def send_update_emails():
    try:
        subject = 'New Update!'
        body = '''<!DOCTYPE html>
<html>
<head>
  <!-- Email CSS here -->
</head>
<body>
  <div class="container">
    <!-- Email content here -->
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
</html>'''

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


def send_email_for_update():
    try:
        subject = 'Subscribed!'
        body = '''<!DOCTYPE html>
<html>
<head>
  <!-- Email CSS here -->
</head>
<body>
  <div class="container">
    <!-- Email content here -->
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
</html>'''

        # Get the subscribed emails from the database
        recipients = get_subscribed_emails()

        if not recipients:
            return jsonify({'message': 'No subscribers found!'})

        # Send the update email to all subscribed users
        send_email(subject, body, recipients)

        return jsonify({'message': 'Update emails sent successfully!'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Run your update email sending task
    with app.app_context():
        send_update_emails()
        send_email_for_update()

    # Run the Flask app
    app.run()
