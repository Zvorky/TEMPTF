# TEMPTF - Central Voter Server
This module implements the central voter server for the TEMPTF system. It is responsible for receiving temperature data from multiple sensors, applying the voting logic to determine the consensus temperature, and managing sensor isolation based on their performance. The server operates in a continuous loop, processing incoming data and updating the system state accordingly.

---

See [README.md](../README.md) for an overview of the entire project and its components.

## TODO
- [ ] **Data Reception:** Listens for incoming temperature data from connected sensors.
- [ ] **Voting Logic:** Implements the consensus algorithm to determine the final temperature reading based on the data received from the sensors.
- [ ] **Sensor Isolation:** Monitors sensor performance and isolates any sensor that consistently diverges from the consensus value.
- [ ] **Degraded Operation:** Continues to operate with remaining sensors if one sensor is isolated, and signals a degraded state if necessary.
- [ ] **System Stability Monitoring:** Declares the system unstable if the remaining sensors diverge significantly, and displays the last safe measurement.
- [ ] **Recovery Mechanism:** Continuously monitors isolated sensors for potential reintegration based on their performance.