/*
 * Using two photocells on which 2 laser pointers are set, arduino counts how many people enter and how many people exit the area
 * delimited by these 2 lasers. Depending on which order the lasers are tripped, Arduino will print to serial a "+" or a "-".
 * It is the responsability of the server to actually maintain the correct number of people.
 */
#define LIGHT_TH 850
#define DETECTION_DURATION 300 // how much time to allow between the two lasers to activate.

// photocells attached to A0 and A1 analog input pins
int sens1 = 0;
int sens2 = 1;

int photocellReading;

int voltage = 2;

void setup(void) {
  Serial.begin(9600);
  Serial.setTimeout(1);

  pinMode(voltage, OUTPUT);
  digitalWrite(voltage, HIGH);
}
 
void loop(void) {
  int val;
//  while(true) {
//    val = analogRead(sens1);
//    Serial.print(val);
//    val = analogRead(sens2);
//    Serial.print(" ");
//    Serial.println(val);
//  }

  // Count how many people enter
  if(analogRead(sens1) < LIGHT_TH) {
    for(int i=0; i < DETECTION_DURATION; i++) {
      if(analogRead(sens2) < LIGHT_TH) {
        Serial.println("+");

        // make sure the person exits the second tripped laser; will have multiple false counts otherwise
        delay(100);
        while(analogRead(sens2) < LIGHT_TH) {}
        
        break;
        }
      delay(1);
    }
  }

  // Count how many people exit
  else if(analogRead(sens2) < LIGHT_TH) {
    for(int i=0; i < DETECTION_DURATION; i++) {
      if(analogRead(sens1) < LIGHT_TH) {
        Serial.println("-");
        
        // make sure the person exits the second tripped laser; will have multiple false counts otherwise
        delay(100);
        while(analogRead(sens1) < LIGHT_TH) {}
        break;
      }
      delay(1);
    }
  }
}
