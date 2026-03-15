enum ledStateS {
  GREEN,
  YELLOW,
  RED,
  WHITE
};

// --- FIX 1: Changed pins to avoid conflict with LED2 ---
const int TRIG_PIN = 7; // Sends the sound wave
const int ECHO_PIN = 8; // Listens for the bounce

// Initial states
ledStateS led1State = GREEN;
ledStateS led2State = WHITE;
volatile bool Vibrate = false;

// --- STATE TRACKING VARIABLES ---
ledStateS currentLed1State = (ledStateS)-1; 
ledStateS currentLed2State = (ledStateS)-1;
int currentVibrate = -1;

// --- FIX 2: Added a timer variable for the sensor ---
unsigned long lastSonarTime = 0;
const unsigned long sonarInterval = 500; // Send distance every 500ms (half a second)

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
  if (Serial.available() >= 2) {
    if (Serial.read() == 'S') { 
      char val = Serial.read(); 
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
  digitalWrite(LEDR, HIGH);
  digitalWrite(LEDG, HIGH);
  digitalWrite(LEDB, HIGH);

  switch (color) {
    case RED: 
      digitalWrite(LEDR, LOW);
      break;
    case GREEN: 
      digitalWrite(LEDG, LOW);
      break;
    case YELLOW: 
      analogWrite(LEDR, 150);
      analogWrite(LEDG, 0);
      break;
    case WHITE: 
      analogWrite(LEDR, 180);
      analogWrite(LEDG, 100);
      analogWrite(LEDB, 100);
      break;
    default: 
      break; 
  }
}

// Your exact function, untouched!
void readAndSendDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 20000); 
  int distanceCm = duration * 0.0343 / 2;
  
  if (duration == 0) {
    Serial.println("D:Out of range"); 
  } else {
    Serial.print("D:");
    Serial.println(distanceCm);
  }
}

void setup() {
  Serial.begin(9600);
  
  while (!Serial) { ; }
  Serial.println("Serial is ready. Send S0, S1, or S2.");

  pinMode(VIB_MOTOR, OUTPUT);
  pinMode(LED1_R, OUTPUT);
  pinMode(LED1_G, OUTPUT);
  pinMode(LED1_B, OUTPUT);
  pinMode(LED2_R, OUTPUT);
  pinMode(LED2_G, OUTPUT);
  pinMode(LED2_B, OUTPUT);
  
  // Setup sonar pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  // 1. Read commands from Python
  ReadSer();

  // 2. Update LEDs/Vibration if the state changed
  if (led1State != currentLed1State) {
    setRGB(LED1_R, LED1_G, LED1_B, led1State);
    currentLed1State = led1State; 
  }
  if (led2State != currentLed2State) {
    setRGB(LED2_R, LED2_G, LED2_B, led2State);
    currentLed2State = led2State; 
  }
  if (Vibrate != currentVibrate) {
    vibrate(Vibrate);
    currentVibrate = Vibrate; 
  }

  // --- FIX 3: Check if 500ms have passed, then send distance ---
  if (millis() - lastSonarTime >= sonarInterval) {
    readAndSendDistance();
    lastSonarTime = millis(); // Reset the stopwatch
  }
}