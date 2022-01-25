

def fib(idx):
        f_n1 = 1            #Fibonacci sequence at index 1
        f_n2 = 0            #Fibonacci sequence at index 0
        if idx == 0:        
            num = 0         #Sets the returned value to Fibonacci sequence at index 0
        if idx == 1:
            num = f_n1      #Sets the returned value to Fibonacci sequence at index 0
        if idx > 1:         
            for a in range(idx-1):      #Loops through to index user specified
                num = f_n1 + f_n2       #Sets the returned number equal to the addition of the 2 initial fibonnaci numbers
                f_n2 = f_n1             #Increases index of the F(n-2) term to F(n-1) to be used in the next loop
                f_n1 = num              #Increases index of the F(n-1) term to F(n), (the returned number) to be used in the next loop
     
                
        return num                      #Returns the specified fibonnaci number at requested index once finished with the loop or specified above if statements

if __name__ == '__main__':
    idx = 0                             #Sets the index to a value so it is specified for the while loop
    while idx != -1:                    #While loop with exit condition once user is done with program
        try:                            #If no error is found with the program
            idx = int(input("Enter an index for the Fibonacci sequence or type -1 to quit: "))  #Asks user to enter a value for the index
            if idx >= 0:                #If statement to check for exit condition
                print ('Fib number at index {:} is {:}.'.format(idx,fib(idx)))
            if idx < -1:                #If statement to check for exit condition
                print ('Enter a positive number!')
        except ValueError:              #If the value enterned is not an integer the program will let the user know
            print('The index must be an integer!')