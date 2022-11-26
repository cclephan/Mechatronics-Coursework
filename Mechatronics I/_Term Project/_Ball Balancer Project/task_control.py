'''
    @file       task_control.py
    @brief      control task minipulates the duties to each motor to balance the plate-ball system
    @details    the controller was inspired from Hw 2 and 3 which incorporates a state–space system
                and state-feedback control to calculate motor duties. baised on ball position and platform angles
    @author     Christian Clephan
    @author     John Bennett
    @date       December 8, 2021
'''

from ulab import numpy as np
import utime



class Task_Controller:
    ''' @brief              Task Controller minipulates the duties to each motor to balance a ball
        @details            The task reads angles from IMU task and Ball position from Tp task baised on the selected 
                            controller the platform will send dutues the motors to correct the balls motion
    '''
    def __init__(self, period, BallShare, IMUShare, DutyShare,StateShare,ModeShare):
        ''' @brief              Task Controller minipulates the duties to each motor to balance a ball
            @details            The task reads angles from IMU task and Ball position from Tp Task
            @param              Period at which the controller task updates.
            @param              BallShare reads Ball position from Tp task 
            @param              IMUShare reads platform angles from IMU task
            @param              DutyShare controls motor duty and is read in the motor task 
            @param              StateShare holds each states current data
            @param              ModeShare is written in the user task to toggle the controller from Ideal to balancing
        '''
        
        ## @brief Defines period as what is called in main for period parameter
        self.period = period
        self.getTime = utime.ticks_ms
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + self.getTime()
        ## @brief ModeShare is written in the user task to toggle the controller from Ideal to balancing
        self.Mode = ModeShare
        ## @brief BallShare reads Ball position from Tp task 
        self.Ball_Data = BallShare
        ## @brief IMUShare reads platform angles from IMU task
        self.IMU_Data = IMUShare
        ## @brief DutyShare controls motor duty and is read in the motor task 
        self.Duty_S = DutyShare
        ## @brief StateShare holds each states current data
        self.State_S = StateShare
        
 
        
        
        
        # Controller Data
        ## @brief Kp1 is the motor controller
        self.Kp1 = np.array([[-1.09,-.84,-690, 5]])
        ## @brief Kp2 is the motor2 controller
        self.Kp2 = np.array([[-1.34,-.86,-690, 5]])
        
        ## @brief D1C is the saved motor 1 duty from the previous run which will be incremented in the run task
        self.D1c = 0
        ## @brief D2C is the saved motor 2 duty from the previous run which will be incremented in the run task
        self.D2c = 0
        
        R = 2.21 # oms
        Kt = 13.8
        Vdc = 12        
        ## @brief C is the torque to duty conversion constant
        self.C = 100*R/(4*Kt*Vdc)
    
    def run(self):
        ''' 
        @brief              runs the controller task and gets the desired motor duties baised on the current state
        @details            Baised on the controller mode the platform will be in a balance state or ideal state
                            When in balance mode the platform uses the current states and K to balance to get the torques and duties
                            then the coutput duty is incromented to prevent motor slippage
        '''
        if (self.getTime() >= self.next_time):
            self.next_time += self.period
            
            # Get State Data
            (x,y,xdot,ydot,z,dt) = self.Ball_Data.read()
            (th_x, thd_x, th_y, thd_y) = self.IMU_Data.read()
            
            # Ideal Mode
            if self.Mode.read()[0] == 0:
                self.D1c = 0
                self.D2c = 0
                
            # Balance Mode  
            else:
                # Build States
                q1 = np.array([[x],[xdot],[th_y],[thd_y]])
                q2 = np.array([[y],[ydot],[th_x],[thd_x]])
                
                # Torques Proportional
                Tp1 =  np.dot(-self.Kp1,q1)[0,0]
                Tp2 = -np.dot(-self.Kp2,q2)[0,0]
                
                # Duty
                D1 = self.C*Tp1
                D2 = self.C*Tp2
                
                # Increment Duty
                inc = 5
                if self.D1c + inc < D1:
                    self.D1c += inc
                elif self.D1c - inc > D1:
                    self.D1c -= inc
                else:
                    self.D1c = D1
                    
                if self.D2c + inc < D2:
                    self.D2c += inc
                elif self.D2c - inc > D2:
                    self.D2c -= inc
                else:
                    self.D2c = D2
            
            # Write Duty
            self.Duty_S.write((self.D1c,self.D2c))
        
            # System States
            self.State_S.write([x,xdot,y, ydot,th_x, thd_x, th_y, thd_y,self.D1c,self.D2c])
            
                
        
            