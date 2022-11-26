/** @file stat_tracker.h
 *  This is the header for the stat tracker file which can add values together
 *  and return the set of value's average/standard deviation
 * 
 *  @author Christian Clephan
 */

#include <Arduino.h>
#include "PrintStream.h"


/** @brief   Class which keeps track of statistics for set of numbers
 * 
 */
class StatTracker
{
protected:
    float the_sum = 0;
    float f_val = 0;
    int32_t i32_val = 0;
    uint32_t u32_val = 0;
    uint32_t count = 0;
    float sqd_val_sum = 0;
public:
    StatTracker (void);
    void add_data(float);
    void add_data(uint32_t);
    void add_data(int32_t);
    void clear(void);
    float average(void);
    float std_dev (void);

    uint32_t num_points(void);
};