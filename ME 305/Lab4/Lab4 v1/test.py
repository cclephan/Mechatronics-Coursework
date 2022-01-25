import pyb
import time
import task_motor

pinB4 = pyb.Pin(pyb.Pin.cpu.B4)
pinB5 = pyb.Pin(pyb.Pin.cpu.B5)

pinB0 = pyb.Pin(pyb.Pin.cpu.B0)
pinB1 = pyb.Pin(pyb.Pin.cpu.B1)

pinA15 = pyb.Pin(pyb.Pin.cpu.A15, mode = pyb.Pin.OUT_PP)
pinA15.high()

tim3 = pyb.Timer(3, freq = 20000)
t2c1 = tim3.channel(1, mode = pyb.Timer.PWM, pin=pinB4)
t2c2 = tim3.channel(2, mode = pyb.Timer.PWM, pin=pinB5)
t2c3 = tim3.channel(3, mode = pyb.Timer.PWM, pin=pinB0)
t2c4 = tim3.channel(4, mode = pyb.Timer.PWM, pin=pinB1)
t2c1.pulse_width_percent(0)
t2c2.pulse_width_percent(0)



while True:
    try:
        t2c1.pulse_width_percent(50)
        time.sleep(2)
        t2c1.pulse_width_percent(0)
        t2c3.pulse_width_percent(50)
        print('Waiting')
        time.sleep(2)
        t2c3.pulse_width_percent(0)
       
        
    except KeyboardInterrupt:
        print('Done')
        pinA15.low()
        break
