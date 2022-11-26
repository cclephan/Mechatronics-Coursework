'''
    @file encoder.py
    @brief Instructs user on how to use program, then cycles through states of different LED light patterns. Link to FSM Diagram: https://imgur.com/a/4q4KJSU / Link to Video: https://youtu.be/cFzSvv7zzRE
    @details First welcomes the user and instructs user on how to operate hardware (by pressing the blue button to cycle LED patterns).
             Once the user presses the button the first pattern is loaded (square wave pattern). Once it is pressed again the program
             changes states and the LED now displays a sinewave pattern. Once pressed again the state changes and the LED displays a
             sawtooth pattern. Once the button is pressed again the pattern changes back to square and the cycle repeats. To exit the
             program the user can press Ctrl+C. This is meant to be run on a Nucleo
             
    @author Christian Clephan
    @author John Bennett
    @date   October 4, 2021
'''
import pyb

Encoder_Period = (2**16);


#Defines a class for our example FSM
class Encoder:
    ''' @brief                  Interface with quadrature encoders
        @details
    '''
    
    def __init__(self,Pinch1,Pinch2,timerNum):

        ''' 
        @brief              Constructs an encoder object
        @details
        
        '''

        ## @brief Configures Nucleo timer at extreme high frequency. The frequency is set very high so human eye can only see the LED on when it's activated.
        self.timX = pyb.Timer(timerNum, prescaler=0, period=Encoder_Period-1)
        
        ## @brief Configures relationship between timer and LED pin
        self.timX.channel(1, mode = pyb.Timer.ENC_B, pin=Pinch1)
        
        self.timX.channel(2, mode = pyb.Timer.ENC_A, pin=Pinch2)
        
        self.position  = self.timX.counter();
        self.Eposition = self.timX.counter();
        
        print('Creating encoder object')

    def update(self):

        ''' 
        @brief              Updates encoder position and delta
        @details
        '''
        
        self.position = self.get_position() + self.get_delta()
        self.Eposition = self.timX.counter()
        
        
        #print('Reading encoder count and updating position and delta values')
        #print(self.position)
        
    def get_position(self):

        ''' @brief              Returns encoder position
            @details
            @return             The position of the encoder shaft
        '''
        return self.position

    def set_position(self, pos):

        ''' @brief              Sets encoder position
            @details
            @param  pos    The new position of the encoder shaft
        
        '''
        self.position = pos
        
       #print('Setting position and delta values')

    def get_delta(self):

        ''' @brief              Returns encoder delta
            @details
            @return             The change in position of the encoder shaft
                                between the two most recent updates
        '''
        
        delp = self.timX.counter() - self.Eposition
        
        if delp>Encoder_Period/2:
            return delp - Encoder_Period
        elif delp<-Encoder_Period/2:
            return delp + Encoder_Period
        
        return delp
    
    def __repr__(self):
        return "Encoder Position: " + str(self.position)
    