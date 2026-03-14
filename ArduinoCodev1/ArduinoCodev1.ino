enum ledStateS {
  GREEN,
  YELLOW,
  RED,
  WHITE
};
//Ultrasonic Sensor
const int TRIG_PIN = 3; // Sends the sound wave
const int ECHO_PIN = 4; // Listens for the bounce

// Initial states
ledStateS led1State = GREEN;
ledStateS led2State = WHITE;
volatile bool Vibrate = false;

// --- STATE TRACKING VARIABLES ---
//initialize dummy value (-1) so update initially
ledStateS currentLed1State = (ledStateS)-1; 
ledStateS currentLed2State = (ledStateS)-1;
int currentVibrate = -1;

// Pinouts
const int VIB_MOTOR = 2;
const int LED1_R = 9;
const int LED1_G = 10;
const int LED1_B = 11;
const int LED2_R = 3; 
const int LED2_G = 5; 
const int LED2_B = 6;

//read serial buffer
void ReadSer() {
  // Package S,0-2
  if (Serial.available() >= 2) {
    if (Serial.read() == 'S') { // Check for header 'S' ASCII 83
      
      char val = Serial.read(); // Read as char to handle ASCII correctly
      
      // Update global target vars, ASCII chars or raw bytes
      if (val == '0' || val == 0) {
        led1State = GREEN;
        Vibrate = false;
      } else if (val == '1' || val == 1) {
        led1State = YELLOW;
        Vibrate = false;
      } else if (val == '2' || val == 2) {
        led1State = RED;
        Vibrate = true;
      }
    }
    // Flush the rest of the buffer eg. \n
    while (Serial.available()) {Serial.read();}
  }
}

//vibration set
void vibrate(bool vib) {
  if (vib) {
    digitalWrite(VIB_MOTOR, HIGH);
  } else {
    digitalWrite(VIB_MOTOR, LOW);
  }
}

//set led
void setRGB(int LEDR, int LEDG, int LEDB, ledStateS color) {
  // reset so don't mix with prev output
  digitalWrite(LEDR, LOW);
  digitalWrite(LEDG, LOW);
  digitalWrite(LEDB, LOW);

  switch (color) {
    case RED: 
      digitalWrite(LEDR, HIGH);
      break;
      
    case GREEN: 
      digitalWrite(LEDG, HIGH);
      break;
      
    case YELLOW: // Red + Green
      analogWrite(LEDR, 255);
      analogWrite(LEDG, 150);
      break;
    
    case WHITE: // all colors
      analogWrite(LEDR, 150);
      analogWrite(LEDG, 150);
      analogWrite(LEDB, 150);
      break;
      
    default: 
      break; 
  }
}

void readAndSendDistance() {
  // 1. Clear the trigger pin to ensure a clean pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // 2. Send a 10-microsecond HIGH pulse to trigger the sensor
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // 3. Measure how long the Echo pin stays HIGH (in microseconds)
  // A timeout of 30000us (~5 meters) prevents the code from hanging if no echo returns
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); 
  
  // 4. Calculate the distance in centimeters
  // Speed of sound is ~0.0343 cm per microsecond. 
  // We divide by 2 because the sound travels out AND back.
  int distanceCm = duration * 0.0343 / 2;
  
  // 5. Send the data to the laptop via Serial
  // I added a "D:" prefix so your laptop (or Python script) knows this is Distance data
  if (duration == 0) {
    Serial.println("D:Out of range"); // Handle the timeout gracefully
  } else {
    Serial.print("D:");
    Serial.println(distanceCm);
  }
}

void setup() {
  Serial.begin(9600);
  
  // Wait for the serial port to connect
  while (!Serial) {
    ;
  }
  Serial.println("Serial is ready. Send S0, S1, or S2.");

  pinMode(VIB_MOTOR, OUTPUT);
  pinMode(LED1_R, OUTPUT);
  pinMode(LED1_G, OUTPUT);
  pinMode(LED1_B, OUTPUT);
  pinMode(LED2_R, OUTPUT);
  pinMode(LED2_G, OUTPUT);
  pinMode(LED2_B, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Initial states will be set automatically in the first loop!
}

void loop() {
  // Read serial and update target variables
  ReadSer();

  // only update led and vib if state changes
  if (led1State != currentLed1State) {
    setRGB(LED1_R, LED1_G, LED1_B, led1State);
    currentLed1State = led1State; // Save the new state
  }
  if (led2State != currentLed2State) {
    setRGB(LED2_R, LED2_G, LED2_B, led2State);
    currentLed2State = led2State; // Save the new state
  }
  if (Vibrate != currentVibrate) {
    vibrate(Vibrate);
    currentVibrate = Vibrate; // Save the new state
  }

}