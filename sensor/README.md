# TEMPTF - Sensor Module (ESP32 - Arduino Framework)
This module contains the source code for the ESP32 platform using the Arduino framework. It is responsible for interfacing with the LM35 temperature sensor, collecting temperature data, applying local averaging and safety checks, and transmitting the processed temperature readings to the central voter server at regular intervals. The module ensures that the data is formatted correctly and adheres to the specified protocols for reliable communication within the TEMPTF system.

[Leia-me em Português](LEIAME.md)

---

See the root [README.md](../README.md) for an overview of the entire project and its components.

## Circuit Assembly

**LM35 Sensor Pinout:**
![LM35 Pinout](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fclubedomaker.com%2Fwp-content%2Fuploads%2F2026%2F01%2Fimagem_2026-01-05_224447026-768x315.png&f=1&nofb=1&ipt=7b2fded10111e792c8cf17502ca55a56a0a0da5f85643e53d30d63f1a7a68bfa)

**Pin Connections:**

| LM35      | ESP32         |
|-----------|---------------|
| +Vs       | 3V3           |
| Vout      | GPIO ADC (ex: 34) |
| GND       | GND           |

> **Notes:**
> - No resistor is needed between the LM35 and the ESP32.
> - It is recommended to power the LM35 with 3V3 for compatibility with the ESP32 ADC.
> - The Vout output of the LM35 should be connected to an analog input pin (ADC) of the ESP32, such as GPIO34, GPIO35, etc.