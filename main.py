import time
import os

print("Importing log module")
from log import reset_file, write_file
print("Importing camera module")
from camera import capture_image, release_camera
print("Importing phone tracker")
from phone_tracker import person_status
print("Importing eye tracker")
from eye_tracker import is_not_looking
print("Importing phone table finder")
from phone_table_finder import is_phone_off_table
print("Importing Arduino controller")
from arduino_controller import ArduinoController


def main():
    DISTRACTION_THRESHOLD = 3  # 5 minutes until red alert
    '''
    looks at the batch of 5 photos, checks if any of them caught you slipping, 
    and sends the command.
    
    0 = GREEN (Locked in)
    1 = YELLOW (Eyes distracted and phone not on table, or phone detected (eyes unimportant))
    2 = RED + Vibrate (when yellow for 5 minutes)
    '''
    print("Starting Distraction Monitor...") #'COM12' for windows
    arduino = ArduinoController(port='/dev/cu.usbserial-10') # Change COM, initiate arduino connection
    yellow_start_time = None # This variable stores when first got distracted, none if currently locked in, timestamp if currently distracted

    reset_file()
    
    print("\nMonitoring active! Press Ctrl+C to stop.")

    try:
        phone_off_table = True # Assume phone is off the table at start, so we don't always get green if csv is empty and no serial reading
        while True:
            #Take a picture every some time and save it (overwriting the previous one)
            capture_image()
            
            # Grab the latest reports from trackers
            phone_data = person_status()
            eye_data = is_not_looking()
            
            # check if ANY of the frames flagged a distraction, essentially, only one frame is in the list
            # The trackers return tuples (True, "msg"), check index [0]
            phone_detected = any(status[0] for status in phone_data)
            eyes_wandering = any(status[0] for status in eye_data)
            
            arduino_message = arduino.read_serial()
            phone_off_table = is_phone_off_table(arduino_message, "PhoneSensorData.csv") #check if phone is off the table based on ultrasonic and orientation data

            # Distracted if: phone is detected OR eyes are wandering
            is_distracted = phone_detected or (eyes_wandering and phone_off_table) or ((eye_data[1] == "Looking Down") and phone_off_table )
            
 

            if not is_distracted:
                print("GREEN")
                arduino.send_command(0)
                yellow_start_time = None  # Reset the 5-minute timer
                # adds distracted state to matlab read file
                write_file("Green")
            else:
                # If we just became distracted, start the stopwatch
                if yellow_start_time is None:
                    yellow_start_time = time.time()
                
                # Calculate how many seconds we've been in the Yellow state
                time_in_yellow = time.time() - yellow_start_time
                
                if time_in_yellow >= DISTRACTION_THRESHOLD:
                    print(f"RED: Distracted for {DISTRACTION_THRESHOLD} seconds!")
                    # adds distracted state to matlab read file
                    write_file("Red")
                    arduino.send_command(2)
                else:
                    # Still in the warning window
                    time_left = int(DISTRACTION_THRESHOLD - time_in_yellow)
                    min_left = time_left // 60
                    sec_left = time_left % 60
                    
                    reason = "Phone detected" if phone_detected else "Eyes wandering and phone not on table"
                    print(f"YELLOW: {reason}! (Red alert in {min_left}m {sec_left}s)")
                    # adds distracted state to matlab read file
                    write_file("Yellow")
                    arduino.send_command(1)

            # Wait before checking the next batch
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        arduino.close() #Close the Arduino connection when done
        release_camera() #Release the camera when done
        

if __name__ == "__main__":
    main()