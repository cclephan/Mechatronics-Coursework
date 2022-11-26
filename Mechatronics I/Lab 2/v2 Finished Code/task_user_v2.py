'''
    @file task_user_v2.py
    @brief User task file created with its own class to be accessed in main2.py
    @details Task handles zero boolean value, that is shared with encoder task, and recieves shared update tuple on 
             encoder position and delta. Contains a read function to return a key command, write to print encoder data,
             and run, which handles FSM transitions and calling out read and write functions.           
    @author Christian Clephan
    @author John Bennett
    @date   October 16, 2021
'''

import utime
import pyb

## @brief Communication reader between PuTTY and Nucleo board so user can type commands
CommReader = pyb.USB_VCP()

## @brief State 0 variable, Initializing state
S0_INIT = 0
## @brief State 1 variable, Waiting for the user to input a key command
S1_WAIT_FOR_KEYINPUT = 1

## @brief 30 seconds of time used in g command collecting data
DisplayPosisionTime = 30000


#Defines a class for our example FSM
class Task_User:
    ''' @brief                  Task user interface
        @details                Handles all serial communication between user and backend running on Nucleo. Creates
                                user friendly interface for all key commands and communicates with encoder task.
    '''
    
    def __init__(self,period):

        ''' 
        @brief              Constructs an user task object
        @details            Instantiates period, , a variable changing for every period, state, and variables used for 
                            actions and conditions in user commands.
        @param              Period at which encoder updates defined by user in main.
        '''
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()
        
        ## @brief Sets the task to whatever state it is in based on FSM conditions
        self.State = S0_INIT
        
        ## @brief   Boolean that turns true once g command is sent by user
        self.displayPos = False
        ## @brief Variable for telling the current time
        self.endPrint = utime.ticks_ms()
        ## @brief Array for time data collected for g command
        self.tArray = []
        ## @brief Array for position data collected for g command
        self.PosArray = []

    def run(self, Update): 
        ''' 
        @brief              Runs helper functions for user task
        @details            Transitions through states for every period and prints out user interface. Depending on
                            current state runs through commands, such as at state 1 a key command is first read and
                            zero is returned after writing whether if its condition is met or not.
        @param              Period at which encoder updates defined by user in main.
        '''
        # Checks if current time is past the current time plus the period before running
        if (utime.ticks_ms() >= self.next_time): 
            #Resets new time for function to run
            self.next_time += self.period
            #Initialize condition
            if (self.State == S0_INIT):
                #Print user interface
                print("_____USER COMMANDS INTERFACE_____\n"
                      "z:   Zero the position of encoder\n"
                      "p:   Print out the position of encoder\n"
                      "d:   Print out the delta for encoder\n"
                      "g:   Collect encoder 1 data for 30 seconds and print it to PuTTY as a comma separated list\n"
                      "s:   End data collection prematurely\n"
                      "esc: Redisplay user command interface")
                #Transitions to state 1
                self.transition_to(S1_WAIT_FOR_KEYINPUT) # Transisions to state 1
            #Checks if state 1 condition is met
            elif (self.State == S1_WAIT_FOR_KEYINPUT):
                #Run the State 1 code 
                ## @brief Stores returned key command from read function
                keyCommand = self.read()
                ## @brief Stores boolean value if zero condition is met.       
                zero = self.write(keyCommand,Update)        
                return zero
            
        return False
    
    def write(self,keyCommand, Update):
        ''' 
        @brief              Prints out results from a certain user command
        @details            Contains logic for all user commands and printing values such as the encoder position and
                            delta, which is shared by task encoder. Additionally returns zero boolean value if condition
                            is met (z is pressed).
        @param              Key command that is found by read function, used in logic
        @param              Tuple containing encoder position and delta value
        '''
        # Update tuple containing position and delta shared by task encoder
        (pos,del_ticks) = Update
        ## @brief Current time in ms
        tcur = utime.ticks_ms()   
        
        #Controls g command array formatting and printing, and once data recording finishes, resets array and g command condition
        if self.displayPos == True and (keyCommand == b's' or utime.ticks_diff(utime.ticks_add(self.to, DisplayPosisionTime), tcur) <= 0):
            print("Time (s), Posision (ticks)")
            for n in range(len(self.tArray)):
                print("{:}, {:}".format(self.tArray[n]/1000,self.PosArray[n]))
            self.displayPos = False
            self.tArray = []
            self.PosArray = []
        
        #Appends data to each array
        elif (self.displayPos):
            self.tArray.append(utime.ticks_diff(tcur, self.to))
            self.PosArray.append(pos)
        
        #Sets g command condition to true and starts clock for collecting data
        elif keyCommand == b'g':
            print('Collecting Data...')
            self.displayPos = True
            ## @brief Sets initial time for collecting data with g command
            self.to = tcur
        
        #Returns true for zero, which will then be shared with task encoder
        if keyCommand == b'z':
            return True
        
        #Prints delta value from Update tuple
        elif keyCommand == b'd':
            print("Encoder Delta: " + str(del_ticks))                
        
        #Prints encoder position value from Update tuple
        elif (keyCommand == b'p'):
            print("Encoder Position: " + str(pos))             
        
        #Sets zero shared variable to false  
        return False            
                
        
        
        
    def read(self):     
        ''' 
        @brief              Reads serial communication between user and Nucleo
        @details            CommReader detects if any communication is being sent by the user, and if so then it is read
                            and stored as a byte with variable keyCommand. The read function then clears the queue and
                            returns keyCommand byte value. If the user wants to reread the user interface they can press
                            escape where state transitions back to 0 (initialize).
        '''       
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
        
            
    def transition_to(self,new_state):
        ''' 
        @brief              Transitions states
        @details            When called takes in parameter for whatever state needs to be transitioned to.
        @param              Next state to transition to.
        
        '''
        self.State = new_state;