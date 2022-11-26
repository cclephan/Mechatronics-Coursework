'''@file main.py
    @brief Main file runs tasks through loop.
    @details Runs through seperate tasks at defined period and shares data to accomplish overall task of ballancing the
             ball. Share objects are instantiated with initial values (0) and tasks with corresponding shares are also
             instantiated. The user can exit program by pressing cntrl+c
    @author Christian Clephan
    @author John Bennett
    @date   December 7, 2021
    
    @page LABff HW0xff: Ball Balancer Term Project
    @section task_diagram Task Diagram
            Below is our task diagram which demonstrates how each task will communicate with eachother and the variables contained
            within each share.
    @section fsm_diagrams FSM Diagrams
            Below are the finite state machines for individual tasks and how they all contribute to the goal of balancing the
            ball on a platform and record data when the user requests.
    @section User_Interface User Interface
    @section Contrl Controller Selection 
    @section Plots Data Plots
    @section Video Video Demonstration
    

'''
import motor
import task_motor
import shares
import task_control
import task_TP
import Task_IMU
import task_User
import pyb
import task_data


##  @brief Moter task period (1 millisecond)
T_motor = 3
##  @brief User task period (100 milliseconds)
T_user = 100

##  @brief Data task period (5000 milliseconds)
T_data = 5000
##  @brief User task period (1 millisecond)
T_control = 3


if __name__ == '__main__':
    
    ##  @brief Share containing ball state variables x, y, vx, vy, z, and time change.
    ball_share = shares.Share((0,0,0,0,0,0))
    ##  @brief Share containing theta in x/y and angular velocity in x/y
    IMU_share = shares.Share((0,0,0,0))
    ##  @brief Duties for both motors
    duty_share = shares.Share((0,0))
    ##  @brief Share containing all state variable data x,y, dx, dy, theta x/y, angular velocity x/y, and duties
    State_share = shares.Share([0,0,0,0,0,0,0,0,0,0])
    ##  @brief Determines whether motors are on or off.
    Mode_share = shares.Share([0])
    ##  @brief Data collection parameters
    #   @details Contains frequency and total time of data collection, then determines what data should be collected
    collectStatus = shares.Share([0,0,[0,0,0,0,0,0,0,0,0,0]])
    
    
    ##  @brief Creating a variable for the motor task in the Task_Motor Class at period T_motor
    motor_drv = motor.DRV8847(3)
    ##  @brief Motor task running at defined period and using motor driver object.
    motorTask = task_motor.Task_Motor(T_motor,duty_share,motor_drv)
    
    ##  @brief Touch panel task sharing ball data
    tpTask = task_TP.Task_TP(ball_share)   
    ##  @brief Runs IMU task logic communicating IMU data in a share.
    IMUTask = Task_IMU.Task_IMU(IMU_share)
    
    ## @brief Communication reader between PuTTY and Nucleo board so user can type commands
    CommReader = pyb.USB_VCP()
    ##  @brief User task running at specified period and using USB VCP for reading communication.
    #   @details Uses system mode, state, and collect status shares
    UserTask = task_User.Task_User(T_user, Mode_share, State_share, collectStatus, CommReader)
    
    
    ##  @brief Task that uses data collected by IMU and touch panel to send a duty for motors to run.
    cntrlTask = task_control.Task_Controller(T_control,ball_share, IMU_share, duty_share,State_share,Mode_share)
    
    dataTask = task_data.Task_Data(T_data,collectStatus,State_share)
    
    
    while (True):
        try:
            tpTask.update()
            IMUTask.update()
            cntrlTask.run()
            motorTask.run()  
            UserTask.run()
            dataTask.run()
              
            
        except KeyboardInterrupt:      
            
            break
    
    duty_share.write((0,0))
    motorTask.run() 
    print('Program Terminating')
    

