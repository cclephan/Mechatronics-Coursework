'''
    @file Lab1.py
    @brief Instructs user on how to use program, then cycles through states of different LED light patterns
    @details First welcomes the user and instructs user on how to operate hardware (by pressing the blue button to cycle LED patterns).
             Once the user presses the button the first pattern is loaded (square wave pattern). Once it is pressed again the program
             changes states and the LED now displays a sinewave pattern. Once pressed again the state changes and the LED displays a
             sawtooth pattern. Once the button is pressed again the pattern changes back to square and the cycle repeats. To exit the
             program the user can press Ctrl+C. This is meant to be run on a Nucleo
    @author Christian Clephan
    @author John Bennett
    @date
'''

import time;
import pyb;
import math;
## Variable defining button state
ButtonPushed = False 

## Function checking when button is pressed and setting its respective value to true
def onButtonPressFCN(IRQ_src):
    ''' @brief A callback function that runs when the button is pressed
        @details When the button is pressed on the Nucleo board a variable defining if the button is pressed or not turns true.
        @param IRQ_src detects button presses by checking for high-to-low transition (falling edge) on PC13
    '''
    global ButtonPushed
    ButtonPushed = True
    
#"""
#Created on Tue Sep 28 13:02:25 2021
#
#@author: melab15
#"""
#
##The main progra should go at the bottom and run
## continuouusly until user exits
if __name__ =='__main__':

    ##  @brief The current state for this iteration of the FSM
    #   @details Defines what state the hardware is at and loops through code of the state action until a condition to change state occurs.
    State = 0
    ##  @brief Keeps track of the number of Cycles in the FSM
    runs = 0
    ##  @brief Keeps of current time
    tcur = -1
    ##  @brief Keeps of a single instance of time
    to = -1
    ##  @brief Keeps track of the time difference the current time,tcur and a single instance in time, to
    delt = tcur - to;    
    ##  @brief Value between 0-100 that commands LED brightness
    #   @details Integer that is used as a variable to define LED brightness for various patterns.
    P = 0
    
    ##  @brief Sets up Button
    #   @details Creates an object variable to a pin, which is the button (B1) on the Nucleo board, which can be used for user input.
    pinC13 = pyb.Pin (pyb.Pin.cpu.C13)
    try: # try a button Push if its already configured an error will occur so we scip it
        ButtonInt = pyb.ExtInt(pinC13, mode=pyb.ExtInt.IRQ_FALLING,pull=pyb.Pin.PULL_NONE, callback=onButtonPressFCN)
    except:
        print('')
    
    #sets up PIN/LED/Timer
    pinA5 = pyb.Pin (pyb.Pin.cpu.A5)
    tim2 = pyb.Timer(2, freq = 20000)
    t2ch1 = tim2.channel(1, pyb.Timer.PWM, pin=pinA5)
         
    while (True):
        #Attempt to run FSM unless Ctrl+c is hit
        try:
            tcur = time.ticks_ms()
            
            ## Keeps track of the time difference the current time,tcur and a single instance in time, to
            delt = tcur - to;
            
            if (State == 0):
                #Run the State 0 code
                print('Welcome, LED enthusiasts here is a blinking LED\n'
                      'with a variety of amazing patterns'
                      '\nClick the blue button (B1 on the Nucleo) to cycle through 3 patterns: \nSquare, Sinewave, and Sawtooth.'
                      '\nToo stop press Cntrl+C.')
                print('\nPRESS THE BLUE BUTTON TO START!!!!')
                
                State = 1; # Transisions to state 1
                
            elif (State == 1):
                #Run the State 1 code
                
                if ButtonPushed == True:
                    State = 2; # Transisions to state 2
                    to = tcur;
                    print('Square    Pattern Selected')
                    
            elif (State == 2):
                #Run the State 2 code       
                
                # Generates Square wave responce with a period of 1000 ms
                # We first divide each instance by half secodes and round down so every number is odd of even
                # Modulus makes every odd or even a 1 or 0 
                # Adject the ampletude to 100
                P = (((delt) // 500) % 2)*100
                
                
                if ButtonPushed == True:
                    State = 3 # Transisions to state 3
                    to = tcur;
                    print('Sinewave  Pattern Selected')
                    
            elif (State == 3):
                #Run the State 3 code
                
                # Generates Sine wave responce with a period of 10000 ms
                # Adject the peak to peak ampletude to 100 make the center of the sine wave 50
                P = 50*math.sin(2*math.pi*delt/10000) + 50

                if ButtonPushed == True:
                    State = 4  # Transisions to state 4
                    to = tcur;
                    print('Sawtooth  Pattern Selected')
                    
            elif (State == 4):
                #Run the State 4 code
                
                # Generates Sawtooth wave responce with a period of 1000 ms
                # delt increase P at a constant slope
                # Modulus makes every instance that exceeds 1s or 1000ms restart
                # Adject the ampletude to 100 by dividing by 10
                P = ((delt) % 1000) /10
                             
                if ButtonPushed == True:
                    State = 2  # Transisions to state 2
                    to = tcur;
                    print('Square    Pattern Selected')
                
            
            ButtonPushed = False
            t2ch1.pulse_width_percent(P) # Command LED
            runs += 1       # increments runs
        
        #If there is an interuption break
        except KeyboardInterrupt:
            break
        
    print('Program Terminating')
#  execfile('in.py')

    

        
    