''' @file main3.py
    @brief Main file, which hardeware and user task are being run.
    @details File imports the classes for each task and calls out the period at which they will be run.
            The tasks are created as objects and share objects containing information shared to operate motor.
            Additionally a motor driver is created to be called as a parameter in motor task.
            A while loop is created to constantly run through tasks at their frequency specified by period variables.
            The user can press cntrl+c as a keyboard interupt to stop the program. See Results/Discussion page for data collection. <br>
    @page Results/Discussion
    @section sec_report Lab 4 Discussion
            Below are images of our FSM used by our lab 4 code, a block diagram of the closed loop control, and our progression plot. 
            For this assignment we incorporated our encoder driver with our motor
            driver to perform closed-loop speed control. We added new variables to the motor such as PID and  
            REF_ VELOCITY and a new class called closedloop. This allowed us to track the error in the system and 
            perform closed loop control. Our closedloop class can perform integral and derivative control but we 
            decided to start our tuning with only proportional control.
            \image html Lab4FSM.jpg "Figure 1: Lab 4 State Machine" <br>
            To accomplish this we created a new FSM seen in Figure 1. 
            The new state PID Prompt in the user task can be accessed by inputting 1 or 2 in the putty command terminal this task prompts 
            for numeric values to proportional, integral, derivative and the desired velocity of the system. Then our motor waits 1 
            second in the waiting for user input task then the motor starts and the data collection continues for 9 
            more seconds. totalling 10 seconds of data collection. Then turns off and waits for a new PID Prompt.       
            
            \image html block.JPG "Figure 2: Closed Loop Block Diagram" <br>
            
            Our closed loop controller (Figure 2) begins with a step input function, which is specified by the user when either a 1 or 2 is pressed. 
            This prompts the user for PID gains and a set-point velocity, which will be the magnitude of the input step function. 
            The PID gains act on an error signal which is the difference between input motor speed versus what’s output and measured 
            by the encoder. After the PID gain block the signal is in duty percent, which is saturated between -100 and 100%. 
            This signal is converted to a voltage by Kpwm, where 12V from the power supply would create 100% duty cycle. Next, the signal 
            is sent to the plant (motor) where the output is motor speed. The encoder reads motor velocity and sends feedback to the 
            beginning of the block diagram to compare what’s being input by the code versus the real world motor speed. <br>
            
            When beginning our testing of the closed loop controller we started our tuning of the controller with our positionial 
            controller, Kp of our PID. In Figure 3, we set the goal velocity to 100 rad/s for tuning with 4 different Kp gains. 
            We began with small proportional gain values to ensure our response did not overload or fault the hardware. <br>
        
            \image html Data.JPG "Figure 3: Progression Plot" <br>
            
            The first test was a Kp = .5 %V/(rad/s) (gray) this value produced a max velocity of 50 rad/s much smaller than what we 
            expected. We then decided to increase the Kp = 1 %V/(rad/s)  (blue) this significantly increased the velocity to 75 rad/s. 
            Since we didn't hit the desired velocity we doubled the gain, Kp = 2 %V/(rad/s) (orange) the steady state velocity was 
            85 rad/s. From the three data points recorded we could tell there was a natural decay when increasing 100 rad/s that caused 
            us to choose a Kp = 5 %V/(rad/s) (yellow), which yielded a velocity near 100 rad/s. From further testing any Kp values above 
            5 %V/(rad/s) has a chance of making the system go unstable and faults the motor. Therefore we conclude that a Kp = 5 %V/(rad/s)
            is the optimal choice when performing pure proportional control on a free shaft.            
            
    
    
    @author Christian Clephan
    @author John Bennett
    @date November 14 2021    
'''
import motor
import task_hardware
import task_user_v3
import shares

##  @brief Encoder task period (2 milliseconds)
T_motor = 2
##  @brief User task period (40 milliseconds)
T_user = 40

## Motor Shares Index referances
## @brief Index reference for encoder number
ID = 0
## @brief Index reference for current position (rad)
POSITION = 1
## @brief Index reference for current velocity (rad/s)
VELOCITY = 2
## @brief Index reference for reference (previous) position (rad)
REF_POSITION = 3
## @brief Index reference for reference (previous) velocity (rad/s)
REF_VELOCITY = 4
## @brief Index reference for zero flag
IS_ZERO = 5
## @brief Index reference for disable fault flag
DIS_FAULT = 6
## @brief Index reference for PID controller
PID = 7
## @brief Index reference for current duty (% PWM)
DUTY = 8
## @brief Index reference for checking if there is a fault
IS_FAULT = 9



if __name__ =='__main__':
    
    ## @brief Motor1Share and Motor2Share contains all the share data for a given motor
    # [Encoder number (int), Current Position (ticks), Current delta (ticks/period), duty(int), Zero (boolean), Fault(boolean)]
    Motor1Share = shares.ShareMotorInfo([1,0,0,0,0,False,False,[0,0,0],0,False])
    Motor2Share = shares.ShareMotorInfo([2,0,0,0,0,False,False,[0,0,0],0,False])
    
    ## @brief Creates motor driver object
    motor_drv = motor.DRV8847(3)
    
    

    ##  @brief Creating a variable for the hardware task in the Task_Hardware Class at period T_motor
    motorTask1 = task_hardware.Task_Hardware(T_motor,Motor1Share,motor_drv)
    ##  @brief Creating a variable for the hardware task in the Task_Hardware Class at period T_motor
    motorTask2 = task_hardware.Task_Hardware(T_motor,Motor2Share,motor_drv)
    ##  @brief Creating a variable for the user task in the Task_User Class at period T_user
    userTask = task_user_v3.Task_User(T_user,Motor1Share,Motor2Share)

    
    
         
    while (True):
        #Attempt to run FSM unless Ctrl+c is hit
        try:
            
            userTask.run()
            motorTask1.run()
            motorTask2.run()
            
        #If there is an interuption break
        except KeyboardInterrupt:
            break
    motor_drv.disable()   
    print('Program Terminating')