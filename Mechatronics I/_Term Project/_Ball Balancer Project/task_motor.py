''' 
    @file task_motor.py
    @brief Task to assign motors to hardware pins, and setting duty cycle to shared value
    @details Sets motors to their repective pins and channel numbers then enables motor and sets duty to initial value
             in shares. Runs through setting the motor duty specified by user and checking for if the user disables a
             fault at period defined in main.
    @author Christian Clephan
    @author John Bennett
    @date December 8, 2021    
'''
import pyb
import utime

pinB4 = pyb.Pin(pyb.Pin.cpu.B4)
pinB5 = pyb.Pin(pyb.Pin.cpu.B5)

pinB0 = pyb.Pin(pyb.Pin.cpu.B0)
pinB1 = pyb.Pin(pyb.Pin.cpu.B1)

class Task_Motor:
    ''' @brief                  Motor task running motor driver functions
        @details                updates motor duty
    '''
    
    
    def __init__(self, period,duty_shares, motor_drv):

        ''' 
        @brief              Constructs an motor task object
        @details            Instantiates period, a variable changing for every period, motor object
        @param              Period at which motor task updates.
        @param              duty_shares is a shared viariable with the controller task corrosponds to the duty of each motor
        @param              motor_drv object is used to create motor objects
        
        '''
        
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + utime.ticks_ms()

        ## @brief Shares duty values to motars
        self.duty_shares = duty_shares       

        ## @brief motor 1 object
        self.motor1 = motor_drv.motor(1,pinB4,pinB5)
        ## @brief motor 2 object
        self.motor2 = motor_drv.motor(3,pinB0,pinB1)
        
        self.motor1.set_duty(0)
        self.motor2.set_duty(0)
    
    def run(self):
        ''' 
        @brief      Runs motor task updates the duty when needed
        '''

        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (utime.ticks_ms() >= self.next_time):
                    
            self.next_time += self.period
            
            (d1, d2) = self.duty_shares.read()
            self.motor1.set_duty(d1) 
            self.motor2.set_duty(d2) 
            
            
        
        