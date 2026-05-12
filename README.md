# TEMPTF: Fault-Tolerant Temperature Sensor System
This project focuses on the development of a **Fault-Tolerant Temperature Sensor System (TEMPTF)**. It simulates a high-reliability monitoring environment for equipment used in the transportation of human organs for transplantation. The system is designed to provide accurate temperature readings through redundancy and a robust voting mechanism to ensure data integrity even in the event of sensor failures.

[Leia-me em Português](LEIAME.md)

## Repository Scope
This repository contains the specific implementation for a subset of the distributed system:
 - [**Central Voter Server:**](server/README.md) The application responsible for collecting data via network, executing voting logic, and managing sensor isolation states.
 - [**ESP32 Module (Arduino Framework):**](sensor/README.md) Source code for the ESP32 platform using the Arduino framework.
 - **LM35 Sensor Integration:** Specialized logic for measuring and validating data from the LM35 temperature sensor.
 - [**MQTT Communication:**](COMMUNICATION.md) Details about the communication protocol used for data transmission between sensors and the central server.

Additional scripts for testing and simulation are included at [`tools/`](tools/).

### Authors
 - [Cícero Pizetta Pizutti](https://github.com/ciceropizutti)
 - [Enzo Zavorski Delevatti](https://github.com/zvorky)
 - [Felipe Borges da Silva](https://github.com/znyctus)
 - [Thiago Reis Petereit Dos Santos](https://github.com/thiagopetereit)

## Technical Specifications & Logic
_Prof. Dr. Marcelo Trindade Rebonatto_

### 1. Sensor Devices
Each sensing unit must adhere to strict data transmission and safety protocols:
 - **Data Frequency:** A single temperature value must be transmitted every 5 seconds.
 - **Local Averaging:** The transmitted value is the average of 10 regular readings taken within the 5-second window.
 - **Safety Check (Checkpoint):** If the coefficient of variation of the 10 readings exceeds 10%, the device must revert to the last successfully calculated measurement (checkpoint) and monitor subsequent readings until a stable value is found.
 - **Formatting:** Readings are transmitted in Celsius with two decimal places.

### 2. Central Voter System
The server processes incoming data from the diverse sensor network to determine the final system temperature:
 - **Consensus & Masking:** If all sensor values are within 10% of the arithmetic mean (x), the system displays the lowest temperature as the consensus value. If a sensor diverges by more than 10% from the mean, it indicates a "fault masking" event.
 - **Sensor Isolation:** If a specific sensor remains divergent for 3 consecutive cycles, it is flagged as compromised and isolated from the primary calculation.
 - **Degraded Operation:** After isolation, the system continues to operate with the remaining two sensors, signaling a "degraded" state.
 - **System Instability:** If the remaining two sensors diverge by more than 10%, the system is declared unstable and displays the last safe measurement.
 - **Recovery Logic:** Isolated sensors are continuously monitored. They are reintegrated if they show consistent agreement (less than 10% divergence) for 3 consecutive measurements.
<!-- - **Communication Protocol:** Waiting for other groups to decide between MQTT or TCP/IP. -->

