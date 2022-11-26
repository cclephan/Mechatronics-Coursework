#include "motor_driver.h"
#include "task_motor.h"
#include "PrintStream.h"
#include "shares.h"
#include <Arduino.h>

#define OUTA 36
#define OUTB 39

uint8_t state = 0;
MotorDriver motor;
bool spot = 0;

bool OUTA_val1 = digitalRead(OUTA);
bool OUTA_val2 = digitalRead(OUTA);
bool OUTB_val1 = digitalRead(OUTB);
int32_t counter = 0;
float calib_coeff = (3.4/4096)/2; //converting ticks to revolutions
float rev_to_mm = 2*3.1415*3;
float pos = 0;
int16_t my_duty = 100;
float encoder_pos = 0;
float spot_distance = (22.5-8)*25.4; //(distance from bench to highest rack - depth of persons chest) * inch-to-millimeters

Share<bool> spot_complete("Is complete?");

/** @brief ISR that updates encoder count when there is a change in encoder digitalRead value
*/
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

void task_motor(void* p_params){
    pinMode(OUTA, INPUT);
    pinMode(OUTB, INPUT);
    attachInterrupt(OUTA, update_pos, CHANGE);
    attachInterrupt(OUTB, update_pos, CHANGE);
    while(1){
        if (state == 0){
            spot = spot_me_bro.get();
            if(spot){
                motor.set_duty(my_duty);
                state = 1;
            }
        }
        if (state == 1){
            encoder_pos = counter*calib_coeff*rev_to_mm; //convert ticks to revolutions and revolutions to millimeters
            if (my_duty > 0){    //if duty is positive flip sign
                encoder_pos *= -1;
            }
            Serial << encoder_pos << endl;
            if(encoder_pos >= spot_distance){ //Checks if motor has pulled passed distance between user and rack
                motor.stop();
                spot_complete.put(1); //Set spot complete share to true
                state = 0;
                spot_me_bro.put(0);
            }
        }
        vTaskDelay(50);
    }

}