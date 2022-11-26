"""!
    @file main.py
    @brief This file contains functions and a test scrip to fluctuate LED brightness
    @details Functions within this file set up an LED pin on the Nucleo and fluctuates the PWM. The test script
             uses these two functions to create a sawtooth pattern for LED brightness.The user can end the program by 
             pressing control+c.
    @author Christian Clephan
    @author Kyle McGrath
    @date January 11th, 2022
"""

import pyb
import time

def led_setup():
    """!
        @brief Sets up LED pin on Nucleo
        @details Creates object for the LED pin A0 on the Nucleo, a timer used by the Nucleo, and finally the channel
                 to relate the timer and LED pin. 
        @return Timer channel used to control PWM
    """
    ## @brief Configures LED pin A0 on Nucleo
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    ## @brief Configures Nucleo timer at extreme high frequency so it appears always on while the pin is set to high.
    tim2 = pyb.Timer(2, freq = 20000)
    ## @brief Configures relationship between timer and LED pin
    ch2 = tim2.channel(1, pyb.Timer.PWM_INVERTED, pin=pinA0)
    return ch2
    
def led_brightness(P,ch):
    """!
        @brief Controls PWM of a channel based on parameter P.
        @param P is the PWM value being used by the channel.
        @param ch is the channel to change PWM.
    """
    ch.pulse_width_percent (P)
    
if __name__ == "__main__":
    ## @brief Setting up channel for LED
    ch2 = led_setup()
    ## @brief Initial time, which will be used to create sawtooth wave.
    t0 = time.ticks_ms()
    while True:
        try:
            ## @brief Current time, also used to create sawtooth wave.
            tcur = time.ticks_ms()
            ## @brief Difference between when program was started and current time.
            tdif = time.ticks_diff(tcur,t0)
            led_brightness((tdif%5000)/50,ch2)
        except KeyboardInterrupt:
            break
    print('Program End')
