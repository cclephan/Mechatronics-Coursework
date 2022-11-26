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
S2_PROMPT_P = 2
S3_PROMPT_I = 3
S4_PROMPT_D = 4
S5_PROMPT_VEL = 5
## @brief 30 seconds of time used in g command collecting data
DisplayPosisionTime = 30000
DisplayStepTime = 10000

## Motor Shares Index referances
ID = 0
POSITION = 1
VELOCITY = 2
REF_POSITION = 3
REF_VELOCITY = 4
IS_ZERO = 5
DIS_FAULT = 6
PID = 7
DUTY = 8


#Defines a class for our example FSM
class Task_User:
    ''' @brief                  Task user interface
        @details                Handles all serial communication between user and backend running on Nucleo. Creates
                                user friendly interface for all key commands and communicates with encoder task.
    '''
    
    def __init__(self,period, MotorShare1, MotorShare2):

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
        
        
        # @brief Shares all relevavant motor info
        # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
        self.MotorShare1 = MotorShare1
        self.MotorShare2 = MotorShare2
        
        ## @brief   Boolean that turns true once m command is sent by user
        self.buildDuty = [False,False]
        self.building = [0,0]
        
        ## @brief Variable for telling the current time
        self.endPrint = utime.ticks_ms()
        ## @brief   Boolean that turns true once g command is sent by user
        self.displayPos = [False,False]
        ## @brief Array for time data collected for g command
        self.tArray = [[],[]]
        ## @brief Array for position data collected for g command
        self.PosArray = [[],[]]
        
        self.VelArray = [[],[]]
        

    def run(self): 
        ''' 
        @brief              Runs helper functions for user task
        @details            Transitions through states for every period and prints out user interface. Depending on
                            current state runs through commands, such as at state 1 a key command is first read and
                            zero is returned after writing whether if its condition is met or not.
        @param              Period at which encoder updates defined by user in main.
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
                if(keyCommand[0] == b'1'[0]):
                    self.transition_to(S2_PROMPT_P)
                    self.MotorStepped = self.MotorShare1
                    print("Running State 2")
                elif(keyCommand[0] == b'2'[0]):
                    self.transition_to(S2_PROMPT_P)
                    self.MotorStepped = self.MotorShare2
                    print("Running State 2")
            elif (self.State == S2_PROMPT_P):
                keyCommand = self.read()
                P_value = self.askForNum(0, keyCommand, 0)
                if(P_value != 0):
                    self.P_value = P_value
                    self.transition_to(S3_PROMPT_I)
                    print("Running State 3")
            elif (self.State == S3_PROMPT_I):
                print("Running State 3")
                keyCommand = self.read()
                I_value = self.askForNum(0, keyCommand, 0)
                if(I_value != 0):
                    self.I_value = I_value    
                    self.transition_to(S4_PROMPT_D)
                    print("Running State 4")
            elif (self.State == S4_PROMPT_D):
                keyCommand = self.read()
                D_value = self.askForNum(0, keyCommand, 0)
                if(D_value != 0):
                    self.D_value = D_value    
                    self.transition_to(S5_PROMPT_VEL)
                    print("Running State 5")
            elif (self.State == S5_PROMPT_VEL):    
                keyCommand = self.read()
                Vel_value = self.askForNum(0, keyCommand, 0)
                if(Vel_value != 0):
                    self.Vel_value = Vel_value    
                    self.transition_to(S1_WAIT_FOR_KEYINPUT)
                    print("Running State 1")
                    self.MotorStepped.write(PID,[self.P_value,self.I_value,self.D_value])
                    self.MotorStepped.write(REF_VELOCITY,Vel_value)
                    print('Collecting Data...')
                    self.displayPos[self.MotorStepped.read(ID)-1] = True
                    ## @brief Sets initial time for collecting data with g command
                    self.to = utime.ticks_ms() 
                

    
    def write(self,keyCommand, MotorShare):
        ''' 
        @brief              Prints out results from a certain user command
        @details            Contains logic for all user commands and printing values such as the encoder position and
                            delta, which is shared by task encoder. Additionally returns zero boolean value if condition
                            is met (z is pressed).
        @param              Key command that is found by read function, used in logic
        @param              Tuple containing encoder position and delta value
        '''
        # Update tuple containing position and delta shared by task encoder
        pos = MotorShare.read(POSITION)
        vel = MotorShare.read(VELOCITY)
        num = MotorShare.read(ID) - 1
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
            self.building[num] = 0
            #MotorShare.write(DUTY,int(pwm))
            
        elif keyCommand == b'c'[0]:
            MotorShare.write(DIS_FAULT,True)
            print('Fault Fixed')
            
            
        if(self.displayPos[num]):
            self.recordGData(num,pos,vel,keyCommand == b's'[0])
            
        if(self.buildDuty[num]):
            outDuty = self.askForNum(num,keyCommand,duty)
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
    
    def askForNum(self,num,keyCommand,startNum):
        # correctly adjusts keycommand
        keyCommand = keyCommand - num*32;
        
        if (keyCommand>=b'0'[0] and keyCommand<=b'9'[0]):
            new = keyCommand - 48
            self.building[num] = self.building[num]*10 + new
        elif keyCommand == 127:
            self.building[num] = self.building[num]//10
        elif keyCommand == 46:
            self.building[num] =  self.building[num]/10
        elif keyCommand == 45:
            self.building[num] = -self.building[num]
        elif keyCommand == 13:
            self.buildDuty[num] = False
            return self.building[num]
        
        if(keyCommand != 32):
            print("\033c", end="")
            print("Enter % motor speed: " + str(self.building[num]))
        
        return startNum
        
    def recordGData(self,num,pos,vel,Stop):
        ## @brief Current time in ms
        tcur = utime.ticks_ms()   
        
        #Controls g command array formatting and printing, and once data recording finishes, resets array and g command condition
        if Stop or utime.ticks_diff(utime.ticks_add(self.to, DisplayPosisionTime), tcur) <= 0:
            print("Time (s), Position (rad), Velocity (rad/s)")
            for n in range(len(self.tArray[num])):
                print("{:}, {:}, {:}".format(self.tArray[num][n]/1000,self.PosArray[num][n],self.VelArray[num][n]))
            self.displayPos[num] = False
            self.tArray[num] = []
            self.PosArray[num] = []
            self.VelArray[num] = []
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
    