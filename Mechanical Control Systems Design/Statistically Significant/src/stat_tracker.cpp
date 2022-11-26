/** @file stat_tracker.cpp
 *  This program demonstrates a simple statistics tracker which
 *  uses overloaded method add_data to add float/32 signed and unsigned
 *  integers to a variable sum. The squared sum is also tracked for 
 *  calculating the standard deviation. Sum and squared sum are tracked
 *  as well as the overall count of numbers added to the set until all the
 *  variables are cleared using clear method (when the class is called all
 *  the data is set to 0 too). Calling average or std_dev methods returns
 *  values associated with the set.
 * 
 *  @author Christian Clephan
 *  @date   11-16-22
 */

#include "stat_tracker.h"
#include "math.h"

/** @brief   Constructor which creates a stat tracker object.
 */
StatTracker::StatTracker (void)
{
    clear();
}

/** @brief   Adds data to overall sum, squared sum, and adds 1 to numbers passed count
 *  @details Adds passed float f_val into overall sum and squarred sum. Adds one to counter
 *           for numbers being added
 *  @param   f_val Some passed float value
 */
void StatTracker::add_data(float f_val){
    the_sum += f_val;
    sqd_val_sum += f_val*f_val;
    count +=1;
}

/** @brief   Adds data to overall sum, squared sum, and adds 1 to numbers passed count
 *  @details Adds passed signed 32 bit integer i32_val into overall sum and squarred sum. Adds one to counter
 *           for numbers being added
 *  @param   i32_val Some passed 32 bit integer value
 */
void StatTracker::add_data(int32_t i32_val){
    the_sum += i32_val;
    sqd_val_sum += i32_val*i32_val;
    count +=1;
}

/** @brief   Adds data to overall sum, squared sum, and adds 1 to numbers passed count
 *  @details Adds passed unsigned 32 bit integer u32_val into overall sum and squarred sum. Adds one to counter
 *           for numbers being added
 *  @param   u32_val Some passed 32 bit integer value
 */
void StatTracker::add_data(uint32_t u32_val){
    the_sum += u32_val;
    sqd_val_sum += u32_val*u32_val;
    count +=1;
}
/** @brief   Returns the count of numbers that have been added to set
 *  @return  Count of numbers that have been added
 */
uint32_t StatTracker::num_points(void){
    return count;
}

/** @brief   Calculates and returns average (overall sum of values added/number of values added)
 *  @return  Average of numbers added
 */
float StatTracker::average(void){
    float average = (the_sum)/count;
    return average;
}

/** @brief   Calculates and returns standard deviation
 *  @return  Standard deviation of numbers added to set
 */
float StatTracker::std_dev(void){
    float stand_dev = sqrt((sqd_val_sum/count)-((the_sum)/count)*((the_sum)/count));
    return stand_dev;
}

/** @brief   Clears all values being summed and the sum/squared sum
 */
void StatTracker::clear (void)
{
    f_val = 0;
    i32_val = 0;
    u32_val = 0;
    count = 0;
    the_sum = 0;
    sqd_val_sum = 0;
}