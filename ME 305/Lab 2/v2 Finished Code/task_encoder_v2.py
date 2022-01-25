'''
    @file task_encoder_v2.py
    @brief Encoder task created with its own class to be accessed in main2.py
    @details Task works with the encoder driver to zero the encoder if task user calls out for the encoder to be zero'd.
             Additionally the encoder position and delta is being updated at period specified in constructor.
    @author Christian Clephan
    @author John Bennett

    @date   October 16, 2021
'''

import utime
import encoder2
import pyb

## @brief Sets up first pin for encoder 1
pinB6 = pyb.Pin (pyb.Pin.cpu.B6)

## @brief Sets up second pin for encoder 1
pinB7 = pyb.Pin (pyb.Pin.cpu.B7)

#pinC6 = pyb.Pin (pyb.Pin.cpu.C6)
#pinC7 = pyb.Pin (pyb.Pin.cpu.C7)


#Defines a class for our example FSM
class Task_Encoder:
    ''' @brief                  Encoder task runninng encoder driver functions
        @details                Keeps track of encoder position and delta, while also setting calling the set position
                                function in driver to 0 when zero boolean is true.
    '''
    
    
    def __init__(self, period):

        ''' 
        @brief              Constructs an encoder task object
        @details            Instantiates period, a variable changing for every period, encoder object, and update tuple containing position and delta
        @param              Period at which encoder updates defined by user in main.
        
        '''
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()
        
        ## @brief Creates encoder object
        #  @details Creates encoder object with functionallity described in encoder driver file. Parameters for object dictate encoder pins and timer.
        self.encoder_1 = encoder2.Encoder(pinB6,pinB7,4)
        #self.encoder_2 = encoder2.Encoder(pinC6,pinC7,3)
        
        self.lastUpdate = (0,0)

    
    def run(self, zero):
        ''' 
        @brief      Runs encoder task zeroing encoder and updating position when necessary
        @details    Function that is run in main setting encoder position to 0 if it receives zero command from task user.
                    Task also updates encoder position/delta and returns the tuple to be used in user task if required.
        @param      Boolean value that is sent from user task to encoder task when the user wants to zero the encoder. If true the encoder is zero'd.
        '''
        # If zero command is True then encoder position is set to 0
        if zero:
            self.encoder_1.set_position(0)
        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (utime.ticks_ms() >= self.next_time):
            self.lastUpdate = self.nextUpdate()
            
        return self.lastUpdate
        
    def nextUpdate(self):
        ''' 
        @brief      Updates encoder position, updates next next time to an additional period.             
        @details    Encoder 1 is updated based on functionallity in encoder driver (setting position to the original position plus how far it has moved in the period).
                    Next time variable is updated to itself plus the period value that was instantiated. Function returns encoders new position and delta position in tuple.                
        '''
        self.encoder_1.update() 
        self.next_time += self.period
        return (self.encoder_1.get_position(),self.encoder_1.get_delta())
        