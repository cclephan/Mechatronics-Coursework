#include <Arduino.h>
#include "PrintStream.h"
#include "motor_driver.h"

#define OUTA 36
#define OUTB 39

bool OUTA_val1 = digitalRead(OUTA);
bool OUTA_val2 = digitalRead(OUTA);
bool OUTB_val1 = digitalRead(OUTB);
int32_t counter = 0;
float calib_coeff = (3.4/4096)/2; //converting ticks to revolutions
float rev_to_mm = 2*3.1415*3;
float pos = 0;
int16_t my_duty = 50;
float encoder_pos = 0;
float spot_distance = (22.5-6)*25.4; //(distance from bench to highest rack - depth of persons chest) * inch-to-millimeters


void update_pos(){
  OUTA_val1 = digitalRead(OUTA);
  if (OUTA_val1 != OUTA_val2 && OUTA_val1 == 1){
    if (OUTB_val1 == OUTA_val1){
      counter ++;
    }
    else{
      counter --;
    }
  }
  OUTA_val2 = OUTA_val1;
}

void setup() {
  Serial.begin (115200);
  while (!Serial) 
  {
  }
  MotorDriver motor;

  pinMode(OUTA, INPUT);
  pinMode(OUTB, INPUT);
  OUTA_val2 = digitalRead(OUTA);
  motor.set_duty(my_duty);

  //Encoder Setup
  attachInterrupt(OUTA, update_pos, CHANGE);
  attachInterrupt(OUTB, update_pos, CHANGE);
}


void loop() {
  vTaskDelay(500);
  encoder_pos = counter*calib_coeff*rev_to_mm; //convert ticks to revolutions and revolutions to millimeters
  if (my_duty > 0){    //if duty is positive flip sign
      encoder_pos *= -1;
  }
  Serial << "Motor Position: " << encoder_pos << "mm"<< endl;
  // put your main code here, to run repeatedly:
}