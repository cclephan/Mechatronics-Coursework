#include <Arduino.h>
#include "PrintStream.h"
#include "stat_tracker.h"

void setup() {
  Serial.begin (115200);
  delay (100);
  while (!Serial) { }                   // Wait for serial port to be working
  Serial << "Hello world" << endl;
  StatTracker stat1;
  stat1.add_data(32);
  stat1.add_data(-20);
  float x = 3.2;
  stat1.add_data(x);
  float avg =  stat1.average();
  float std = stat1.std_dev();
  Serial << avg << endl;
  Serial << std << endl;
  stat1.clear();
  stat1.add_data(100);
  stat1.add_data(50);
  stat1.add_data(89);
  x = 93.5;
  stat1.add_data(x);
  float avg2 =  stat1.average();
  float std2 = stat1.std_dev();
  Serial << avg2 << endl;
  Serial << std2 << endl;

}

void loop() {
  // put your main code here, to run repeatedly:
}