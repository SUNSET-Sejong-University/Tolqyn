/* Adopted from Jim Lindblom of Sparkfun's code */

#include <Wire.h>
#include <ArduinoBLE.h>

/* configuration registers from datasheet */
#define CTRL_REG1 0x20
#define CTRL_REG2 0x21
#define CTRL_REG3 0x22
#define CTRL_REG4 0x23
#define CTRL_REG5 0x24

/* hold the raw gyro readings */
#define OUT_X_L 0x28
#define OUT_X_H 0x29
#define OUT_Y_L 0x2A
#define OUT_Y_H 0x2B
#define OUT_Z_L 0x2C
#define OUT_Z_H 0x2D

const int L3G4200D_ADDR = 0x69; //I2C address of the L3G4200D

int16_t x, y, z; // 16-bit  signed integers
float lastX, lastY, lastZ;
float threshold = 20.0;
float x_dps, y_dps, z_dps; // converted to degrees per second

const int X_LED = 3;
const int Y_LED = 6;
const int Z_LED = 5;
const int DEBUG_LED = 8;
const int BUZZER_PIN = 9;
const float startTune[3] = {739.99, 659.25, 587.33};
const float endTune[3] = {587.33, 415.30, 440.00};

String serialCmd = "";

BLEService gyroService("180A"); // creating the service
BLECharacteristic gyroChar("2A57", BLERead | BLENotify, 32);

void setup()
{  
  Serial.begin(9600);
  while(!Serial);
  if(!BLE.begin()) while(1);

  Wire.begin();
  
  //Serial.println("starting up L3G4200D...");
  setupL3G4200D(2000); // Configure L3G4200  +/- 250, 500 or 2000 deg/sec

  delay(1500); //wait for the sensor to be ready 
  //Serial.println("gyro ready");

  pinMode(X_LED, OUTPUT);
  pinMode(Y_LED, OUTPUT);
  pinMode(Z_LED, OUTPUT);
  pinMode(DEBUG_LED, OUTPUT); 
  pinMode(BUZZER_PIN, OUTPUT);

  BLE.setLocalName("Tolkyn");
  BLE.setAdvertisedService(gyroService);

  gyroService.addCharacteristic(gyroChar);
  BLE.addService(gyroService);

  BLE.advertise();
}

void loop()
{
  BLEDevice central = BLE.central();
  if (central)
  {
    while (central.connected())
    {
      getGyroValues();

      char buffer[32];
      snprintf(buffer, sizeof(buffer), "%.2f,%.2f,%.2f\n", x_dps, y_dps, z_dps);
      gyroChar.writeValue((uint8_t*)buffer, strlen(buffer));

      delay(30);
    }
  }
  while (Serial.available())
  {
    char c  = Serial.read();
    if (c == '\n')
    {
      serialCmd.trim();
      if (serialCmd == "START")
      {
        noTone(BUZZER_PIN);
        playSound(startTune);
      }
      else if (serialCmd == "TERMINATE")
      {
        lastX = lastY = lastZ = 0;
        digitalWrite(X_LED, LOW);
        digitalWrite(Y_LED, LOW);
        digitalWrite(Z_LED, LOW);
        digitalWrite(DEBUG_LED, LOW);
        noTone(BUZZER_PIN);
        playSound(endTune);
      }
      serialCmd = "";
    }
    else
    {
      serialCmd += c;
    }
  }

  getGyroValues();  // reads raw x, y, and z values and updates with new values

  // convert raw values to degrees per second
  float sensitivity = 14.35; // LSB/deg/s for 2000 dps
  x_dps = x / sensitivity;
  y_dps = y / sensitivity;
  z_dps = z / sensitivity; 

  Serial.print(x_dps, 2); Serial.print(",");
  Serial.print(y_dps, 2); Serial.print(",");
  Serial.println(z_dps, 2);

  delay(100); //Just here to slow down the serial to make it more readable

  if (fabs(x_dps - lastX) >= threshold)
  {
    digitalWrite(X_LED, HIGH);
    lastX = x_dps;
  }
  else
  {
    digitalWrite(X_LED, LOW);
  }
  
  if (fabs(y_dps - lastY) >= threshold)
  {
    digitalWrite(Y_LED, HIGH);
    lastY = y_dps;
  }
  else
  {
    digitalWrite(Y_LED, LOW);
  }

  if (fabs(z_dps - lastZ) >= threshold)
  {
    digitalWrite(Z_LED, HIGH);
    lastZ = z_dps;
  }
  else
  {
    digitalWrite(Z_LED, LOW);
  }
  digitalWrite(DEBUG_LED, HIGH);
}


void setupL3G4200D(int scale)
{
  // enable x/y/z, normal mode, 100Hz
  writeRegister(CTRL_REG1, 0b00001111);

  // no high pass filter (HPF)
  writeRegister(CTRL_REG2, 0b00000000);

  // INT2 Data ready (optional)
  writeRegister(CTRL_REG3, 0b00001000);

  // full scale selection
  if (scale == 250)
  {
    writeRegister(CTRL_REG4, 0b00000000);
  }
  else if (scale == 500)
  {
    writeRegister(CTRL_REG4, 0b00010000);
  }
  else
  {
    writeRegister(CTRL_REG4, 0b00110000);
  }

  // high pass disabled
  writeRegister(CTRL_REG5, 0b00000000);
}

void getGyroValues()
{
  /* combine LSB to MSB, then cast to signed 16 bit */
  x = (int16_t)((readRegister(OUT_X_H) << 8) | readRegister(OUT_X_L));
  y = (int16_t)((readRegister(OUT_Y_H) << 8) | readRegister(OUT_Y_L));
  z = (int16_t)((readRegister(OUT_Z_H) << 8) | readRegister(OUT_Z_L));
}

void writeRegister(byte reg, byte val)
{
  Wire.beginTransmission(L3G4200D_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

byte readRegister(byte reg)
{
  Wire.beginTransmission(L3G4200D_ADDR);
  Wire.write(reg);
  Wire.endTransmission();

  Wire.requestFrom(L3G4200D_ADDR, 1); // read a byte
  while(!Wire.available());
  return Wire.read();
}

void playSound(const float* tune) {
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, tune[i]);
    delay(300);
  }
  noTone(BUZZER_PIN);
}

