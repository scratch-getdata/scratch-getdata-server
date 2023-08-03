import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

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
            return {'message': 'No subscribers found!'}

        # Send the update email to all subscribed users
        send_email(subject, body, recipients)

        return {'message': 'Update emails sent successfully!'}

    except Exception as e:
        return {'error': str(e)}


def send_email_for_update(email):
    try:
        subject = 'Subscribed!'
        body = '''<!DOCTYPE html>
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
</html>'''

        # Get the subscribed emails from the database
        recipients = [email]

        # Send the update email to the specified email address
        send_email(subject, body, recipients)

        return {'message': 'Update email sent successfully!'}

    except Exception as e:
        return {'error': str(e)}
