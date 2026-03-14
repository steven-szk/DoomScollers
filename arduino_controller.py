import serial
import time

class ArduinoController: #make the arduino controller a class so we can easily manage the connection and sending commands from main.py
    def __init__(self, port='COM3', baudrate=9600): #Default port and baudrate
        """
        Initializes the serial connection to the Arduino.
        Change 'COM3' to whatever port your Arduino is plugged into 
        (e.g., '/dev/ttyACM0' on Mac/Linux or 'COM5' on Windows).
        """
        self.port = port
        self.baudrate = baudrate
        self.arduino = None #This will hold the serial connection object if successfully connected
        
        try: #try to open the serial port
            # keep the connection open so the Arduino doesn't reset every time we send a command
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=1) 
            #The .arduino attribute will hold the serial connection object
            time.sleep(2)  # Give the Arduino 2 seconds to reboot after the serial connection opens
            print(f" Successfully connected to Arduino on {self.port}")
        except Exception as e:
            print(f" Failed to connect to Arduino: {e}")
            print("Running in simulation mode (commands will be printed but not sent).")

    def send_command(self, state_code):
        """
        Sends the state code to the Arduino.
        0 = GREEN (Locked in)
        1 = YELLOW (Eyes distracted and phone not on table, or phone detected (eyes unimportant))
        2 = RED + Vibrate (when yellow for 5 minutes)
        """
        command = f"S{state_code}"
        
        if self.arduino and self.arduino.is_open:
            # Send the command as bytes (e.g., b'S0')
            self.arduino.write(command.encode('utf-8'))
            print(f"Sentto Arduino: {command}")
        else:
            print(f"(Simulation): {command}")

    def close(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            print("Arduino connection closed.")
            

            
            
#Debug code
if __name__ == "__main__": 
    arduino_controller = ArduinoController()
    try:
        # Example usage: send a command every 5 seconds
        while True:
            arduino_controller.send_command(0)  # Simulate "Locked in"
            time.sleep(5)
            arduino_controller.send_command(1)  # Simulate "Distracted"
            time.sleep(5)
            arduino_controller.send_command(2)  # Simulate "Vibrate"
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping Arduino communication.")
    finally: #always close the connection when done
        arduino_controller.close()