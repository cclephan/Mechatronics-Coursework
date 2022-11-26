import pyb
import time

class MotorDriver:
    '''! 
    This class implements a motor driver for an ME405 kit. 
    '''

    def __init__ (self, en_pin, in1pin, in2pin, timer):
        '''! 
        Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. 
        @param en_pin enables the motor driver
        @param in1pin is the pin number associated with channel 2 of the motor
        @param in2pin is the pin number associated with channel 1 of the motor
        '''        
        print ('Creating a motor driver')
        en_pin.high()
        self.timX = pyb.Timer(timer, freq = 20000)
        self.ch1 = self.timX.channel(1,pyb.Timer.PWM, pin=in2pin)
        self.ch2 = self.timX.channel(2,pyb.Timer.PWM, pin=in1pin)

    def set_duty_cycle (self, level):
        '''!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
               cycle of the voltage sent to the motor 
        '''
        if level > 0:
            self.ch1.pulse_width_percent(level)
            self.ch2.pulse_width_percent(0)
        elif level < 0:
            self.ch2.pulse_width_percent(abs(level))
            self.ch1.pulse_width_percent(0)
        else:
            self.ch2.pulse_width_percent(0)
            self.ch1.pulse_width_percent(0)
        print ('Setting duty cycle to ' + str (level))
        
# if __name__ == "__main__":
#     pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
#     pinB4 = pyb.Pin(pyb.Pin.board.PB4)
#     pinB5 = pyb.Pin(pyb.Pin.board.PB5)
#     motor = MotorDriver(pinA10, pinB4, pinB5, 3)
#     motor.set_duty_cycle(30)
#     time.sleep(2)
#     motor.set_duty_cycle(60)
#     time.sleep(2)
#     motor.set_duty_cycle(90)
#     time.sleep(2)
#     motor.set_duty_cycle(30)
#     time.sleep(2)
#     motor.set_duty_cycle(-30)
#     time.sleep(2)
#     motor.set_duty_cycle(-60)
#     time.sleep(2)