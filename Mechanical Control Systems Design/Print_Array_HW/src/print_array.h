/** @file print_array.h
 *  This file contains the source paramaterization for the "overloaded"
 *  print_array function. Print_array needs to be able to point to float,
 *  uint8_t, int8_t, and bool data types. The function also requires the
 *  input array size and where value is printed to (Serial).
 */

#include <Arduino.h>
#include "PrintStream.h"

void print_array (float* p_array, uint8_t size, Print& device = Serial);

void print_array (uint8_t* p_array, uint8_t size, Print& device = Serial);

void print_array (int8_t* p_array, uint8_t size, Print& device = Serial);

void print_array (bool* p_array, uint8_t size, Print& device = Serial);