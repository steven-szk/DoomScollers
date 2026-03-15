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
    
