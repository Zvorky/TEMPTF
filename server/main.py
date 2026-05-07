try:
    import paho.mqtt.client as mqtt  
except Exception:
    mqtt = None

import time # Importado para controlar o ciclo de 5 segundos
from nmr import NMR


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/"

voter = None


def on_connect(client, _userdata, _flags, rc, _properties=None): # Função para se conectar ao MQTT
    if rc == 0: # Se a conexão for bem sucedida (código 0)...
        client.subscribe(MQTT_TOPIC + "+") # Se inscreve no tópico "sensors/+" . O '+' quer dizer "qualquer coisa"
        print("Conectado ao broker MQTT com sucesso")
        print(f"Executando em: {mqtt.socket.gethostbyname(mqtt.socket.gethostname())}:{MQTT_PORT}") # Algo assim: "Executando em: IP_LOCAL:PORTA"
    else:
        print(f"Falha na conexão, código {rc}")


def on_message(client, _userdata, msg): # Função para processar mensagens recebidas do MQTT
    try:
        if not msg.topic.startswith(MQTT_TOPIC): # Se o tópico da mensagem não começar com "sensors/", é um tópico inesperado
            print(f"Tópico inesperado '{msg.topic}'")
            return

        sensor_id = msg.topic[len(MQTT_TOPIC):] # Extrai o ID do sensor do tópico. Por exemplo, se o tópico for "sensors/sensor1", o sensor_id vai ser "sensor1"
        if not sensor_id or "/" in sensor_id: # Se não tiver um ID de sensor válido, é um tópico inesperado
            print(f"Tópico inesperado '{msg.topic}'")
            return

        try:
            payload = msg.payload.decode().strip() # Tenta decodificar o payload da mensagem como UTF-8 e remover espaços em branco no início e no fim
        except UnicodeDecodeError:
            print("Não foi possível decodificar o payload como UTF-8")
            return

        try:
            raw_value = int(payload) # Tenta transformar em int. Se o payload não for, não vale
        except ValueError:
            print(f"Formato de payload inválido '{payload}'")
            return

        # Agora o on_message APENAS atualiza o valor no votador.
        # A avaliação (votação) foi movida para o loop principal para respeitar o ciclo de 5s.
        if voter is not None:
            voter.update_sensor(sensor_id, raw_value) 
            # print(f"Log: {sensor_id} recebeu {raw_value/100:.2f} °C") # Opcional para debug
            
    except Exception as error:
        print(f"Erro ao receber mensagem: {error}")


def on_disconnect(client, _userdata, _flags, rc, _properties=None): 
    if rc != 0: # Se a desconexão não for intencional (código diferente de 0)...
        print(f"Desconexão inesperada: {rc}")


def create_client():
    if mqtt is None:
        raise RuntimeError("paho-mqtt não está instalado; instale com: pip install paho-mqtt")
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client 


def run():
    global voter
    voter = NMR()
    client = create_client()

    try:
        print(f"Conectando ao broker MQTT em {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        
        # loop_start inicia uma thread separada para o MQTT, não travando o código abaixo
        client.loop_start() 

        print("Iniciando loop de votação (Ciclo de 5 segundos)...")
        while True:
            # O trabalho exige uma medição a cada 5 segundos
            time.sleep(5) 
            
            # Realiza a votação com os dados acumulados no intervalo
            result = voter.evaluate() 
            
            if result['estado'] == "sem_dados":
                print("Aguardando dados dos sensores...")
            else:
                # Mostra a temperatura final e o estado conforme exigido
                # "TEMPTF: 23.45 °C (consenso)"
                temp_formatada = result['temperatura'] / 100
                print(f"TEMPTF: {temp_formatada:.2f} °C ({result['estado']})")

    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    except Exception as error:
        print(f"Erro de execução: {error}")
    finally:
        client.loop_stop() # Para a thread do MQTT com segurança
        client.disconnect()


if __name__ == "__main__":
    run()