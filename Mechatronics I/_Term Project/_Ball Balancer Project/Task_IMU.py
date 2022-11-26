'''
    @file Task_IMU.py
    @brief Task IMU runs logic for getting calibration coefficients and updating data collected
    @details Sets up IMU using driver class and first checks for coefficients on a text file. If they are not there the
             task runs through calibration then updates euler angles and angular velcoties constantly.
    @author Christian Clephan
    @author John Bennett
    @date   December 7, 2021
'''
import IMU
import os
import utime
from pyb import I2C

## @brief Converts degrees to radians
deg2rad = 3.14159/180

class Task_IMU:
    '''@brief IMU task class running logic
        @details Collects IMU data and checks for calibration coefficients
    '''
    
    def __init__(self,Shares):
        ''' @brief Initial conditions done by IMU task
            @details Sets up serial communication to I2C, creates IMU driver object, and checks for file coefficients
        '''
        ## @brief Creates I2C object
        i2c = I2C(1,I2C.MASTER)
        i2c.init(I2C.MASTER, baudrate=400000)
        
        ## @brief Creates IMU driver object with defined default address 0x28
        self.IMU_driver = IMU.BNO055(0x28, i2c)
        
        ## @brief Function to wait
        self.wait = utime.sleep
        
        ## @brief Instantiates share for communication between task
        self.Shares = Shares
        
        self.getFileCoef()
    
    def getFileCoef(self):
        '''@brief Checks for IMU file calibration coefficients or writes a file with the coefficients
        '''
        ## @brief Name of file that will be searched for on flashdrive or that will be created if not there.
        filename = "IMU_cal_coeffs.txt"
        if filename in os.listdir():
            with open(filename, 'r') as f:
                ## @brief Read the first line of the file
                p = f.readline()
                ## @brief Split the line into multiple strings and then convert each one to a float
                data = [int(i,16) for i in p.strip().split(',')]
                buf = bytearray(data)
                self.IMU_driver.writeCalibCoef(buf)
        else:
            with open(filename, 'w') as f:
                # Perform manual calibration
                data = self.calibrate()
                data = ",".join([hex(i) for i in data])
                # Then, write the calibration coefficients to the file
                # as a string. The example uses an f-string, but you can
                # use string.format() if you prefer
                f.write(f"{data}\r\n")
                
                
    def calibrate(self):
        '''@brief Calibrates IMU using driver method
            @details Constantly prints and updates user on calibration status for IMU and returns the calibrated coefficients
                    once every system on the IMU is calibrated.
            @return Calibrated coefficients
        '''
      
        while (True):
            ## @brief Calibration status containing for integers (all will be 3 when fully calibrated)
            stat = self.IMU_driver.getCalibStatus()
            print("Value: " + str(stat))
            print("\n")
            self.wait(.2)
            
            if(stat[0]*stat[1]*stat[2]*stat[3]==81):
                print("calibrated")
                return self.IMU_driver.getCalibCoef()
            
    def update(self):
        ''' 
        @brief Updates euler angles and angular velocities and writes them to the IMU share
        '''
        ## @brief Tuple containing heading, pitch, and roll for IMU
        (h, th_x, th_y) = self.IMU_driver.readEuler()
        ## @brief Tuple containing heading, pitch, and roll change over time
        (hdot, thd_x, thd_y)  = self.IMU_driver.readOmega()
        
        self.Shares.write((th_x*deg2rad, thd_x*deg2rad, th_y*deg2rad, thd_y*deg2rad))
            
            