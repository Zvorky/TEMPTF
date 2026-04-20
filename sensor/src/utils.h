// General Utils


#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <WiFi.h>


// Get an user input from Serial
String input(String msg, bool hide = false);

// Connect to WiFi and return its status. Get ssid and passwd from user input by default. Timeout in seconds.
wl_status_t setupWiFi(String ssid = "", String passwd = "", int timeout = 5);

// True if the string is a valid number
bool isNumber(String str);

#endif