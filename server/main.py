import logging
import re
import time
from datetime import datetime
from pathlib import Path
from src import nmr

import paho.mqtt.client as mqtt


NMR_LOOP_INTERVAL = 5 # seconds
NMR_LOOP_ACTIVE = False

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/"

LOG_DIR = Path(__file__).resolve().parent / ".logs"
SESSION_LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOGGER_NAME = "temptf.server"

logger = logging.getLogger(LOGGER_NAME)
VOTER = nmr.NMR(tolerance=10, isolation_steps=3, recovery_steps=3, failsafe=None, verbose=True, logger=logger)


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(SESSION_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = True
    return logger


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(MQTT_TOPIC + "+")
        logger.info("Connected to MQTT broker successfully")
        logger.info(f"Running on: {mqtt.socket.gethostbyname(mqtt.socket.gethostname())}:{MQTT_PORT}")
    else:
        logger.error("Connection failed with code %s", rc)


def on_message(client, userdata, msg):
    try:
        if msg.topic.startswith(MQTT_TOPIC):
            sensor_id = msg.topic[len(MQTT_TOPIC):]
        else:
            logger.warning("Unexpected topic '%s'", msg.topic)
            return

        if not sensor_id or "/" in sensor_id:
            logger.warning("Unexpected topic '%s'", msg.topic)
            return

        try:
            raw_value = msg.payload.decode().strip()
        except UnicodeDecodeError:
            logger.warning("Could not decode payload as UTF-8")
            return

        if not re.fullmatch(r"-?\d+", raw_value):
            logger.warning("Invalid payload format '%s'", raw_value)
            return

        VOTER.update_sensor(sensor_id, int(raw_value))

        temperature = int(raw_value) / 100 # float Cº
        logger.info("%s: \t%.2f\t°C", sensor_id, temperature)
    except Exception as error:
        logger.exception("Error processing message: %s", error)


def on_disconnect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        logger.warning("Unexpected disconnection: %s", rc)


def create_client():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client


def run():
    global NMR_LOOP_ACTIVE

    setup_logging()
    client = create_client()

    try:
        logger.info("Connecting to MQTT broker at %s:%s...", MQTT_BROKER, MQTT_PORT)
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start() # Start the network loop in a separate thread
    except Exception as error:
        logger.error("Connection error: %s", error)

    time.sleep(1)
    logger.info("Starting NMR loop with interval of %s seconds", NMR_LOOP_INTERVAL)
    try:
        NMR_LOOP_ACTIVE = True
        while NMR_LOOP_ACTIVE:
            last = time.time()
            voted = VOTER.get_value()
            state = VOTER.get_state()

            if state == "NO_DATA":
                logger.info("Aguardando dados dos sensores...")
            elif voted is None:
                logger.warning("NMR sem valor votado disponível (estado=%s)", state)
            else:
                logger.info("TEMPTF: %.2f °C (%s)", voted / 100, state.lower())

            # Busy Wait
            while time.time() - last < NMR_LOOP_INTERVAL:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print()
        logger.info("Shutting down...")
        NMR_LOOP_ACTIVE = False
    finally:
        client.loop_stop()
        client.disconnect()


def tune_sensors():
    x = ''
    while x != '0':
        x = input("Enter sensor ID to tune (or '0' to finish): ").strip()
        if x == '0':
            break
        if x:
            factor_input = input(f"Enter factor for {x} (default 1.0): ").strip()
            offset_input = input(f"Enter offset for {x} (default 0.0): ").strip()

            try:
                factor = float(factor_input) if factor_input else 1.0
                offset = float(offset_input) if offset_input else 0.0
                VOTER.tune_sensor(x, factor, offset)
            except ValueError:
                logger.warning("Invalid input for factor or offset.")


if __name__ == "__main__":
    if input("Tune sensors? (y/N)").strip().lower() == "y":
        tune_sensors()
    run()
