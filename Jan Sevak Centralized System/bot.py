import telebot
import threading
import mysql.connector
from config import *

accident_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ambulance_bot = telebot.TeleBot(AMBULANCE_BOT_TOKEN)

def db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

# Accident Bot: Receives accident alerts and informs the ambulance bot
@accident_bot.message_handler(commands=['alert'])
def accident_alert(msg):
    chat_id = msg.chat.id
    data = msg.text.split('\n')

    if len(data) < 3:
        accident_bot.send_message(chat_id, "Invalid format! Please use:\n/alert\nLocation: XYZ\nSpeed: 50")
        return

    location = data[1].split(': ')[1]
    speed = data[2].split(': ')[1]

    db = db_connection()
    cursor = db.cursor()

    cursor.execute("INSERT INTO active_cases (location, speed, assigned_ambulance) VALUES (%s, %s, %s)",
                   (location, speed, "Ambulance 1"))
    db.commit()
    db.close()

    accident_bot.send_message(chat_id, "🚨 Accident Reported! Ambulance Dispatched.")

    # Notify the ambulance bot
    ambulance_chat_id = 7248064417  # Replace with the actual chat ID of the ambulance bot
    alert_message = f"🚑 Emergency Alert!\n📍 Location: {location}\n💨 Speed: {speed}"
    ambulance_bot.send_message(ambulance_chat_id, alert_message)

# Ambulance Bot: Updates patient condition
@ambulance_bot.message_handler(commands=['update'])
def ambulance_update(msg):
    chat_id = msg.chat.id
    data = msg.text.split('\n')

    if len(data) < 3:
        ambulance_bot.send_message(chat_id, "Invalid format! Please use:\n/update\nLocation: XYZ\nCondition: Critical")
        return

    location = data[1].split(': ')[1]
    patient_condition = data[2].split(': ')[1]

    db = db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT name, location FROM hospitals WHERE specialization LIKE %s ORDER BY location ASC LIMIT 1",
                   (f"%{patient_condition}%",))
    hospital = cursor.fetchone()

    if hospital:
        hospital_name = hospital["name"]
        hospital_location = hospital["location"]

        cursor.execute("UPDATE active_cases SET patient_condition=%s, hospital_assigned=%s WHERE status='Active' ORDER BY accident_time DESC LIMIT 1",
                       (patient_condition, hospital_name))
        db.commit()

        ambulance_bot.send_message(chat_id, f"🏥 Hospital Assigned: {hospital_name}\n📍 Location: {hospital_location}")
    
    db.close()

# Run both bots simultaneously using threads
def start_accident_bot():
    accident_bot.polling(none_stop=True)

def start_ambulance_bot():
    ambulance_bot.polling(none_stop=True)

# Create threads for each bot
t1 = threading.Thread(target=start_accident_bot)
t2 = threading.Thread(target=start_ambulance_bot)

# Start both threads
t1.start()
t2.start()
