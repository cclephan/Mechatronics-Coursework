'''@file Task_TP.py
    @brief Touch panel task
    @details Runs logic for collecting ball position and velocity from touch panel and writes them to a share that will be
            used by a controller.
    @author Christian Clephan
    @author John Bennett
    @date   December 7, 2021

'''

import utime
import tp
from ulab import numpy as np
import os

## @brief Prompt for calibrating touch panel
prompt = ['Touch Left Bottom (Origin)', 
          'Touch Left Middle', 
          'Touch Left Top', 
          'Touch Middle Top', 
          'Touch Center', 
          'Touch Middle Bottom', 
          'Touch Right Bottom', 
          'Touch Right Middle', 
          'Touch Right Top']


class Task_TP:
    '''@brief IMU task class running logic
        @details Collects IMU data and checks for calibration coefficients
    '''
    
    def __init__(self,Share):
        '''@brief Initial conditions when running touch panel task
            @details Instantiates touch panel object, sets initial conditions of ball position and velocity,
                     calibrates touch panel, and sets up share object.
        '''
        ## @brief Sets up touch panel driver to obtain methods
        self.tp = tp.TouchPanel()
        ## @brief Function to get time
        self.getTime = utime.ticks_us
        ## @brief Function to take time difference
        self.tdif = utime.ticks_diff
        ## @brief Function to wait
        self.wait = utime.sleep_us
        ## @brief Period used to get velocities
        self.T_s = 0
        ## @brief Initial time
        self.t0 = self.getTime()
        
        (self.xcur,self.ycur,self.zcur,self.Vxcur,self.Vycur,self.t0) = (0,0,False,0,0,0)
        
        ## @brief Gets calibration coefficient values
        calV = self.getCalCoef()
        self.tp.setCalV(calV)
        
        ## @brief Sets up share object
        self.Share = Share
        
    def getCalCoef(self):
        '''@brief Gets calibration coefficients
            @details Checks a file for calibration coefficients, if it is not there then task runs through calibrating
                    touch panel to find coefficients.
            @return cal_values are the 6 calibration values
        '''
        ## @brief Name of file that will be searched for on flashdrive or that will be created if not there.
        filename = "RT_cal_coeffs.txt"
        if filename in os.listdir():
            with open(filename, 'r') as f:
                ## @brief Read the first line of the file
                cal_string = f.readline()
                ## @brief Split the line into multiple strings and then convert each one to a float
                cal_values = tuple([float(cal_value) for cal_value in cal_string.strip().split(',')])
        else:
            with open(filename, 'w') as f:
                # Perform manual calibration
                cal_values = self.calibrate()
                (Kxx, Kxy, Kyx, Kyy, Xc, Yc) = cal_values
                # Then, write the calibration coefficients to the file
                # as a string. The example uses an f-string, but you can
                # use string.format() if you prefer
                f.write(f"{Kxx}, {Kxy}, {Kyx}, {Kyy}, {Xc}, {Yc}\r\n")
                
        return cal_values    

    def calibrate(self):
        '''@brief Calibrates touch panel
            @details Uses actual measurements on touch panel with respect to the center and compares what is measured
                     by the user by touching in 9 different spots.
            @return Calibration coefficients Kxx Kxy Kyx Kyy Xc Yc
        '''
        ## @brief Sets up array for X matrix
        X = np.ones((9,3))
        ## @brief Sets up array for ADC values
        ADC_vals = np.ones((9,2))
        ## @brief Array of real world platform values for corresponding touch test
        X_act = np.array([[-88,-50],[-88,0],[-88, 50],[0,50],[0,0],[0,-50],[88,-50],[88,0],[88,50]])
        ## @brief Counter for running through calibration
        n = 0
        r = False
        while(n<9):
            ## @brief Positions of ball and condition whether the platform is pressed
            (x,y,z) = self.tp.getScan()
            if z and r :
                ADC_vals[n,:] = [x,y]
                r = False
                print('REMOVE HAND NOW!!!!')
                print(ADC_vals) 
                n += 1
            elif z == False and r == False:
                r = True
                print(prompt[n])
                self.wait(200000)
                print('go now')                
                
        X[:,0:2] = ADC_vals
        Y = np.dot(X.transpose(),X_act)
        print(X)
        print(Y)
        ## @brief Calibration coefficients in a matrix
        B = np.dot(np.linalg.inv(np.dot(X.transpose(),X)),Y)
        print(B)
        
        return (B[0,0], B[0,1], B[1,0], B[1,1], B[2,0], B[2,1])
        
    
    
    def contactPoint(self):
        '''@brief Updates current x and y position/velocity, and if something is pressing the platform
            @details Uses alpha beta filtering to update positions and velocity over some time period. Resets position and
                    velocity when the ball is not on the platform.
        '''
        (x,y,z) = self.tp.getScan()
        self.T_s = self.tdif(self.getTime(),self.t0)/1E6
        self.t0 = self.getTime()
        if not self.zcur and z:
            ## @brief Current x position
            self.xcur = x
            ## @brief Current x velocity
            self.Vxcur = 0
            ## @brief Current y position
            self.ycur = y
            ## @brief Current y velocity
            self.Vycur = 0
            ## @brief Current condition if something is pressing platform
            self.zcur = z
        elif z:
            ## @brief Alpha filter
            alpha = 0.85
            ## @brief Beta filter
            beta = 0.005            
            xcur_temp = self.xcur
            ycur_temp = self.ycur
            self.xcur = xcur_temp+alpha*(x-xcur_temp)+self.T_s*self.Vxcur
            self.ycur = ycur_temp+alpha*(y-ycur_temp)+self.T_s*self.Vycur
            self.Vxcur = self.Vxcur+beta/self.T_s*(x-xcur_temp)
            self.Vycur = self.Vycur+beta/self.T_s*(y-ycur_temp)
            
        else:
            self.zcur  = False
            self.xcur  = 0
            self.Vxcur = 0
            self.ycur  = 0
            self.Vycur = 0
            
    def update(self):
        '''@brief Updates position and velocity of ball and writes values to a share
        '''
        self.contactPoint()
        self.Share.write((self.xcur,self.ycur,self.Vxcur,self.Vycur,self.zcur,self.T_s))
        
    
    