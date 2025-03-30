import json
import firebase_admin
from firebase_admin import credentials, db
import gpiod  # GPIO access for Raspberry Pi
import time

# Firebase Setup
cred = credentials.Certificate("firebase_config.json")  # Update with your Firebase credentials file
firebase_admin.initialize_app(cred, {"databaseURL": "https://smart-home-automation-cd398-default-rtdb.asia-southeast1.firebasedatabase.app/"})

# GPIO Setup
chip = gpiod.Chip('gpiochip0')  # Use the correct GPIO chip (check with 'ls /dev/gpiochip*')
gpio_pins = {
    'hall_light': 17,  # Replace with the correct GPIO pins for your relays
    'bedroom_light': 27,
    'second_floor_light': 22,
    'second_floor_fan': 5,
    'ground_floor_light': 6,
    'street_light': 13
}

# Setup GPIO lines for relay control
lines = {}
for device, pin in gpio_pins.items():
    line = chip.get_line(pin)
    line.request(consumer="smart-home-relay", type=gpiod.LINE_REQ_DIR_OUT)
    lines[device] = line

# Firebase Listener
def firebase_listener(event):
    devices = db.reference("devices").get()  # Get devices data from Firebase
    if devices:
        for device_id, status in devices.items():
            # Get corresponding GPIO line for the device
            line = lines.get(device_id)
            if line:
                # If device status is "ON", turn on the relay (set pin HIGH)
                # If device status is "OFF", turn off the relay (set pin LOW)
                if status == "ON":
                    line.set_value(1)  # Set GPIO pin HIGH (ON)
                    print(f"{device_id} is now ON - Relay activated.")
                else:
                    line.set_value(0)  # Set GPIO pin LOW (OFF)
                    print(f"{device_id} is now OFF - Relay deactivated.")

# Attach Firebase listener (runs only when data changes)
db.reference("devices").listen(firebase_listener)

# Keep script running indefinitely
try:
    while True:
        time.sleep(1)  # Sleep to prevent 100% CPU usage, Firebase listener is working in the background
except KeyboardInterrupt:
    print("Script interrupted, closing.")