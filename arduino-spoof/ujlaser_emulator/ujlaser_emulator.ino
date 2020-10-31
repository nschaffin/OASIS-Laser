// Status variables
bool laser_enabled = false;
bool laser_active = false;
bool diode_external_trigger = false;
bool external_interlock = false;
bool resonator_over_temp = false;
bool electrical_over_temp = false;
bool power_failure = false;
bool ready_to_enable = false;
bool ready_to_fire = false;
bool low_power_mode = false;
bool high_power_mode = false;

#define DEFAULT_BURST_COUNT 31
#define DEFAULT_PULSE_MODE 0
#define DEFAULT_DIODE_TRIGGER 0
#define DEFAULT_PULSE_WIDTH 0.00014000
#define DEFAULT_PULSE_PERIOD 0.20000000
#define DEFAULT_REP_RATE 5.0;

unsigned int shot_count = 0;
unsigned int burst_count = DEFAULT_BURST_COUNT;
unsigned short pulse_mode = DEFAULT_PULSE_MODE;
unsigned short diode_trigger = DEFAULT_DIODE_TRIGGER;

const float diode_current = 110.00; // Latest models of QC ujlasers have this fixed
float pulse_width = DEFAULT_PULSE_WIDTH;
float pulse_period = DEFAULT_PULSE_PERIOD;
float rep_rate = DEFAULT_REP_RATE;
float resonator_temp = -0.401; // NOTE: This value was taken while the diode was not connected.
float fet_temp = 34.082;
double bank_voltage = 0;

unsigned long fire_duration = 0; // This is in milliseconds
unsigned long last_fire = 0;
unsigned long last_disable = 0;
unsigned long last_command = 0;
const float discharge_time_constant = 29.41; // This is for modelling the time it takes for the bank voltage to discharge

#define ID_STRING "QC,MicroJewel,08130,1.0.9"

#define MIN_RR 0.100
#define MAX_RR 50.000

#define MIN_DW 0.00000100
#define MAX_DW 0.00024000

#define MIN_PE 0.02000000
#define MAX_PE 10.00000000

#define MIN_DC 1.000
#define MAX_DC 130.000

#define MIN_RT -0.401
#define MAX_RT 50.000

#define MAX_FT 125.000

//GPIO Pins
#define LED_PIN 8
#define INTERLOCK_PIN 4

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(INTERLOCK_PIN, INPUT);
  digitalWrite(LED_PIN, HIGH);
  delay(10);
  digitalWrite(LED_PIN, LOW);
  Serial.setTimeout(500);
}

void ok() {
  Serial.print("ok\r\n");
}

// Returns -1 if the scanned integer is negative, a float, or not a number
int scanNumber() {
  bool done = false;
  char buff[15];
  memset(buff, 0, 15);
  unsigned short i = 0;
  while(i < 14) {
    Serial.readBytes(&buff[i], 1);
    if(buff[i] == '.') {
      return -1;
    }
    if(buff[i] == '\r' || buff[i] == '\n' || buff[i] == ' ') {
      buff[i] = '\0';
      break;
    }
    if(buff[i] < 48 || buff[i] > 57) {
      buff[i] = '\0';
      break; // This isn't a numerical character
    }
    i++;
  }
  if(i == 0) {
    return -1; // None of the chatacters in the stream were numerical
  }
  return atoi(buff);
}

unsigned int get_status() {
  unsigned int i = 0;
  i += laser_enabled ? 1 : 0;
  i += laser_active ? 2 : 0;
  i += diode_external_trigger ? 8 : 0;
  i += external_interlock ? 0 : 64; // We're flip flopped.
  i += resonator_over_temp ? 128 : 0;
  i += electrical_over_temp ? 256 : 0;
  i += power_failure ? 512 : 0;
  i += ready_to_enable ? 1024 : 0;
  i += ready_to_fire ? 2048 : 0;
  i += low_power_mode ? 4096 : 0;
  i += high_power_mode ? 8192 : 0;
  return i;
}

char c;
char k[2];
char cmd[3];
void loop() {

  if (digitalRead(INTERLOCK_PIN) == HIGH) { // Check to see if the external interlock is connected or not
    external_interlock = true; // External interlock is connected
    if(power_failure || electrical_over_temp || resonator_over_temp) {
      ready_to_enable = false; // External interlock is connected, but we have errors/failures
      if(laser_enabled) {
        laser_enabled = false;
      }
    }
    else {
      ready_to_enable = true;
      if(laser_enabled) {
        ready_to_fire = true;
      }
    }
  }
  else { // External interlock is dicsconnected, so disable everything
    external_interlock = false;
    ready_to_enable = false;
    ready_to_fire = false;
    laser_enabled = false;
  }

  if(bank_voltage > 0 && !laser_enabled) {
    unsigned long time_delta = millis() - last_disable;
    //Serial.print(time_delta);
    if(time_delta % 100 == 0) { // Only do this expensive math every 100ms
      bank_voltage = 34 / pow(2.718, 1 * time_delta * 0.000034);
      if(bank_voltage < 0.002) {
        bank_voltage = 0;
      }
    }
  }

  if(laser_active) {
    unsigned long time_delta = millis() - last_fire;
    unsigned long timeout_delta = millis() - last_command;
    if(timeout_delta > 3000) { // Laser will timout after 3 seconds during long fire durations
      laser_active = false;
      digitalWrite(LED_PIN, LOW);
    }
    
    if(time_delta > fire_duration) {
      laser_active = false;
      digitalWrite(LED_PIN, LOW);
    }
  }

  c = 0;
  while(Serial.available() > 0) {
     c = Serial.read();
     if (c != ':') {
      continue;
     }
     
     if (Serial.readBytes(cmd, 2) < 2) {
      Serial.print("?1\r");
      continue;
     }
     last_command = millis();
    if (strcmp(cmd, "EN") == 0) {
      Serial.readBytes(k,1);
      if(*k == ' ') {
        int mode = scanNumber();
        if (mode == 0) {
          if(laser_enabled) {
            last_disable = millis();
          }
          laser_enabled = false;
          
          ok();
        }
        else if (mode == 1) {
          if(external_interlock && !power_failure && ready_to_enable) {
            laser_enabled = true;
            bank_voltage = 34.56;
            ok();
          }
          else {
            Serial.print("?8\r\n");
          }
        }
        else {
         Serial.print("?5\r\n");
        }
      }
      else if (*k == '?') {
        Serial.print(laser_enabled ? "1" : "0");
        Serial.print("\r\n");
      }
      else {
        Serial.print("?4\r\n");
      }
    }
    else if (strcmp(cmd, "BC") == 0) {
      Serial.readBytes(k,1);
      if(*k == ' ') {
        int i = scanNumber();
        if (i == -1){
          Serial.print("?5\r\n");
          continue;
        }
        else if(i < 1 || i > 65535) {
          Serial.print("?5\r\n");
          continue;
        }
        burst_count = i;
        ok();
      }
      else if (*k == '?') {
        Serial.print(burst_count, DEC);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?2\r\n");
      }
    }
    else if (strcmp(cmd, "SS") == 0) {
      Serial.readBytes(k,1);
      if(*k == '?') {
        Serial.print(get_status(), DEC);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "PE") == 0) {
      Serial.readBytes(k, 1);
      if(*k == '?') {
        Serial.print(pulse_period, 3);
        Serial.print("\r\n");
      }
      else if (*k == ' ') {
        float f = -1000;
        f = Serial.parseFloat();
        if (f == -1000) {
          Serial.print("?4\r\n");
          continue;
        }
        if(f < MIN_PE || f > MAX_PE) {
          Serial.print("?5\r\n");
          continue;
        }
        pulse_period = f;
        rep_rate = 1.0/f;
        ok();
      }
      else if (*k == ':') {
        char keyword[4];
        memset(keyword, 0, 4);
        if(Serial.readBytesUntil('?', keyword, 3) != 3){
          Serial.print("?5\r\n");
          Serial.flush();
          delay(200); // Idk why this must be here, but it makes it pass the test bench....... And yes, it must be 200ms, i tested it... idc
          continue;
        }
        if(strcmp(keyword, "MIN")==0) {
          Serial.print(MIN_PE);
          Serial.print("\r\n");
          continue;
        }
        else if(strcmp(keyword, "MAX")==0) {
          Serial.print(MAX_PE);
          Serial.print("\r\n");
          continue;
        }
        else {
          Serial.print("?3\r\n");
          continue;
        }
      }
      else {
        Serial.print("?5\r\n");
      }
    }
    else if (strcmp(cmd, "RR") == 0) {
      Serial.readBytes(k, 1);
      if(*k == '?') {
        Serial.print(rep_rate, 3);
        Serial.print("\r\n");
      }
      else if (*k == ' ') {
        float f = -1000;
        f = Serial.parseFloat();
        if (f == -1000) {
          Serial.print("?4\r\n");
          continue;
        }
        if(f < MIN_RR || f > MAX_RR) {
          Serial.print("?5\r\n");
          continue;
        }
        rep_rate = f;
        pulse_period = 1/f;
        ok();
      }
      else if (*k == ':') {
        char keyword[4];
        memset(keyword, 0, 4);
        if(Serial.readBytesUntil('?', keyword, 3) != 3){
          Serial.print("?5\r\n");
          Serial.flush();
          continue;
        }
        if(strcmp(keyword, "MIN")==0) {
          Serial.print(MIN_RR);
          Serial.print("\r\n");
          continue;
        }
        else if(strcmp(keyword, "MAX")==0) {
          Serial.print(MAX_RR);
          Serial.print("\r\n");
          continue;
        }
        else {
          Serial.print("?3\r\n");
          continue;
        }
      }
      else {
        Serial.print("?5\r\n");
      }
    }
    else if (strcmp(cmd, "DT") == 0) {
      Serial.readBytes(k, 1);
      if(*k == '?') {
        Serial.print(diode_trigger);
        Serial.print("\r\n");
      }
      else if (*k == ' ') {
        int i = scanNumber();
        if (i == -1){
          Serial.print("?5\r\n");
          continue;
        }
        if (i != 0 && i != 1) {
          Serial.print("?5\r\n");
          continue;
        }
        diode_trigger = i;          
        ok();
      }
      else {
        Serial.print("?5\r\n");
      }
    }
    else if (strcmp(cmd, "FL") == 0) {
      Serial.readBytes(k, 1);
      if(*k == '?') {
        Serial.print(laser_active ? 1 : 0);
        Serial.print("\r\n");
      }
      else if (*k == ' ') {
        int i = scanNumber();
        if (i == -1){
          Serial.print("?5\r\n");
          continue;
        }
        if (i != 0 && i != 1) {
          Serial.print("?5\r\n");
          continue;
        }
        if(!ready_to_fire){
          Serial.print("?8\r\n");
          continue;
        }
        else {
          laser_active = true;
          last_fire = millis();
          digitalWrite(LED_PIN, HIGH);
          fire_duration = burst_count * (pulse_period*1000);
          ok();
        }
      }
      else {
        Serial.print("?5\r\n");
      }
    }
    else if (strcmp(cmd, "PM") == 0) {
      Serial.readBytes(k, 1);
      if(*k == '?') {
        Serial.print(pulse_mode);
        Serial.print("\r\n");
      }
      else if (*k == ' ') {
        int i = scanNumber();
        if (i == -1) {
          Serial.print("?5\r\n"); // Parameter missing
          continue;
        }
        if(i != 0 && i != 1 && i != 2) {
          Serial.print("?5\r\n");
          continue;
        }
        pulse_mode = i;
        ok();
      }
      else {
        Serial.print("?5\r\n");
      }
    }
    else if (strcmp(cmd, "DW") == 0) {
      Serial.readBytes(k,1);
      if(*k == '?') {
        Serial.print(pulse_width, 8);
        Serial.print("\r\n");
      }
      else if (*k == ' ') {
        float f = -1000;
        f = Serial.parseFloat();
        if (f == -1000) {
          Serial.print("?4\r\n");
          continue;
        }
        if(f < MIN_DW || f > MAX_DW) {
          Serial.print("?5\r\n");
          continue;
        }
        pulse_width = f;
        ok();
      }
      else if (*k == ':') {
        char keyword[4];
        memset(keyword, 0, 4);
        if(Serial.readBytesUntil('?', keyword, 3) != 3){
          Serial.print("?5\r\n");
          Serial.flush();
          delay(200); // Idk why this must be here, but it makes it pass the test bench....... And yes, it must be 200ms, i tested it... idc
          continue;
        }
        if(strcmp(keyword, "MIN")==0) {
          Serial.print(MIN_DW);
          Serial.print("\r\n");
          continue;
        }
        else if(strcmp(keyword, "MAX")==0) {
          Serial.print(MAX_DW);
          Serial.print("\r\n");
          continue;
        }
        else {
          Serial.print("?3\r\n");
          continue;
        }
      }
      else {
        Serial.print("?5\r\n");
        continue;
      }
    }
    else if (strcmp(cmd, "SC") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(shot_count, DEC);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?5\r\n");
      }
    }
    else if (strcmp(cmd, "FT") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(fet_temp, 5);
        Serial.print("\r\n");
      }
      else if(*k == ':') {
        char keyword[4];
        memset(keyword, 0, 4);
        if(Serial.readBytesUntil('?', keyword, 3) != 3){
          Serial.print("?5\r\n");
          //Serial.flush();
          //delay(200); // Idk why this must be here, but it makes it pass the test bench....... And yes, it must be 200ms, i tested it... idc
          continue;
        }
        else if(strcmp(keyword, "MAX")==0) {
          Serial.print(MAX_FT, 3);
          Serial.print("\r\n");
          continue;
        }
        else {
          Serial.print("?3\r\n");
        }
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "IM") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(0.258, 5);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "FV") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(0.000, 5);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "BV") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(bank_voltage, 3);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "RS") == 0) {
      Serial.end();
      pulse_mode = DEFAULT_PULSE_MODE;
      diode_trigger = DEFAULT_DIODE_TRIGGER;
      pulse_width = DEFAULT_PULSE_WIDTH;
      pulse_period = DEFAULT_PULSE_PERIOD;
      rep_rate = DEFAULT_REP_RATE;
      burst_count = DEFAULT_BURST_COUNT;
      Serial.begin(115200);
    }
    else if (strcmp(cmd, "TR") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(resonator_temp, 3);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "ID") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(ID_STRING);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else if (strcmp(cmd, "LS") == 0) {
      Serial.readBytes(k,1);
      if (*k == '?') {
        Serial.print(external_interlock ? 0 : 64);
        Serial.print("\r\n");
      }
      else {
        Serial.print("?6\r\n");
      }
    }
    else {
      Serial.print("?1\r\n");
    }
  }
}
