#include <Wire.h>

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
float x_dps, y_dps, z_dps; // converted to degrees per second

const int X_LED = 6;
const int Y_LED = 5;
const int Z_LED = 3;

void setup()
{  
  Serial.begin(9600);
  while(!Serial);

  Wire.begin();
  
  Serial.println("starting up L3G4200D...");
  setupL3G4200D(2000); // Configure L3G4200  +/- 250, 500 or 2000 deg/sec

  delay(1500); //wait for the sensor to be ready 
  Serial.println("gyro ready");

  pinMode(X_LED, OUTPUT);
  pinMode(Y_LED, OUTPUT);
  pinMode(Z_LED, OUTPUT);
}

void loop()
{
  float lastX, lastY, lastZ;
  
  getGyroValues();  // reads raw x, y, and z values and updates with new values

  // convert raw values to degrees per second
  float sensitivity = 14.35; // LSB/deg/s for 2000 dps
  x_dps = x / sensitivity;
  y_dps = y / sensitivity;
  z_dps = z / sensitivity; 

  Serial.print("X: "); Serial.print(x_dps, 2);
  Serial.print("Y: "); Serial.print(y_dps, 2);
  Serial.print("Z: "); Serial.print(z_dps, 2);
  Serial.println();

  delay(100); //Just here to slow down the serial to make it more readable

  if (x_dps - lastX >= 1)
  {
    digitalWrite(X_LED, HIGH);
    lastX = x_dps;
  }
  else
  {
    digitalWrite(X_LED, LOW);
  }
  
  if (y_dps - lastY >= 1)
  {
    digitalWrite(Y_LED, HIGH);
    lastY = y_dps;
  }
  else
  {
    digitalWrite(Y_LED, LOW);
  }
    if (z_dps - lastZ >= 1)
  {
    digitalWrite(Z_LED, HIGH);
    lastZ = z_dps;
  }
  else
  {
    digitalWrite(Z_LED, LOW);
  }
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
// void getGyroValues(){

//   byte xMSB = readRegister(L3G4200D_Address, 0x29);
//   byte xLSB = readRegister(L3G4200D_Address, 0x28);
//   x = ((xMSB << 8) | xLSB);

//   byte yMSB = readRegister(L3G4200D_Address, 0x2B);
//   byte yLSB = readRegister(L3G4200D_Address, 0x2A);
//   y = ((yMSB << 8) | yLSB);

//   byte zMSB = readRegister(L3G4200D_Address, 0x2D);
//   byte zLSB = readRegister(L3G4200D_Address, 0x2C);
//   z = ((zMSB << 8) | zLSB);
// }

// int setupL3G4200D(int scale){
//   //From  Jim Lindblom of Sparkfun's code

//   // Enable x, y, z and turn off power down:
//   writeRegister(L3G4200D_Address, CTRL_REG1, 0b00001111);

//   // If you'd like to adjust/use the HPF, you can edit the line below to configure CTRL_REG2:
//   writeRegister(L3G4200D_Address, CTRL_REG2, 0b00000000);

//   // Configure CTRL_REG3 to generate data ready interrupt on INT2
//   // No interrupts used on INT1, if you'd like to configure INT1
//   // or INT2 otherwise, consult the datasheet:
//   writeRegister(L3G4200D_Address, CTRL_REG3, 0b00001000);

//   // CTRL_REG4 controls the full-scale range, among other things:

//   if(scale == 250){
//     writeRegister(L3G4200D_Address, CTRL_REG4, 0b00000000);
//   }else if(scale == 500){
//     writeRegister(L3G4200D_Address, CTRL_REG4, 0b00010000);
//   }else{
//     writeRegister(L3G4200D_Address, CTRL_REG4, 0b00110000);
//   }

//   // CTRL_REG5 controls high-pass filtering of outputs, use it
//   // if you'd like:
//   writeRegister(L3G4200D_Address, CTRL_REG5, 0b00000000);
// }

// void writeRegister(int deviceAddress, byte address, byte val) {
//     Wire.beginTransmission(deviceAddress); // start transmission to device 
//     Wire.write(address);       // send register address
//     Wire.write(val);         // send value to write
//     Wire.endTransmission();     // end transmission
// }

// int readRegister(int deviceAddress, byte address){

//     int v;
//     Wire.beginTransmission(deviceAddress);
//     Wire.write(address); // register to read
//     Wire.endTransmission();

//     Wire.requestFrom(deviceAddress, 1); // read a byte

//     while(!Wire.available()) {
//         // waiting
//     }

//     v = Wire.read();
//     return v;
// }
