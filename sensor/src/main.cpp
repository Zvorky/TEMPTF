/* 
TEMPTF - Sensor Module

Cícero Pizetta Pizutti          - 68612
Enzo Zavorski Delevatti         - 199575
Felipe Borges da Silva          - 184387
Thiago Reis Petereit Dos Santos - 198853
*/


#include <Arduino.h>
#include "utils.h"


// ---[ CONFIGURABLES ]---
// Leave blank to get user input OR set a default value

// WiFi
const String ssid = "";
const String passwd = "";


void setup() {
    Serial.begin(9600);
    delay(1000);
    while (setupWiFi(ssid, passwd) != WL_CONNECTED) delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
}