'''
    @file task_data.py
    @brief data task file created with its own class to be accessed in main file to save and print recorded values.
    @details Task handles all recorded values, recording and print with respect to time.   
    @author Christian Clephan
    @author John Bennett
    @date   December 8, 2021
'''

import utime

## @brief State 0 variable, waiting state.
S0_WAIT = 0
## @brief State 1 variable, record state.
S1_RECORD = 1
    
class Task_Data:
    ''' @brief                  Task data records and prints data
        @details                Values that are recorded and printed are specified from the user task
                                the recorded for a specified amount of time then prints 
    '''

    def __init__(self,period, collectStatus, State_Share):

        ''' 
        @brief              Constructs an data task object
        @details            Instantiates period all variables periab and data record values
        @param              State_Share contains all the current variables to discribe the state
        @param              collectStatus controls the data how and what is collected
        '''
        self.getTime = utime.ticks_ms
        
        ## @brief Defines period as what is called in main for period parameter
        self.OffPeriod = period
        ## @brief current run period
        self.period = period
        ## @brief Time adjusts once clock reaches the period value plus the current time
        self.next_time = period + self.getTime()
        ## @brief current state
        self.state = S0_WAIT
        
        
        ## @brief Controls the data how and what is collected 
        self.collect_Status = collectStatus
        ## @brief Contains all the current variables to discribe the state
        self.State_S = State_Share
        
        
        ## @brief record start time
        self.t0 = 0
        ## @brief record index
        self.idx = [0]
        
        ## @brief Recording counter for filename convention
        self.record_n = 0
        
        ## @brief counts the total number of lines in data
        self.count = 0
        ## @brief built String
        self.data = ""
        
             
    def run(self):
        ''' 
        @brief      Runs data task switches from collecting data to ideal
        @details    This Function runs through a couple states a Wait state and a record state 
                    first the data is triggered by collect status after collecting data the this 
                    task prints and goes back to being ideal
        '''

        # If the current time passes next time (time to update) then next update is utilized to obtain encoder position and delta
        if (self.getTime() >= self.next_time):
            
            
            if self.state == S0_WAIT:
                if self.collect_Status.read()[1]>0:
                    self.period = self.collect_Status.read()[0] * 1000
                    self.collect_Status.read()[0] = 0
                    
                    self.setUpData()
                    self.t0 = self.next_time  
                    self.record()
                    self.transition_to(S1_RECORD)
                    
            elif self.state == S1_RECORD:  
                
                self.record() 
                self.collect_Status.read()[1] -= self.period/1000
                
                if self.collect_Status.read()[1]<= 0 or self.collect_Status.read()[0] > 0:
                    
                    self.count += 100
                    self.setUpData()
                    self.period = self.OffPeriod
                    self.printData()
                    self.transition_to(S0_WAIT)
                  
            
            self.next_time += self.period

    def record(self):
        ''' 
        @brief      Records data baised on current state
        '''
        t = (self.next_time-self.t0)/1000//.01/100
        n = 0
        b = []
        for i in self.idx:
            b.append(self.State_S.read()[i])
            n+=1
            
        self.saveData(t,b)
        
    def printData(self):
        ''' 
        @brief      Prints data currently can only print 2 things at a time
        '''

        print("done!! see file.txt for date")
        
        
    def setUpData(self):
        ''' 
        @brief      sets up data arrays
        '''
        
        val = self.collect_Status.read()[2]
        self.idx = [i for i, element in enumerate(val) if element!=0]
      
        with open("file.txt", 'a') as f:
            ## @brief Read the first line of the file
            f.write("Data:\n")
    
    def saveData(self,t,b):
        ''' 
        @brief      saves the data to a file
        '''
        
        d = ", ".join(map(str,b))
        self.data += "{:}, {:}\n".format(t,d)
        self.count += 1
        
        if self.count >50:    
            ## @brief Name of file that will be searched for on flashdrive or that will be created if not there.
            with open("file.txt", 'a') as f:
                
                f.write(self.data)
            self.count = 0
            self.data = ''
            
    def transition_to(self,new_state):
        ''' 
        @brief              Transitions states
        @details            When called takes in parameter for whatever state needs to be transitioned to.
        @param              Next state to transition to.
        
        '''
        self.state = new_state;
            