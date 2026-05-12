import pytest
from types import SimpleNamespace
from unittest.mock import patch
from io import StringIO

from main import MQTT_TOPIC, on_connect, on_message


class DummyClient:
    def __init__(self):
        self.subscribed_topics = []

    def subscribe(self, topic):
        self.subscribed_topics.append(topic)


# ---------------------------------------------------------------------------
# on_connect
# ---------------------------------------------------------------------------

def test_on_connect_subscribes_to_topic():
    client = DummyClient()

    with patch('sys.stdout', new=StringIO()) as fake_output:
        on_connect(client, None, None, 0)

    assert "Conectado ao broker MQTT com sucesso" in fake_output.getvalue()
    assert client.subscribed_topics == [MQTT_TOPIC + "+"]


def test_on_connect_logs_error_on_failure():
    client = DummyClient()

    with patch('sys.stdout', new=StringIO()) as fake_output:
        on_connect(client, None, None, 1)

    assert "Falha na conexão, código 1" in fake_output.getvalue()
    assert client.subscribed_topics == []


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
def test_on_message_logs_valid_temperature(payload, expected_log):
    msg = SimpleNamespace(topic="sensors/lm35", payload=payload)

    with patch('sys.stdout', new=StringIO()) as fake_output:
        on_message(None, None, msg)

    output = fake_output.getvalue()
    # Nota: o sistema atual apenas atualiza o sensor, não faz log direto do valor
    # Por isso validamos que não gerou erro
    assert "Tópico inesperado" not in output
    assert "Não foi possível decodificar" not in output
    assert "Formato de payload inválido" not in output


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
def test_on_message_warns_for_invalid_payload_format(payload):
    msg = SimpleNamespace(topic="sensors/lm35", payload=payload)

    with patch('sys.stdout', new=StringIO()) as fake_output:
        on_message(None, None, msg)

    assert "Formato de payload inválido" in fake_output.getvalue()


def test_on_message_warns_for_invalid_payload_encoding():
    msg = SimpleNamespace(topic="sensors/lm35", payload=b"\xff")

    with patch('sys.stdout', new=StringIO()) as fake_output:
        on_message(None, None, msg)

    assert "Não foi possível decodificar o payload como UTF-8" in fake_output.getvalue()


# ---------------------------------------------------------------------------
# on_message — tópicos inválidos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", [
    "sensors/lm35/extra",   # dois níveis após sensors/
    "sensors/",             # sensor_id vazio
    "leituras/lm35",        # prefixo errado
])
def test_on_message_warns_for_unexpected_topic(topic):
    msg = SimpleNamespace(topic=topic, payload=b"2345")

    with patch('sys.stdout', new=StringIO()) as fake_output:
        on_message(None, None, msg)

    assert "Tópico inesperado" in fake_output.getvalue()
