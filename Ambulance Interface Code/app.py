from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend

TELEGRAM_BOT_TOKEN = "7836052108:AAH2gWeE8xEk1nCNWmLzEe-bKPPuQXbI_T4"
CHAT_ID = 7248064417

@app.route('/send_telegram_alert', methods=['POST'])
def send_telegram_alert():
    """Sends an alert to Telegram when an accident is detected."""
    data = request.get_json()

    if not data or "injuries" not in data:
        return jsonify({"error": "Invalid data received"}), 400

    # Define location (you can modify this to get dynamic location)
    location = "XYZ"  # Placeholder, replace with actual location logic

    # Construct the message in the required format
    message = "/update\n"
    message += f" Location: {location}\n"
    message += " Patient Condition: "

    for injury in data["injuries"]:
        injury_type = injury.get("injury", "Unknown").replace("_", " ").title()  # Format injury name
        severity = injury.get("severity", "Unknown")
        message += f"{injury_type} Injury - Severe {severity}\n"

    print("\nSending Telegram Alert:\n", message)  # Print message in the terminal

    # Send Telegram message
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
        if response.status_code == 200:
            print("✅ Alert sent to Telegram!")
            return jsonify({"status": "success", "message": "Alert sent to Telegram"}), 200
        else:
            print("❌ Failed to send alert:", response.text)
            return jsonify({"status": "failed", "error": response.text}), 500
    except Exception as e:
        print("⚠ Error sending Telegram alert:", e)
        return jsonify({"status": "failed", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
