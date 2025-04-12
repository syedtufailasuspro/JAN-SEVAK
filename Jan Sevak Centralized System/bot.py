from flask import Flask, request
import telebot
import threading
import mysql.connector
import time
from config import *

from telethon.sync import TelegramClient, events

# ======== Bots Setup ===========
accident_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ambulance_bot = telebot.TeleBot(AMBULANCE_BOT_TOKEN)

app = Flask(__name__)
pending_cases = {}

# ======== MySQL Connection ===========
def db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

# ======== Accident API ===========
@app.route('/accident', methods=['POST'])
def handle_accident():
    data = request.get_json()
    location = data.get("location")
    speed = data.get("speed")

    message = f"🚨 Accident Detected!\n📍 Location: {location}\n💨 Speed: {speed}\n\nDo you confirm this is a real accident?"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Yes", callback_data=f"yes|{location}|{speed}"),
        telebot.types.InlineKeyboardButton("❌ No", callback_data=f"no|{location}|{speed}")
    )

    sent = accident_bot.send_message(chat_id=5460664029, text=message, reply_markup=markup)
    pending_cases[sent.message_id] = {"location": location, "speed": speed, "responded": False}
    threading.Thread(target=wait_for_response, args=(sent.message_id,)).start()

    return "OK", 200

def wait_for_response(msg_id):
    time.sleep(5)
    if msg_id in pending_cases and not pending_cases[msg_id]["responded"]:
        info = pending_cases[msg_id]
        location, speed = info["location"], info["speed"]
        insert_and_notify(location, speed)
        del pending_cases[msg_id]

@accident_bot.callback_query_handler(func=lambda call: call.data.startswith("yes") or call.data.startswith("no"))
def handle_callback(call):
    action, location, speed = call.data.split('|')
    if call.message.message_id in pending_cases:
        pending_cases[call.message.message_id]["responded"] = True

        if action == "no":
            insert_and_notify(location, speed)
            accident_bot.send_message(call.message.chat.id, "✅ Report confirmed. Ambulance dispatched.")
        else:
            accident_bot.send_message(call.message.chat.id, "🛑 Report ignored. No ambulance sent.")
        
        del pending_cases[call.message.message_id]

def insert_and_notify(location, speed):
    db = db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO active_cases (location, speed, assigned_ambulance) VALUES (%s, %s, %s)",
                   (location, speed, "Ambulance 1"))
    db.commit()
    db.close()

    ambulance_bot.send_message(7248064417, f"🚑 Emergency Alert!\n📍 Location: {location}\n💨 Speed: {speed}")

# ======== Original Ambulance Bot Command ===========
@ambulance_bot.message_handler(commands=['update'])
def ambulance_update(msg):
    chat_id = msg.chat.id
    data = msg.text.split('\n')

    if len(data) < 3:
        ambulance_bot.send_message(chat_id, "Invalid format! Please use:\n/update\nLocation: XYZ\nPatient Condition: Critical")
        return

    location = data[1].split(': ')[1]
    patient_condition = data[2].split(': ')[1]

    db = db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, location FROM hospitals WHERE specialization LIKE %s ORDER BY location ASC LIMIT 1",
                   (f"%{patient_condition}%",))
    hospital = cursor.fetchone()

    if hospital:
        cursor.execute("UPDATE active_cases SET patient_condition=%s, hospital_assigned=%s WHERE status='Active' ORDER BY accident_time DESC LIMIT 1",
                       (patient_condition, hospital["name"]))
        db.commit()
        ambulance_bot.send_message(chat_id, f"🏥 Hospital Assigned: {hospital['name']}\n📍 Location: {hospital['location']}")
    
    db.close()

# ======== Threads to Run Bots ===========
def start_accident_bot():
    accident_bot.polling(none_stop=True)

def start_ambulance_bot():
    ambulance_bot.polling(none_stop=True)

# ======== TELETHON Integration ===========
API_ID = 20278651  # Replace with integer
API_HASH = '175dbe46a44695db2e9b4d7b8dfdeae6'  # Replace with your hash

client = TelegramClient('tuf_bot', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/update'))
async def telethon_update_handler(event):
    msg_text = event.raw_text
    lines = msg_text.split('\n')

    if len(lines) < 3:
        await event.reply("Invalid format! Please use:\n/update\nLocation: XYZ\nPatient Condition: Critical")
        return

    try:
        location = lines[1].split(': ')[1]
        patient_condition = lines[2].split(': ')[1]
    except IndexError:
        await event.reply("❌ Error parsing message. Please follow correct format.")
        return

    db = db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, location FROM hospitals WHERE specialization LIKE %s ORDER BY location ASC LIMIT 1",
                   (f"%{patient_condition}%",))
    hospital = cursor.fetchone()

    if hospital:
        cursor.execute("UPDATE active_cases SET patient_condition=%s, hospital_assigned=%s WHERE status='Active' ORDER BY accident_time DESC LIMIT 1",
                       (patient_condition, hospital["name"]))
        db.commit()
        await event.reply(f"🏥 Hospital Assigned: {hospital['name']}\n📍 Location: {hospital['location']}")
    
    db.close()

# ======== Main Runner ===========
if __name__ == '__main__':
    threading.Thread(target=start_accident_bot).start()
    threading.Thread(target=start_ambulance_bot).start()

    # Start Flask
    threading.Thread(target=lambda: app.run(port=5000)).start()

    # Start Telethon client (must run in main thread ideally)
    client.start(phone='+917395905658')
    client.run_until_disconnected()
