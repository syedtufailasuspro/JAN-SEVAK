# JAN-SEVAK
JAN SEVAK is an accident response system that Automates the process of Ambulance end to end thereby reducing delays and increasing optimization.

JAN SEVAK - Emergency Accident Response System

**Problem Statement:**

Road accidents claim thousands of lives every year due to delays in accident reporting, inefficient ambulance assignment, misallocation of hospitals, and improper routing. In India alone, over 168,000 road accident deaths were reported in 2022, with nearly 40% of critical patients losing their lives due to the lack of timely ambulance services. More than 50% of accident victims do not receive help within the golden hour, significantly reducing their chances of survival.


**Team Members:**

1)Sabeer Sulaiman Khan G

2)Innocent Pious

3)Syed Tufail Ahmed

4)Virubash


**Solution Overview:**

JAN SEVAK is an automated accident response system designed to address inefficiencies in emergency medical services. It ensures quick accident detection, real-time ambulance dispatch, optimized routing, hospital assignment, and patient condition monitoring. The system leverages IoT devices, AI-based risk analysis, and a seamless communication network to optimize response times and save lives.

**Key Features:**

  1)Accident Detection & Ambulance Assignment:

    Uses smartphone sensors to detect accidents with 90% accuracy.

    Sends an alert message to the user.

    If no response is received, an ambulance is dispatched automatically.


  2)Ambulance Routing & Green Corridor Control:

    Determines the optimal route for the ambulance using real-time traffic data.

    Controls traffic signals to create a green corridor for the ambulance.


  3)Hospital Assignment & Patient Management:

    Assigns the nearest suitable hospital based on patient condition.

    Updates hospital staff through the JAN SEVAK portal.


  4)Real-time Patient Monitoring:

    Uses wearable devices to track vitals (heart rate, oxygen levels, etc.).

    Sends real-time health data to the hospital.


**Tech Stack**

  1)Hardware:


    Raspberry Pi
    
    ESP32
    
    Arduino Uno
    
    Relay Modules
    
    LED Indicators


  2)Software:

    Frontend: HTML, CSS, JavaScript
    
    Backend: Python (Flask)
    
    Database: Firebase, MongoDB
    
    Tracking: Google Maps API
    
    Communication: Telegram Bot, SMS

Setup & Run Instructions:

Follow the steps below to download and run the JAN SEVAK ambulance interface.

1️⃣ Download the Files

Clone or download the project files from the repository. If using Git, run:

git clone <your-repository-link>

Or manually download and extract the files.


2️⃣ Open Terminal & Navigate to Project Folder

Use the terminal (Command Prompt, PowerShell, or Linux/macOS terminal) and navigate to the project directory:

cd <project-folder>


3️⃣ Install Dependencies

Ensure Python is installed, then install the required packages:

pip install -r requirements.txt


4️⃣ Run the Backend (Flask App)

Start the backend by running:

python app.py

If running on Linux/macOS, you may use:

python3 app.py


5️⃣ Open the Web Interface

Once the server is running, open receive.html in a web browser (Chrome, Edge, Firefox, etc.).

Open manually by double-clicking receive.html.
