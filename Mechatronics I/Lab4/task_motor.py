import pyb
import utime
import closedloop

pinB4 = pyb.Pin(pyb.Pin.cpu.B4)
pinB5 = pyb.Pin(pyb.Pin.cpu.B5)

pinB0 = pyb.Pin(pyb.Pin.cpu.B0)
pinB1 = pyb.Pin(pyb.Pin.cpu.B1)

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

class Task_Motor:
    ''' @brief                  Encoder task runninng encoder driver functions
        @details                Keeps track of encoder position and delta, while also setting calling the set position
                                function in driver to 0 when zero boolean is true.
    '''
    
    
    def __init__(self, period,MotorShare, motor_drv):

        ''' 
        @brief              Constructs an motor task object
        @details            Instantiates period, a variable changing for every period, motor object
        @param              Period at which motor updates defined by user in main.
                            MotorShare is a share object that contains all relevent info about the motor
        
        '''
        
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()

        # @brief Shares all relevavant motor info
        # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
        self.MotorShare = MotorShare
        
        self.motor_drv = motor_drv


        ## @brief Creates encoder object
        if self.MotorShare.read(ID) == 1:
            #  @details Creates encoder object with functionallity described in encoder driver file. Parameters for object dictate encoder pins and timer.
            self.motor = self.motor_drv.motor(1,pinB4,pinB5)
        elif self.MotorShare.read(ID) == 2:
            #  @details Creates encoder object with functionallity described in encoder driver file. Parameters for object dictate encoder pins and timer.
            self.motor = self.motor_drv.motor(3,pinB0,pinB1)
            
        self.motor_drv.enable()
        self.motor.set_duty(0)
        
        self.Controller = closedloop.ClosedLoop(self.MotorShare.read(PID), [-100,100])
    
    def run(self):
        ''' 
        @brief      Runs encoder task zeroing encoder and updating position when necessary
        @details    Function that is run in main setting encoder position to 0 if it receives zero command from task user.
                    Task also updates encoder position/delta and returns the tuple to be used in user task if required.
        @param      Boolean value that is sent from user task to encoder task when the user wants to zero the encoder. If true the encoder is zero'd.
        '''

        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (utime.ticks_ms() >= self.next_time):
                    # If zero command is True then encoder position is set to 0
            self.next_time += self.period
                        
            if (self.MotorShare.read(DIS_FAULT)):
                self.MotorShare.write(REF_VELOCITY, 0)
                self.MotorShare.write(PID,[0,0,0])
                self.motor_drv.enable()
                self.MotorShare.write(DIS_FAULT,False)
           
            if (self.MotorShare.read(PID) != self.Controller.get_PID()):
                self.Controller.set_PID(self.MotorShare.read(PID))
            
            duty = self.Controller.update(self.MotorShare.read(REF_VELOCITY), self.MotorShare.read(VELOCITY))
            self.MotorShare.write(DUTY, duty)

            self.motor.set_duty(duty) 
            
            
        
        