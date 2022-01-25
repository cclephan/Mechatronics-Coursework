''' @file main3.py
    @brief Main file, which encoder and user task are being run.
    @details File imports the two classes for each task and calls out the period at which they will be run.
            The tasks are created as objects and a variable zero is a boolean determining whether the encoder must be zero'd.
            A while loop is created to constantly run through tasks at their frequency where if the user wants to zero, the
            information is fed from the user task to encoder, and if the user calls out for a position or delta, that 
            information is passed from encoder task to user.
            
            FSM Diagram Link: https://imgur.com/a/KH3PAQ6
            
    @author Christian Clephan
    @author John Bennett
    @date October 16, 2021    
'''
import motor
import task_motor
import task_encoder_v2
import task_user_v3
import shares

##  @brief Encoder task period (2 milliseconds)
T_encoder = 2
##  @brief Encoder task period (2 milliseconds)
T_motor = 2
##  @brief User task period (100 milliseconds)
T_user = 100

## Motor Shares Index referances
ID = 0
POSITION = 1
VELOCITY = 2
REF_POSITION = 3
REF_VELOCITY = 4
IS_ZERO = 5
DIS_FAULT = 6
PID = 7
DUTY = 8

if __name__ =='__main__':
    
    ## @brief Motor1Share and Motor2Share contains all the share data for a given motor
    # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
    Motor1Share = shares.ShareMotorInfo([1,0,0,0,0,False,False,[0,0,0],0])
    Motor2Share = shares.ShareMotorInfo([2,0,0,0,0,False,False,[0,0,0],0])
    
    ## @brief Creates motor driver object
    motor_drv = motor.DRV8847(3)
    
    
    
    ##  @brief Creating a variable for the encoder task in the Task_Encoder Class at period T_encoder
    encoderTask1 = task_encoder_v2.Task_Encoder(T_encoder,Motor1Share)
    ##  @brief Creating a variable for the encoder task in the Task_Encoder Class at period T_encoder
    encoderTask2 = task_encoder_v2.Task_Encoder(T_encoder,Motor2Share)
    ##  @brief Creating a variable for the motor task in the Task_Motor Class at period T_motor
    motorTask1 = task_motor.Task_Motor(T_motor,Motor1Share,motor_drv)
    ##  @brief Creating a variable for the encoder task in the Task_Encoder Class at period T_motor
    motorTask2 = task_motor.Task_Motor(T_motor,Motor2Share,motor_drv)
    ##  @brief Creating a variable for the user task in the Task_User Class at period T_user
    userTask = task_user_v3.Task_User(T_user,Motor1Share,Motor2Share)

    
    
         
    while (True):
        #Attempt to run FSM unless Ctrl+c is hit
        try:
            
            ##  @brief Tuple containing encoder position and delta from the encoder task to user task
            encoderTask1.run()
            encoderTask2.run()
            userTask.run()
            motorTask1.run()
            motorTask2.run()
            
            
            
        #If there is an interuption break
        except KeyboardInterrupt:
            break
    motor_drv.disable()   
    print('Program Terminating')