import time
import os
from phone_tracker import person_status
from eye_tracker import is_not_looking
from arduino_controller import ArduinoController

def main():
    DISTRACTION_THRESHOLD = 300  # 5 minutes until red alert
    '''
    looks at the batch of 5 photos, checks if any of them caught you slipping, 
    and sends the command.
    
    0 = GREEN (Locked in)
    1 = YELLOW (Eyes distracted and phone not on table, or phone detected (eyes unimportant))
    2 = RED + Vibrate (when yellow for 5 minutes)
    '''
    print("Starting Distraction Monitor...")
    arduino = ArduinoController(port='COM3') # Change COM3 if needed!, initiate arduino connection
    
    print("Waiting for camera.py to take the first 5 pictures...")
    while not os.path.exists("captured_images/photo_4.jpg"):
        time.sleep(1)
        
    # This variable stores when first got distracted
    yellow_start_time = None

    print("\nMonitoring active! Press Ctrl+C to stop.")

    try:
        while True:
            # Grab the latest reports from trackers
            phone_data = person_status()
            eye_data = is_not_looking()
            
            # heck if ANY of the 5 frames flagged a distraction
            # The trackers return tuples (True, "msg"), check index [0]
            phone_detected = any(status[0] for status in phone_data)
            eyes_wandering = any(status[0] for status in eye_data)
            
            phone_off_table = True # Placeholder - we can add this logic later based on the phone tracker data (e.g., if phone is detected but not on table, we might still consider it a distraction)
            '''EDIT THIS WITH ULTRASONIC OR MATLAB DATA'''

            # Distracted if: phone is detected OR eyes are wandering
            is_distracted = phone_detected or (eyes_wandering and phone_off_table)

            if not is_distracted:
                print("Locked in! Sending GREEN.")
                arduino.send_command(0)
                yellow_start_time = None  # Reset the 5-minute timer
                
            else:
                # If we just became distracted, start the stopwatch
                if yellow_start_time is None:
                    yellow_start_time = time.time()
                
                # Calculate how many seconds we've been in the Yellow state
                time_in_yellow = time.time() - yellow_start_time
                
                if time_in_yellow >= DISTRACTION_THRESHOLD:
                    print(f"Distracted for {DISTRACTION_THRESHOLD} seconds! Sending RED + VIBRATE.")
                    arduino.send_command(2)
                else:
                    # Still in the warning window
                    time_left = int(DISTRACTION_THRESHOLD - time_in_yellow)
                    min_left = time_left // 60
                    sec_left = time_left % 60
                    
                    reason = "Phone detected" if phone_detected else "Eyes wandering and phone not on table"
                    print(f"⚠️ {reason}! Sending YELLOW. (Red alert in {min_left}m {sec_left}s)")
                    arduino.send_command(1)

            # Wait 5 seconds before checking the next batch
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        arduino.close() #Close the Arduino connection when done

if __name__ == "__main__":
    main()