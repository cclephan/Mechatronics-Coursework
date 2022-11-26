/** @file print_array.cpp
 *  This file contains the overloaded function print_array to handle 4 different
 *  data types (floats, unsigned/signed 8 bit integer, and booleans). This will
 *  run on an ESP32 and print out arrays similar to Python formatting.
 */


#include "print_array.h"

/** @brief   Task which prints an array of float values.
 *  @details This task first checks the size of an input float array and if it's empty
 *           the function outputs square brackets with nothing inside (similar to Python).
 *           When there is a value in the array the function first prints the open bracket
 *           then indexes through values of the array printing them out with commas in
 *           between. Once the index reaches the maximal size-1 the array values have been
 *           completely printed out so an empty bracket is printed.
 *  @param   p_array A pointer to array of float values.
 *  @param   size The size of an array (unsigned 8 bit integer type).
 *  @param   device Location where the array is being printed.
 */
void print_array (float* p_array, uint8_t size, Print& device)
{
    if (size != 0){
        device << "[";
        for(int8_t i = 0; i < size; i++)
        {
            //device.print(p_array[i], DEC);
            device.print(p_array[i]);
            if( i < size-1){
                device << ", ";
            }
            if(i == size-1){
                device << "]";
            }
        }
    }
    else{
        device << "[]";
    }
}

/** @brief   Task which prints an array of unsigned 8 bit integer values.
 *  @details This task first checks the size of an input unsigned 8 bit integer array and if it's empty
 *           the function outputs square brackets with nothing inside (similar to Python).
 *           When there is a value in the array the function first prints the open bracket
 *           then indexes through values of the array printing them out with commas in
 *           between. Once the index reaches the maximal size-1 the array values have been
 *           completely printed out so an empty bracket is printed.
 *  @param   p_array A pointer to array of unsigned 8 bit integer values.
 *  @param   size The size of an array (unsigned 8 bit integer type).
 *  @param   device Location where the array is being printed.
 */
void print_array (u_int8_t* p_array, uint8_t size, Print& device)
{
    if (size != 0){
        device << "[";
        for(int8_t i = 0; i < size; i++)
        {
            device << p_array[i];
            if( i < size-1){
                device << ", ";
            }
            if(i == size-1){
                device << "]";
            }
        }
    }
    else{
        device << "[]";
    }
}

/** @brief   Task which prints an array of signed 8 bit integer values.
 *  @details This task first checks the size of an input signed 8 bit integer array and if it's empty
 *           the function outputs square brackets with nothing inside (similar to Python).
 *           When there is a value in the array the function first prints the open bracket
 *           then indexes through values of the array printing them out with commas in
 *           between. Once the index reaches the maximal size-1 the array values have been
 *           completely printed out so an empty bracket is printed.
 *  @param   p_array A pointer to array of signed 8 bit integer values.
 *  @param   size The size of an array (unsigned 8 bit integer type).
 *  @param   device Location where the array is being printed.
 */
void print_array (int8_t* p_array, uint8_t size, Print& device)
{
    if (size != 0){
        device << "[";
        for(int8_t i = 0; i < size; i++)
        {
            device << p_array[i];
            if( i < size-1){
                device << ", ";
            }
            if(i == size-1){
                device << "]";
            }
        }
    }
    else{
        device << "[]";
    }
}

/** @brief   Task which prints an array of boolean values.
 *  @details This task first checks the size of an input boolean array and if it's empty
 *           the function outputs square brackets with nothing inside (similar to Python).
 *           When there is a value in the array the function first prints the open bracket
 *           then indexes through values of the array printing them out with commas in
 *           between. If a value is 1 or True in the array a T is printed and if the value
 *           is 0 or False then F is printed. Once the index reaches the maximal size-1 the 
 *           array values have been completely printed out so an empty bracket is printed.
 *  @param   p_array A pointer to array of boolean values.
 *  @param   size The size of an array (unsigned 8 bit integer type).
 *  @param   device Location where the array is being printed.
 */
void print_array (bool* p_array, uint8_t size, Print& device)
{
    if (size != 0){
        device << "[";
        for(int8_t i = 0; i < size; i++)
        {
            if (p_array[i] == 1){
                device << "T";
            }
            else{
                device << "F";
            } 
            if( i < size-1){
                device << ", ";
            }
            if(i == size-1){
                device << "]";
            }
        }
    }
    else{
        device << "[]";
    }
}
