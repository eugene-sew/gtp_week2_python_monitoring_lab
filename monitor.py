import time
import psutil
from util import secs_to_hours
from send_mail import send_email


CPU_THRESHOLD = 5
MEMORY_THRESHOLD = 40
DISK_THRESHOLD = 70

def format_sensors():
    """Format system sensor data for display."""
    # Retrieve sensor data
    temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
    fans = psutil.sensors_fans() if hasattr(psutil, "sensors_fans") else {}
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None

    # Initialize output
    sensor_output = []

    # Format temperature data
    if temps:
        sensor_output.append("<b>Temperatures:</b>")
        for name, entries in temps.items():
            sensor_output.append(f"  <u>{name}</u>")
            for entry in entries:
                sensor_output.append(
                    f"    {entry.label or name:<20} {entry.current:.1f}°C "
                    f"(High: {entry.high:.1f}°C, Critical: {entry.critical:.1f}°C)"
                )
        sensor_output.append("")

    # Format fan data
    if fans:
        sensor_output.append("<b>Fans:</b>")
        for name, entries in fans.items():
            sensor_output.append(f"  <u>{name}</u>")
            for entry in entries:
                sensor_output.append(f"    {entry.label or name:<20} {entry.current} RPM")
        sensor_output.append("")

    # Format battery data
    battery_percentage = None
    if battery:
        sensor_output.append("<b>Battery / Power:</b>")
        battery_percentage = round(battery.percent, 2)
        sensor_output.append(f"  Charge:     {battery_percentage}%")
        if battery.power_plugged is not None:
            if battery.power_plugged:
                status = "Charging" if battery.percent < 100 else "Fully Charged"
            else:
                status = "Discharging"
        else:
            status = "N/A"
        sensor_output.append(f"  Status:     {status}")
        sensor_output.append(f"  Plugged in: {'Yes' if battery.power_plugged else 'No'}")
        if not battery.power_plugged and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
            sensor_output.append(f"  Time left:  {secs_to_hours(battery.secsleft)}")
        sensor_output.append("")

    # Return formatted sensor data or a default message
    formatted_output = "\n".join(sensor_output).strip() if sensor_output else "No sensor data available."

    return formatted_output

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

