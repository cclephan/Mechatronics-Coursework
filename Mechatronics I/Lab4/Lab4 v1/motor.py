''' @file DRV8847.py
'''

import pyb
import utime

class DRV8847:
    ''' @brief A motor driver class for the DRV8847 from TI.
    @details Objects of this class can be used to configure the DRV8847
    motor driver and to create one or moreobjects of the
    Motor class which can be used to perform motor
    control.
    Refer to the DRV8847 datasheet here:
    https://www.ti.com/lit/ds/symlink/drv8847.pdf
    '''
 
        
    def __init__ (self,timerNum):
        ''' @brief Initializes and returns a DRV8847 object.
        '''
        #Timer
        self.timX = pyb.Timer(timerNum, freq = 20000)
        self.pinA15 = pyb.Pin(pyb.Pin.cpu.A15)
        self.pinB2 = pyb.Pin(pyb.Pin.cpu.B2)
        self.motorInt = pyb.ExtInt(self.pinB2, mode=pyb.ExtInt.IRQ_RISING,pull=pyb.Pin.PULL_NONE, callback= self.fault_cb)


    def enable (self):
        ''' @brief Brings the DRV8847 out of sleep mode.
        '''
        self.motorInt.disable()
        self.pinA15.high()
        utime.sleep_us(25)
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
        self.disable()
    
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
            @details Objects of this class should not be instantiated
                    directly. Instead create a DRV8847 object and use
                    that to create Motor objects using the method
                    DRV8847.motor().
        '''
        self.t2c1 = timX.channel(motorChannel, mode = pyb.Timer.PWM, pin=pinCH1)
        self.t2c2 = timX.channel(motorChannel+1, mode = pyb.Timer.PWM, pin=pinCH2)
        
    def set_duty (self, duty):
        
        ''' @brief Set the PWM duty cycle for the motor channel.
            @details This method sets the duty cycle to be sent
                    to the motor to the given level. Positive values
                    cause effort in one direction, negative values
                    in the opposite direction.
            @param duty A signed number holding the duty
                      cycle of the PWM signal sent to the motor
        '''
        if duty >= 0:
            self.t2c1.pulse_width_percent(duty)
            self.t2c2.pulse_width_percent(0)

        elif duty < 0:
            self.t2c2.pulse_width_percent(-duty)
            self.t2c1.pulse_width_percent(0)
