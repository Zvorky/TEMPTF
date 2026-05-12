# General MQTT Communication Rules

[Leia-me em Português](COMUNICACAO.md)

## 1. Connection to MQTT Broker
Since we cannot predict the server IP address (we only know it will be an IPv4), it is recommended to use a constant that is easy to edit or a configurable variable during device-sensor startup.

### Port: `1883`
We use the default MQTT Broker port `:1883`.

### MQTT Publication Parameters
- **QoS:** `0` (best-effort delivery, without confirmation).
- **Retain:** `false` (do not keep last reading on broker).
> *`0` and `false`, respectively, are the default values in most MQTT libraries.*

Since readings are continuous (every 5 seconds), this mode prevents accumulation of retained messages and keeps the flow simple.

## 2. Topic for *Publishing*
Each device-sensor should publish its readings to the topic `sensors/{sensor_id}` every 5 seconds, where `sensor_id` is what distinguishes each device-sensor. It can be the device+technology, group, or the sensor itself.

Any message in a topic outside a single level after `sensors/` will be ignored by the server.

Since we are dividing into subtopics, your device's client_id does not matter. The server will extract the sensor_id from the topic and associate the reading with the corresponding sensor.

### ✅ Correct:
- `sensors/dht11`
- `sensors/esp32_micropython`
- `sensors/raspberry_pi`
- `sensors/marcos_joao`

### ❌ Incorrect:
- `sensors/`
- `sensors`
- `sensors/lm35/temperature`
- `leituras/lm35`

## 3. Message Format
Published messages must be integer numerical values in hundredths of degrees Celsius, that is, the temperature in Celsius multiplied by 100. The server will interpret these values and convert them to the correct format.

The message should be just the int, without units or other characters. The server will process the message and format it for display.

### Strict Payload Rules
- Encoding: **UTF-8**.
- Content: string containing **only one decimal integer** in hundredths of degree Celsius.
- Sign: only `-` allowed at the beginning for negative values.
- Do not use: period, comma, unit (`C`, `°C`), scientific notation, additional text.

### ✅ Correct:
Reading (°C) | MQTT Message | Server Reading |
---|---|---
23.45   | 2345  | 23.45°C  |
0.23    | 23    | 0.23°C   |
100.51  | 10051 | 100.51°C |
1.639   | 164   | 1.64°C   |
-0.69   | -69   | -0.69°C  |
-2.10   | -210  | -2.10°C  |

### ❌ Incorrect:
Reading (°C) | MQTT Message | Server Reading |
---|---|---
24.00   | 24     | 0.24°C       |
1.639   | 1639   | 16.39°C      |
23.45   | 23.45  | **Ignored** |
24.12   | 2412°C | **Ignored** |
0.23    | 0.23   | **Ignored** |
-2.10   | -2.10  | **Ignored** |

---

# MQTT Test Server
The MQTT test server ([`tools/test_mqtt_server.py`](tools/test_mqtt_server.py)) is a simple implementation using the `paho-mqtt` library in Python. It connects to an MQTT broker, subscribes to the `sensors/#` topic to receive messages from sensors, and displays formatted readings on the console with payload verification.

## Installation and Usage
1. Make sure you have Python 3 installed.
2. Install the `paho-mqtt` library:
    ```bash
    pip install paho-mqtt
    ```
3. Install and run a local MQTT broker, such as Mosquitto:
    ### Linux 
    #### Debian/Ubuntu:
    ```bash
    sudo apt update
    sudo apt install mosquitto mosquitto-clients
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    ```
    #### Via Snap:
    ```bash
    sudo snap install mosquitto
    sudo snap start mosquitto
    ```
    #### Via Podman:
    ```bash
    podman run -d --name mosquitto -p 1883:1883 eclipse-mosquitto
    ```

    ### Windows:
    Download the Mosquitto installer from https://mosquitto.org/download/ and follow the installation instructions.
4. Run the MQTT test server:
    ```bash
    python tools/test_mqtt_server.py
    ```
5. Connect your Device-Sensor to the same MQTT broker and publish messages to the correct topic to validate communication.
