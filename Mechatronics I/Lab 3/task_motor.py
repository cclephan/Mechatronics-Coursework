''' @file task_motor.py
    @brief Task to assign motors to hardware pins, checking for user to disable faults, and setting duty cycle to shared value
    @details Sets motors to their repective pins and channel numbers then enables motor and sets duty to initial value
             in shares. Runs through setting the motor duty specified by user and checking for if the user disables a
             fault at period defined in main.
    @author Christian Clephan
    @author John Bennett
    @date October 16, 2021    
'''

import pyb
import utime

pinB4 = pyb.Pin(pyb.Pin.cpu.B4)
pinB5 = pyb.Pin(pyb.Pin.cpu.B5)

pinB0 = pyb.Pin(pyb.Pin.cpu.B0)
pinB1 = pyb.Pin(pyb.Pin.cpu.B1)

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

class Task_Motor:
    ''' @brief                  Motor task runninng motor driver functions
        @details                Keeps track of motor duty cycle and if the user wants to disable motor faults
    '''
    
    
    def __init__(self, period,MotorShare, motor_drv):

        ''' 
        @brief              Constructs an motor task object
        @details            Instantiates period, a variable changing for every period, motor object
        @param              Period is the frequency at which motor updates defined by user in main.
        @param              MotorShare is a share object that contains all relevent info about the motor
        @param              motor_drv is the DRV8847 driver
        '''
        
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()

        # @brief Shares all relevavant motor info
        # @details Shared values in order include Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)
        self.MotorShare = MotorShare
        
        ## @brief Instantiates motor driver object
        self.motor_drv = motor_drv


        if self.MotorShare.read(ID) == 1:
            ##  @brief Creates motor object from motor function in DRV8847 driver with specified chanel and pins
            self.motor = self.motor_drv.motor(1,pinB4,pinB5)
        elif self.MotorShare.read(ID) == 2:
            self.motor = self.motor_drv.motor(3,pinB0,pinB1)
            
        self.motor_drv.enable()
        self.motor.set_duty(self.MotorShare.read(DUTY))
    
    def run(self):
        ''' 
        @brief      Detects whether the user wants to diable faults or set duty
        @details    Function that is run in main detecting any commands sent through user regarding disabling a fault or
                    setting a duty. When a fault is disabled the motor driver is re-enabled, duty is set to 0, and the
                    boolean flag to disbale faults is set back to false.
        '''

        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (utime.ticks_ms() >= self.next_time):
                    # If zero command is True then encoder position is set to 0
            self.next_time += self.period
            if (self.MotorShare.read(DIS_FAULT)):
                self.motor_drv.enable()
                print('Motor Enabled')
                self.MotorShare.write(DUTY, 0)
                self.MotorShare.write(DIS_FAULT,False)
            self.motor.set_duty(self.MotorShare.read(DUTY)) 
            
            
        
        