import pytest
from types import SimpleNamespace

import main
from main import LOGGER_NAME, MQTT_TOPIC, on_connect, on_message, setup_logging


class DummyClient:
    def __init__(self):
        self.subscribed_topics = []

    def subscribe(self, topic):
        self.subscribed_topics.append(topic)


# ---------------------------------------------------------------------------
# on_connect
# ---------------------------------------------------------------------------

def test_on_connect_subscribes_to_topic(caplog):
    setup_logging()
    client = DummyClient()

    with caplog.at_level("INFO", logger=LOGGER_NAME):
        on_connect(client, None, None, 0)

    assert "Connected to MQTT broker successfully" in caplog.text
    assert client.subscribed_topics == [MQTT_TOPIC + "+"]


def test_on_connect_logs_error_on_failure(caplog):
    setup_logging()
    client = DummyClient()

    with caplog.at_level("ERROR", logger=LOGGER_NAME):
        on_connect(client, None, None, 1)

    assert "Connection failed with code 1" in caplog.text
    assert client.subscribed_topics == []


def test_on_disconnect_logs_warning_when_unexpected(caplog):
    setup_logging()

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        main.on_disconnect(None, None, None, 1)

    assert "Unexpected disconnection: 1" in caplog.text


# ---------------------------------------------------------------------------
# on_message — payloads válidos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("payload,expected_log", [
    (b"2345",  "23.45"),   # 23,45 °C
    (b"23",    "0.23"),    # 0,23 °C
    (b"10051", "100.51"),  # 100,51 °C
    (b"164",   "1.64"),    # 1,64 °C
    (b"-69",   "-0.69"),   # -0,69 °C
    (b"-210",  "-2.10"),   # -2,10 °C
    (b"0",     "0.00"),    # 0 °C
])
def test_on_message_logs_valid_temperature(payload, expected_log, caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35", payload=payload)

    main.VOTER.sensor_data.clear()

    with caplog.at_level("INFO", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert expected_log in caplog.text
    assert "lm35" in main.VOTER.sensor_data


# ---------------------------------------------------------------------------
# on_message — payloads inválidos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("payload", [
    b"36.0",      # float com ponto
    b"-2.10",     # float negativo com ponto
    b"23.45",     # float com ponto
    b"2412\xc2\xb0C",  # com unidade °C em UTF-8
    b"PING",      # texto não numérico
    b"",          # vazio
    b"1e3",       # notação científica
    b" ",         # só espaço
])
def test_on_message_warns_for_invalid_payload_format(payload, caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35", payload=payload)

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "Invalid payload format" in caplog.text


def test_on_message_warns_for_invalid_payload_encoding(caplog):
    setup_logging()
    msg = SimpleNamespace(topic="sensors/lm35", payload=b"\xff")

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "Could not decode payload as UTF-8" in caplog.text


# ---------------------------------------------------------------------------
# on_message — tópicos inválidos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", [
    "sensors/lm35/extra",   # dois níveis após sensors/
    "sensors/",             # sensor_id vazio
    "leituras/lm35",        # prefixo errado
])
def test_on_message_warns_for_unexpected_topic(topic, caplog):
    setup_logging()
    msg = SimpleNamespace(topic=topic, payload=b"2345")

    with caplog.at_level("WARNING", logger=LOGGER_NAME):
        on_message(None, None, msg)

    assert "Unexpected topic" in caplog.text


def test_on_message_updates_existing_sensor_value():
    setup_logging()
    main.VOTER.sensor_data.clear()

    first = SimpleNamespace(topic="sensors/lm35", payload=b"2100")
    second = SimpleNamespace(topic="sensors/lm35", payload=b"2200")

    on_message(None, None, first)
    on_message(None, None, second)

    assert main.VOTER.sensor_data["lm35"].raw_value == 2200
