''' @file main3.py
    @brief Main file, which encoder, motor, and user task are being run.
    @details File imports the classes for each task and calls out the period at which they will be run.
            The tasks are created as objects and share objects containing information shared to operate motor.
            Additionally a motor driver is created to be called as a parameter in motor task.
            A while loop is created to constantly run through tasks at their frequency specified by period variables.
            The user can press cntrl+c as a keyboard interupt to stop the program
            
    @author Christian Clephan
    @author John Bennett
    @date October 16, 2021    
'''
import motor
import task_motor
import task_encoder_v2
import task_user_v3
import shares

##  @brief Encoder task period (1.5 milliseconds)
T_encoder = 1.5
##  @brief Encoder task period (2 milliseconds)
T_motor = 2
##  @brief User task period (50 milliseconds)
T_user = 40

if __name__ =='__main__':
    
    ## @brief Motor1Share contains all data shared for motor 1
    # @details Shared initial values in order include Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)
    # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
    Motor1Share = shares.ShareMotorInfo([1,0,0,0,False,False])
    
    ## @brief Motor2Share contains all data shared for motor 2
    # @details Shared initial values in order include Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)
    Motor2Share = shares.ShareMotorInfo([2,0,0,0,False,False])
    
    ## @brief Creates motor driver object
    motor_drv = motor.DRV8847(3)
    
    
    
    ##  @brief Creating a variable for the encoder task in the Task_Encoder Class at period T_encoder
    encoderTask1 = task_encoder_v2.Task_Encoder(T_encoder,Motor1Share)
    ##  @brief Creating a variable for the encoder task in the Task_Encoder Class at period T_encoder
    encoderTask2 = task_encoder_v2.Task_Encoder(T_encoder,Motor2Share)
    ##  @brief Creating a variable for the motor task in the Task_Motor Class at period T_motor
    motorTask1 = task_motor.Task_Motor(T_motor,Motor1Share,motor_drv)
    ##  @brief Creating a variable for the motor task in the Task_Motor Class at period T_motor
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