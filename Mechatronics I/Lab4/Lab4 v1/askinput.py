# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 19:55:17 2021

@author: johna
"""
class askInput:
 
        
    def __init__ (self):
         self.new()      
        

    def UpdateNum(self,keyCommand, prompt):
        
        if (keyCommand>=b'0'[0] and keyCommand<=b'9'[0]):
            new = keyCommand - 48
            if self.decimal == 1:
                self.building = self.building*10 + new
            else:
                self.building = self.building + new/self.decimal
                self.decimal *= 10
        elif keyCommand == 127:
            if self.decimal == 1:
                self.building = self.building//(10)
            else:
                self.decimal /= 10
                self.building = (self.building//(10/self.decimal))*(10/self.decimal)
        elif keyCommand == 46 and self.decimal < 10:
            self.decimal *= 10
        elif keyCommand == 45:
            self.building = -self.building
        elif keyCommand == 13:
            return self.building
        
        if(keyCommand != 32):
            print("\033c", end="")
            print(prompt + str(self.building))
        
        return None
                
    def new(self):
        self.decimal = 1
        self.building  = 0
        
# if __name__ =='__main__':
#     a = askInput()
#     while(True):
#         a.UpdateNum(input("798:").encode()[0],"num: ")
    
#     print("Done")
        