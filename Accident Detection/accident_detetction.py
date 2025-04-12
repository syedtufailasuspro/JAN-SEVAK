import requests
import time

PHYPOX_URL = "http://192.168.97.206:8080/get?accX&accY&accZ"
BOT_SERVER_URL = "http://127.0.0.1:5000/accident"  # Flask server running in bot.py

ACCIDENT_THRESHOLD = 25

def send_alert_to_server(acceleration):
    data = {
        "location": "12.972116870584953, 80.04291799581253",
        "speed": f"{acceleration:.2f}"
    }
    try:
        response = requests.post(BOT_SERVER_URL, json=data)
        if response.status_code == 200:
            print("✅ Alert sent to bot server!")
        else:
            print("❌ Failed to send alert:", response.text)
    except Exception as e:
        print("⚠️ Error:", e)

def get_sensor_data():
    try:
        response = requests.get(PHYPOX_URL)
        data = response.json()
        acc_x = data['buffer']['accX']['buffer'][-1]
        acc_y = data['buffer']['accY']['buffer'][-1]
        acc_z = data['buffer']['accZ']['buffer'][-1]
        return (acc_x**2 + acc_y**2 + acc_z**2)**0.5
    except Exception as e:
        print("⚠️ Sensor error:", e)
        return None

while True:
    acc = get_sensor_data()
    if acc:
        print(f"📊 Acceleration: {acc:.2f} m/s²")
        if acc > ACCIDENT_THRESHOLD:
            print("⚠️ Accident Detected! Sending to bot...")
            send_alert_to_server(acc)
    time.sleep(1)
