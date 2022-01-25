''' @file task_hardware.py
    @brief Task to assign motors and encoders to hardware pins, checking for user to disable faults, and setting duty cycle to shared value
    @details Sets motors/encoders to their repective pins and channel numbers then enables the driver. A controller is instantiated to be
    used to control duty based on a current and reference velocity. Tasks constantly updates shared values and checks for flags executed
    in task user.
    @author Christian Clephan
    @author John Bennett
    @date November 13, 2021    
'''

import pyb
import utime
import closedloop
import math
import encoder2 

# Motor Pins
## @brief Sets up first pin for motor 1
pinB4 = pyb.Pin(pyb.Pin.cpu.B4)
## @brief Sets up second pin for motor 1
pinB5 = pyb.Pin(pyb.Pin.cpu.B5)
## @brief Sets up first pin for motor 2
pinB0 = pyb.Pin(pyb.Pin.cpu.B0)
## @brief Sets up second pin for motor 2
pinB1 = pyb.Pin(pyb.Pin.cpu.B1)


## Encoder Pins
## @brief Sets up first pin for encoder 1
pinB6 = pyb.Pin (pyb.Pin.cpu.B6)
## @brief Sets up second pin for encoder 1
pinB7 = pyb.Pin (pyb.Pin.cpu.B7)
## @brief Sets up first pin for encoder 2
pinC6 = pyb.Pin (pyb.Pin.cpu.C6)
## @brief Sets up second pin for encoder 2
pinC7 = pyb.Pin (pyb.Pin.cpu.C7)

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

## @brief Ratio of radians to ticks on encoder
ticks_to_rad = (2*math.pi/4000)
class Task_Hardware:
    ''' @brief                  Encoder and motor task methods.
        @details                Contains logic to be used with hardware based on what is desired from commands sent by
                                task user.
    '''
    
    
    def __init__(self, period,MotorShare, motor_drv):

        ''' 
        @brief              Constructs an hardware task object
        @details            Instantiates period, a variable changing for every period, motor object
        @param              Period at which motor updates defined by user in main.
        @param              MotorShare is a share object that contains all relevent info about the motor
        @param              motor_drv is the DRV8847 driver
        '''
        
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period*1000
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period*1000 + utime.ticks_us()
         ## @brief Time time of last run
        self.last_time = utime.ticks_us()
        
        ## @brief Shares all relevavant motor info
        # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
        self.MotorShare = MotorShare
        
        ## @brief Instantiates motor driver object
        self.motor_drv = motor_drv


        if self.MotorShare.read(ID) == 1:
            ##  @brief Creates motor object from motor function in DRV8847 driver with specified chanel and pins
            self.motor = self.motor_drv.motor(1,pinB4,pinB5)
            ## @brief Creates encoder object with functionallity described in encoder driver file. Parameters for object dictate encoder pins and timer.
            self.encoder = encoder2.Encoder(pinB6,pinB7,4)
        elif self.MotorShare.read(ID) == 2:
            self.motor = self.motor_drv.motor(3,pinB0,pinB1)
            self.encoder = encoder2.Encoder(pinC6,pinC7,8)
            
        #Enable motor driver
        self.motor_drv.enable()
        
        ## @brief Instantiates controller object that reads PID initial values and sets duty limits to -100 and 100.
        self.Controller = closedloop.ClosedLoop(self.MotorShare.read(PID), [-100,100])
    
    def run(self):
        ''' 
        @brief      Updates shared values of current/reference position and velocity. Detects for UI flags and if PID gains change.
        @details    Constantly updates motor position and velocity and executes logic for flags sent from task_user such as zeroing
                    position or reseting velocity and PID gains when a fault is disabled.
        '''

        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (utime.ticks_us() >= self.next_time):
            # Update motor share values with new current position, velocity, and set duty to controller output that takes in a 
            # reference velocity, velocity, and time difference.
        
            self.nextUpdate()
            
            # If zero command is True then encoder position is set to 0
            if self.MotorShare.read(IS_ZERO):
                self.encoder.set_position(0)
                self.MotorShare.write(IS_ZERO,False)
            
            if self.motor_drv.fault_status():
                self.MotorShare.write(IS_FAULT, True)
                
            # If the disable fault flag is true: reference velocity and PID are reset and the driver is re-enabled.
            if (self.MotorShare.read(DIS_FAULT)):
                self.MotorShare.write(REF_VELOCITY, 0)
                self.MotorShare.write(PID,[0,0,0])
                self.motor_drv.enable()
                self.MotorShare.write(IS_FAULT, False)
                self.MotorShare.write(DIS_FAULT,False)
               
            # If there's a difference in PID values then change the PID to what is new.
            if (self.MotorShare.read(PID) != self.Controller.get_PID()):
                self.Controller.set_PID(self.MotorShare.read(PID))
            
            
            
    def nextUpdate(self):
        ''' 
        @brief      Updates encoder position, velocity, and time then sets duty to what is calculated in controller update method.         
        @details    Uses encoder driver to update position/velocity from which the values are written into the MotorShare list
                    and the period is updated. Duty is determined by controller update method, which takes in reference/current
                    velocity and a time difference.
        '''
        ## @brief Time difference between runs
        tdif = utime.ticks_diff(utime.ticks_us(), self.last_time)
        self.encoder.update()
        self.next_time += self.period
        self.last_time = utime.ticks_us()
        
        
        self.MotorShare.write(POSITION,self.encoder.get_position()*ticks_to_rad)
        self.MotorShare.write(VELOCITY,self.encoder.get_delta()*ticks_to_rad/((tdif)/1000000))
        
        ## @brief Motor duty value obtained from controller update method.
        duty = self.Controller.update(self.MotorShare.read(REF_VELOCITY), self.MotorShare.read(VELOCITY),tdif)
        self.MotorShare.write(DUTY, duty)
        self.motor.set_duty(duty) 
           
        
        