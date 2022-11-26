import struct
import pyb


SCL = pyb.Pin(pyb.Pin.cpu.B8)
SDA = pyb.Pin(pyb.Pin.cpu.B9)


class BNO055:
    def __init__(self, addr,i2c):
        self.addr = addr
        self.i2c = i2c
        self.changeMode(0x00)
        self.changeMode(0x0C)

    
    def changeMode(self, data):
        self.i2c.mem_write(data,self.addr, 0x3D)
    
    def getCalibStatus(self):
        buf = bytearray(1)
        self.i2c.mem_read(buf,self.addr, 0x35)
        
        cal_status = ( buf[0] & 0b11,
              (buf[0] & 0b11 << 2) >> 2,
              (buf[0] & 0b11 << 4) >> 4,
              (buf[0] & 0b11 << 6) >> 6)
        return cal_status
        
    def getCalibCoef(self):
        buf = bytearray(22)
        self.i2c.mem_read(buf,self.addr, 0x55)
        return buf
        
        
    def writeCalibCoef(self, data):
        self.i2c.mem_write(data,self.addr, 0x55)
    
    def readEuler(self):
        buf = bytearray(6)
        self.i2c.mem_read(buf, self.addr, 0x1A)
        eul_signed_ints = struct.unpack('<hhh', buf)
        
        eul_vals = tuple(eul_int/16 for eul_int in eul_signed_ints)
        return eul_vals        
        
    def readOmega(self):
        buf = bytearray(6)
        self.i2c.mem_read(buf, self.addr, 0x14)
        omg_signed_ints = struct.unpack('<hhh', buf)
        
        omg_vals = tuple(omg_int/16 for omg_int in omg_signed_ints)
        return omg_vals
        
    def deint(self):
        self.i2c.deinit()


    
    
    
