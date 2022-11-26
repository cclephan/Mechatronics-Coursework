/** @file motor_driver.h
 *  This is the header for the motor driver file
 * 
 *  @author Christian Clephan
 */

#include <Arduino.h>
#include "PrintStream.h"

#define INB1 12
#define INB2 27
#define PWMB 14
#define MAX_DUTY 255

/** @brief   Class which drives geared dc motor
 * 
 */
class MotorDriver
{
protected:
    int16_t duty = 0;
public:
    MotorDriver (void);
    void set_duty(int16_t);
    void stop(void);
    void SOS(void);
};