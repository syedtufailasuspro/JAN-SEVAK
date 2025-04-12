from flask import Flask, render_template, request, jsonify
import mysql.connector
import requests
import time
from config import *

app = Flask(__name__)

# Connect to MySQL
def db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )


@app.route("/")
def home():
    return render_template("index.html")


# Handle Accident Alerts from Telegram Bot
@app.route("/accident", methods=["POST"])
def accident_alert():
    data = request.get_json()
    
    # Extract accident details
    location = data["location"]
    speed = data["speed"]
    gyroscope = data["gyroscope_data"]
    
    # Assign an ambulance (1 or 2 based on case number)
    db = db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM active_cases")
    case_count = cursor.fetchone()[0]
    ambulance_assigned = f"Ambulance {case_count + 1}"

    # Insert into active_cases
    cursor.execute(
        "INSERT INTO active_cases (location, speed, gyroscope_data, assigned_ambulance) VALUES (%s, %s, %s, %s)",
        (location, speed, gyroscope, ambulance_assigned)
    )
    db.commit()
    db.close()

    # Notify the ambulance
    msg = f"🚨 Emergency Alert 🚨\n📍 Location: {location}\n🚗 Speed: {speed}\n🌀 Gyroscope Data: {gyroscope}"
    requests.post(f"https://api.telegram.org/bot{AMBULANCE_BOT_TOKEN}/sendMessage", data={"chat_id":  "ambulance_chat_id", "text": msg})

    return jsonify({"message": "Accident alert received!"})

#This new route allows the frontend to fetch active cases.
@app.route("/get-active-cases")
def get_active_cases():
    db = db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM active_cases WHERE status='Active'")
    cases = cursor.fetchall()

    db.close()
    return jsonify(cases)


# Handle Ambulance Arrival & Assign Hospital
@app.route("/ambulance-update", methods=["POST"])
def ambulance_update():
    data = request.get_json()
    
    location = data["location"]
    patient_condition = data["patient_condition"]

    # Find nearest hospital
    db = db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT name, location FROM hospitals WHERE specialization LIKE %s ORDER BY location ASC LIMIT 1",
        (f"%{patient_condition}%",)
    )
    hospital = cursor.fetchone()
    hospital_name = hospital["name"]
    hospital_location = hospital["location"]

    # Update active case
    cursor.execute(
        "UPDATE active_cases SET patient_condition=%s, hospital_assigned=%s WHERE status='Active' ORDER BY accident_time DESC LIMIT 1",
        (patient_condition, hospital_name)
    )
    db.commit()
    db.close()

    # Notify ambulance
    msg = f"🏥 Hospital Assigned: {hospital_name}\n📍 Location: {hospital_location}"
    requests.post(f"https://api.telegram.org/bot{AMBULANCE_BOT_TOKEN}/sendMessage", data={"chat_id": "ambulance_chat_id", "text": msg})

    return jsonify({"message": "Hospital assigned!"})

# Case Closure
@app.route("/close-case", methods=["POST"])
def close_case():
    db = db_connection()
    cursor = db.cursor()
    
    # Move from active_cases to closed_cases
    cursor.execute(
    """
    INSERT INTO closed_cases (case_id, accident_time, close_time, location, patient_condition, hospital)
    SELECT 
        COALESCE((SELECT MAX(case_id) FROM closed_cases), 0) + 1 AS new_case_id,
        accident_time,
        NOW(),
        location,
        patient_condition,
        hospital_assigned
    FROM active_cases
    WHERE status='Active'
    ORDER BY accident_time DESC
    LIMIT 1
    """
)

    cursor.execute("DELETE FROM active_cases WHERE status='Active' ORDER BY accident_time DESC LIMIT 1")
    
    db.commit()
    db.close()

    return jsonify({"message": "Case closed and logged!"})

#statistics
@app.route("/get-accident-statistics")
def get_accident_statistics():
    db = db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Get accidents by hour of day (including hours with 0 accidents)
        cursor.execute("""
            SELECT 
                HOUR(accident_time) as hour,
                COUNT(*) as count
            FROM closed_cases
            GROUP BY hour
            ORDER BY hour
        """)
        hourly_data = cursor.fetchall()
        
        # If no data exists, return sample data for testing
        if not hourly_data:
            hourly_data = [
                {"hour": 8, "count": 3},
                {"hour": 12, "count": 5},
                {"hour": 17, "count": 7},
                {"hour": 20, "count": 2}
            ]
        
        return jsonify({
            'hourly': hourly_data,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        return jsonify({
            'hourly': [
                {"hour": 8, "count": 3},
                {"hour": 12, "count": 5},
                {"hour": 17, "count": 7},
                {"hour": 20, "count": 2}
            ],
            'status': 'error',
            'message': str(e)
        })
    finally:
        db.close()

        
@app.route("/get-accident-hotspots")
def get_accident_hotspots():
    db = db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        # More robust location parsing
        cursor.execute("""
            SELECT 
                TRIM(SUBSTRING_INDEX(location, ',', 1)) as lat,
                TRIM(SUBSTRING_INDEX(location, ',', -1)) as lng,
                COUNT(*) as count
            FROM closed_cases
            WHERE location LIKE '%,%'
            GROUP BY lat, lng
            HAVING COUNT(*) > 0
        """)
        hotspots = cursor.fetchall()
        
        # Validate coordinates
        valid_hotspots = []
        for hotspot in hotspots:
            try:
                lat = float(hotspot['lat'])
                lng = float(hotspot['lng'])
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    valid_hotspots.append(hotspot)
            except ValueError:
                continue
                
        return jsonify(valid_hotspots)
        
    except Exception as e:
        print(f"Error getting hotspots: {str(e)}")
        return jsonify([])
    finally:
        db.close()

if __name__ == "__main__":
    app.run(port=2600)
