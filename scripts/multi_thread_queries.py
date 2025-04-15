import mysql.connector
import threading
import time
from datetime import datetime, timedelta
import random

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'project_db'
}

def insert_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        locations = ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Halifax']
        today = datetime.now().date()
        
        for _ in range(5):
            location = random.choice(locations)
            temperature = round(random.uniform(10, 25), 1)
            precipitation = round(random.uniform(0, 5), 1)
            humidity = round(random.uniform(40, 80), 1)
            
            query = """
            INSERT INTO ClimateData (location, record_date, temperature, precipitation, humidity)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (location, today, temperature, precipitation, humidity))
            conn.commit()
            print(f"Inserted data for {location}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error in insert_data: {e}")

def select_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
        SELECT location, AVG(temperature) as avg_temp, AVG(humidity) as avg_humidity
        FROM ClimateData
        WHERE temperature > 20
        GROUP BY location
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\nLocations with temperature > 20°C:")
        for row in results:
            print(f"Location: {row[0]}, Avg Temp: {row[1]:.1f}°C, Avg Humidity: {row[2]:.1f}%")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error in select_data: {e}")

def update_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        locations = ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Halifax']
        
        for location in locations:
            new_humidity = round(random.uniform(50, 90), 1)
            query = """
            UPDATE ClimateData
            SET humidity = %s
            WHERE location = %s
            """
            cursor.execute(query, (new_humidity, location))
            conn.commit()
            print(f"Updated humidity for {location} to {new_humidity}%")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error in update_data: {e}")

def main():
    # Create threads for each operation
    insert_thread = threading.Thread(target=insert_data)
    select_thread = threading.Thread(target=select_data)
    update_thread = threading.Thread(target=update_data)
    
    # Start all threads
    insert_thread.start()
    select_thread.start()
    update_thread.start()
    
    # Wait for all threads to complete
    insert_thread.join()
    select_thread.join()
    update_thread.join()

if __name__ == "__main__":
    main() 