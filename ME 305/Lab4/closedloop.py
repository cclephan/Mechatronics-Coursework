# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 19:55:17 2021

@author: johna
"""
import utime

class ClosedLoop:
 
        
    def __init__ (self,PID, satLim ):
         
        
        self.PID = PID
        # self.Kp = Kp #(*%/rad)
        # self.Ki = Ki #(*%/rad)
        # self.Kd = Kd #(*%s2/rad)
        self.satLim = satLim
        
        self.esum = 0
        self.laste = 0
        
        self.to = utime.ticks_ms()/1000

    def update (self,Ref, Read):
        tcur = utime.ticks_ms()/1000
        delt = utime.ticks_diff(tcur,self.to)
        self.to = tcur
        
        e = Ref - Read
        self.esum += e*delt
        dele = e - self.laste
        self.laste = e
        

        
        # PositionControl
        duty = self.PID[0]*(e) + self.PID[1]*(self.esum) + self.PID[2]*(dele/delt) 
        return self.sat(duty)
                
    def get_PID(self):
        return self.PID
    
    def set_PID(self, PID):
        print('set PID')
        self.PID = PID
    
    def set_Kp(self, newKp):
        self.PID[0] = newKp
        
    def set_Ki(self, newKi):
        self.PID[1] = newKi
        
    def set_Kd(self, newKd):
        self.PID[2] = newKd
        
        
    def sat(self,num):
        if num<self.satLim[0]:
            return self.satLim[0]
        elif num>self.satLim[1]:
            return self.satLim[1]
        return num