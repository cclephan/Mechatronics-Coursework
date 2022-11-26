'''
    @file encoder2.py
    @brief Encoder driver that handles instantiates timers and channels for encoder pins. Functions are set for basic functionality to get, set, and find delta of encoder
    @details Driver creates a timer which can count up to the 16 bit limit, and channels set up basic logic for what counts as a tick moving the rotor.
             The driver also acts as the very basic functionallity of transmitting encoder position to the encoder task
    @author Christian Clephan
    @author John Bennett
    @date   October 16, 2021
'''
import pyb

## @brief Highest tick count for Nucleo 16bit microcontroller
Encoder_Period = (2**16)
class Encoder:
    ''' @brief                  Interface with quadrature encoders
        @details                Contains all basic encoder functionallity that will be sent to task encoder when task user
                                requests encoder information.
    '''
    
    def __init__(self,Pinch1,Pinch2,timerNum):

        ''' 
        @brief      Constructs an encoder object
        @details    Creates timer thats number is defined in task encoder, counting up to 16 bit overflow keeping track of encoder position. 
                    The timer channels can be defined in task encoder where pins are defined for the hardware encoders.
                    Lastly two variables are created one accounting for overflow while one can go up and down infinitely.
        @param      Pinch1 defines channel one pin in task encoder
        @param      Pinch2 defines channel two pin in task encoder
        @param      timerNum defines the timer number that will be used for pyb Timer.
        '''

        ## @brief Timer created with no prescalar that counts up to 2^16-1 (before overflow)
        self.timX = pyb.Timer(timerNum, prescaler=0, period=Encoder_Period-1)
        
        ## @brief Timer channel to indicate if a tick has occured or not
        self.timX.channel(1, mode = pyb.Timer.ENC_B, pin=Pinch1)
        
        ## @brief Other timer channel to indicate if a tick has occured when the other channel is on
        self.timX.channel(2, mode = pyb.Timer.ENC_A, pin=Pinch2)
        
        ## @brief Position of the encoder that can go infinitely up or down
        self.position  = self.timX.counter();
        
        ## @brief Position of the encoder that can only go up to max bit count (2^16-1)
        self.Eposition = self.timX.counter();
        
        print('Creating encoder object')

    def update(self):

        ''' 
        @brief      Update function takes in values from other basic functions to define the encoder position with and without overflow
        '''
        
        self.position = self.get_position() + self.get_delta()
        self.Eposition = self.timX.counter()
        
    def get_position(self):

        ''' @brief              Returns encoder position
            @return             The position of the encoder shaft
        '''
        return self.position

    def set_position(self, pos):

        ''' @brief              Sets encoder position
            @param              The new position of the encoder shaft
        
        '''
        self.position = pos

    def get_delta(self):

        ''' @brief              Returns encoder delta
            @return             The change in position of the encoder shaft between the two most recent updates                                
        '''
        
        delp = self.timX.counter() - self.Eposition
        
        if delp>Encoder_Period/2:
            return delp - Encoder_Period
        elif delp<-Encoder_Period/2:
            return delp + Encoder_Period
        
        return delp
    
    def __repr__(self):
        ''' @brief              Prints encoder position
        '''
        return "Encoder Position: " + str(self.position)
    