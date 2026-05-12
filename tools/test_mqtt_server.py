import re
import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPICO_BASE = "sensors/"
QOS_ESPERADO = 0
RETAIN_ESPERADO = False
REGEX_INT_CENTESIMOS = re.compile(r"^-?\d+$")


def status(ok):
    return "OK" if ok else "FALHA"


def validar_topico(topic):
    if not topic.startswith(TOPICO_BASE):
        return False, "tópico fora de sensors/{sensor_id}", None

    sensor_id = topic[len(TOPICO_BASE):]
    if not sensor_id:
        return False, "sensor_id vazio", None

    if "/" in sensor_id:
        return False, "tópico com mais de um nível após sensors/", None

    return True, "tópico válido", sensor_id


def validar_payload(payload_bytes):
    try:
        payload_texto = payload_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return False, "payload não está em UTF-8", None

    if payload_texto != payload_texto.strip():
        return False, "payload contém espaços ou quebras de linha", payload_texto

    if not REGEX_INT_CENTESIMOS.fullmatch(payload_texto):
        return False, "payload não é inteiro", payload_texto

    return True, "payload válido", payload_texto


def exibir_resultado(msg):
    topico_ok, topico_motivo, sensor_id = validar_topico(msg.topic)
    payload_ok, payload_motivo, payload_texto = validar_payload(msg.payload)
    qos_ok = msg.qos == QOS_ESPERADO
    retain_ok = bool(msg.retain) == RETAIN_ESPERADO

    aprovado = topico_ok and payload_ok and qos_ok and retain_ok
    print(f"\n{'[APROVADO]' if aprovado else '[REPROVADO]'}")

    print(f"[{status(topico_ok)}] \tTópico: {msg.topic}")
    if not topico_ok:
        print(f"Motivo: {topico_motivo}")
    print(f"[{status(qos_ok)}] \tQoS: {msg.qos}")
    if not qos_ok:
        print(f"Motivo: QoS esperado {QOS_ESPERADO}")
    print(f"[{status(retain_ok)}] \tRetain: {bool(msg.retain)}")
    if not retain_ok:
        print(f"Motivo: Retain esperado {RETAIN_ESPERADO}")

    print(f"[{status(payload_ok)}] \tPayload: ", end="")
    if payload_texto is None:
        print(f"{msg.payload} <não decodificável em UTF-8>")
    else:
        print(f"'{payload_texto}'")

    if not payload_ok:
        print(f"Motivo: {payload_motivo}")
    elif topico_ok:
        temperatura_c = int(payload_texto) / 100.0
        print(f"{sensor_id}: \t{temperatura_c:.2f} °C")


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe("#")
        print(f"Conectado ao broker com sucesso.")
        print(f"IP/Porta: {mqtt.socket.gethostbyname(mqtt.socket.gethostname())}:{MQTT_PORT}")
        print("Aguardando mensagens para validação...")
    else:
        print(f"Falha ao conectar. Código de retorno: {rc}")


def on_disconnect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        print(f"Desconexão inesperada. Código: {rc}")
    else:
        print(f"Desconectado.")


def on_message(client, userdata, msg):
    exibir_resultado(msg)


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        print(f"Conectando em {MQTT_BROKER}:{MQTT_PORT}...")
        client.loop_forever()
    except KeyboardInterrupt:
        print("")
    except Exception as erro:
        print(f"Erro fatal: {erro}")


if __name__ == "__main__":
    main()