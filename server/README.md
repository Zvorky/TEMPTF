# TEMPTF - Central Voter Server
This module implements the central voter server for the TEMPTF system. It is responsible for receiving temperature data from multiple sensors, applying the voting logic to determine the consensus temperature, and managing sensor isolation based on their performance. The server operates in a continuous loop, processing incoming data and updating the system state accordingly.

---

See [README.md](../README.md) for an overview of the entire project and its components.

## TODO
- [x] **Data Reception:** Listens for incoming temperature data from connected sensors.
- [x] **Voting Logic:** Implements the consensus algorithm to determine the final temperature reading based on the data received from the sensors.
- [x] **Sensor Isolation:** Monitors sensor performance and isolates any sensor that consistently diverges from the consensus value.
- [x] **Degraded Operation:** Continues to operate with remaining sensors if one sensor is isolated, and signals a degraded state if necessary.
- [x] **System Stability Monitoring:** Declares the system unstable if the remaining sensors diverge significantly, and displays the last safe measurement.
- [x] **Recovery Mechanism:** Continuously monitors isolated sensors for potential reintegration based on their performance.

## Setup & Run
This server uses MQTT at `localhost:1883` (topic `sensors/{sensor_id}`).  
See [mosquitto.org/download](https://mosquitto.org/download/) for more installation options.

### Linux
1. Install and start the Mosquitto broker 

    #### **Debian/Ubuntu**:

    ```bash
    sudo apt update && sudo apt install -y mosquitto mosquitto-clients
    sudo systemctl enable --now mosquitto
    ```
    Check whether the broker is running
    ```bash
    systemctl status mosquitto --no-pager
    ```

    #### **Snap Alternative**:

    ```bash
    sudo snap install mosquitto
    sudo snap start mosquitto
    ```
    Check whether the broker is running
    ```bash
    snap services
    ```

    #### **Podman Alternative**:

    ```bash
    podman run -d --name mosquitto \
        -p 1883:1883 \
        -v mosquitto-data:/mosquitto/data \
        -v mosquitto-log:/mosquitto/log \
        docker.io/library/eclipse-mosquitto:2
    ```
    Check whether the broker is running
    ```bash
    podman ps
    podman logs mosquitto --tail 50
    ```
    Optional: generate a user systemd unit for auto-start
    ```bash
    podman generate systemd --name mosquitto --files --new
    ```

2. Create and activate a virtual environment in the server directory and install dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Run the server:

    ```bash
    python main.py
    ```

### Windows

1. Install Mosquitto with `winget` and start the broker service (PowerShell as Administrator):

    ```powershell
    winget install EclipseMosquitto.Mosquitto
    net start mosquitto
    ```
    Check whether the broker is running
    ```powershell
    Get-Service mosquitto
    ```

2. Create and activate a virtual environment in the server directory and install dependencies:

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

3. Run the server:

    ```powershell
    python main.py
    ```