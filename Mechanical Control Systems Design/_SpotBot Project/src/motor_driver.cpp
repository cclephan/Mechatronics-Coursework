/** @file motor_driver.cpp
 *  This program 
 * 
 *  @author Christian Clephan
 *  @date   11-16-22
 */

#include "motor_driver.h"

/** @brief   Constructor which creates a motor driver object.
 */
MotorDriver::MotorDriver (void)
{
  pinMode(INB1, OUTPUT);
  digitalWrite(INB1, HIGH);

  pinMode(INB2, OUTPUT);
  digitalWrite(INB2, LOW);

  pinMode(PWMB, OUTPUT);
}

void MotorDriver::set_duty(int16_t duty)
{
    if (duty >= 0){
        digitalWrite(INB1, HIGH);
        digitalWrite(INB2, LOW);
        analogWrite(PWMB, duty);
    }
    else{
        digitalWrite(INB1, LOW);
        digitalWrite(INB2, HIGH);
        analogWrite(PWMB, -duty); 
    }
}

void MotorDriver::stop(void){
    analogWrite(PWMB, 0);
}

void MotorDriver::SOS(void){
    digitalWrite(INB1, HIGH);
    digitalWrite(INB2, LOW);
    analogWrite(PWMB, MAX_DUTY);
}