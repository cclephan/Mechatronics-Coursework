/** @file shares.h
 *  This file contains extern declarations of shares and queues which are used
 *  in more than one file of a demonstration project.
 * 
 *  @author JR Ridgely
 *  @date   2021-Oct-23 Original file
 *  @copyright (c) 2021 by JR Ridgely, released under the LGPL 3.0. 
 */

#ifndef _SHARES_H_
#define _SHARES_H_

#include "taskqueue.h"
#include "taskshare.h"

// A share which holds boolean whether or not to be spotted
extern Share<bool> spot_me_bro;

// A share which holds boolean whether spotting is completed or not
extern Share<bool> spot_complete;

// A queue which triggers a task to print the count at certain times
extern Queue<float> vel_queue;

#endif // _SHARES_H_