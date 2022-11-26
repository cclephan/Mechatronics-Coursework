'''
    @file IMU.py
    @brief IMU driver, sets up calibration and reading data from device.
    @details Driver instantiates I2C for communication and changes modes to get/write calibration coefficients 
             and get calibration status.
    @author Christian Clephan
    @author John Bennett
    @date   December 7, 2021
'''


import struct
import pyb

## @brief Establishes clock line pin on CPU
SCL = pyb.Pin(pyb.Pin.cpu.B8)
## @brief Establishes data line pin on CPU
SDA = pyb.Pin(pyb.Pin.cpu.B9)


class BNO055:
    ''' @brief                  BNO055 IMU class
        @details                Handles calibrating the IMU and methods for collecting data (angles and angular velocity)
    '''
    def __init__(self, addr,i2c):
        ''' @brief Initializes and returns a BNO055 object.
            @detials Sets address to parameter defined when calling BNO055 object, sets up I2C communication, and NDOF mode
            @param addr is the address defined in IMU_task
            @param i2c is the communication defined in IMU_task
        '''
        ## @brief Address for BNO055
        self.addr = addr
        ## @brief Communication for BNO055
        self.i2c = i2c
        #Change to NDOF mode
        self.changeMode(0x0C)
        
    def changeMode(self, data):
        ''' @brief Changes mode on BNO055
            @detials Changes mode to some register address provided.
            @param data is the register address set to operating mode (0x3D)
        '''
        self.i2c.mem_write(data,self.addr, 0x3D)
    
    def getCalibStatus(self):
        ''' @brief Gets the calibration status for BNO055
            @detials sets up a buffer as a bytearray that reads from CALIB_STAT mode returning the values
            @return cal_status is a tuple of 4 values for system, gyroscope, accelerometer, and magnetometer.
        '''
        ## @brief Buffer object
        buf = bytearray(1)
        self.i2c.mem_read(buf,self.addr, 0x35)
        ## @brief Calibration status values read from buffer
        cal_status = ( buf[0] & 0b11,
              (buf[0] & 0b11 << 2) >> 2,
              (buf[0] & 0b11 << 4) >> 4,
              (buf[0] & 0b11 << 6) >> 6)
        return cal_status
        
    def getCalibCoef(self):
        ''' @brief Gets calibration coefficients 
            @detials Reads 22 calibration coefficients starting with the x acceleration offset LSB up to 
                     magnetometer radius MSB
            @return Hexidecimal of 22 calibration coefficients for IMU
        '''
        buf = bytearray(22)
        self.i2c.mem_read(buf,self.addr, 0x55)
        ## @brief Data unpacked from buffer being read
        data = struct.unpack('BBBBBBBBBBBBBBBBBBBBBB', buf)
        return data
        
        
    def writeCalibCoef(self, data):
        ''' @brief Writes calibration coefficients
            @param data is the register address starting from 0x55 ( x acceleration offset LSB)
        '''
        self.i2c.mem_write(data,self.addr, 0x55)
    
    def readEuler(self):
        ''' @brief Returns euler angles
            @detials Reads 6 bytes starting from EULER_DATA_X_LSB (0X1A)
            @return eul_vals are the euler angles in degrees
        '''
        buf = bytearray(6)
        self.i2c.mem_read(buf, self.addr, 0x1A)
        ## @brief Unpacked buffer containg heading,pitch,roll of euler angles
        eul_signed_ints = struct.unpack('<hhh', buf)
        
        ## @brief Euler angles in degrees
        eul_vals = tuple(eul_int/16 for eul_int in eul_signed_ints)
        return eul_vals        
        
    def readOmega(self):
        ''' @brief Returns angluar velocity.
            @detials Reads 6 bytes starting from GYR_DATA_X_LSB (0X14)
            @return omg_vals are angular velocities in deg/s
        '''
        buf = bytearray(6)
        self.i2c.mem_read(buf, self.addr, 0x14)
        ## @brief Unpacked buffer containg heading,pitch,roll change over time.
        omg_signed_ints = struct.unpack('<hhh', buf)
        
        ## @brief Angular velocity in deg/s
        omg_vals = tuple(omg_int/16 for omg_int in omg_signed_ints)
        return omg_vals
        
    def deint(self):
        ''' @brief Turns off communication for IMU
        '''
        self.i2c.deinit()


    
    
    
