'''
    @file task_user_v2.py
    @brief User task file created with its own class to be accessed in main file.
    @details Task handles user interface, sending key commands to hardware task and recieving values such as motor speed and position.
             Runs through FSM for collecting data for user input step function and closed loop control.   
    @author Christian Clephan
    @author John Bennett
    @date   November 9, 2021
'''

import utime
import pyb
import array

## @brief Communication reader between PuTTY and Nucleo board so user can type commands
CommReader = pyb.USB_VCP()

## @brief State 0 variable, Initializing state.
S0_INIT = 0
## @brief State 1 variable, Waiting for the user to input a key command.
S1_WAIT_FOR_KEYINPUT = 1
## @brief State 2 for requesting prompts of PID and set-point velocity.
S2_PROMPT = 2
## @brief State 3 for time delay while recording data until the motors are run.
S3_DELAY = 3

## @brief 30 seconds of time used in g command collecting data
DisplayPosisionTime = 30000
## @brief 10 seconds of time used in Lab 4 step function data collection
DisplayStepTime = 10000

## @brief Prompts for user input step function
PID_Prompt = ["Enter Positional Gain (%-s/rad): ",
              "Enter Integral Gain (%/rad): ",
              "Enter Derivative Gain (%-s2/rad): ",
              "Enter Step Velocity (%-s2/rad): "]

## Motor Shares Index referances
## @brief Index reference for encoder number
ID = 0
## @brief Index reference for current position (rad)
POSITION = 1
## @brief Index reference for current velocity (rad/s)
VELOCITY = 2
## @brief Index reference for reference (previous) position (rad)
REF_POSITION = 3
## @brief Index reference for reference (previous) velocity (rad/s)
REF_VELOCITY = 4
## @brief Index reference for zero flag
IS_ZERO = 5
## @brief Index reference for disable fault flag
DIS_FAULT = 6
## @brief Index reference for PID controller
PID = 7
## @brief Index reference for current duty (% PWM)
DUTY = 8
## @brief Index reference for checking if there is a fault
IS_FAULT = 9


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
        @param              MotorShare1 contains all shared values for motor 1
        @param              MotorShare2 contains all shared values for motor 2
        '''
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()
        
        ## @brief Sets the task to whatever state it is in based on FSM conditions (Start at state 0)
        self.State = S0_INIT        
        
        ## @brief Shares all relevavant motor info
        # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
        self.MotorShare1 = MotorShare1
        self.MotorShare2 = MotorShare2
        
        ## @brief PID
        self.PID = [0,0,0]
        
        ## @brief Time at which PID gains will be written based on difference between itself and current time (time delay).
        self.tPID = 0
        
        ## @brief Index of PID gains of shared PID variable
        self.PIDInx = 0

    def run(self): 
        ''' 
        @brief              Runs helper functions for user task
        @details            Transitions through states for every period and prints out user interface. When the PID gains are changed
                            then a time delay of 1 second is implemented before setting the new motor duty cycle. State 2 occurs when
                            either a 1 or 2 is pressed where prompts tell the user to type the new PID gains/set-point velocity. Once
                            the user has finished with each prompt data collection is prepared and completed then transitions back to
                            state one (wait for user input).
        '''
        ## @brief Current time.
        tcur = utime.ticks_ms()
        # Checks if current time is past the current time plus the period before running
        if (tcur >= self.next_time): ### need to fix
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
                      "1 or 2    Set PID and run a step function on motor 1 or 2\n"
                      "lower case commands == motor 1\n" 
                      "UPPER CASE COMMANDS == MOTOR 2\n"
                      "_________________________________________\n"
                      "esc: Redisplay user command interface")
                
                #Transitions to state 1
                self.transition_to(S1_WAIT_FOR_KEYINPUT) # Transisions to state 1
                
                self.reset_states()
            #Checks if state 1 condition is met
            elif (self.State == S1_WAIT_FOR_KEYINPUT):
                #Run the State 1 code 
                ## @brief Stores returned key command from read function
                keyCommand = self.read()
                self.write(keyCommand[0],self.MotorShare1)   
                self.write(keyCommand[0] + 32, self.MotorShare2)
                
                if(self.PID != [0,0,0]):
                    
                    if utime.ticks_diff(tcur,self.tPID) >= 1000:
                        print("Motor Start")
                        self.MotorStepped.write(PID,self.PID)
                        self.PID = [0,0,0]
                        
                
                    
            elif (self.State == S2_PROMPT):
                keyCommand = self.read()
                ## @brief PID value that is built by askForNum method.
                PID_value = self.askForNum(0,keyCommand[0],PID_Prompt[self.PIDInx])
                if keyCommand == b'\x1b'[0]:
                    self.transition_to(S0_INIT)
                elif(PID_value != None):
                    if(self.PIDInx > 2):
                        #Transitions to state 1
                        self.MotorStepped.write(REF_VELOCITY,PID_value)
                        self.setuprecord(DisplayStepTime,self.MotorStepped.read(ID)-1,[DUTY, VELOCITY],'DUTY (%V), Velocity (rad/s)')
                        self.tPID = tcur
                        self.PIDInx = 0
                        ## @brief Built variable used in askForNum method.
                        self.building[0] = ''
                        
                        self.transition_to(S1_WAIT_FOR_KEYINPUT)
                        print("Running State 1") 
                    else:
                        self.building[0] = ''
                        self.PID[self.PIDInx] = PID_value
                        self.PIDInx += 1
                        self.askForNum(0,b'None'[0],PID_Prompt[self.PIDInx])

                

    
    def write(self,keyCommand, MotorShare):
        ''' 
        @brief              Prints out results from a certain user command
        @details            Contains logic for all user commands such as printing motor velocity/position, zeroing position, reseting faults,
                            collecting 30 seconds of data, and collecting 10 seconds of an impulse step function in closed loop control,
        @param              Key command that is found by read function, used in logic
        @param              MotorShare is a tuple containing all shared values.
        '''
        ## @brief Either a 0 or 1 depending on motor ID.
        num = MotorShare.read(ID) - 1
        
        # Goes back to State 0 the initial state when the esc key is hit
        if keyCommand == b'\x1b'[0]:
            self.transition_to(S0_INIT)
            
        #Returns true for zero, which will then be shared with task encoder
        elif keyCommand == b'z'[0]:
            print('Moter ' + str(num+1) + ', Has Been Zeroed.')
            MotorShare.write(IS_ZERO,True)
        
        #Prints delta value from Update tuple
        elif keyCommand == b'd'[0]:
            print('Moter ' + str(num+1) + ', Velocity (rad/s): ' + str(MotorShare.read(VELOCITY)))                
        
        #Prints encoder position value from Update tuple
        elif (keyCommand == b'p'[0]):
            print('Moter ' + str(num+1) + ', Position (rad): ' + str(MotorShare.read(POSITION))) 
            
        #Sets g command condition to true and starts clock for collecting data
        elif keyCommand == b'g'[0] and not self.displayPos[num]:
            self.setuprecord(DisplayPosisionTime,num,[POSITION, VELOCITY],'Position (rad), Velocity (rad/s)')
            
        elif keyCommand == b'm'[0]:
            #pwm = input('Enter % motor speed: ')
            self.buildDuty[num] = True
            self.building[num] = ''
            
        elif keyCommand == b'c'[0]:
            MotorShare.write(DIS_FAULT,True)
            print('Fault Fixed')
            
        elif keyCommand == b's'[0] or MotorShare.read(IS_FAULT):
            self.tf[num] = utime.ticks_ms()
            
        # Save Encoder Stuff   
        if(self.displayPos[num] and 0 == self.next_time%(2*self.period)//self.period):
            Data1 = MotorShare.read(self.toRecord[num][0])
            Data2 = MotorShare.read(self.toRecord[num][1])
            self.recordGData(num,Data1,Data2)
        
        if(self.buildDuty[num]):
            outVel = self.askForNum(num,keyCommand,"Moter " + str(num+1) + ", Enter % motor speed: ")
            if(outVel != None):
                MotorShare.write(REF_VELOCITY,outVel)
                
        elif(keyCommand == 49 + 33*num and not self.buildDuty[not num] ):
            self.transition_to(S2_PROMPT)
            self.MotorStepped = MotorShare
            print("Running State 2")
            self.askForNum(0,b'None'[0],PID_Prompt[self.PIDInx])
            self.MotorStepped.write(PID,[0,0,0])
        

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

        
    def setuprecord(self, delt, num, toRecord, Prompt):
        ''' 
        @brief              Sets up recording data
        @details            Prints collecting data prompt based on record time, motor number, what is being recorded,
                            and table title prompt.
        @param              delt is the time to record data.
        @param              num determines which motor the user records from.
        @param              toRecord contains a list of what values will be recorded.
        @param              Prompt contains table title prompt.
        '''  
        print('Moter ' + str(num+1) + ', \nCollecting {:} Data...'.format(Prompt))
        self.displayPos[num] = True
        
        self.to[num] = utime.ticks_ms()
        self.tf[num] = utime.ticks_add(self.to[num], delt)
        self.toRecord[num] = toRecord
        self.Prompt[num] = Prompt

    def recordGData(self,num, data1, data2):
        ''' 
        @brief              Records data collected
        @details            Appends to data1 and 2 arrays of data collected over some time difference and resets all arrays once recording
                            has been finished.
        @param              num is the motor ID subtracted by 1, so either a 0 for motor 1, or 1 for motor 2.
        @param              data1 is the first variable being recorded
        @param              data2 is the second variable being recorded
        '''  
        ## @brief Current time in ms
        tcur = utime.ticks_ms()   
        #Controls g command array formatting and printing, and once data recording finishes, resets array and g command condition
        if utime.ticks_diff(self.tf[num], tcur) <= 0:
            self.MotorShare1.write(REF_VELOCITY,0)
            self.MotorShare2.write(REF_VELOCITY,0)
            self.MotorShare1.write(PID,[0,0,0])
            self.MotorShare2.write(PID,[0,0,0])
            print('Moter ' + str(num+1) + ', Data:\n'
                  'Time (s), {:}'.format(self.Prompt[num]))
            for n in range(len(self.tArray[num])):
                print("{:}, {:}, {:}".format(self.tArray[num][n],self.DataArray1[num][n],self.DataArray2[num][n]))
            #Appends data to each array
            self.displayPos[num] = False
            self.tArray[num]     = [array.array('f',[]),array.array('f',[])]
            self.DataArray1[num] = [array.array('f',[]),array.array('f',[])]
            self.DataArray2[num] = [array.array('f',[]),array.array('f',[])]
        else:
            self.tArray[num].append(utime.ticks_diff(tcur, self.to[num])/1000//.01/100)
            print(utime.ticks_diff(tcur, self.to[num])/1000//.01/100)
            self.DataArray1[num].append(data1)
            self.DataArray2[num].append(data2) 

    def askForNum(self,num,keyCommand,prompt):
        ''' 
        @brief          Asks for a number from the user    
        @details        Adjusts keyCommand based on the motor ID (num) and only accepts values between 0 and 9.
                        Additionally takes in backspace, negative, or decimal command. Once the user finishes typing
                        their number they press enter and the number is returned. Otherwise the original duty is returned.
        @param          num is the motor ID subtracted by 1, so either a 0 for motor 1, or 1 for motor 2.
        @param          keyCommand is the read ASCII decimal value of character entered in PuTTY.
        @param          duty is the initial duty in MotorShares list.
        @return         duty is motor PWM duty
        @return         float(prompt + self.building[num]) is the float of whatever number was built by the user in entering their desired duty
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
            if (self.building[num] == '' or self.building[num] == '.' or self.building[num] == '-'):
                self.building[num] = '0'
            temp = self.building[num]
            self.building[num] == ''
            return float(temp)
        if(keyCommand != 32):
            print("\033c", end="")
            print(prompt + str(self.building[num]))
        return None
        
    def transition_to(self,new_state):
        ''' 
        @brief              Transitions states
        @details            When called takes in parameter for whatever state needs to be transitioned to.
        @param              Next state to transition to.
        
        '''
        self.State = new_state;
        
    def reset_states(self):
        
        self.PIDInx = 0
        
        
        ## m commands
        ## @brief   Boolean that turns true once m command is sent by user
        self.buildDuty = [False,False]
        self.building = ['','']


        
        ## g commands
        ## @brief   Boolean that turns true once g command is sent by user
        self.displayPos = [False,False]
        
        
        self.tf = array.array('l',[0,0])
        self.to = array.array('l',[0,0])
        self.toRecord = [[0,0],[0,0]]
        self.Prompt = ['','']
        
        ## @brief Array for time data collected for g command
        self.tArray = [array.array('f',[]),array.array('f',[])]
        ## @brief First array for data collected for g command
        self.DataArray1 = [array.array('f',[]),array.array('f',[])]
        ## @brief Second array for data collected for g command
        self.DataArray2 = [array.array('f',[]),array.array('f',[])]
        

        
    