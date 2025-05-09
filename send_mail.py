import time
import os
import resend
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(subject, body, sensor_data):
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
<title>{subject}</title>
<style>
  body {{ font-family: sans-serif; margin: 20px; background-color: #f4f4f4; }}
  .container {{ background-color: #ffffff; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
  h1 {{ color: #333; }}
  p {{ color: #555; line-height: 1.6; }}
  .footer {{ margin-top: 20px; font-size: 0.8em; color: #777; text-align: center; }}
  pre {{ background-color: #eee; padding: 10px; border-radius: 3px; white-space: pre-wrap; word-wrap: break-word; }}
  .sensor-data {{ color: blue; /* Blue text for sensor data */ }}
  .timestamp {{ color: #666; font-size: 0.9em; margin-bottom: 15px; }}
</style>
</head>
<body>
<div class="container">
  <h1>{subject} - ChefsMonitor</h1>
  <div class="timestamp">Alert Time: {time.strftime('%Y-%m-%d %H:%M:%S')}</div>
  <p>The following system alerts were triggered:</p>
  <pre style="color: red; font-weight: bold; text-size: 20px;">{body if body else "No system resource alerts."}</pre>

  <p>Current Sensor Status:</p>
  <pre class="sensor-data">{sensor_data}</pre>
  

  <p>Please review the system status.</p>
  <div class="footer">
    ChefsMonitor - Automated System Monitoring
  </div>
</div>
</body>
</html>
"""

    params = {
        "from": f"ChefsMonitor Alert <{os.getenv('EMAIL_FROM')}>",
        "to": [os.getenv('EMAIL_TO')],
        "subject": subject,
        "html": html_template,
    }

    try:
        email_response = resend.Emails.send(params)
        print(f"Email sent successfully: {subject}, ID: {email_response['id']}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

