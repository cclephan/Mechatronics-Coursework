#include <Arduino.h>
#include "PrintStream.h"
#include "task_debounce.h"

//Pin that will create a fast square wave
#define FAST_PIN 12

/** @brief   Task which creates a fast square wave
 *  @details This task creates a squsare wave at 500Hz and 50% duty cycle.
 *  @param   p_params A pointer to parameters passed to this task. This 
 *           pointer is ignored; it should be set to @c NULL in the 
 *           call to @c xTaskCreate() which starts this task
 */
void task_fast (void* p_params)
{
    pinMode(FAST_PIN, OUTPUT);
    while (true){

        digitalWrite(FAST_PIN, HIGH);
        vTaskDelay(1);
        digitalWrite(FAST_PIN, LOW);
        vTaskDelay(1);
    }
    
}

void setup() {
    //Begin serial communication
    Serial.begin (115200);
    while (!Serial) 
    {
    }
    //Say hello to SLO folks
    Serial << "Hello, SLO Town." << endl;
    //Run task creating PWM
    xTaskCreate (task_fast, "Fast Pin", 2048, NULL, 5, NULL);
    //Run debounce button task
    xTaskCreate (task_debounce, "Debounce Button", 2048, NULL, 2, NULL);

}

void loop() {
  // put your main code here, to run repeatedly:
}