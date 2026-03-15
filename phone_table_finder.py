import os
import pandas as pd

def PhoneUltrasonicOffTable(serial_data, threshold_cm=4):
    """
    Analyzes the Arduino's ultrasonic data to check if the phone is picked up.
    AND the Phone sensor data csv file
    
    Args:
        serial_data (str): The raw text from the Arduino (e.g., "D:15" or "D:Out of range").
        threshold_cm (int): If smaller, then on table. ALSO on table if Out of range
                            
    Returns:
        bool: True if phone is OFF the table, False if it is ON the table.
        None: If the data is empty or isn't a distance message.
    """
    # 1. Ignore empty data or messages that aren't from the ultrasonic sensor
    if not serial_data or not serial_data.startswith("D:"):
        return None 
        
    # 2. Extract the actual reading (Everything after the "D:")
    value_str = serial_data.split(":")[1].strip()
    
    # If out of range, then on table, ret false
    if value_str == "Out of range":
        return False
        
    try:
        distance = int(value_str)
        # If the distance is smaller than threshold, phone is on the table
        if distance < threshold_cm:
            return False
        else:
            # The phone is resting close to the sensor
            return False 
            
    except ValueError:
        # Just in case the Arduino sends a corrupted/garbled message
        print(f"Could not parse distance from: {serial_data}")
        return None

#read csv from phone sensor matlab code
def PhoneOrientationOffTable(file_path="PhoneSensorData.csv", threshold_deg=10):
    """
    Reads the phone sensor CSV data and checks if the tilt exceeds a threshold.
    
    Args:
        file_path (str): The path to the CSV file containing phone sensor data.
        threshold_deg (float): The angle threshold in degrees. If the phone's
                               tilt exceeds this, it is considered OFF the table.
                               
    Returns:
        bool: True if phone is OFF the table, False otherwise.
    """
    # 1. Check if the CSV actually exists
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return False
        
    try:
        # 2. Read the CSV data
        df = pd.read_csv(file_path)
        
        # Handle case where the CSV might be empty
        if df.empty:
            return False
            
        # 3. Get the most recent reading (the very last row)
        last_row = df.iloc[-1]
        
        # Extract the absolute angles of last row of csv
        left_right = abs(last_row['LeftRight_deg'])
        vertical = abs(last_row['Vertical_deg'])
        
        # 4. If either angle is greater than our threshold, you picked it up!
        if left_right > threshold_deg or vertical > threshold_deg:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")
        return False

def phone_off_table(serial_data, file_path="PhoneSensorData.csv"):
    """
    Combines both the ultrasonic and orientation checks to determine if the phone is off the table.
    
    Args:
        serial_data (str): The raw text from the Arduino's ultrasonic sensor.
        file_path (str): The path to the CSV file containing phone sensor data.
    Returns:
        bool: True if the phone is off the table, False otherwise.
    """
    # Check if the phone is off the table based on ultrasonic data
    ultrasonic_off = PhoneUltrasonicOffTable(serial_data)
    
    # Check if the phone is off the table based on orientation data
    orientation_off = PhoneOrientationOffTable(file_path)
    
    # If either check indicates the phone is off the table, return True
    return ultrasonic_off or orientation_off

if __name__ == "__main__":
    # Example usage:
    # Simulate some Arduino serial data
    test_serial_data = "D:15"  # Example distance reading (15 cm)
    
    # Check if the phone is off the table
    if phone_off_table(test_serial_data):
        print("Phone is OFF the table!")
    else:
        print("Phone is ON the table.")