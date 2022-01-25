# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 13:07:01 2021

@author: johna
"""

import pyb

CommReader = pyb.USB_VCP()

S0_INIT = 0
S1_WAIT_FOR_KEYINPUT = 1



#Defines a class for our example FSM
class Task_User:
    ''' @brief                  Interface with quadrature encoders
        @details
    '''
    
    def __init__(self):

        ''' 
        @brief              Constructs an encoder object
        @details
        
        '''
        ## The Current state for this iterations of the FSM
        self.State = S0_INIT

    def run(self):        
        
        
        if (self.State == S0_INIT):
            #Run the State 0 code
            print("_____USER COMMANDS INTERFACE_____\n"
                  "z:   Zero the position of encoder\n"
                  "p:   Print out the position of encoder\n"
                  "d:   Print out the delta for encoder\n"
                  "g:   Collect encoder 1 data for 30 seconds and print it to PuTTY as a comma separated list\n"
                  "s:   End data collection prematurely\n"
                  "esc: Redisplay user command interface")
            
            self.transition_to(S1_WAIT_FOR_KEYINPUT) # Transisions to state 1
            
        elif (self.State == S1_WAIT_FOR_KEYINPUT):
            #Run the State 1 code      
            
            if(CommReader.any()):
                #Reads Most recent Command
                keyCommand = CommReader.read(1)
                
                # Clears Queue
                CommReader.read()
                
                # Goes back to State 0 the initial state when the esc key is hit
                if(keyCommand == b'\x1b'):
                    self.transition_to(S0_INIT)
                    return ''
                
                return keyCommand
            
        return ''
            
    def transition_to(self,new_state):
        self.State = new_state;