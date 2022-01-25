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
import array

## @brief Communication reader between PuTTY and Nucleo board so user can type commands
CommReader = pyb.USB_VCP()

## @brief State 0 variable, Initializing state
S0_INIT = 0
## @brief State 1 variable, Waiting for the user to input a key command
S1_WAIT_FOR_KEYINPUT = 1

## @brief 30 seconds of time used in g command collecting data
DisplayPosisionTime = 30000

## Motor Shares Index referances
## @brief Index reference for encoder number
ID = 0
## @brief Index reference for current position (rad)
POSITION = 1
## @brief Index reference for current velocity (rad/s)
VELOCITY = 2
## @brief Index reference for current duty (% PWM)
DUTY = 3
## @brief Index reference for boolean defining whether to zero encoder
IS_ZERO = 4
## @brief Index reference for boolean defining whether to disable fault
DIS_FAULT = 5


#Defines a class for our example FSM
class Task_User:
    ''' @brief                  Task user interface
        @details                Handles all serial communication between user and backend running on Nucleo. Creates
                                user friendly interface for all key commands and communicates with encoder task.
    '''
    
    def __init__(self,period, MotorShare1, MotorShare2):

        ''' 
        @brief              Constructs an user task object
        @details            Instantiates period, a variable changing for every period, state, and variables used for 
                            actions and conditions in user commands.
        @param              period is the period at which encoder updates defined by user in main.
        @param              MotorShare1 contains all shared values between tasks for motor 1
        @param              MotorShare2 contains all shared values between tasks for motor 2
        '''
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()
        
        ## @brief Sets the task to whatever state it is in based on FSM conditions
        self.State = S0_INIT
        
        
        ## @brief Shares all relevavant motor info for motor 1
        # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
        self.MotorShare1 = MotorShare1
        ## @brief Shares all relevavant motor info for motor 2
        self.MotorShare2 = MotorShare2
        
        ## @brief List containing flags that is turned true when the user presses m or M running through askForDuty function
        self.buildDuty = [False,False]
        ## @brief List containing integers for built duty
        self.building = [0,0]
        
        ## @brief Variable for telling the current time
        self.endPrint = utime.ticks_ms()
        ## @brief Boolean that turns true once g or G command is sent by user
        self.displayPos = [False,False]
        ## @brief Array for time data collected for g command
        self.tArray = [array.array('f',[]),array.array('f',[])]
        ## @brief Array for position data collected for g command
        self.PosArray = [array.array('f',[]),array.array('f',[])]
        ## @brief Array for velocity data collected for g command
        self.VelArray = [array.array('f',[]),array.array('f',[])]
        

    def run(self): 
        ''' 
        @brief              Runs helper functions for user task
        @details            Transitions through states for every period and prints out user interface. Depending on
                            current state runs through commands and writes key command to MotorShare list.
        '''
        # Checks if current time is past the current time plus the period before running
        if (utime.ticks_ms() >= self.next_time): ### need to fix
            #Resets new time for function to run
            self.next_time += self.period
            #Initialize condition
            if (self.State == S0_INIT):
                #Print user interface
                print("\033c", end="")
                print("_________USER COMMANDS INTERFACE_________\n\n"
                      "z or Z:   Zero the position of encoder\n"
                      "p or P:   Print out the position of encoder\n"
                      "d or D:   Print out the delta for encoder\n"
                      "m or M:   Prompt the user to enter a duty cycle for motor\n"
                      "g or G:   Collect encoder 1 data for 30 seconds and print it to PuTTY as a comma separated list\n"
                      "s or S:   End data collection prematurely\n"
                      "c or C:   Clears a fault condition triggered by the DRV8847\n"
                      "lower case commands == motor 1\n" 
                      "UPPER CASE COMMANDS == MOTOR 2\n"
                      "_________________________________________\n"
                      "esc: Redisplay user command interface")
                
                #Transitions to state 1
                self.transition_to(S1_WAIT_FOR_KEYINPUT) # Transisions to state 1
            #Checks if state 1 condition is met
            elif (self.State == S1_WAIT_FOR_KEYINPUT):
                #Run the State 1 code 
                ## @brief Stores returned key command from read function
                keyCommand = self.read()
                
                
                self.write(keyCommand[0],self.MotorShare1)   
                
                self.write(keyCommand[0] + 32, self.MotorShare2) 

    
    def write(self,keyCommand, MotorShare):
        ''' 
        @brief              Prints out results from a certain user command
        @details            Contains logic for all user commands and printing values such as the motor position and
                            velocity, which is shared by task encoder and motor.
        @param              keyCommand is a key command that is found by read function, used in logic
        @param              MotorShare is a tuple containing all shared values
        '''
        ## @brief Variable containing value of MotorShare array at position index
        pos = MotorShare.read(POSITION)
        ## @brief Variable containing value of MotorShare array at velocity index
        vel = MotorShare.read(VELOCITY)
        ## @brief Variable containing value of MotorShare array at motor ID index
        num = MotorShare.read(ID) - 1
        ## @brief Variable containing value of MotorShare array at duty index
        duty = MotorShare.read(DUTY)
        
        # Goes back to State 0 the initial state when the esc key is hit
        if keyCommand == b'\x1b'[0]:
            self.transition_to(S0_INIT)
            
        #Returns true for zero, which will then be shared with task encoder
        elif keyCommand == b'z'[0]:
            MotorShare.write(IS_ZERO,True)
        
        #Prints delta value from Update tuple
        elif keyCommand == b'd'[0]:
            print("Motor Velocity (rad/s): " + str(vel))                
        
        #Prints encoder position value from Update tuple
        elif (keyCommand == b'p'[0]):
            print("Motor Position (rad): " + str(pos)) 
            
        #Sets g command condition to true and starts clock for collecting data
        elif keyCommand == b'g'[0] and not self.displayPos[num]:
            print('Collecting Data...')
            self.displayPos[num] = True
            ## @brief Sets initial time for collecting data with g command
            self.to = utime.ticks_ms() 
        elif keyCommand == b'm'[0]:
            #pwm = input('Enter % motor speed: ')
            self.buildDuty[num] = True
            self.building[num] = ''
            #MotorShare.write(DUTY,int(pwm))
            
        elif keyCommand == b'c'[0]:
            MotorShare.write(DIS_FAULT,True)
            print('Fault Fixed')
            
            
        if(self.displayPos[num]):
            self.recordGData(num,pos,vel,keyCommand == b's'[0])
            
        if(self.buildDuty[num]):
            outDuty = self.askForDuty(num,keyCommand,duty)
            if(outDuty != duty):
                MotorShare.write(DUTY,outDuty)
        
        
        
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
            
            return keyCommand
        return b' '      
    
    def askForDuty(self,num,keyCommand,duty):
        ''' 
        @brief          Asks for a number from the user    
        @details        Adjusts keyCommand based on the motor ID (num) and only accepts values between 0 and 9.
                        Additionally takes in backspace, negative, or decimal command. Once the user finishes typing
                        their number they press enter and the number is returned. Otherwise the original duty is returned.
        @param          num is the motor ID subtracted by 1, so either a 0 for motor 1, or 1 for motor 2.
        @param          keyCommand is the read ASCII decimal value of character entered in PuTTY.
        @param          duty is the initial duty in MotorShares list.
        @return         duty is motor PWM duty
        @return         float(self.building[num]) is the float of whatever number was built by the user in entering their desired duty
        '''  
        keyCommand = keyCommand - num*32
        if (keyCommand>=b'0'[0] and keyCommand<=b'9'[0]):
            new = str(keyCommand-48)
            self.building[num] = self.building[num] + new
        elif keyCommand == 127:
            self.building[num] = self.building[num][:-1]
        elif keyCommand == 46:
            if "." not in self.building[num]:
                self.building[num] = self.building[num] + '.'
        elif keyCommand == 45:
            if self.building[num] == '' or self.building[num][0] != '-':
                self.building[num] = '-'+self.building[num]
        elif keyCommand == 13:
            self.buildDuty[num] = False
            if (self.building[num] == ''):
                self.building[num] = '0'
            return float(self.building[num])
        if(keyCommand != 32):
            print("\033c", end="")
            print("Enter % motor speed: " + str(self.building[num]))
        return duty
        
    def recordGData(self,num,pos,vel,Stop):
        ''' 
        @brief              Records data when g or G command is pressed
        @details            Sets the current time using utime library and appends data to time, position, and velocity
                            arrays based on current conditions. Once the stop condition (pressing s or S key) or the time
                            reaches passed 30 seconds the data collection stops and arrays are printed then reset.
        @param              num is the motor ID subtracted by 1, so either a 0 for motor 1, or 1 for motor 2.
        @param              pos is the shared position of motor position that is updated in task_encoder
        @param              vel is the shared velocity of motor velocity that is updated in task_encoder
        @param              Stop is flag boolean that turns true when the user enters an s or S key command.
        '''  
        ## @brief Current time in ms
        tcur = utime.ticks_ms()   
        
        #Controls g command array formatting and printing, and once data recording finishes, resets array and g command condition
        if Stop or utime.ticks_diff(utime.ticks_add(self.to, DisplayPosisionTime), tcur) <= 0:
            print("Time (s), Position (rad), Velocity (rad/s)")
            for n in range(len(self.tArray[num])):
                print("{:}, {:}, {:}".format(self.tArray[num][n]/1000,self.PosArray[num][n],self.VelArray[num][n]))
            self.displayPos[num] = False
            self.tArray[num] = array.array('f',[])
            self.PosArray[num] = array.array('f',[])
            self.VelArray[num] = array.array('f',[])
        #Appends data to each array
        else:
            self.tArray[num].append(utime.ticks_diff(tcur, self.to))
            self.PosArray[num].append(pos)
            self.VelArray[num].append(vel)
        
    def transition_to(self,new_state):
        ''' 
        @brief              Transitions states
        @details            When called takes in parameter for whatever state needs to be transitioned to.
        @param              Next state to transition to.
        
        '''
        self.State = new_state;
    