from pyb import I2C
import IMU
import utime


if __name__ == '__main__':
    print('ranning')
    i2c = I2C(1,I2C.MASTER)
    i2c.init(I2C.MASTER, baudrate=400000)
    IMU_driver = IMU.BNO055(0x28, i2c)
    
    calibrated = True
    
    while (calibrated):
        try:
            stat = IMU_driver.getCalibStatus()
            print("Value: " + str(stat))
            print("\n")
            utime.sleep(.2)
            
            if(stat[0]*stat[1]*stat[2]*stat[3]==81):
                calibrated = False
                print("calibrated")
                print("Coef: " + str(IMU_driver.getCalibCoef()))
                while (True):
                    #Attempt to run FSM unless Ctrl+c is hit
                    try:
                        print("Euler: " + str(IMU_driver.readEuler()))
                        print("Velocity: " + str(IMU_driver.readOmega()))
                        print("\n")
                        utime.sleep(1)
                        
                        #If there is an interuption break
                    except KeyboardInterrupt:                        
                        break
            
            
        except KeyboardInterrupt:                        
            break
    
    IMU_driver.deint()
    print('Program Terminating')
    

