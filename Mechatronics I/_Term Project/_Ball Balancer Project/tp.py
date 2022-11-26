'''@file tp.py
    @brief Touch panel driver
    @details Contains methods necessary for touch panel task logic such as setting calibration values and getting scan
             in X,Y,and Z
        @author Christian Clephan
        @author John Bennett
        @date   December 7, 2021

'''

import pyb
import utime


class TouchPanel:
    ''' @brief                  Interface with touch panel
        @details                Contains all basic touch panel functionallity such as setting up pins, getting scans, and
                                setting calibration values
    '''
    
    def __init__(self):

        ''' 
        @brief      Constructs touch panel object
        @details    Creates pins connected to the CPU for x-, x+, y-, and y+ to properly get scans. Sets up ADC pin, and
                    other functionallity to speed up data collection.
        '''
        ## @brief ym pin on CPU
        self.A0 = pyb.Pin.cpu.A0
        ## @brief xm pin on CPU
        self.A1 = pyb.Pin.cpu.A1
        ## @brief yp pin on CPU
        self.A6 = pyb.Pin.cpu.A6
        ## @brief xp pin on CPU
        self.A7 = pyb.Pin.cpu.A7
        ## @brief Out push pull mode
        self.out = pyb.Pin.OUT_PP
        ## @brief Set pin to input mode
        self.inn = pyb.Pin.IN
        ## @brief Shortens time to execute setting a pin
        self.pin = pyb.Pin
        ## @brief Shortens time to execute setting an ADC pin
        self.ADC = pyb.ADC
        
        self.pin(self.A0,self.out,value = 1)
        self.pin(self.A7,self.out,value = 0)
        self.ADC(self.A1)
        self.ADC(self.A6)
        
        ## @brief Wait function
        self.wait = utime.sleep_us
        
        ## @brief Intial conditions for calibration coefficients
        (self.Kxx, self.Kxy, self.Kyx, self.Kyy, self.xc, self.yc) = (1,0,0,1,0,0)

    def setCalV(self,calV):
        '''@brief Set calibration values
            @param calV are calibration values Kxx Kxy Kyx Kyy xc and yc
        '''
        (self.Kxx, self.Kxy, self.Kyx, self.Kyy, self.xc, self.yc) = calV              

    
    @micropython.native    
    def getScan(self):
        '''@brief Scans X,Y,Z of touchpad
            @details Quick method for changing pins around to find values for x and y positions and z condition.
            @return Positions of ball and condition whether ball is on touch panel
        
        '''
        self.pin(self.A0,self.out,value = 1)
        self.wait(4)
        ## @brief ADC pin to Xm
        ADCxm = self.ADC(self.A1)
        ## @brief Z value that is true when a something touches the panel
        z = ADCxm.read() > 69
        self.wait(4)
        self.pin(self.A6,self.out,value = 0)
        self.wait(4)
        ## @brief Sets ADC pin to Xp
        ADCxp = self.ADC(self.A7)        
        ## @brief y value that doesn't account for calibration
        yr = ADCxp.read()
        self.wait(4)
        self.pin(self.A1,self.out,value = 1)
        self.pin(self.A7,self.out,value = 0)
        self.wait(4)
        ## @brief Sets ADC pin to Ym
        ADCym = self.ADC(self.A0)
        self.pin(self.A6,self.inn)
        ## @brief x value that doesn't account for calibration
        xr = ADCym.read() 
        ## @brief True x position of ball with respect to the center of the platform using calibration coefficients
        x = xr*self.Kxx+yr*self.Kxy+self.xc
        ## @brief True y position of ball  with respect to the center of the platform using calibration coefficients
        y = xr*self.Kyx+yr*self.Kyy+self.yc
        return (x,y,z)



    