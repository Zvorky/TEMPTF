# TEMPTF - Sensor Module (ESP32 - Arduino Framework)
This module contains the source code for the ESP32 platform using the Arduino framework. It is responsible for interfacing with the LM35 temperature sensor, collecting temperature data, applying local averaging and safety checks, and transmitting the processed temperature readings to the central voter server at regular intervals. The module ensures that the data is formatted correctly and adheres to the specified protocols for reliable communication within the TEMPTF system.

---

See [README.md](../README.md) for an overview of the entire project and its components.

## TODO
- [ ] **LM35 Sensor Integration:** Reads temperature data from the LM35 sensor and processes it according to the defined logic.
- [ ] **Local Averaging:** Computes the average of 10 regular readings taken within a 5-second window to ensure data stability.
- [ ] **Safety Check (Checkpoint):** Implements a mechanism to revert to the last successful measurement if the coefficient of variation exceeds 10%, ensuring that only reliable data is transmitted.
- [ ] **Data Transmission:** Transmits the processed temperature readings to the central voter server every 5 seconds in Celsius with two decimal places.
- [ ] **Error Handling:** Monitors sensor performance and handles any anomalies in the readings to maintain the integrity of the data being sent to the server.