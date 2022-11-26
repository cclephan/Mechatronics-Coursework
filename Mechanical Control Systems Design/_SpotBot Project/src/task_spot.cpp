#include <Arduino.h>
#include <PrintStream.h>
#include "task_spot.h"
#include "shares.h"

float r_vel;
float l_vel;
uint8_t state_spot = 0;
uint16_t timer_counter = 0;
uint16_t rep_counter = 0;
uint16_t spot_counter = 0;


Share<bool> spot_me_bro("Spot Trigger");

void task_spot(void* p_params){
    while(1){
        if(state_spot != 6){
            r_vel = vel_queue.get();
            l_vel = vel_queue.get();
        }
        if(state_spot == 0){
            timer_counter = 0;
            if(r_vel == 0 && l_vel == 0){
                state_spot = 1;
            }
        }
        if(state_spot == 1){
            timer_counter = 0;
            Serial << "Bar is racked" << endl;
            if(r_vel < 0 && l_vel < 0){
                state_spot = 2;
            }
            }
        if (state_spot == 2){
            Serial << "Bar is in descent | Rep timer: " << timer_counter << endl;
            timer_counter++;
            if ((r_vel < 0.04 && r_vel > -0.04) || (l_vel < 0.04 && l_vel > -0.04)){
                state_spot = 3;
            }
             if(timer_counter >= 12){
                state_spot = 5;
            }           
        }
        if (state_spot == 3){
            Serial << "Bar is stopped at chest | Rep timer: " << timer_counter << endl;
            timer_counter++;
            if(r_vel > 0 && l_vel > 0){
                state_spot = 4;
                
            }
            if(timer_counter >= 18){
                state_spot = 5;
            }
        }
        if (state_spot == 4){
            Serial << "Bar is going up | Rep timer: " << timer_counter << endl;
            timer_counter++;
            if (r_vel == 0 && l_vel == 0){
                rep_counter++;
                Serial << "Nice bench bro you've done " << rep_counter << " rep(s)" << endl;
                state_spot = 1;
            }
            if(timer_counter >= 18){
                state_spot = 5;
            }
        }
        if (state_spot == 5){
            Serial << "Rep failed spotting initiated" << endl;
            spot_me_bro.put(1);
            if(spot_complete.get()){
                state_spot = 6;
            }
        }
        if (state_spot == 6){
            Serial << "Spot finished reset slack" << endl;
        }
        vTaskDelay(50);
    }
}