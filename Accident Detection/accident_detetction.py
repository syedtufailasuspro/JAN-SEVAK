import requests
import time

# Replace with your phone's IP from Phyphox Remote Access
PHYPOX_URL = "http://172.16.199.191:8080/get?accX&accY&accZ"

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "7796389368:AAG_zB1GCTztXLwFn8wg3X7_dJi40BRlbEA"  # Replace with your bot token
CHAT_ID = 5460664029 # Replace with your chat ID

# Accident detection threshold
ACCIDENT_THRESHOLD = 25  # Adjust based on testing

def send_telegram_alert(acceleration):
    """Sends an alert to Telegram when an accident is detected."""
    message = f"/alert \nLocation: 12.972116870584953, 80.04291799581253\nSpeed: {acceleration:.2f}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
        if response.status_code == 200:
            print("✅ Alert sent to Telegram!")
        else:
            print("❌ Failed to send alert:", response.text)
    except Exception as e:
        print("⚠️ Error sending Telegram alert:", e)

def get_sensor_data():
    """Fetches acceleration data from the smartphone via Phyphox."""
    try:
        response = requests.get(PHYPOX_URL)
        data = response.json()
        acc_x = data['buffer']['accX']['buffer'][-1]  # Last X-axis value
        acc_y = data['buffer']['accY']['buffer'][-1]  # Last Y-axis value
        acc_z = data['buffer']['accZ']['buffer'][-1]  # Last Z-axis value

        total_acc = (acc_x**2 + acc_y**2 + acc_z**2) ** 0.5  # Magnitude
        return total_acc
    except Exception as e:
        print("⚠️ Error fetching sensor data:", e)
        return None

while True:
    acceleration = get_sensor_data()
    
    if acceleration:
        print(f"📊 Acceleration: {acceleration:.2f} m/s²")

        if acceleration > ACCIDENT_THRESHOLD:
            print("⚠️ Accident Detected! Sending Alert...")
            send_telegram_alert(acceleration)

    time.sleep(1)  # Fetch data every second
