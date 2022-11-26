'''
    @file task_User.py
    @brief User task file created with its own class to be accessed in main file.
    @details Task handles user interface, sending key commands to hardware task and recieving values such as ball and platform speed and position.   
    @author Christian Clephan
    @author John Bennett
    @date   December 8, 2021
'''

import utime

## @brief State 0 variable, Initializing state.
S0_INIT = 0
## @brief State 1 variable, Waiting for the user to input a key command.
S1_WAIT_FOR_KEYINPUT = 1

    
class Task_User:
    ''' @brief                  Task user interface
        @details                Handles all serial communication between user and backend running on Nucleo. Creates
                                user friendly interface for all key commands and communicates with encoder task.
    '''
   
    
    def __init__(self,period, Mode_Control_Share, State_Share, collectStatus, CommReader):

        ''' 
        @brief              Constructs an user task object
        @details            Instantiates period, a variable changing for every period, state, and variables used for 
                            actions and conditions in user commands.
        @param              Period at which user updates defined by user in main.
        @param              Mode_Control_Share controls control tasks mode tasks mode 0 being Ideal 1 is balance 
        @param              State_Share contains all the current variables to discribe the state
        @param              collectStatus controls the data collect task
        @param              CommReader Communication reader between PuTTY and Nucleo board so user can type commands
        '''
        ## @brief gets time in ms
        self.Time = utime.ticks_ms
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + self.Time()        
        ## @brief discribes current state
        self.State = S0_INIT
        
        ## @brief Controls control tasks mode tasks mode 0 being Ideal 1 is balance 
        self.mode_Share = Mode_Control_Share
        ## @brief Contains all the current variables to discribe the state
        self.state_Share = State_Share
        ## @brief Controls the data collect task
        self.collect_Status = collectStatus
        ## @brief Communication reader between PuTTY and Nucleo board so user can type commands
        self.CommReader = CommReader
        
        ## @brief if 1 continues to print data
        self.displayP = 0
                
    def run(self):
        ''' 
        @brief      Runs User task
        @details    Transitions through states for every period and prints out user interface. Once the user 
                    has finished with each prompt data collection is prepared and completed then transitions 
                    back to state one (wait for user input).
        '''

        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (self.Time() >= self.next_time):
            
            self.next_time += self.period
            
            if (self.State == S0_INIT):
                #Print user interface
                print("\033c", end="")
                print("_________USER COMMANDS INTERFACE_________\n\n"
                      "p:       Print out the position of the ball and the angle of the platform\n"
                      "P:       Toggels print display\n"
                      "g:       Collect data and print it as a comma separated list\n"
                      "s:       End data collection prematurely and print\n"
                      "_________________________________________\n"
                      "enter:   Toggle motors from on to off\n"
                      "esc  :   Redisplay user command interface")
                

                self.transition_to(S1_WAIT_FOR_KEYINPUT)
            elif self.State == S1_WAIT_FOR_KEYINPUT:
                ## @brief Stores returned key command from read function
                keyCommand = self.read()
                self.write(keyCommand[0])
            
            
    def write(self,keyCommand):
        ''' 
        @brief              Baised on a user command this code will interact with the rest of the shares
        @details            Contains logic for all user commands such as printing platform theta, ball position, and duty,
                            collecting data and turning off and on the motor. 
        @param              Key command found by read function, used in logic
        '''

        
        

        if self.displayP or keyCommand == b'p'[0]:
            (x,xd,y,yd,thx,thxd,thy,thyd,D1,D2) = self.state_Share.read()
            print("\033c_________State Data Display_________\n\n"
                  "Ball    :    x   = {:.2f}mm,\t\ty   = {:.2f}mm\n"
                  "Platform:    thx = {:.2E}rad,\t\tthy = {:.2E}rad\n"
                  "Duty    :    D1 = {:.2f}%,\t\tD2 = {:.2f}%\n\n".format(x,y,thx,thy,D1,D2),end="")
            
        # Goes back to State 0 the initial state when the esc key is hit
        if keyCommand == b'\x1b'[0]:
            self.transition_to(S0_INIT)
            
        # perminatly prints
        elif keyCommand == b'P'[0]:
            self.displayP ^= 1
            
        # records data 
        elif keyCommand == b'g'[0]:
            self.collect_Status.write([.1,25,[1,1,1,1,1,1,1,1,1,1]])
            print("recording data")
        # stops recording 
        elif keyCommand == b's'[0]: 
            self.collect_Status.read()[1] = -1 
        # toggles motor on to off   
        elif keyCommand == 13:
            self.mode_Share.read()[0] ^= 1
            print("Motor Mode: {:}".format(self.mode_Share.read()[0]))
                     
    def read(self):     
        ''' 
        @brief              Reads serial communication between user and Nucleo
        @details            CommReader detects if any communication is being sent by the user, and if so then it is read
                            and stored as a byte with variable keyCommand. The read function then clears the queue and
                            returns keyCommand byte value.
        '''       
        if(self.CommReader.any()):
            #Reads Most recent Command
            keyCommand = self.CommReader.read(1)
            # Clears Queue
            self.CommReader.read()  
            
            return keyCommand
        return b' ' 
    
    def transition_to(self,new_state):
        ''' 
        @brief              Transitions states
        @details            When called takes in parameter for whatever state needs to be transitioned to.
        @param              Next state to transition to.
        
        '''
        self.State = new_state;
            
