import utime
import encoder
import pyb


S0_INIT = 0
#sets up PIN/LED/Timer
##  @brief Configures Nucleo pinB6 (green LED) as a variable
pinB6 = pyb.Pin (pyb.Pin.cpu.B6)
pinB7 = pyb.Pin (pyb.Pin.cpu.B7)

pinC6 = pyb.Pin (pyb.Pin.cpu.C6)
pinC7 = pyb.Pin (pyb.Pin.cpu.C7)

DisplayPosisionTime = 30000


#Defines a class for our example FSM
class Task_Encoder:
    ''' @brief                  Interface with quadrature encoders
        @details
    '''
    
    def __init__(self, period):

        ''' 
        @brief              Constructs an encoder object
        @details
        
        '''
        self.state = S0_INIT
        
        self.period = period
        self.next_time = period + utime.ticks_ms()
        
        self.encoder_1 = encoder.Encoder(pinB6,pinB7,4)
        self.encoder_2 = encoder.Encoder(pinC6,pinC7,3)
        
        self.displayPos = False
        self.endPrint = utime.ticks_ms()
        self.dataList = []
        


    def run(self, keyCommand):

        tcur = utime.ticks_ms()   
        
        if (tcur >= self.next_time):
              
            self.nextUpdate()             
            
            if self.displayPos == True and (keyCommand == b's' or utime.ticks_diff(utime.ticks_add(self.to, DisplayPosisionTime), tcur) <= 0):
                print("Time (ms), Posision (ticks)")
                for n in range(len(self.dataList)):
                    print(self.dataList[n])
                self.displayPos = False
                self.dataList = []
                
            elif (self.displayPos):
                self.dataList.append("{:}, {:}".format(utime.ticks_diff(tcur, self.to),self.encoder_1.get_position()))
            
            elif keyCommand == b'g':
                self.displayPos = True
                self.to = tcur
                
            if keyCommand == b'z':
                self.encoder_1.set_position(0)
                
            elif keyCommand == b'd':
                print("Encoder Delta: " + str(self.encoder_1.get_delta()))                
            
                
            elif (keyCommand == b'p'):
                print(self.encoder_1)                
            
                
            return True 
            
        return keyCommand == ''             
                

    def transition_to(self,new_state):
        self.state = new_state;
        
    def nextUpdate(self):
        self.encoder_1.update() 
        self.encoder_2.update()
        self.next_time += self.period
        