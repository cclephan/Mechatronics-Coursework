#include <Arduino.h>
#include <PrintStream.h>
#include <Wire.h>
#include <cstdlib>
#include "taskqueue.h"
#include "shares.h"
#include "task_spot.h"
#include "task_motor.h"

const int MPU_ADDR = 0x68; // I2C address of the MPU-6050. If AD0 pin is set to HIGH, the I2C address will be 0x69.
const int MPU_ADDR2 = 0x69;
float calib_const = 1825.5; // Calibrating IMU 1 acceleration to m/s^2
float calib_const2 = 1485.2; // Calibrating IMU 2 acceleration to m/s^2
float thresh = 0.3; // Threshold to get rid of acceleration noise when IMU isn't moving
float vel = 0; // IMU 1 current velocity
float vel2 = 0; // IMU 2 current velocity
float vel_init = 0; //IMU 1 initial velocity
float vel_init2 = 0; //IMU 2 initial velocity

uint16_t vel_size = 200; //Number of acceleration values averaged to calculate velocity

int16_t accelerometer_x, accelerometer_y, accelerometer_z, accelerometer_z_2; // variables for accelerometer raw data
int16_t gyro_x, gyro_y, gyro_z; // variables for gyro raw data
int16_t temperature; // variables for temperature data

Queue<float> vel_queue(2, "Velocities");

void task_IMU(void* p_params){
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR); // Begins a transmission to the I2C slave (GY-521 board)
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0); // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU_ADDR2); // Begins a transmission to the I2C slave (GY-521 board)
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0); // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  while (1){
    for (uint8_t i = 0; i < vel_size; i++){
      //Reading IMU 1
      Wire.beginTransmission(MPU_ADDR);
      Wire.write(0x3F); // starting with register 0x3F (ACCEL_XOUT_H) 
      Wire.endTransmission(false); // the parameter indicates that the ESP32 will send a restart. As a result, the connection is kept active.
      Wire.requestFrom(MPU_ADDR, 2, true); // request a total of 2 registers
      accelerometer_z = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)
      float az = accelerometer_z/calib_const - 9.81;  //Adjusting acceleration in z to be 0 m/s^2

      //Reading IMU 2
      Wire.beginTransmission(MPU_ADDR2);
      Wire.write(0x3F); // starting with register 0x3F (ACCEL_ZOUT_H) 
      Wire.endTransmission(false); // the parameter indicates that the ESP32 will send a restart. As a result, the connection is kept active.
      Wire.requestFrom(MPU_ADDR2, 2, true); // request a total of 2 registers
      accelerometer_z_2 = Wire.read()<<8 | Wire.read();
      float az_2 = accelerometer_z_2/calib_const2 - 9.81; //Adjusting acceleration in z to be 0 m/s^2

      //Using threshold value to get rid of acceleration noise
      if (abs(az) < thresh || abs(az_2) < thresh){
        az = 0;
        az_2 = 0;
      }
      //Summing velocities together to eventually average over 1 second (v = v0 + a*dt)
        vel += az;
        vel2 += az_2;
        vTaskDelay(5);
    }
    //New velocity being averaged and adding to previous velocity
    vel = vel/vel_size + vel_init;
    vel2 = vel2/vel_size + vel_init2;

    //IMU loses track of velocity due to error propogation so if it is stopped it may still read nonzero values
    //that don't change so this condition checks for that and sets velocity back to 0
    if(vel < vel_init+.02 && vel > vel_init-0.02){
      vel = 0;
      vel2 = 0;
    }
    vel_init = vel;
    vel_init2 = vel2;

    // if (vel > 0){
    //   Serial << "UP" << endl;
    // }
    // if(vel < 0){
    //   Serial << "DOWN" << endl;
    // }
    // if(vel == 0){
    //   Serial << "STOPPED" << endl;
    // }
    Serial << "IMU 1: " << vel << " | IMU 2: " << vel2 << endl;

    vel_queue.put(vel2);
    vel_queue.put(vel);
  }
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  while (!Serial) { } 
  xTaskCreate(task_IMU, "IMU", 2048, NULL, 5, NULL);
  xTaskCreate(task_spot, "Ey you need a spot bro", 2048, NULL, 4, NULL);
  xTaskCreate(task_motor, "Motor go brrr", 2048, NULL, 3, NULL);

}

void loop() {
  // put your main code here, to run repeatedly:

}