''' @file motor.py
    @brief Motor driver containing DRV8847 class used by both motors and a Motor class called for each individual motor.
    @details DRV8847 is the motor driver used universally between motors with functions to enable, disable, check faults,
             and return a motor object.
    @author Christian Clephan
    @author John Bennett
    @date November 9, 2021    
'''

import pyb
import utime

class DRV8847:
    ''' @brief A motor driver class for the DRV8847 from TI.
        @details Objects of this class can be used to configure the DRV8847
            motor driver and to create one or more objects of the
            Motor class which can be used to perform motor
            control.
            Refer to the DRV8847 datasheet here:
            https://www.ti.com/lit/ds/symlink/drv8847.pdf
    '''
 
        
    def __init__ (self,timerNum):
        ''' @brief Initializes and returns a DRV8847 object.
            @detials Creates timer, pins, and external interupt that will be used universally for motors.
            @param timerNum is timer used for motors determined by the user in main held in variable timX.
        '''
        ## @brief Timer that is used in motors taking in parameter timerNum defined in main.
        self.timX = pyb.Timer(timerNum, freq = 20000)
        ## @brief Pin used to enable and disable motors
        self.pinA15 = pyb.Pin(pyb.Pin.cpu.A15)
        ## @brief Pin used to detect faults in motors
        self.pinB2 = pyb.Pin(pyb.Pin.cpu.B2)
        ## @brief External interupt object that is used to detect faults, and if they are detected, uses callback function fault_cb to disable motor.
        self.motorInt = pyb.ExtInt(self.pinB2, mode=pyb.ExtInt.IRQ_RISING,pull=pyb.Pin.PULL_NONE, callback= self.fault_cb)
        ## @brief Boolean that turns true when a fault occurs
        self.isFault = False


    def enable (self):
        ''' @brief Brings the DRV8847 out of sleep mode.
            @details First disables external interupt to allow motor sleep pin to be turned on then enables external interupt object.
        '''
        self.motorInt.disable()
        self.pinA15.high()
        utime.sleep_us(25)
        self.isFault = False
        self.motorInt.enable()

    def disable (self):
        ''' @brief Puts the DRV8847 in sleep mode.
        '''
        self.pinA15.low()
    
    def fault_cb (self, IRQ_src):
        ''' @brief Callback function to run on fault condition.
            @param IRQ_src The source of the interrupt request.
        '''
        print('Fault Occurred')
        self.isFault = True
        self.disable()
    
    def fault_status(self):
        ''' @brief Returns fault status.
            @return Fault status.
        '''
        return self.isFault
    
    def motor (self,motorChannel,pinCH1,pinCH2):
        ''' @brief Initializes and returns a motor object associated with the DRV8847.
            @return An object of class Motor
        '''
        return Motor(motorChannel,pinCH1,pinCH2, self.timX)

class Motor:
    ''' @brief A motor class for one channel of the DRV8847.
        @details Objects of this class can be used to apply PWM to a given
                 DC motor.
    '''
    def __init__ (self,motorChannel,pinCH1,pinCH2,timX):
        ''' @brief Initializes and returns a motor object associated with the DRV8847.
            @details Creates timer channels that will be used specific to each motor channel.
        '''
        ## @brief Timer channel to the first motor channel for some motor
        self.t2c1 = timX.channel(motorChannel, mode = pyb.Timer.PWM, pin=pinCH1)
        ## @brief Timer channel to the second motor channel for some motor
        self.t2c2 = timX.channel(motorChannel+1, mode = pyb.Timer.PWM, pin=pinCH2)
        self.set_duty(0)
        
    def set_duty (self, duty):
        
        ''' @brief Set the PWM duty cycle for the motor channel.
            @details This method sets the duty cycle to be sent
                    to the motor to the given level. Positive values
                    cause effort in one direction, negative values
                    in the opposite direction.
            @param duty A signed number holding the duty
                      cycle of the PWM signal sent to the motor
        '''
        #if duty is positive then set the first channel to specified duty and other to 0.
        if duty >= 0:
            self.t2c1.pulse_width_percent(duty)
            self.t2c2.pulse_width_percent(0)
        #if duty is negative then set the second channel to a specified duty (negative sign will make duty positive) and other to 0.
        elif duty < 0:
            self.t2c2.pulse_width_percent(-duty)
            self.t2c1.pulse_width_percent(0)
