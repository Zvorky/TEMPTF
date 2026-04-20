import logging
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/"

LOG_DIR = Path(__file__).resolve().parent / ".logs"
SESSION_LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOGGER_NAME = "temptf.server"

logger = logging.getLogger(LOGGER_NAME)


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(SESSION_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = True
    return logger


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(MQTT_TOPIC + "+")
        logger.info("Connected to MQTT broker successfully")
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
            temperature = float(raw_value)
        except UnicodeDecodeError:
            logger.warning("Could not decode payload as UTF-8")
            return
        except (ValueError, TypeError):
            logger.warning("Could not convert value '%s' to float", raw_value)
            return

        logger.info("%s: %.1f°C", sensor_id, temperature)
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
    setup_logging()
    client = create_client()

    try:
        logger.info("Connecting to MQTT broker at %s:%s...", MQTT_BROKER, MQTT_PORT)
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()
    except Exception as error:
        logger.error("Connection error: %s", error)


if __name__ == "__main__":
    run()
