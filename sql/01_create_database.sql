-- Create the database
CREATE DATABASE IF NOT EXISTS project_db;
USE project_db;

-- Create the ClimateData table
CREATE TABLE IF NOT EXISTS ClimateData (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    location VARCHAR(100) NOT NULL,
    record_date DATE NOT NULL,
    temperature FLOAT NOT NULL,
    precipitation FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    INDEX idx_location_date (location, record_date),
    INDEX idx_temperature (temperature)
); 