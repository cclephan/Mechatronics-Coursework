import task_encoder
import task_user



T = 160


if __name__ =='__main__':

    encoderTask = task_encoder.Task_Encoder(T)
    userTask = task_user.Task_User()
    needUserCommand = True
         
    while (True):
        #Attempt to run FSM unless Ctrl+c is hit
        try:
            if needUserCommand:
                keyCommand = userTask.run()
            
            needUserCommand = encoderTask.run(keyCommand)
            
        #If there is an interuption break
        except KeyboardInterrupt:
            break
        
    print('Program Terminating')