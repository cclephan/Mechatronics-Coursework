import pyb
import time


class EncoderReader:
    def __init__(self,pin1,pin2,timer):
        self.e_count = 2**16-1
        self.timX = pyb.Timer(timer, prescaler = 1, period = self.e_count)
        self.ch1 = self.timX.channel(1, mode = pyb.Timer.ENC_B, pin=pin1)
        self.ch2 = self.timX.channel(2, mode = pyb.Timer.ENC_A, pin=pin2)    
        self.position = self.timX.counter()
        self.lastPosition = self.timX.counter()
        
        
    def read(self):
        
        self.lastPosition = self.position
        self.position = self.timX.counter()
        
        return self.position 
        
        
    def zero(self):
        self.lastPosition = self.position
        self.position = 0
        


if __name__ == "__main__":
    pinC6 = pyb.Pin(pyb.Pin.board.PC6)
    pinC7 = pyb.Pin(pyb.Pin.board.PC7)
    encoder = EncoderReader(pinC6,pinC7,8)
    while True:
        try:
            pos = encoder.read()
            print(pos)
            time.sleep(5)
            encoder.zero()
        except KeyboardInterrupt():
            break
    print('Program End')
   
