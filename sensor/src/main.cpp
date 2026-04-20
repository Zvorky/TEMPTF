/* 
TEMPTF - Sensor Module

Cícero Pizetta Pizutti          - 68612
Enzo Zavorski Delevatti         - 199575
Felipe Borges da Silva          - 184387
Thiago Reis Petereit Dos Santos - 198853
*/


#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFiClient.h>
#include "utils.h"


// ---[ DEFINITIONS ]---

// MQTT
#define MQTT_PORT 1883
#define MQTT_CLIENT "lm35"
#define MQTT_TOPIC "sensors/lm35"
#define PUBLISH_INTERVAL 5000


// ---[ CONFIGURABLES ]---
// Leave blank to get user input OR set a default value

// WiFi
const String ssid = "";
const String passwd = "";

// MQTT
String mqtt_broker_ip = "";


// ---[ GLOBAL OBJECTS ]---

WiFiClient espClient;
PubSubClient mqttClient(espClient);
unsigned long last_publish = 0;


// ---[ FUNCTION DECLARATIONS ]---

bool ensure_mqtt_connection();
void publish_sensor_data(char* payload);


// ---[ MAIN LOGIC ]---

void setup() {
    Serial.begin(9600);
    delay(1000);
    while (setupWiFi(ssid, passwd) != WL_CONNECTED) delay(1000);
    while (!isIPAddress(mqtt_broker_ip)) mqtt_broker_ip = input("MQTT Broker IP: ");
    mqttClient.setServer((char*)mqtt_broker_ip.c_str(), MQTT_PORT);
    last_publish = millis();
}

void loop() {
    // Keep MQTT connection alive
    ensure_mqtt_connection();
    mqttClient.loop();

    // Publish sensor data at regular intervals
    if (millis() - last_publish >= PUBLISH_INTERVAL) {
        const char* payload = "36.0"; // Test value
        publish_sensor_data((char*)payload);
        last_publish = millis();
    }
}


// ---[ FUNCTION DEFINITIONS ]---

bool ensure_mqtt_connection() {
    if (mqttClient.connected()) return true;

    Serial.print("Attempting MQTT connection to ");
    Serial.print(mqtt_broker_ip);
    Serial.print(":");
    Serial.println(MQTT_PORT);
    
    if (mqttClient.connect(MQTT_CLIENT)) {
        Serial.println("Connected to MQTT broker");
        return true;
    } else {
        Serial.print("MQTT connection failed, rc=");
        Serial.println(mqttClient.state());
        return false;
    }
}

void publish_sensor_data(char* payload) {
    if (!ensure_mqtt_connection()) return;
    if (mqttClient.publish(MQTT_TOPIC, payload)) Serial.printf("Published: %s\n", payload);
    else Serial.println("Failed to publish message");
}