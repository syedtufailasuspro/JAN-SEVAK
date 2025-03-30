CREATE DATABASE jan_sevak;
USE jan_sevak;

-- Active Cases Table
CREATE TABLE active_cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    accident_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(255),
    speed VARCHAR(20),
    gyroscope_data VARCHAR(255),
    assigned_ambulance VARCHAR(50),
    patient_condition VARCHAR(255),
    hospital_assigned VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Active'
);

-- Hospitals Table
CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    location VARCHAR(255),
    specialization VARCHAR(255),
    contact_number VARCHAR(20)
);

-- Closed Cases Table
CREATE TABLE closed_cases (
    case_id INT PRIMARY KEY,
    accident_time TIMESTAMP,
    close_time TIMESTAMP,
    location VARCHAR(255),
    patient_condition VARCHAR(255),
    hospital VARCHAR(255)
);
