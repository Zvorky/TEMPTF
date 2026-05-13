import re
import time
import nmr

import paho.mqtt.client as mqtt

INTERVALO_LOOP_NMR = 5 
LOOP_NMR_ATIVO = False

BROKER_MQTT = "localhost"
PORTA_MQTT = 1883
TOPICO_MQTT = "sensors/"

# Se quiser debugar é só ativar o verboso
votador = nmr.NMR(tolerancia=10, passos_isolamento=3, passos_recuperacao=3, valor_falha=None, verboso=False)   # Instância do nmr


def on_connect(client, _userdata, flags, rc, _properties=None):
    if rc == 0:
        client.subscribe(TOPICO_MQTT + "+")
        print("Conectado ao broker MQTT com sucesso")
        print(f"Executando em: {mqtt.socket.gethostbyname(mqtt.socket.gethostname())}:{PORTA_MQTT}")
    else:
        print(f"Falha na conexão, código {rc}")


def on_message(_client, _userdata, msg):
    try:
        if msg.topic.startswith(TOPICO_MQTT):
            id_senso r = msg.topic[len(TOPICO_MQTT):]
        else:
            return

        if not id_sensor or "/" in id_sensor:
            return

        try:
            valor_bruto = msg.payload.decode().strip()
        except UnicodeDecodeError:
            print("Não foi possível decodificar o payload como UTF-8")
            return

        # Valida se o payload é um número inteiro (suporta negativos)
        if not re.fullmatch(r"-?\d+", valor_bruto):           # pode ou não começar com "-", com o restante sendo dígitos
            print(f"Formato de payload inválido '{valor_bruto}'")
            return

        # Passa o valor validado para o núcleo de votação
        votador.atualizar_sensor(id_sensor, int(valor_bruto))
            
    except Exception as erro:
        print(f"Erro ao processar mensagem: {erro}")


def on_disconnect(_client, _userdata, _flags, rc, _properties=None):
    if rc != 0:
        print(f"Desconexão inesperada: {rc}")


def criar_cliente():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client


def executar():
    global LOOP_NMR_ATIVO
    cliente = criar_cliente()

    try:
        print(f"Conectando ao broker MQTT em {BROKER_MQTT}:{PORTA_MQTT}...")
        cliente.connect(BROKER_MQTT, PORTA_MQTT, keepalive=60)
        cliente.loop_start() 
    except Exception as erro:
        print(f"Erro de conexão: {erro}")
        return

    time.sleep(1)
    print(f"Iniciando loop de votação (Ciclo de {INTERVALO_LOOP_NMR} segundos)")
    
    try:
        LOOP_NMR_ATIVO = True
        while LOOP_NMR_ATIVO:
            ultimo_tempo = time.time()
            votado = votador.avaliar()
            estado = votador.obter_estado()

            if estado == "SEM_DADOS":
                print("Aguardando dados dos sensores...")
            elif votado is None:
                print(f"NMR sem valor votado disponível (estado={estado})")
            else:
                # Mostra a temperatura final e o estado conforme exigido
                temperatura_formatada = votado / 100
                print(f"TEMPTF: {temperatura_formatada:.2f} °C ({estado.lower()})")

            # Busy Wait para garantir cravado os 5 segundos sem travar o processador
            while time.time() - ultimo_tempo < INTERVALO_LOOP_NMR:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        LOOP_NMR_ATIVO = False
    finally:
        cliente.loop_stop() 
        cliente.disconnect()


if __name__ == "__main__":
    executar()