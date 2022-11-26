/** @file pleasedontcrash.cpp
 *  This file contains an example which was used in lecture to show how to
 *  (not) crash an ESP32 or similar microcontroller running more than one
 *  task under FreeRTOS.
 */

#include <Arduino.h>
#include "PrintStream.h"

//Pin that will create a fast square wave
#define FAST_PIN 12

//Pin that will create a slow square wave
#define SLOW_PIN 13

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

/** @brief   Task which creates a slow square wave
 *  @details This task creates a squsare wave at 5Hz and 50% duty cycle.
 *  @param   p_params A pointer to parameters passed to this task. This 
 *           pointer is ignored; it should be set to @c NULL in the 
 *           call to @c xTaskCreate() which starts this task
 */
void task_slow (void* p_params)
{
    pinMode(SLOW_PIN, OUTPUT);
    while (true){
        digitalWrite(SLOW_PIN, HIGH);
        vTaskDelay(100);
        digitalWrite(SLOW_PIN, LOW);
        vTaskDelay(100);
    }

}

void task_dash (void* p_params)
{
    Serial << "Dash is running" << endl;

    // Every task must contain an infinite loop, or things will crash.
    // Most tasks contain a vTaskDelay() or vTaskDelayUntil() call; 
    // otherwise they may read a queue and delay until the queue has
    // data in it.
    while (true)
    {
        Serial << '-';
        vTaskDelay (783);
    }
}


/** @brief   Task which prints dots now and then.
 *  @details This task prints a hello message, then prints dots until the
 *           microcontroller's power is turned off.
 *  @param   p_params An unused pointer to (no) parameters passed to this task
 */
void task_dot (void* p_params)
{
    Serial << "Dots is running" << endl;

    for (;;)
    {
        Serial << '.';
        vTaskDelay (1300);
    }
}


/** @brief   The Arduino setup function.
 *  @details This function is used to set up the microcontroller by starting
 *           the serial port, saying hello, and creating the tasks.
 */
void setup (void) 
{
    // The serial port must begin before it may be used
    Serial.begin (115200);
    while (!Serial) 
    {
    }
    Serial << "Hello, SLO Town." << endl;
    // Create the task which prints dashes. The stack size should be large
    // enough to prevent the program from crashing no matter what the inputs
    //xTaskCreate (task_dash, "Dashes", 1024, NULL, 3, NULL);
    
    // Create the task which prints dots. This task has a higher priority than
    // the dashes task because dots are better (nobody knows why)
    //xTaskCreate (task_dot, "Dots", 2048, NULL, 5, NULL);

    xTaskCreate (task_fast, "Fast Pin", 2048, NULL, 7, NULL);
    xTaskCreate (task_slow, "Slow Pin", 2048, NULL, 6, NULL);
}


/** @brief   The Arduino loop function.
 *  @details This function is called periodically by the Arduino system. It
 *           runs as a low priority task. On some microcontrollers it will
 *           crash when FreeRTOS is running, so we usually don't use this
 *           function for anything, instead just having it delay itself. 
 */
void loop (void)
{
    // Delay for a whole minute, which is an eternity to a microcontroller
    vTaskDelay (1000);
}

