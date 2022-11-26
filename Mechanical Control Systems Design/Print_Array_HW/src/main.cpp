#include <Arduino.h>
#include "print_array.h"

void setup() {
  Serial.begin (115200);
  while (!Serial) 
  {
  }
  Serial << "Hello, SLO Town." << endl;
  float blah[3] = {1.000,1.001,2.022};
  bool thing[0] = {};
  int8_t thingy [10] = {0,1,2,3,4,5,6,-7,-8,-9};

  while(1){
    print_array(blah, 3, Serial);
    print_array(thing,0,Serial);
    print_array(thingy,10,Serial);
    vTaskDelay(1000);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
}