''' @file main2.py
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

import task_encoder_v2
import task_user_v2

##  @brief Encoder task period (2 milliseconds)
T_encoder = 2
##  @brief User task period (50 milliseconds)
T_user = 50

if __name__ =='__main__':
    
    ##  @brief Creating a variable for the encoder task in the Task_Encoder Class at period T_encoder
    encoderTask = task_encoder_v2.Task_Encoder(T_encoder)
    ##  @brief Creating a variable for the user task in the Task_User Class at period T_user
    userTask = task_user_v2.Task_User(T_user)
    ##  @brief Boolean variable determining whether the user wants the encoder to be zero'd
    zero = False
         
    while (True):
        #Attempt to run FSM unless Ctrl+c is hit
        try:
            ##  @brief Tuple containing encoder position and delta from the encoder task to user task
            Update = encoderTask.run(zero)
            zero = userTask.run(Update)
            
            
            
        #If there is an interuption break
        except KeyboardInterrupt:
            break
        
    print('Program Terminating')