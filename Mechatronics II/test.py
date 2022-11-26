import pyb
import time

pinA1 = pyb.Pin (pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
tim2 = pyb.Timer (2, freq=20000)
ch2 = tim2.channel (2, pyb.Timer.PWM, pin=pinA1)
for a in range(100):
    time.sleep(.2)
    ch2.pulse_width_percent (a)
