from types import SimpleNamespace

from main import LOGGER_NAME, MQTT_TOPIC, on_connect, on_message, setup_logging


class DummyClient:
    def __init__(self):
        self.subscribed_topics = []

    def subscribe(self, topic):
        self.subscribed_topics.append(topic)


def test_on_connect_subscribes_to_topic(caplog):
    setup_logging()
    client = DummyClient()

    with caplog.at_level("INFO", logger=LOGGER_NAME):
        on_connect(client, None, None, 0)

    assert "Connected to MQTT broker successfully" in caplog.text
    assert client.subscribed_topics == [MQTT_TOPIC + "+"]


def test_on_message_logs_temperature_value(caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35", payload=b"36.0")

    with caplog.at_level("INFO", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "lm35: 36.0" in caplog.text


def test_on_message_warns_when_value_is_not_float(caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35", payload=b"PING")

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "Could not convert value 'PING' to float" in caplog.text


def test_on_message_warns_for_unexpected_topic(caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35/extra", payload=b"36.0")

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "Unexpected topic 'sensors/lm35/extra'" in caplog.text


def test_on_message_warns_for_invalid_payload_encoding(caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35", payload=b"\xff")

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "Could not decode payload as UTF-8" in caplog.text
