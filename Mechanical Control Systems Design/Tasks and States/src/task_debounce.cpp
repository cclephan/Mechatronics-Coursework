/** @file task_debounce.cpp
 *  This file contains task debounce which utilizes GPIO pin 13 as
 *  a simulated pushbutton (input with pull up resistor) to switch
 *  through states. The task starts is state 0 where nothing will
 *  be printed unless the button is pressed (active low by connecting
 *  small resistor to ground from GPIO pin). Once the button is pressed
 *  ? characters are printed until it has been held for at least 5 seconds.
 *  After a 5 second press the state machine checks again whether the button is
 *  pressed printing an @ sign if pressed. Next, !s are printed while the button
 *  is held for at least 1 second consecutively, after which the state machine
 *  returns back to state 0.
 */

#include <Arduino.h>
#include "PrintStream.h"

//Defining states for tasks (same state machine for both tasks)
#define STATE_0 0
#define STATE_1 1
#define STATE_2 2
#define STATE_3 3

#include "task_debounce.h"

//Defining GPIO pin for button
const uint8_t BUTTON_PIN = 13;

//creating integer variables for count and state values
uint8_t count = 0;
uint8_t state = 0;

/** @brief   Task which runs button debounce FSM
 *  @details This task starts by printing nothing until a button is pressed,
 *           after which ?s are printed while the button is held down. If held
 *           for 5 seconds the FSM moves to printing an @ sign until the button 
 *           is pressed again. Next, !s are printed as long as the button is pressed
 *           and if held for 1 second the FSM goes back to it's initial state.
 *  @param   p_params An unused pointer to (no) parameters passed to this task
 */
void task_debounce(void* p_params)
{   
    pinMode(BUTTON_PIN, INPUT_PULLUP);      //Setting the button pin to be input with a pullup resistor
    while(1)
    {
        if (state == STATE_0){
            //If in state 0 reset the count such that the button must be held down consecutively for 5 seconds
            count = 0;
            //If the button is pressed go to state 1                      
            if (!digitalRead(BUTTON_PIN))    
            {
                state = STATE_1;   
            }
        }
        if (state == STATE_1){
            //Print ?, add 1 to the count, and check to make sure if the button is still being pressed (if not reset)
            Serial << "?";
            count++;
            if (digitalRead(BUTTON_PIN)){
                state = STATE_0;
            }
            //After 5 seconds (running task 100ms so once count reaches 50) go to state 2
            if (count == 50)
            {
                state = STATE_2;
            }
        }
        if (state == STATE_2){
            //Print @ sign to show we are now in state 2
            Serial << "@";
            //If the button is pressed we can reset the counter and move to state 3
            if (!digitalRead(BUTTON_PIN))
            {
                state = STATE_3;
                count = 0;
            }
        }
        if (state == STATE_3){
            //Print ! to show we are in state 3, add one to the count, and check to see if the button is still pressed
            Serial << "!";
            count++;
            if (digitalRead(BUTTON_PIN)){
                state = STATE_2;
            }
            //After 1 seconds (running task 100ms so once count reaches 10) go to state 0
            if (count == 10){
                state = STATE_0;
            }
        }
        //Run this task for the time it takes to run above state machine (really fast 1ms<) + 100ms
        vTaskDelay(100);
    }
}


