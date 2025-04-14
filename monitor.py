import time
import resend
from dotenv import load_dotenv
load_dotenv()
import os
import psutil

resend.api_key = os.getenv("RESEND_API_KEY")



CPU_THRESHOLD = 5
MEMORY_THRESHOLD = 40
DISK_THRESHOLD = 70

def secs2hours(secs):

    if secs == psutil.POWER_TIME_UNKNOWN or secs == psutil.POWER_TIME_UNLIMITED:
        return "N/A"
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return f"{int(hh)}:{int(mm):02}:{int(ss):02}"

def format_sensors():
    temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
    fans = psutil.sensors_fans() if hasattr(psutil, "sensors_fans") else {}
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None

    sensor_output = ""

    if temps:
        sensor_output += "<b>Temperatures:</b>\n"
        for name, entries in temps.items():
            sensor_output += f"  <u>{name}</u>\n"
            for entry in entries:
                sensor_output += (
                    f"    {entry.label or name:<20} {entry.current}°C "
                    f"(High: {entry.high}°C, Critical: {entry.critical}°C)\n"
                )
        sensor_output += "\n"

    if fans:
        sensor_output += "<b>Fans:</b>\n"
        for name, entries in fans.items():
             sensor_output += f"  <u>{name}</u>\n"
             for entry in entries:
                sensor_output += f"    {entry.label or name:<20} {entry.current} RPM\n"
        sensor_output += "\n"

    if battery:
        sensor_output += "<b>Battery / Power:</b>\n"
        sensor_output += f"  Charge:     {round(battery.percent, 2)}%\n"
        status = "N/A"
        if battery.power_plugged is not None:
            if battery.power_plugged:
                status = "Charging" if battery.percent < 100 else "Fully Charged"
            else:
                status = "Discharging"
        sensor_output += f"  Status:     {status}\n"
        sensor_output += f"  Plugged in: {'Yes' if battery.power_plugged else 'No' if battery.power_plugged is not None else 'N/A'}\n"
        if not battery.power_plugged and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
             sensor_output += f"  Time left:  {secs2hours(battery.secsleft)}\n"
        sensor_output += "\n"

    if not sensor_output:
        return "No sensor data available."

    return sensor_output.strip()


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


def monitor_system():
    alert_message = ""
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        current_alert = "" 
        if cpu_usage > CPU_THRESHOLD:
            current_alert += f"⚠️ ALERT: High CPU usage: {cpu_usage}%\n"
        if memory_usage > MEMORY_THRESHOLD:
            current_alert += f"⚠️ ALERT: High Memory usage: {memory_usage}%\n"
        if disk_usage > DISK_THRESHOLD:
            current_alert += f"⚠️ ALERT: High Disk usage: {disk_usage}% (Threshold: {DISK_THRESHOLD}%)\n"


        alert_message += current_alert

        sensor_info = format_sensors()

      
        if current_alert:
            print(f"ALERT DETECTED:\n{current_alert.strip()}")
            print(f"Sensor Status:\n{sensor_info}")
           
            send_email("System Alert", alert_message.strip(), sensor_info)
            alert_message = "" 
        else:
           
            print("System is running normally")


        time.sleep(60) 
if __name__ == "__main__":
    print("Starting system monitor...")
    monitor_system()

